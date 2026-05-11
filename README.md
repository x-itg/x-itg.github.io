<p align="center">
  <img src="https://img.shields.io/badge/license-CC_BY--SA_4.0-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/status-Active-brightgreen?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/methodology-Harness_Engineering-blue?style=flat-square" alt="Methodology">
  <img src="https://img.shields.io/badge/topics-Embedded_AI%20|%20Toolchain%20|%20Agents-orange?style=flat-square" alt="Topics">
  <img src="https://img.shields.io/badge/pages-live-222?style=flat-square&logo=github" alt="GitHub Pages">
</p>

# 嵌入式 AI 工程化体系

> **为 AI 立宪：让代码在物理世界中负责任地运行。**

这是一个从真实嵌入式开发痛点中生长出来的完整方法论体系。它回答了一个核心问题：**如何让 AI 生成的代码，从“能在 IDE 里运行”进化到“能在残酷物理世界中安全、可观测、可演化地自治”？**

这套方法论并非空谈——它是在**十二年一线嵌入式开发**中，近些年来与 AI 深度协作、持续迭代的产物。如今，它以七篇体系文章的形式完整呈现，并已部署为静态站点，可直接在线阅读。

👉 **在线阅读：[https://x-itg.github.io](https://x-itg.github.io)**

---

## 🧭 体系概览

本系列共七篇文章，以**一纵一横**的架构，覆盖了嵌入式 AI 工程化的全生命周期：

| 维度 | 文章 | 定位 |
|------|------|------|
| **纵轴** | ①~⑤ | 定义"未来的系统怎么建"：从可观测性到自治演化的五层进化 |
| **横轴** | ⑥ | 承接"过去的项目怎么救"：让封闭 IDE 的老项目进入 AI 协作生态 |
| **应用层** | ⑦ | 覆盖"日常的工作怎么用"：Skills 让高频需求享受体系红利 |

七篇文章共同构成了 **Core 层（法则与基础设施）** + **Skill 层（快消费应用方法）** 的双层共生架构。

---

## 📚 系列文章导航

### ① 五层进化：从"摸黑调试"到"拨云见日"
> 定义问题域与成熟度坐标系。

提出嵌入式 AI 编程的五层进化模型（L0~L5），原创"负日志"概念，让 AI 能够"看见"那些应该发生却未发生的物理事件。这是整个体系的**总纲**。

- 📄 [阅读全文](https://x-itg.github.io/index.html)

### ② 高复用模板：嵌入式 AI 编程的工程骨架
> 将方法论固化为可落地的工程骨架。

提供从固件（STM32）、上位机（Python/Qt）到调试助手的完整项目模板，让可观测性与闭环反馈内建到每一个新项目中。

- 📄 [阅读全文](https://x-itg.github.io/true.html)

### ③ 闭环收敛方法：代码修复与测试增强的自治闭环
> 注入自驱灵魂，让系统自己变强。

设计了双轨收敛机制与 ConvergenceAgent，让 AI 能同时驱动代码修复与测试增强，形成螺旋上升的质量改进循环。

- 📄 [阅读全文](https://x-itg.github.io/test.html)

### ④ PCB 电路图分析器：打通物理世界的最后一百米
> 让 AI 拥有"阅读硬件"的能力。

开发 PDF 电路图解析与 VSCode 关联工具，使 AI 可以理解电路原理图，并一键跳转至相关代码行，真正贯通物理与数字的认知屏障。

- 📄 [阅读全文](https://x-itg.github.io/pcb.html)

### ⑤ 知识的生命体征：为 AI 编程工程化立宪
> 知识资产 · 主动协作。

提出知识文档的三重生命体征体系：热力分布图、健康度分析、唤醒关键词。配合中央监视器与决策账本，让知识资产从被动存储进化为主动协作，具备持续自我修复能力。

- 📄 [阅读全文](https://x-itg.github.io/exc.html)

### ⑥ 历史的包袱：Keil/IAR 老项目的解放之路
> 向现实俯身，处理工程遗产。

提出防御-抽象-进攻三层策略，将那些被封闭 IDE 死锁的老项目逐步翻译、解耦、迁入 AI 友好生态，让历史不再是负资产。

- 📄 [阅读全文](https://x-itg.github.io/history.html)

### ⑦ 最后的拼图：Skills
> 让高速公路上的车跑起来。

定义 Core 层之上的 Skill 应用层。以"规则感知型 Skill"为核心理念，演示如何在项目规约、硬件上下文和决策账本的加持下，实现 5 分钟即插即用的嵌入式驱动开发。

- 📄 [阅读全文](https://x-itg.github.io/pt.html)

---

## 🧠 核心哲学

- **意图定义者 > 代码执行者**：人的核心价值从"编写指令"跃迁为"定义约束和边界"。
- **可观测性即权利**：结构化日志是 AI 在物理世界中的"眼睛"；正日志记录"发生了什么"，负日志捕获"应该发生却未发生"。
- **闭环是思维，契约是边界**：每一次修改必须有新日志驱动；用提示词模板和规约文件限制 AI 的输出空间。
- **共生而非替代**：人保有最终裁决权，AI 负责追踪分歧、展示后果、请求决策。

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

## 🙋 关于作者

**itg**，一位擅长用 AI 构建复杂工程体系的嵌入式实践者。

这套方法论是他在**十二年一线嵌入式开发**中，近些年来与 AI 深度协作、持续迭代的产物。它不是一套纸上谈兵的理论，而是从真实物理世界的残酷调试中生长出来的生存工具。它是教程，更是一部个人工作纲领——它会随实践持续演化。

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

<sub align="center">© 2025 x-itg | 遵循"人定义法则，AI 在法则内执行"原则构建</sub>