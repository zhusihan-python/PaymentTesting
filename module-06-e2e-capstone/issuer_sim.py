"""
迷你发卡行核心模拟器（MiniIssuer）
整合：CMS 卡状态机、可用/冻结双桶账务、0100/0420 冲正与幂等、T+1 差额强制入账、钱包令牌联动、PCI-DSS 脱敏日志
"""
from decimal import Decimal
from typing import Dict, List


class MiniIssuer:
    def __init__(self) -> None:
        self.cards: Dict[str, Dict] = {}
        self.tokens: Dict[str, Dict] = {}       # dpan -> {fpan, device, status}
        self.txns: Dict[str, Dict] = {}         # stan -> {pan, amount, status}
        self.logs: List[str] = []

    @staticmethod
    def _mask_pan(pan: str) -> str:
        return f"{pan[:6]}{'*' * (len(pan) - 10)}{pan[-4:]}"

    def _log(self, msg: str) -> None:
        self.logs.append(msg)

    # --- CMS & Wallet ---
    def create_card(self, pan: str, balance_usd: str) -> None:
        self.cards[pan] = {
            "status": "ACTIVE",
            "available": Decimal(balance_usd),
            "frozen": Decimal("0.00"),
            "cleared": Decimal("0.00"),
        }
        self._log(f"INFO create_card pan={self._mask_pan(pan)} status=ACTIVE")

    def bind_wallet(self, pan: str, device_id: str) -> str:
        dpan = f"999900{len(self.tokens) + 1:010d}"
        self.tokens[dpan] = {"fpan": pan, "device": device_id, "status": "ACTIVE"}
        self._log(f"INFO bind_wallet pan={self._mask_pan(pan)} device={device_id}")
        return dpan

    def freeze_card(self, pan: str) -> None:
        self.cards[pan]["status"] = "SUSPENDED"
        for tok in self.tokens.values():
            if tok["fpan"] == pan and tok["status"] == "ACTIVE":
                tok["status"] = "SUSPENDED"
        self._log(f"INFO freeze_card pan={self._mask_pan(pan)} sync_tokens=OK")

    # --- ISO 8583 0100 Auth ---
    def auth_0100(self, pan: str, stan: str, amount_str: str) -> str:
        if not amount_str.isdigit():
            self._log(f"WARN auth_0100 stan={stan} f39=30 reason=MALFORMED_AMOUNT")
            return "30"

        amount = Decimal(amount_str) / Decimal("100")
        card = self.cards[pan]

        # 1. 卡状态校验
        if card["status"] != "ACTIVE":
            self._log(f"WARN auth_0100 pan={self._mask_pan(pan)} stan={stan} f39=62")
            return "62"

        # 2. 乱序预冲正拦截
        if stan in self.txns and self.txns[stan]["status"] == "PRE_REVERSED":
            self.txns[stan]["status"] = "REVERSED"
            self._log(f"WARN auth_0100 stan={stan} f39=05 reason=PRE_REVERSED_HIT")
            return "05"

        # 3. 余额校验与冻结
        if card["available"] < amount:
            self._log(f"WARN auth_0100 pan={self._mask_pan(pan)} stan={stan} f39=51")
            return "51"

        card["available"] -= amount
        card["frozen"] += amount
        self.txns[stan] = {"pan": pan, "amount": amount, "status": "AUTHORIZED"}
        self._log(f"INFO auth_0100 pan={self._mask_pan(pan)} stan={stan} amt={amount} f39=00")
        return "00"

    # --- ISO 8583 0420 Reversal ---
    def reversal_0420(self, pan: str, stan: str) -> str:
        # 情况 A：冲正先于原交易到达 -> 写入预冲正占位
        if stan not in self.txns:
            self.txns[stan] = {"pan": pan, "amount": Decimal("0.00"), "status": "PRE_REVERSED"}
            self._log(f"WARN reversal_0420 stan={stan} action=PRE_REVERSED_CREATED")
            return "00"

        txn = self.txns[stan]
        # 情况 B：重复冲正 -> 幂等直接返回成功，不重复退钱
        if txn["status"] in ("REVERSED", "PRE_REVERSED"):
            self._log(f"INFO reversal_0420 stan={stan} action=IDEMPOTENT_SKIP")
            return "00"

        # 情况 C：正常超时冲正 -> 释放冻结额度
        card = self.cards[pan]
        card["frozen"] -= txn["amount"]
        card["available"] += txn["amount"]
        txn["status"] = "REVERSED"
        self._log(f"INFO reversal_0420 pan={self._mask_pan(pan)} stan={stan} f39=00")
        return "00"

    # --- T+1 Clearing (Force Post) ---
    def clearing_t1(self, stan: str, actual_amount_usd: str) -> None:
        txn = self.txns[stan]
        card = self.cards[txn["pan"]]
        actual = Decimal(actual_amount_usd)
        diff = actual - txn["amount"]

        card["frozen"] -= txn["amount"]
        card["available"] -= diff      # 允许扣成负数（Force Post）
        card["cleared"] += actual
        txn["status"] = "CLEARED"

        if card["available"] < Decimal("0.00"):
            card["status"] = "SUSPENDED"  # 欠款自动风控冻结
        self._log(f"INFO clearing_t1 stan={stan} actual={actual} avail={card['available']}")