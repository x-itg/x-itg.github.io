<p align="center">
  <img src="https://img.shields.io/badge/license-CC_BY--SA_4.0-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/status-Active-brightgreen?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/methodology-Harness_Engineering-blue?style=flat-square" alt="Methodology">
  <img src="https://img.shields.io/badge/topics-Embedded_AI%20|%20Toolchain%20|%20Agents-orange?style=flat-square" alt="Topics">
  <img src="https://img.shields.io/badge/articles-10+4-orange?style=flat-square" alt="Articles">
  <img src="https://img.shields.io/badge/pages-live-222?style=flat-square&logo=github" alt="GitHub Pages">
</p>

# 嵌入式 AI 工程化体系

> **为 AI 立宪：让代码在物理世界中负责任地运行。**

这是一个从真实嵌入式开发痛点中生长出来的完整方法论体系。它回答了一个核心问题：**如何让 AI 生成的代码，从"能在 IDE 里运行"进化到"能在残酷物理世界中安全、可观测、可演化地自治"？**

这套方法论是在**十二年一线嵌入式开发**中，近些年来与 AI 深度协作、持续迭代的产物。如今以十篇体系文章完整呈现，并已部署为静态站点可在线阅读。

👉 **在线阅读：[https://x-itg.github.io](https://x-itg.github.io)**

---

## 🧭 技术体系概览

本系列共十篇文章，以**一纵一横一应用**的架构覆盖嵌入式 AI 工程化的全生命周期：

| 维度 | 文章 | 定位 |
|------|------|------|
| **纵轴 · 核心进化** | ①~⑤ | 定义"未来的系统怎么建"：从可观测性到自治演化的五层进化 |
| **横轴 · 旧项目解放** | ⑥~⑧ | 承接"过去的项目怎么救"：扩展维度中的工程遗产与协同基础设施 |
| **应用层** | ⑨~⑩ | 覆盖"日常的工作怎么用"：Skills 与合规验证让体系落地 |

十篇文章共同构成了 **Core 层（法则与基础设施）** + **Skill 层（快消费应用方法）** + **Governance 层（合规与验证）** 的多层共生架构。

---

## 📚 技术系列文章导航

### ① 五层进化：从"摸黑调试"到"拨云见日" — *总纲*
> 定义问题域与成熟度坐标系。

提出嵌入式 AI 编程的五层进化模型（L0~L5），原创"负日志"概念，让 AI 能够"看见"那些应该发生却未发生的物理事件。这是整个体系的**总纲**。

- 📄 [阅读全文](https://x-itg.github.io/index.html)

### ② 高复用模板：嵌入式 AI 编程的工程骨架 — *执行基础*
> 将方法论固化为可落地的工程骨架。

提供从固件（STM32）、上位机（Python/Qt）到调试助手的完整项目模板，让可观测性与闭环反馈内建到每一个新项目中。

- 📄 [阅读全文](https://x-itg.github.io/true.html)

### ③ 闭环收敛方法：代码修复与测试增强的自治闭环 — *自驱灵魂*
> 注入自驱灵魂，让系统自己变强。

设计了双轨收敛机制与 ConvergenceAgent，让 AI 能同时驱动代码修复与测试增强，形成螺旋上升的质量改进循环。

- 📄 [阅读全文](https://x-itg.github.io/test.html)

### ④ 从收敛到进化：决策维度 — *决策智慧*
> 构建具备决策智慧的自治系统。

融合闭环收敛、共生演化与决策切换的完整框架。提出三重智能（执行智能、记忆智能、判断智能）与 Agent 四种性格制衡，是整座殿堂的拱心石。

- 📄 [阅读全文](https://x-itg.github.io/fwd.html)

### ⑤ PCB 电路图分析器：打通物理世界的最后一百米 — *硬件感知*
> 让 AI 拥有"阅读硬件"的能力。

开发 PDF 电路图解析与 VSCode 关联工具，使 AI 可以理解电路原理图，并一键跳转至相关代码行，真正贯通物理与数字的认知屏障。

- 📄 [阅读全文](https://x-itg.github.io/pcb.html)

### ⑥ 知识的生命体征：为 AI 编程工程化立宪 — *知识资产*
> 知识资产 · 主动协作。

提出知识文档的三重生命体征体系：热力分布图、健康度分析、唤醒关键词。配合中央监视器与决策账本，让知识资产从被动存储进化为主动协作，具备持续自我修复能力。

- 📄 [阅读全文](https://x-itg.github.io/exc.html)

### ⑦ 历史的包袱：Keil/IAR 老项目的解放之路 — *工程遗产*
> 向现实俯身，处理工程遗产。

提出防御-抽象-进攻三层策略，将那些被封闭 IDE 死锁的老项目逐步翻译、解耦、迁入 AI 友好生态，让历史不再是负资产。

- 📄 [阅读全文](https://x-itg.github.io/history.html)

### ⑧ 最后的拼图：Skills — *快消费应用*
> 让高速公路上的车跑起来。

定义 Core 层之上的 Skill 应用层。以"规则感知型 Skill"为核心理念，演示如何在项目规约、硬件上下文和决策账本的加持下，实现 5 分钟即插即用的嵌入式驱动开发。

- 📄 [阅读全文](https://x-itg.github.io/pt.html)

### ⑨ 固件铭牌与设备画像 — *协同基础设施*
> 让固件携带"身份证"，让设备会"说话"。

提出固件铭牌系统与设备画像框架，实现多设备协同场景下的自动识别、版本追溯与配置同步，将多设备管理的复杂性变成可感知、可校验、可追溯的工程系统。

- 📄 [阅读全文](https://x-itg.github.io/devs.html)

### ⑩ 合规验证与AI编程 — *治理维度*
> 当合规验证撞上AI编程。

将合规要求从"事后补文档"转变为"事前建法则"的工程化方法。探讨如何在军工、医疗、汽车等需要严格合规的场景中，让 AI 编程既有创造力又有边界感。

- 📄 [阅读全文](https://x-itg.github.io/gmp.html)

---

## 🌿 生活随记系列

除了技术体系之外，也有一组关于作者个人思考与生活感悟的文章，以相同的工程思维审视日常世界：

| 文章 | 主题 |
|------|------|
| 🪶 [我找到了一套法则](https://x-itg.github.io/about.html) | 凌晨两点的示波器，是灵感的起点 |
| 🧠 [以不变应万变](https://x-itg.github.io/aboutmore/tk.html) | 从AI编程到生活法则的认知升维 |
| 🪄 [用工程魔法打败生活魔法](https://x-itg.github.io/aboutmore/fw.html) | 一套思想体系的七种不正经应用 |
| ❤️ [我用调试AI的方法，学会了经营感情](https://x-itg.github.io/aboutmore/sc.html) | 当工程法则走出代码，走进亲密关系 |

---

## 🧠 核心哲学

- **意图定义者 > 代码执行者**：人的核心价值从"编写指令"跃迁为"定义约束和边界"。
- **可观测性即权利**：结构化日志是 AI 在物理世界中的"眼睛"；正日志记录"发生了什么"，负日志捕获"应该发生却未发生"。
- **闭环是思维，契约是边界**：每一次修改必须有新日志驱动；用提示词模板和规约文件限制 AI 的输出空间。
- **共生而非替代**：人保有最终裁决权，AI 负责追踪分歧、展示后果、请求决策。
- **法则从实践中来**：真正的规律不是从书本到书本，而是从实践到理论——从淤青中长出铠甲。

---

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| **嵌入式平台** | STM32 (ARM Cortex-M)、ESP32 |
| **固件语言** | C (CMSIS / HAL / FreeRTOS) |
| **上位机 / 工具链** | Python (PyQt6, pyserial), Make, OpenOCD, JLink |
| **AI 协作** | 结构化日志、负日志引擎、ConvergenceAgent、Spec-Drift Sniffer |
| **文档与可视化** | Markdown, PyMuPDF, PaddleOCR / Tesseract, Matplotlib |
| **编辑与集成** | VSCode (tasks.json, Cline/Continue), Git |

---

## 🚀 如何使用这个体系

1. **新项目启动**：从"高复用模板"开始，用"五层进化"的框架指导架构设计。
2. **日常开发**：运用"Skills"快速生成符合规约的驱动与模块。
3. **调试与迭代**：依靠"闭环收敛方法"让 AI 自动驱动质量改进。
4. **老项目维护**：遵循"历史的包袱"中的三层策略，渐进式解放遗产代码。
5. **团队与长期维护**：用"共生演化"管理 `agents.md` 和决策账本，确保知识不随人员更替流失。

---

## 🖥️ IDE 插件演示

本体系配套提供了一套完整的 **IDE AI 工程工具** Web 演示系统，真实模拟了与 VSCode 等主流 IDE 集成的工具界面。

### 在线演示

👉 **立即体验**：[IDE AI Engineering Tools](https://x-itg.github.io/ide_plugins/web/index.html)

### 演示工具一览

| 工具模块 | 功能描述 |
|---------|---------|
| 📜 **法则管理器** | 管理项目规约网络，定义 AI 执行边界 |
| 📊 **负日志监控器** | 实时监控期望事件与实际事件的分歧 |
| 🎯 **收敛引擎** | 追踪 Bug 修复与测试增强的收敛进度 |
| 🔧 **电路图导航器** | PCB 原理图与代码行的双向跳转 |
| 📈 **知识体征仪表盘** | 知识库热力分布与健康度监控 |
| 🚀 **Skills 启动台** | 一键启动高频嵌入式开发任务 |
| 遗 **遗产项目适配器** | Keil/IAR 老项目的渐进式迁移 |

### 配套示例项目

演示系统配合一个完整的 **嵌入式温湿度监控系统** 示例项目：

```
ide_plugins/
├── web/
│   └── index.html          # IDE 工具演示界面
└── demo_project/
    ├── docs/                # 知识文档（含 I2C 驱动规范）
    ├── hardware/            # 硬件配置
    ├── src/                 # 源代码
    ├── tests/               # 测试文件
    ├── README.md            # 项目说明
    └── run_demo.py          # 演示运行脚本
```

#### 项目硬件配置

- **MCU**: STM32F407VG
- **传感器**: SHT40 (I2C 接口)
- **通信**: RS485 (Modbus RTU)
- **显示**: 0.96" OLED (SPI 接口)

---

## 🙋 关于作者

**itg**，一位擅长用 AI 构建复杂工程体系的嵌入式实践者。

这套方法论是他在**十二年一线嵌入式开发**中，近些年来与 AI 深度协作、持续迭代的产物。它不是一套纸上谈兵的理论，而是从真实物理世界的残酷调试中生长出来的生存工具。它是教程，更是一部个人工作纲领——它会随实践持续演化。

> 除了技术，作者也用同样的工程思维审视生活。从"凌晨两点的示波器"到"用调试AI的方法学会经营感情"——这些思考构成了"生活随记"系列，与工程体系互为映照。

📧 技术交流或合作洽谈：请通过 GitHub Issues 或 Discussions 联系。

---

## 🤝 贡献与反馈

这套体系是一个**活的纲领**——它会随我的实践和社区的反馈持续演化。如果你：

- 发现了文章中的疏漏或可改进之处
- 有相关的实践经验想要分享
- 对某个方向有深入探讨的兴趣

欢迎通过以下方式参与：

- 🐛 **提出问题**：[GitHub Issues](https://github.com/x-itg/x-itg.github.io/issues)
- 💬 **发起讨论**：[GitHub Discussions](https://github.com/x-itg/x-itg.github.io/discussions)
- 🔀 **提交改进**：Fork 本仓库，修改后提交 Pull Request

所有建设性的反馈都将被认真对待——这是我方法论中"共生演化"哲学在知识资产上的自我实践。

---

## 📄 许可证

本作品采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可证进行许可。你可以自由地分享、改编本作品，但必须注明原作者并以相同方式共享。

---

## 🌐 在线浏览

本系列已部署为静态站点，访问以下地址即可阅读全部文章：

👉 **[https://x-itg.github.io](https://x-itg.github.io)**

---

<sub align="center">© x-itg | 遵循"人定义法则，AI 在法则内执行"原则构建</sub>
