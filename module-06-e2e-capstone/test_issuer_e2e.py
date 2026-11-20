"""
Module 6 端到端自动化测试套件
运行方式：pytest -v
"""
import re
from decimal import Decimal
import pytest
from issuer_sim import MiniIssuer

TEST_PAN = "4111111111111111"


def is_valid_luhn(number: str) -> bool:
    if not number.isdigit():
        return False
    digits = [int(d) for d in number]
    checksum = 0
    for idx, d in enumerate(reversed(digits)):
        if idx % 2 == 1:
            d = d * 2 - 9 if d * 2 > 9 else d * 2
        checksum += d
    return checksum % 10 == 0


@pytest.fixture
def issuer() -> MiniIssuer:
    sim = MiniIssuer()
    sim.create_card(TEST_PAN, "100.00")
    return sim


def test_wallet_token_lifecycle_sync(issuer: MiniIssuer):
    """Module 5: 主卡冻结同步挂起所有关联设备令牌，且拦截新授权"""
    dpan_iphone = issuer.bind_wallet(TEST_PAN, "iPhone-16")
    dpan_watch = issuer.bind_wallet(TEST_PAN, "Apple-Watch")

    issuer.freeze_card(TEST_PAN)

    assert issuer.cards[TEST_PAN]["status"] == "SUSPENDED"
    assert issuer.tokens[dpan_iphone]["status"] == "SUSPENDED"
    assert issuer.tokens[dpan_watch]["status"] == "SUSPENDED"
    assert issuer.auth_0100(TEST_PAN, "000101", "000000001000") == "62"


def test_iso8583_malformed_and_insufficient_funds(issuer: MiniIssuer):
    """Module 3: 超额返回 F39=51，畸形金额返回 F39=30，均不冻结资金"""
    assert issuer.auth_0100(TEST_PAN, "000201", "000000020000") == "51"
    assert issuer.auth_0100(TEST_PAN, "000202", "INVALID_AMT") == "30"
    assert issuer.cards[TEST_PAN]["frozen"] == Decimal("0.00")


def test_reversal_out_of_order_and_idempotency(issuer: MiniIssuer):
    """Module 2: 冲正先到拦截迟到授权 + 重复冲正幂等不重复退钱"""
    # 1. 乱序：0420 先于 0100 到达
    assert issuer.reversal_0420(TEST_PAN, "000301") == "00"
    assert issuer.auth_0100(TEST_PAN, "000301", "000000005000") == "05"
    assert issuer.cards[TEST_PAN]["available"] == Decimal("100.00")

    # 2. 幂等：正常授权后连续发送两次相同 0420
    assert issuer.auth_0100(TEST_PAN, "000302", "000000004000") == "00"
    assert issuer.cards[TEST_PAN]["available"] == Decimal("60.00")
    assert issuer.reversal_0420(TEST_PAN, "000302") == "00"
    assert issuer.reversal_0420(TEST_PAN, "000302") == "00"  # 重复冲正
    assert issuer.cards[TEST_PAN]["available"] == Decimal("100.00")
    assert issuer.cards[TEST_PAN]["frozen"] == Decimal("0.00")


def test_auth_and_diff_clearing_force_post(issuer: MiniIssuer):
    """Module 1 & 2: $100 授权 -> T+1 $105 差额强行入账并触发欠款冻结"""
    assert issuer.auth_0100(TEST_PAN, "000401", "000000010000") == "00"
    assert issuer.cards[TEST_PAN]["available"] == Decimal("0.00")
    assert issuer.cards[TEST_PAN]["frozen"] == Decimal("100.00")

    issuer.clearing_t1("000401", "105.00")

    assert issuer.cards[TEST_PAN]["frozen"] == Decimal("0.00")
    assert issuer.cards[TEST_PAN]["available"] == Decimal("-5.00")
    assert issuer.cards[TEST_PAN]["cleared"] == Decimal("105.00")
    assert issuer.cards[TEST_PAN]["status"] == "SUSPENDED"


def test_pcidss_log_compliance_gate(issuer: MiniIssuer):
    """Module 4: 扫描全量业务日志，确保零明文 PAN 与零 SAD 泄露"""
    issuer.bind_wallet(TEST_PAN, "iPhone-16")
    issuer.auth_0100(TEST_PAN, "000501", "000000002000")
    issuer.reversal_0420(TEST_PAN, "000501")

    pan_pattern = re.compile(r"\b\d{13,19}\b")
    sad_pattern = re.compile(r"(?i)\b(?:cvv|cvc|pin)\s*=\s*([^\s,]+)")

    for line in issuer.logs:
        for num in pan_pattern.findall(line):
            assert not is_valid_luhn(num), f"PCI-DSS 违规：日志泄露明文 PAN -> {line}"
        for sad in sad_pattern.findall(line):
            assert set(sad) <= {"*"}, f"PCI-DSS 违规：日志泄露明文 SAD -> {line}"