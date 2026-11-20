# PaymentTesting
这份教程专为支付发卡行测试（CMS / 协议 / 安全 / 钱包）量身定制

# 💳 PaymentTesting — 支付发卡行测试交互式实战教程

> 面向 **发卡行核心系统（CMS）/ 加密支付卡 / 国际卡组织（Visa/Mastercard）** 的端到端测试学习与实战工程。  
> 遵循 **最小认知负荷（Minimal Cognitive Load）** 理念，结合 **交互式分步数据流图（DFD）**、**浏览器内 Python 编程沙箱（Pyodide）** 与 **本地 Pytest 自动化框架**，系统化攻克支付领域核心痛点。

🌐 **在线交互式教程（GitHub Pages）：**  
👉 **[点击立即体验 PaymentTesting 在线演示](https://zhusihan-python.github.io/PaymentTesting/)**

---

## ✨ 作品集亮点（Why This Repo）

1. **零环境配置，开箱即用：** Module 1–5 均以单文件 HTML 承载交互式分步 DFD，Module 2–4 内置 **Pyodide（WebAssembly 版 Python 3）**，访问者无需本地配环境即可在浏览器中直接编写代码并运行 `assert` 断言。
2. **聚焦真实金融资损与合规红线：** 不止于正向功能测试，重点拆解**在途资金冻结、T+1 差额强制入账（Force Post）、0420 超时冲正乱序与幂等、PCI-DSS 日志脱敏扫描**以及 **Apple/Google Pay 多设备令牌联动**。
3. **贴近生产的工程化闭环：** Module 6 提供解耦的被测发卡行模拟器（`MiniIssuer`）与标准 `pytest` 端到端测试套件，涵盖协议异常注入、资金守恒校验与 CI/CD 合规门禁。

---

## 🗺️ 学习路径与模块总览

| 模块 | 主题 | 核心知识点 | 在线交互教程 | 动手实战练习 |
| :--- | :--- | :--- | :--- | :--- |
| **Module 01** | **支付基石与 CMS 状态机** | 联机授权 vs T+1 清算、可用/冻结双桶账务、卡生命周期状态机 | [交互式 DFD](https://zhusihan-python.github.io/PaymentTesting/module-01-cms-basics/index.html) | [需求评审挑刺沙箱](https://zhusihan-python.github.io/PaymentTesting/module-01-cms-basics/exercise.html) |
| **Module 02** | **支付异常与资损防控** | 超时 `0420` 冲正、乱序预冲正占位、重复冲正幂等、T+1 长短款对账 | [交互式 DFD](https://zhusihan-python.github.io/PaymentTesting/module-02-reconciliation/index.html) | [Python 对账沙箱](https://zhusihan-python.github.io/PaymentTesting/module-02-reconciliation/exercise.html) |
| **Module 03** | **ISO 8583 协议与 Mock 挡板** | MTI、64 位 Bitmap 位图计算、核心数据元（F2/F4/F11/F39/F55）、畸形报文 | [Bitmap 组装器](https://zhusihan-python.github.io/PaymentTesting/module-03-iso8583-mock/index.html) | [Python 模拟器沙箱](https://zhusihan-python.github.io/PaymentTesting/module-03-iso8583-mock/exercise.html) |
| **Module 04** | **EMV 与 PCI-DSS 安全合规** | ARQC/ARPC 验签、HSM/PIN Block、CHD/SAD 红线、Luhn 算法日志扫描 | [CHD 审计 DFD](https://zhusihan-python.github.io/PaymentTesting/module-04-emv-pcidss/index.html) | [Python 合规扫描器](https://zhusihan-python.github.io/PaymentTesting/module-04-emv-pcidss/exercise.html) |
| **Module 05** | **数字钱包与令牌化** | Apple/Google Pay、FPAN vs DPAN、VTS/MDES、ID&V 绿/黄/红通、挂失联动 | [绑卡联动 DFD](https://zhusihan-python.github.io/PaymentTesting/module-05-digital-wallets/index.html) | [生命周期测试矩阵](https://zhusihan-python.github.io/PaymentTesting/module-05-digital-wallets/exercise.html) |
| **Module 06** | **端到端发卡行自动化实战** | 串联前 5 章的完整 `pytest` 自动化测试框架与 CI/CD 合规门禁 | [E2E 闭环架构](https://zhusihan-python.github.io/PaymentTesting/module-06-e2e-capstone/index.html) | [本地 Pytest 工程](./module-06-e2e-capstone/) |

---

## 📂 仓库目录结构

```text
PaymentTesting/
├── index.html                          # 在线教程总导航页（GitHub Pages 入口）
├── README.md                           # 项目说明文档
├── module-01-cms-basics/
│   ├── index.html                      # 核心心智模型 + 授权/清算双链路 DFD
│   └── exercise.html                   # 稳定币虚拟卡需求评审交互沙箱
├── module-02-reconciliation/
│   ├── index.html                      # 异常防控模型 + 0420 冲正/乱序/幂等 DFD
│   ├── exercise.html                   # 浏览器 Pyodide 版 T+1 对账练习
│   └── reconcile_exercise.py           # 本地版对账脚本练习
├── module-03-iso8583-mock/
│   ├── index.html                      # ISO 8583 报文结构 + 交互式 Bitmap 组装器
│   ├── exercise.html                   # 浏览器 Pyodide 版协议打包与 Mock 练习
│   └── iso8583_mock_exercise.py        # 本地版模拟器脚本练习
├── module-04-emv-pcidss/
│   ├── index.html                      # EMV/PCI-DSS 红线 + CHD 数据流审计 DFD
│   └── exercise.html                   # 浏览器 Pyodide 版 Luhn + 正则日志扫描器
├── module-05-digital-wallets/
│   ├── index.html                      # Tokenization 原理 + 多设备挂失联动 DFD
│   └── exercise.html                   # 交互式多设备生命周期测试矩阵
└── module-06-e2e-capstone/
    ├── index.html                      # 端到端自动化测试闭环架构图
    ├── issuer_sim.py                   # 迷你发卡行核心模拟器（MiniIssuer）
    └── test_issuer_e2e.py              # Pytest 端到端自动化测试套件
```

---

## 🚀 本地运行 Module 6（Pytest 端到端测试）

```bash
# 1. 克隆仓库
git clone [https://github.com/zhusihan-python/PaymentTesting.git](https://github.com/zhusihan-python/PaymentTesting.git)
cd PaymentTesting/module-06-e2e-capstone

# 2. 安装 pytest
pip install pytest

# 3. 运行全部 5 个端到端核心用例（含状态机、冲正幂等、强行入账、PCI-DSS 日志门禁）
pytest -v
```

---

## 🛠️ 技术栈

- **测试与工程：** Python 3, Pytest, Decimal 金融精度计算, 正则与 Luhn 算法校验
- **领域协议与标准：** ISO 8583, EMV (ARQC/ARPC), PCI-DSS (CHD/SAD/CDE), Tokenization (VTS/MDES)
- **交互可视化：** 原生 HTML5 / CSS3 / Vanilla JS, Pyodide (WebAssembly), GitHub Pages