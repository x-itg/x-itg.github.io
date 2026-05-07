# AI 编程调试的进化之路：从 Vibe Coding 到 Harness Engineering

> 融合结构化日志、多模型协作、契约式设计与闭环反馈，重新定义工程化的人机协作范式

---

## 📖 前言：一场静默的革命

2025 年初，Andrej Karpathy 提出了“Vibe Coding”——开发者沉浸在“感觉”中，用自然语言向 AI 描述需求，AI 直接生成可运行代码。这个概念瞬间点燃了整个技术圈。人们惊叹于“从 0 到 1”的速度：一个没写过 Python 的产品经理，可以在 15 分钟内得到一个能爬取数据的脚本；一个嵌入式新手，可以让 AI 生成 CAN 驱动的基本框架。Vibe Coding 似乎要把编程的门槛彻底打碎。

然而，一年后的今天，我们看到的现实更加复杂。**Vibe Coding 产出的代码，在简单场景下能跑得飞快，但一旦涉及精确的状态机、实时性约束、硬件交互或边界条件，就会暴露出严重的不稳定性**。开发者开始抱怨：“AI 生成的代码像是读不懂规格书的学生作业——表面能跑，暗藏无数的坑。”

与此同时，另一股思潮在悄然酝酿。从 OpenAI 工程师提出的 **“Harness Engineering”** ，到学术界关于 **“语义密度优化”** 的 arXiv 论文，再到一线团队的 **“AI-DLC”** 实践——一场从“氛围编程”到“工程化协作”的范式转移正在加速。

本文正是这场范式转移的亲历笔记。笔者从一次失败的 CAN 自组织调试起步，走过了“结构化日志 → 统一上下文 → 多模型协作 → VSCode 一体化 → Vibe+Verify 混合范式”的五层进化。在吸收了大量前沿文献（Harness Engineering、红绿 TDD、三阶控制模型、AIR 循环、VibeContract、Context Before Code、OpenSpec 等）之后，我将这五层方法重新打磨，并融入“契约式设计”与“反馈控制”的系统工程思想，试图为 AI 辅助嵌入式开发（乃至通用软件工程）提供一个可落地、可度量、可演进的工程化框架。

希望这篇文章，能让你在享受 AI 生成速度的同时，也拥有驾驭复杂系统的底气。

---

## 第零层：Vibe Coding 的辉煌与暗礁

### 0.1 Vibe Coding 为何让人上瘾？

如果你经历过 Vibe Coding，你一定记得那种“魔法时刻”：
- 打开聊天窗口，输入“写一个 STM32 的 CAN 回环测试代码”；
- 几十秒后，AI 给出了包含初始化、发送、接收的完整 `.c` 文件；
- 复制到 IDE，编译、烧录，灯闪了，数据收到了。

从想法到可运行的硬件，不过 5 分钟。这种反馈速度是传统开发无法比拟的。Karpathy 将这种感觉描述为“完全沉浸在指数增长的喜悦中”。

### 0.2 繁荣背后的三个致命缺陷

然而，当项目复杂度提升到真实产品级别时，Vibe Coding 的短板便暴露无遗。我把它总结为三大缺陷：

| 缺陷 | 表现 | 后果 |
|------|------|------|
| **可观测性缺失** | AI 生成的代码几乎没有日志，或者只有 `printf("ok")` | 一旦出错，AI 只能列出通用原因（波特率？终端电阻？）无法精准定位 |
| **上下文割裂** | 用户提问时只贴一小段代码，AI 不了解协议设计、状态机、硬件约束 | AI 的建议经常“文不对题”，甚至破坏原有设计 |
| **反馈周期长** | 修改 → 编译 → 烧录 → 观察 → 再修改，手工操作繁琐 | 调试过程充满试错，开发者沦为“AI 的测试员” |

> 一篇 arXiv 论文《Context Before Code》实证发现：AI 生成的代码总是“欠指定”隔离规则和基础设施约束。换句话说，模型擅长写“理想中的逻辑”，却常常忽略现实世界的边界条件。

### 0.3 行业共识：从“氛围”走向“工程”

面对这些缺陷，业界开始系统性地反思。Harness Engineering 提出核心论断：**“Agents aren‘t hard; the harness is hard.”**（Agent 本身不难，难的是驾驭 Agent 的系统）。所谓 Harness，就是围绕 AI Coding Agent 构建的**约束机制、反馈回路与持续改进循环**。而另一位工程师则提出了 **“三阶控制模型”** ：生成控制（通过提示词限定输出范围）、验证控制（通过测试/静态检查把关）、反馈控制（通过运行日志修正行为）。

这些思想，与我五年前开始践行的“闭环调试”不谋而合。下面，我将沿着五层进化路线，逐一展示如何从零开始，构建一个属于你自己的 **Harness**。

---

## 第一招：结构化日志 —— 构建可观测性的地基

### 1.1 问题：传统 `printf` 让 AI 变成“瞎子”

传统嵌入式调试，我们习惯写：
```c
printf("state=%d", state);   // 输出：state=6
```
这个数字 `6` 是什么意思？你需要查头文件才能知道它是 `ONLINE_FIXED`。AI 看到 `6`，它只能根据“常识”猜测——而这正是 Vibe Coding 失败的根源：**模型没有运行时信息**。

### 1.2 解决方案：语义化键值对 + 源文件行号

我从一次痛苦的 epoch 不匹配调试中顿悟：让设备输出 AI 能直接解析的日志。

```c
#define LOG(level, fmt, ...) \
    printf("[%s] %s:%d " fmt "\r\n", level, __FILE__, __LINE__, ##__VA_ARGS__)

LOG("INFO", "state=%s epoch=%d local=%d remote=%d", 
    state_to_str(state), epoch, local_epoch, rx_epoch);
// 输出：[INFO] can_slave.c:412 state=ONLINE_FIXED epoch=2 local=2 remote=2
```

三个关键设计：
- **语义化名称**：`ONLINE_FIXED` 替代 `6`
- **键值对格式**：`key=value` 方便正则提取
- **文件名+行号**：VSCode 终端自动识别为超链接，点击跳转源码

### 1.3 理论升华：语义密度优化

这看起来只是一个小技巧，但它背后暗合了一个 arXiv 论文提出的新思想：**“Beyond Human-Readable：软件工程准则应转向为 Agent 优化”**。作者称之为“语义密度优化”——让日志信息在人类可读的基础上，最大化对 AI 代理的信息熵效率。换言之，我们输出的每一行日志，都应该让 AI 能用最少的上下文理解最多的运行时状态。

结构化日志是实现语义密度优化的第一步。有了它，AI 不再盲目猜测，而是可以像资深工程师一样，拿着“现场照片”进行分析。

### 1.4 实践效果

- 定位时间从“小时级”降到“分钟级”
- AI 可以直接指出：“第 412 行 epoch 不匹配，说明同步逻辑未触发”
- 配合 VSCode 的超链接，点击日志直接跳转源码，省去手动搜索

### 1.5 本招遗留的问题

AI 虽然有了日志，但它仍然需要理解你的协议设计、状态机期望和硬件约束。只给日志片段是不够的——必须提供完整的工程上下文。

---

## 第二招：统一上下文 —— 让 AI 站在全局视角

### 2.1 问题：碎片化信息导致 AI “断章取义”

许多开发者在提问题时，只贴一个 `.c` 文件或者只有日志。AI 不知道你的状态机有几个状态、不知道 CAN 帧格式定义、不知道上位机发送了什么命令。于是它只能基于局部信息给出看似合理、实则错误的建议。

### 2.2 解决方案：标准工程目录 + 整体交付

我建立了一个统一的目录结构，要求所有项目遵循：

```
project/
├── firmware/           # 固件源码（.c/.h + LOG 宏）
├── host/               # 上位机测试脚本（Python）
├── docs/
│   ├── protocol.md     # 协议说明、帧格式
│   └── state_machine.md# 状态迁移表
├── logs/               # 典型运行日志（正常/异常）
└── .vscode/            # tasks.json 一键任务
```

当问题发生时，我会把**整个目录**（或关键部分）打包发给高性能模型，同时附上一句：“请分析该工程，日志在 logs/failure.txt，现象是……”

### 2.3 理论共鸣：AI-DLC 与 OpenSpec

这种“统一上下文”的做法，其实呼应了最近软件工程领域的两个重要演进：

- **AI-DLC（AI-Driven Development Lifecycle）**：将 AI 定位为“核心协作者”，从需求、设计到编码、测试，全程共享统一的工件模型。你的工程目录本质就是 AI-DLC 的物理载体。
- **OpenSpec（规范驱动开发）**：通过一份“规范文档”同时约束人类和 AI 的行为，确保设计与代码同步。在 `docs/protocol.md` 中精确描述协议格式、状态机，AI 能自动遵循，避免“口说无凭”。

### 2.4 实践效果

- AI 能追踪完整数据流：PC 命令 → CAN 帧 → MCU 状态机 → 应答帧
- 根因分析不再依赖“猜”，而是基于真实的设计文档
- 新人接手项目时，可以直接把整个目录给 AI，快速理解架构

### 2.5 本招遗留的问题

有了全局上下文，AI 的分析质量大幅提升，但有两个新问题浮现：
1. **成本**：每次都把整个工程（几十个文件）发给大模型，token 消耗不低。
2. **修改环节**：AI 给出修改建议后，仍需手工复制 diff、应用 patch，流程中断。

---

## 第三招：多模型协作 —— 用分工实现质量与成本双优

### 3.1 核心思想

为什么让同一个模型既写代码又做深度 debug？这就像让同一个人既画图纸又搬砖——效率低下。

我将任务拆分为两层：

| 角色 | 模型类型 | 典型模型 | 职责 | 调用频率 | token成本 |
|------|----------|----------|------|----------|-----------|
| **编码执行者** | 低成本模型 | minimax, DeepSeek-V2, Copilot | 生成代码、补全、重构、应用 diff | 高（每次修改） | 极低（~$0.02/次） |
| **分析决策者** | 高性能模型 | DeepSeek-R1, GPT-4o, Claude 3.5 | 日志分析、根因定位、架构审查、生成 diff | 低（每个 bug 1-2 次） | 中等（~$0.3/次） |

### 3.2 工作流

1. **初始模板生成**：用低成本模型按提示词生成工程（含 LOG 宏、目录、tasks.json）。
2. **运行捕获日志**：烧录后得到结构化日志。
3. **深度分析**：将工程目录 + 日志发给高性能模型，要求输出 `git diff` 格式修改。
4. **应用修改**：将 diff 交给低成本模型（或手动 `git apply`）完成代码更新。
5. **闭环**：重复 2-4 直到问题解决。

### 3.3 理论支撑：AIR 循环与红绿 TDD

- **AIR 循环（Analysis → Implementation → Reflection）**：这是一个让 Agent 自我反思和评估的框架。高性能模型扮演“Analysis + Reflection”，低成本模型扮演“Implementation”。我们的多模型协作正是 AIR 的具体落地。
- **红绿 TDD**：先写一个失败的测试（红色），然后让 AI 生成让测试通过的代码（绿色）。在多模型协作中，高性能模型可以先“编写测试用例”，再由低成本模型实现，从而保证代码的正确性。

### 3.4 成本量化

一个典型的中等复杂度 bug 调试过程：
- 深度分析调用 1-2 次高性能模型：$0.3 × 2 = $0.6
- 模板生成 + 修改应用调用低成本模型 5-10 次：$0.02 × 10 = $0.2
- 总成本约 **$0.8**，远低于全程使用高性能模型的 $2-3，且分析质量反而更高（因为分工让每个模型专注于自己擅长的任务）。

### 3.5 本招遗留的问题

尽管成本优化了，但“获取日志 → 复制粘贴 → 分析 → 复制 diff → 修改”这个过程仍然有多个手动步骤。能否进一步自动化，形成真正意义上的“一键闭环”？

---

## 第四招：VSCode 一体化 —— 让闭环反馈进入“秒级时代”

### 4.1 目标：消除所有工具切换

传统工作流：
- 在 VS Code 写代码
- 切换到 Keil/IAR 编译
- 切换到烧录软件（ST-Link Utility）
- 打开串口助手看日志
- 发现错误，切回 VS Code
- ……

每次切换至少打断思路半分钟。一天下来，真正的思考时间被碎片化割裂。

### 4.2 解决方案：tasks.json 集成全流程

我将编译、烧录、串口监视全部写成 VSCode 任务，并增加一个 `full_loop` 任务：

```json
{
    "version": "2.0.0",
    "tasks": [
        { "label": "build", "type": "shell", "command": "make -j4" },
        { "label": "flash", "type": "shell", 
          "command": "openocd -f interface/stlink.cfg -f target/stm32f4x.cfg -c 'program build/firmware.elf verify reset exit'",
          "dependsOn": ["build"] },
        { "label": "monitor", "type": "shell", 
          "command": "python -m serial.tools.miniterm COM4 115200 --raw" },
        { "label": "full_loop", "dependsOn": ["build", "flash", "monitor"] }
    ]
}
```

按下 `Ctrl+Shift+B`，选择 `full_loop`，终端自动：
1. 编译
2. 烧录
3. 打开串口监视器

日志中的 `can_slave.c:412` 会变成蓝色超链接，点击直接跳转到源码对应行。

### 4.3 与 Plan-First 工作流的结合

《AI编码时代的最佳实践》中提出了 **Plan-First 工作流**：探索 → 计划 → 实现 → 验证。我们的 `full_loop` 任务将“实现（编译烧录）”和“验证（监视日志）”紧密连接，而 AI 分析则填充“计划”环节。当你在终端看到错误日志时，可以立即向 AI 提问，然后 AI 给出 diff，你再应用、运行 `full_loop`——整个探索-计划-实现-验证循环被压缩到 3-5 分钟。

### 4.4 实践效果

- 反馈延迟从“分钟级”降为“秒级”
- 开发者可以保持“心流”状态，不再在不同工具间奔波
- AI 可以通过 Continue/Cline 等插件直接读取终端输出，进一步自动化

### 4.5 本招遗留的问题

VSCode 一体化解决了调试流程的“最后一公里”，但每次启动新项目时，你仍然需要手动创建目录、编写 LOG 宏、设计状态机框架——这些都是重复劳动，极度影响从“0 到 1”的速度。

---

## 第五招：Vibe + Verify —— Harness Engineering 的终极实践

### 5.1 核心思想：用 Vibe 补全“从 0 到 1”，用 Verify 完成“从 1 到 100”

- **Vibe 层**：使用**极低成本模型**以“氛围编程”模式，生成**已经内置结构化日志、标准目录和 tasks.json** 的工程模板。这一步不需要人类参与深度逻辑，只需要让模型遵循一个精心设计的“提示词模板”。
- **Verify 层**：在模板基础上，通过前四招的闭环调试方法，逐步修复逻辑错误、完善边界条件、提升代码健壮性，最终得到产品级代码。

### 5.2 模板生成提示词（给 Vibe 模型）

```markdown
生成 STM32 CAN 自组织地址协议工程，必须满足以下约束：

1. 日志系统：使用如下 LOG 宏（包含 __FILE__ 和 __LINE__）
   #define LOG(level, fmt, ...) printf("[%s] %s:%d " fmt "\r\n", level, __FILE__, __LINE__, ##__VA_ARGS__)

2. 在每个状态切换、CAN 帧收发、关键变量变化处调用 LOG，输出 key=value 格式。

3. 状态机实现： UNCONFIGURED → CLAIMING → ONLINE_FIXED，并提供 `state_to_str()`。

4. 目录结构：
   firmware/src/, firmware/inc/, host/test.py, docs/protocol.md, logs/.gitkeep

5. 在 .vscode/tasks.json 中定义 build、flash、monitor、full_loop 任务。

6. 所有代码必须一次性完整输出，无需解释。
```

只需 $0.05 的 token 成本，就能得到一个**已经植入了可观测性**的完整工程骨架。

### 5.3 Verify 层的深度调试（一个真实案例）

假设运行模板后，我们得到如下日志：

```
[INFO] main.c:45 system started epoch=1
[INFO] can_slave.c:120 state from=UNCONFIGURED to=CLAIMING
[INFO] can_slave.c:234 send announce epoch=1
[WARN] can_slave.c:415 commit timeout epoch mismatch local=1 remote=2
```

我将整个工程目录 + 这份日志发给 DeepSeek-R1，要求它分析原因并输出 `git diff`。

高性能模型的分析路径：
1. 根据日志中的 `can_slave.c:415` 定位到源码。
2. 发现 `check_commit_timeout()` 函数中，虽然有 `if (rx_epoch > local_epoch)` 更新逻辑，但更新后没有重置 `commit_guard` 计数器。
3. 同时注意到 `local_epoch` 是 `static` 变量，在中断和主循环中都被修改，缺少 `volatile` 关键字。
4. 输出 diff：

```diff
diff --git a/firmware/src/can_slave.c b/firmware/src/can_slave.c
--- a/firmware/src/can_slave.c
+++ b/firmware/src/can_slave.c
@@ -10,6 +10,7 @@
 #include "can_slave.h"
 
 static state_t current_state = UNCONFIGURED;
-static int local_epoch = 1;
+static volatile int local_epoch = 1;
 static int commit_guard = 0;
 
 static void check_commit_timeout(void) {
@@ -410,6 +411,8 @@
 static void check_commit_timeout(void) {
     if (rx_epoch > local_epoch) {
         local_epoch = rx_epoch;
+        LOG("INFO", "epoch updated %d->%d", local_epoch-1, local_epoch);
+        reset_commit_guard();
     }
 }
```

应用 diff → 重新运行 `full_loop` → 新日志显示 epoch 同步成功，状态机进入 `ONLINE_FIXED`。整个闭环耗时 **15 分钟**，token 成本不到 $0.4。

### 5.4 理论支柱：Harness Engineering 的四个维度

第五招之所以被称为“终极范式”，是因为它完整实现了 Harness Engineering 的四项核心实践：

| Harness 维度 | 在 Vibe+Verify 中的体现 |
|--------------|--------------------------|
| **约束机制** | 模板生成提示词限制了输出必须包含 LOG、目录结构、tasks.json |
| **验证机制** | 结构化日志提供了持续的可观测性，高性能模型自动验证日志是否符合预期 |
| **反馈回路** | full_loop 任务 + 日志分析 + git diff 形成闭环，每次运行都产生可行动的反馈 |
| **持续改进** | 成功案例保存到知识库，agents.md 统一行为规范，使经验可复用 |

同时，**VibeContract** 的思想也被融入：模板生成提示词本质上就是一种“契约”（必须含有 LOG 宏、必须提供 `state_to_str` 等）。契约降低了 AI 输出的不确定性，让“氛围代码”变得可审计、可预测。

### 5.5 综合效果对比（前四招 vs 第五招）

| 指标 | 前四招累积 | 第五招 Vibe+Verify |
|------|------------|-------------------|
| 新项目启动时间 | 1 小时（手动建目录 + 写 LOG） | **10 分钟**（Vibe 生成） |
| 日志覆盖率（关键路径） | 80%（人工补充） | **95%+**（AI 自动埋点） |
| 中等 bug 定位轮次 | 2-3 轮 | **1-2 轮** |
| 总 token 成本/项目 | $1-2 | **$0.35** |
| 代码可维护性 | 高 | **高 + 模板可复用** |
| 团队知识沉淀 | 部分文档化 | **agents.md + case 库** |

更重要的是，第五招从“设计角度”解决了 Vibe Coding 的根本矛盾：**我们不再试图让 AI 直接写出完美代码，而是让 AI 先写出“可以被观察和调试的代码”，然后利用人机协作的闭环将其打磨至完美**。

---

## 第六层展望：从 Harness 到 Agentic Engineering

我们走完了五层进化，但终点远不止于此。当前，一批最前沿的团队正在探索“Agentic Engineering”——让 AI 代理自主规划、编码、调试、交付，而人类只负责定义目标和约束。你的 Vibe+Verify 范式，正是这座大厦的**承重墙**。

以下三个方向值得继续深耕：

1. **AIR 循环的自动化**：可以在 full_loop 任务之后，自动调用高性能模型对运行日志进行反思，并将修改建议直接通过 API 写入代码库，实现无人守值的调试闭环。

2. **语义密度优化的代码生成**：训练模型在生成之初就自动插入结构化日志和契约断言，让所有代码天生具备高可观测性。这需要将 Beyond Human-Readable 的论文思想转化为实际的训练数据。

3. **OpenSpec 与 VibeContract 的工程化**：将协议规范、状态机约束写成机器可读的 OpenSpec 文件，AI 在生成代码时自动校验是否符合规格。这不仅减少 bug，更让“氛围代码”拥有了形式化验证的可靠性。


---

## 🔁 核心原则速记

- **可观测性内建**：结构化日志 + 行号是 AI 的眼睛
- **闭环反馈**：每次修改必须有新日志驱动
- **分层分工**：低成本模型写代码，高性能模型做分析
- **契约约束**：用提示词模板和 OpenSpec 限制 AI 输出范围
- **知识版本化**：agents.md + case 库让经验可复用
- **共情 AI**：主动填补模型缺失的上下文和硬件细节

> *日志是 AI 的眼睛，闭环是 AI 的思维，契约是 AI 的边界，共情是你与 AI 的默契。*

---

愿你的每一次调试，都能从“Vibe”轻松跃入“Verify”，从容、高效、优雅。
