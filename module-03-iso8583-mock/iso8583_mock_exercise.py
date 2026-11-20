"""
Module 3 实战练习：ISO 8583 位图计算与简易发卡行 Mock 挡板
运行方式：python3 iso8583_mock_exercise.py
目标：补全 build_primary_bitmap()、pack_iso8583() 和 mock_issuer_auth()，使底部断言全部通过。
"""
from typing import Dict


def build_primary_bitmap(field_numbers: list[int]) -> str:
    """
    TODO 1: 根据传入的域编号列表（范围 1-64），生成 16 位大写十六进制 Primary Bitmap。
    示例：field_numbers = [2, 3, 4, 11]
    - 第 2, 3, 4 位为 1 -> 前 4 位二进制 0111 -> Hex '7'
    - 第 5-8 位为 0 -> '0'
    - 第 9-12 位中第 11 位为 1 -> 0010 -> Hex '2'
    - 其余全 0 -> 返回 '7020000000000000'
    """
    bits = ["0"] * 64
    # --- 在下方编写你的代码 ---

    return ""


def pack_iso8583(mti: str, fields: Dict[int, str]) -> str:
    """
    TODO 2: 组装简化版 ISO 8583 报文：MTI + 16位Hex Bitmap + 按域号升序拼接的字段值。
    """
    # --- 在下方编写你的代码 ---

    return ""


def mock_issuer_auth(balance_cents: int, req_fields: Dict[int, str]) -> Dict[int, str]:
    """
    TODO 3: 模拟发卡行 0100 授权处理逻辑，返回 0110 响应字段字典（包含原 F11 与 F39）：
    - 若缺少 F4（金额）或 F4 不是纯数字 -> 返回 F39 = "30"（格式错误）
    - 若 int(F4) > balance_cents -> 返回 F39 = "51"（余额不足）
    - 否则 -> 返回 F39 = "00"（授权通过）
    """
    resp = {11: req_fields.get(11, "000000")}
    # --- 在下方编写你的代码 ---

    return resp


if __name__ == "__main__":
    # 测试 1：Bitmap 计算
    bmp = build_primary_bitmap([2, 3, 4, 11])
    assert bmp == "7020000000000000", f"Bitmap 计算错误: {bmp}"

    # 测试 2：报文组装
    raw = pack_iso8583("0100", {11: "000123", 4: "000000010000", 2: "164111111111111111", 3: "000000"})
    assert raw == "01007020000000000000164111111111111111000000000000010000000123", f"报文组装错误: {raw}"

    # 测试 3：Mock 发卡行响应码注入
    assert mock_issuer_auth(10000, {4: "000000005000", 11: "000001"})[39] == "00"
    assert mock_issuer_auth(10000, {4: "000000020000", 11: "000002"})[39] == "51"
    assert mock_issuer_auth(10000, {4: "INVALID_AMT", 11: "000003"})[39] == "30"

    print("✅ Module 3 所有 ISO 8583 协议与 Mock 断言全部通过！")