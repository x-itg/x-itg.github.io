# IDE AI Engineering Tools

嵌入式AI工程化体系的VSCode插件后端服务集合。

## 功能模块

| 模块 | 功能 |
|------|------|
| Law Manager | 法则管理器：将agents.md和规约文件变成可交互的法则网络 |
| Negative Logger | 负日志监控器：可视化期望与现实的差距 |
| Convergence Engine | 收敛引擎：让ConvergenceAgent在IDE内可视可控 |
| Schematic Navigator | 电路图导航器：将PDF原理图变成可点击的硬件地图 |
| Knowledge Vitals Dashboard | 知识体征仪表盘：图形化实时监控文档健康度 |
| Skills Launcher | Skills启动台：高频操作变成可点击的按钮 |
| Legacy Adapter | 遗产项目适配器：帮助老项目平滑迁移 |

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
# 启动所有服务
python main.py --all

# 启动单个模块
python main.py --module law_manager
python main.py --module negative_logger
python main.py --module convergence_engine
python main.py --module schematic_navigator
python main.py --module knowledge_vitals
python main.py --module skills_launcher
python main.py --module legacy_adapter

# Web界面
python -m http.server 8080
```

## 项目结构

```
ide_plugins/
├── law_manager/          # 法则管理器
│   ├── __init__.py
│   ├── tree_view.py      # 树形视图
│   ├── validator.py      # 自动验证引擎
│   ├── wizard.py         # 法则创建向导
│   └── chat联动.py        # AI对话联动
├── negative_logger/      # 负日志监控器
│   ├── __init__.py
│   ├── log_stream.py     # 实时日志流
│   ├── expectation_board.py  # 期望看板
│   ├── diagnosis.py       # 一键诊断
│   └── replay.py         # 离线回放
├── convergence_engine/   # 收敛引擎
│   ├── __init__.py
│   ├── task_panel.py     # 任务面板
│   ├── iteration_graph.py # 迭代历史图
│   ├── launcher.py       # 一键启动
│   └── arbitration.py    # 人工裁决接口
├── schematic_navigator/  # 电路图导航器
│   ├── __init__.py
│   ├── pdf_viewer.py     # PDF阅读器
│   ├── code_links.py     # 代码超链接
│   └── ocr识别.py         # OCR识别
├── knowledge_vitals/     # 知识体征仪表盘
│   ├── __init__.py
│   ├── dashboard.py      # 全局概览
│   ├── doc_panel.py      # 文档详情
│   ├── alerts.py         # 预警提醒
│   └── fact_search.py    # 事实索引搜索
├── skills_launcher/      # Skills启动台
│   ├── __init__.py
│   ├── sidebar.py        # 侧边栏列表
│   ├── param_guide.py    # 参数引导
│   └── convergence联动.py
├── legacy_adapter/       # 遗产项目适配器
│   ├── __init__.py
│   ├── remote_build.py   # 远程编译配置
│   ├── translation.py    # 工程翻译向导
│   └── defense_mode.py   # 防御层模式
├── core/                 # 共享核心
│   ├── __init__.py
│   ├── config.py         # 配置管理
│   ├── agents_md.py      # agents.md解析
│   ├── decision_ledger.py # 决策账本
│   └── events.py         # 事件系统
├── web/                  # Web界面
│   ├── index.html
│   ├── app.py
│   └── static/
├── main.py               # 主入口
├── config.yaml           # 配置文件
└── requirements.txt      # 依赖
```

## 配置

编辑 `config.yaml`:

```yaml
project:
  root: ./workspace
  agents_md: docs/agents.md
  decision_ledger: docs/.decision_ledger/

serial:
  port: COM3
  baudrate: 115200

remote_build:
  host: ""
  user: ""
  keil_path: ""

skills:
  definitions_dir: .skills/
```

## 许可证

CC BY-SA 4.0
