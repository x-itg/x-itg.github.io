#!/usr/bin/env python3
"""统一侧边栏导航生成脚本。

将 T / L1-L4 合并为一个可折叠的统一侧边栏，同时为文章 TOC 注入 emoji。
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent

# ── CSS links ──────────────────────────────────────────────────────
CSS_ROOT = '<link rel="stylesheet" href="assets/site-sidebar.css">'
CSS_CHILD = '<link rel="stylesheet" href="../assets/site-sidebar.css">'

# ── 入口页 ──────────────────────────────────────────────────────────
ENTRY_PAGES = {"index.html", "gd.html", "about.html"}

# ═══════════════════════════════════════════════════════════════════
#  T · 嵌入式AI工程化
# ═══════════════════════════════════════════════════════════════════

TECH_ITEMS: list[tuple[str, str, str, str]] = [
    ("in.html", "🧭", "五层进化", "总纲 · 定义整个体系的坐标系和成熟度框架"),
    ("true.html", "🧱", "实践项目模板", "执行基础 · 把方法论固化为可落地的工程骨架"),
    ("test.html", "🛠️", "自主修复闭环", "执行智能 · 双轨收敛让系统在既定路径上自我修正"),
    ("fwd.html", "🧠", "从收敛到进化", "演化与判断智能 · 引入Agent性格制衡与决策切换"),
    ("exc.html", "🫀", "知识的生命体征", "记忆智能 · 知识资产生命周期管理与免疫记忆"),
    ("pcb.html", "🔎", "电路图分析器", "感知根系 · 打通物理世界与数字世界"),
    ("pt.html", "🧩", "最后的拼图：Skills", "支撑根系 · 快消费应用即时方法"),
    ("history.html", "📦", "历史的包袱", "专业延伸 · 遗留工程与AI迁移策略"),
    ("ocd.html", "🧰", "被忽视的工具链组合", "专业延伸 · 用开源命令行工具把AI接入真实硬件调试"),
    ("devs.html", "🏷️", "固件铭牌与设备画像", "专业延伸 · 固件数字身份与协同管理"),
    ("gmp.html", "📜", "合规验证与AI编程", "专业延伸 · 从\"事后补文档\"到\"事前建法则\""),
    ("gxp.html", "📋", "GxP法规工程化", "专业延伸 · 把750页法规翻译成可运行的系统"),
    ("lims.html", "🧪", "LIMS系统集成法则", "专业延伸 · ASTM E1578标准落地与18条集成法则"),
    ("hg.html", "🎯", "回归现实：单Agent实践框架", "综合实战 · 将完整法则体系落地为可立即上手的工程实践"),
    ("12.html", "⚔️", "AI编程的利刃", "工程利器 · 同步生成测试脚本让AI自我调试"),
    ("py.html", "🐍", "批量修改，先问该不该用脚本", "工程利器 · 先判断模式，再把批量改造交给脚本执行"),
    ("13.html", "🧵", "拆解与整合", "工程心法 · 驾驭复杂系统的完整工程法则"),
    ("lj.html", "🎓", "君子不器与灵活调度", "工程心法 · 从古典哲思到AI时代工具调度法则"),
    ("fb.html", "💰", "别把AI用成付费上班", "工程心法 · 够用原则与分层路由，把AI账单用在刀刃上"),
    ("svg.html", "🎨", "别让AI画图，让它写图", "工程心法 · SVG是代码不是图片，编号精准定位，分层策略拆解复杂设计"),
    ("14.html", "⚖️", "AI谄媚与专利", "专业延伸 · 在拿证与保护之间切换审查模式"),
    ("gd.html", "🌾", "始于工程，服务生活", "内核反照 · 工程法则从技术补丁长成生活工具"),
]

TECH_GROUPS = [
    ("总纲", [TECH_ITEMS[0]]),
    ("核心主线", TECH_ITEMS[1:5]),
    ("根系能力", TECH_ITEMS[5:7]),
    ("专业延伸", [TECH_ITEMS[7], TECH_ITEMS[8], TECH_ITEMS[9], TECH_ITEMS[10], TECH_ITEMS[11], TECH_ITEMS[12], TECH_ITEMS[18]]),
    ("实战与心法", TECH_ITEMS[13:18]),
    ("内核反照", [TECH_ITEMS[19]]),
]

# ═══════════════════════════════════════════════════════════════════
#  L1-L4 人文系列
# ═══════════════════════════════════════════════════════════════════

L1_ITEMS = [
    ("about.html", "📖", "我找到了一套法则", "法则起点"),
    ("aboutmore/tk.html", "🧭", "以不变应万变", "法则起点"),
    ("aboutmore/fw.html", "🪄", "工程魔法", "法则起点"),
    ("aboutmore/sc.html", "💞", "调试AI，学会经营感情", "法则起点"),
    ("aboutmore/wx.html", "🗺️", "乾坤大挪移心法 · 文章总览", "法则起点"),
]
L2_ITEMS = [
    ("aboutmore/itg.html", "🌞", "爱婷哥", "家庭·命名与温柔"),
    ("aboutmore/forme.html", "📝", "写给自己", "自省·书信与期许"),
    ("aboutmore/pg.html", "🎤", "家庭直播间", "日常·接话与快乐"),
    ("aboutmore/m.html", "🌙", "周一早上，梦见下班", "日常·疲惫与松弛"),
    ("aboutmore/cc.html", "🪞", "我可能哪里错了", "思辨·反驳与反思"),
    ("aboutmore/ll.html", "💬", "找个不懂的人聊聊", "方法·外行与切换"),
    ("aboutmore/pm.html", "🧠", "他们的提示词，我的交付物", "心法·提示与交付"),
    ("aboutmore/seconed.html", "🎐", "一秒钟的感动", "亲子·棋盘与奔赴"),
    ("aboutmore/ta.html", "♾️", "不必全部收敛", "哲思·余味与收敛"),
    ("aboutmore/xw.html", "⚖️", "先稳，再赢", "心法·先胜再战的完整路径"),
    ("aboutmore/qj.html", "💎", "提供情绪价值的三种姿势", "心法·真诚看见与克制的表达"),
]
L3_ITEMS = [
    ("aboutmore/czy.html", "📘", "蓝牙：陆知意岛", "小说与对话"),
    ("aboutmore/qp-chat.html", "💭", "失控时空·对话版", "小说与对话"),
    ("aboutmore/gary.html", "📍", "失控时空·终极玩家", "小说与对话"),
    ("aboutmore/alone.html", "🌃", "知意知否·孤独玩家", "小说与对话"),
    ("aboutmore/mywj.html", "🪐", "知屿之意·命运玩家", "小说与对话"),
    ("aboutmore/party-high.html", "🎼", "四季Party High玩家", "小说与对话"),
    ("aboutmore/jsxm.html", "🎮", "失控时刻·有趣玩家", "小说与对话"),
    ("aboutmore/npc.html", "🏁", "N-P-C-玩家", "小说与对话"),
]
L4_ITEMS = [
    ("aboutmore/czjs.html", "🧪", "会话的碰撞", "方法与引擎"),
    ("aboutmore/szdl.html", "🏗️", "从碰撞到分工：三足鼎立", "方法与引擎"),
    ("aboutmore/yyjk.html", "🔄", "我的创作永不枯竭", "方法与引擎"),
    ("aboutmore/xg.html", "🏭", "我承认文章都是AI洗稿", "方法与引擎"),
    ("aboutmore/fr.html", "🏛️", "四层结构：创作体系", "方法与引擎"),
    ("aboutmore/jg.html", "🧬", "架构定乾坤，笔墨随法则", "方法与引擎"),
    ("aboutmore/sryj.html", "⚔️", "十日一剑：创作手记", "方法与引擎"),
    ("aboutmore/gc.html", "🖥️", "像调试代码一样创作", "方法与引擎"),
    ("aboutmore/ng.html", "🔧", "我不用天赋，我只用方法", "方法与引擎"),
]

L_SECTIONS = [
    ("law", "L1 · 法则", "法则主线与迁移起点", L1_ITEMS),
    ("persona", "L2 · 人", "日常、关系与自省现场", L2_ITEMS),
    ("literature", "L3 · 小说", "小说、对话、复调与孤独副本", L3_ITEMS),
    ("meta", "L4 · 创作", "创作方法与引擎说明", L4_ITEMS),
]

ALL_FILES = ["index.html"] + [item[0] for item in TECH_ITEMS] + [item[0] for item in L1_ITEMS + L2_ITEMS + L3_ITEMS + L4_ITEMS]
ALL_FILES = list(dict.fromkeys(ALL_FILES))  # 去重保序

# 当前文件所属 T 子组
def find_t_subgroup(file_name: str) -> str | None:
    for gtitle, items in TECH_GROUPS:
        if any(i[0] == file_name for i in items):
            return gtitle
    return None

# 当前文件所属 L 层
def find_l_layer(file_name: str) -> str | None:
    for layer, _, _, items in L_SECTIONS:
        if any(i[0] == file_name for i in items):
            return layer
    return None


# ═══════════════════════════════════════════════════════════════════
#  HTML 生成辅助
# ═══════════════════════════════════════════════════════════════════

def _href(pfx: str, target: str) -> str:
    return f"{pfx}{target}"


def _link(i: str, u: str, pfx: str, target: str, icon: str, title: str, meta: str,
          active: bool, eol: str) -> str:
    ac = " is-active" if active else ""
    return eol.join([
        f'{i}<li><a href="{_href(pfx, target)}" class="site-sidebar__link site-sidebar__article-link{ac}">',
        f'{i}{u}<span class="site-sidebar__article-icon" aria-hidden="true">{icon}</span>',
        f'{i}{u}<span>',
        f'{i}{u}{u}<span class="site-sidebar__link-title">{title}</span>',
        f'{i}{u}{u}<span class="site-sidebar__link-meta">{meta}</span>',
        f"{i}{u}</span>",
        f"{i}</a></li>",
    ])


# ═══════════════════════════════════════════════════════════════════
#  侧边栏生成
# ═══════════════════════════════════════════════════════════════════

def build_sidebar(base_indent: str, current_file: str, eol: str) -> str:
    # Detect indent unit from file context
    unit = "\t" if "\t" in base_indent else "    "
    i1 = base_indent + unit
    i2 = i1 + unit
    i3 = i2 + unit
    i4 = i3 + unit

    is_entry = current_file in ENTRY_PAGES
    pfx = "../" if current_file.startswith("aboutmore/") else ""

    home = _href(pfx, "index.html")
    wx = _href(pfx, "aboutmore/wx.html")
    about = _href(pfx, "about.html")

    current_t_sub = find_t_subgroup(current_file)
    current_l = find_l_layer(current_file)

    L: list[str] = [
        f'{base_indent}<aside class="site-sidebar">',
        f'{i1}<div class="site-sidebar__brand"><a href="{home}"><i class="fas fa-compass"></i> 乾坤大挪移心法</a></div>',
        f'{i1}<div class="site-sidebar__quick-links">',
        f'{i2}<a href="{home}" class="site-sidebar__quick-link site-sidebar__quick-link--primary"><i class="fas fa-house"></i><span>首页入口</span></a>',
        f'{i2}<a href="{wx}" class="site-sidebar__quick-link"><i class="fas fa-map"></i><span>站点总览</span></a>',
        f'{i2}<a href="{about}" class="site-sidebar__quick-link"><i class="fas fa-feather-alt"></i><span>总序法则</span></a>',
        f"{i1}</div>",
    ]

    # ── T · 嵌入式AI工程化 ──
    t_open = " open" if (is_entry or current_t_sub is not None) else ""
    L.append(f'{i1}<details class="site-sidebar__group site-sidebar__group--tech"{t_open}>')
    L.append(f"{i2}<summary>")
    L.append(f'{i2}{unit}<span class="site-sidebar__summary-text">T · 嵌入式AI工程化</span>')
    L.append(f'{i2}{unit}<span class="site-sidebar__summary-meta">技术主线 · 20 篇</span>')
    L.append(f"{i2}</summary>")
    L.append(f'{i2}<div class="site-sidebar__group-body">')
    for gtitle, items in TECH_GROUPS:
        sub_open = " open" if (is_entry or current_t_sub == gtitle) else ""
        L.append(f'{i3}<details class="site-sidebar__subgroup"{sub_open}>')
        L.append(f"{i4}<summary>{gtitle}</summary>")
        L.append(f'{i4}<div class="site-sidebar__group-body">')
        L.append(f"{i4}{unit}<ul>")
        for fn, icon, title, meta in items:
            L.append(_link(f"{i4}{unit}", unit, pfx, fn, icon, title, meta, fn == current_file, eol))
        L.append(f"{i4}{unit}</ul>")
        L.append(f"{i4}</div>")
        L.append(f"{i3}</details>")
    L.append(f"{i2}</div>")
    L.append(f"{i1}</details>")

    # ── L1-L4 ──
    for layer, label, summary, items in L_SECTIONS:
        l_open = " open" if (is_entry or current_l == layer) else ""
        L.append(f'{i1}<details class="site-sidebar__group site-sidebar__group--{layer}"{l_open}>')
        L.append(f"{i2}<summary>")
        L.append(f'{i2}{unit}<span class="site-sidebar__summary-text">{label}</span>')
        L.append(f'{i2}{unit}<span class="site-sidebar__summary-meta">{summary}</span>')
        L.append(f"{i2}</summary>")
        L.append(f'{i2}<div class="site-sidebar__group-body">')
        L.append(f"{i3}<ul>")
        for fn, icon, title, meta in items:
            L.append(_link(i4, unit, pfx, fn, icon, title, meta, fn == current_file, eol))
        L.append(f"{i3}</ul>")
        L.append(f"{i2}</div>")
        L.append(f"{i1}</details>")

    L.append(f'{i1}<a href="{about}" class="site-sidebar__footer-link">→ 关于作者</a>')
    L.append(f"{base_indent}</aside>")

    return eol.join(L) + eol


# ═══════════════════════════════════════════════════════════════════
#  侧边栏替换
# ═══════════════════════════════════════════════════════════════════

def replace_sidebar(text: str, current_file: str, eol: str) -> str:
    pat = re.compile(r'(?P<indent>^[ \t]*)<aside\s+class="(?:site-sidebar|sidebar-series|sidebar)[^"]*"', re.MULTILINE)
    m = pat.search(text)
    if m:
        start = m.start()
        end_pat = re.compile(r'(?P<indent>^[ \t]*)<aside\s+class="sidebar-toc', re.MULTILINE)
        end_m = end_pat.search(text, start + 1)
        if not end_m:
            mc = text.find('<div class="main-content">', start)
            if mc == -1:
                return text
            end_line = text.rfind(eol, 0, mc)
            end_line = 0 if end_line == -1 else end_line + len(eol)
        else:
            end_line = text.rfind(eol, 0, end_m.start())
            end_line = 0 if end_line == -1 else end_line + len(eol)

        line_start = text.rfind(eol, 0, start)
        line_start = 0 if line_start == -1 else line_start + len(eol)
        base_indent = text[line_start:m.start()]
        new_sidebar = build_sidebar(base_indent, current_file, eol)
        return text[:line_start] + new_sidebar + text[end_line:]

    # 无现有侧边栏 → 在 main-content 前插入
    mc = text.find('<div class="main-content">')
    if mc == -1:
        return text
    line_start = text.rfind(eol, 0, mc)
    line_start = 0 if line_start == -1 else line_start + len(eol)
    indent = text[line_start:mc]
    new_sidebar = build_sidebar(indent, current_file, eol)
    return text[:line_start] + new_sidebar + text[line_start:]


# ═══════════════════════════════════════════════════════════════════
#  CSS 链接修复
# ═══════════════════════════════════════════════════════════════════

def fix_css_link(text: str, current_file: str, eol: str) -> str:
    expected = CSS_CHILD if current_file.startswith("aboutmore/") else CSS_ROOT
    other = CSS_ROOT if expected == CSS_CHILD else CSS_CHILD
    if expected in text:
        return text
    if other in text:
        return text.replace(other, expected)
    head_end = text.find("</head>")
    if head_end == -1:
        return text
    return text[:head_end] + expected + eol + text[head_end:]


# ═══════════════════════════════════════════════════════════════════
#  TOC Emoji 注入
# ═══════════════════════════════════════════════════════════════════

EMOJI_KEYWORDS: list[tuple[list[str], str]] = [
    # ── 哲学/法则 ──
    (["君子不器", "主体", "主宰"], "💎"),
    (["法则", "规则", "原则", "规律"], "📐"),
    (["哲学", "哲思", "思考", "反思", "自省"], "🤔"),
    (["认知", "升维", "进化", "成长"], "🧠"),
    (["递归", "循环", "螺旋", "闭环"], "🔄"),
    (["内核", "核心", "本质", "灵魂"], "💠"),
    # ── 工程/技术 ──
    (["工程", "架构", "框架", "结构"], "🏗️"),
    (["实践", "实战", "落地", "上手"], "🎯"),
    (["调试", "debug", "修复", "修正", "自修"], "🔧"),
    (["测试", "验收", "验证", "合规"], "✅"),
    (["项目", "模板", "骨架", "骨架"], "🧱"),
    (["工具", "文具", "装备", "利器"], "🛠️"),
    (["代码", "编程", "脚本"], "💻"),
    (["AI", "人工智能", "Agent", "模型"], "🤖"),
    (["技能", "能力", "skills"], "🧩"),
    (["知识", "记忆", "资产", "生命体征"], "🫀"),
    (["电路", "硬件", "物理", "感知", "pcb"], "🔌"),
    (["设备", "铭牌", "画像", "固件"], "🏷️"),
    (["历史", "遗留", "迁移", "包袱"], "📦"),
    (["工具链", "开源", "命令行"], "🧰"),
    (["利刃", "效率", "批量", "脚本"], "⚔️"),
    (["拆解", "整合", "复杂", "系统"], "🧵"),
    (["调度", "灵活", "切换", "决策"], "⚡"),
    (["谄媚", "专利", "审查", "守关"], "⚖️"),
    (["回归", "现实", "单Agent"], "🎯"),
    # ── 人/关系 ──
    (["爱", "感情", "关系", "家庭", "亲密"], "💕"),
    (["人", "日常", "生活", "自己"], "🌿"),
    (["梦", "疲惫", "休息", "下班"], "🌙"),
    (["错", "反思", "自省", "诚实"], "🪞"),
    (["聊", "对话", "沟通", "表达", "直播"], "💬"),
    (["收敛", "克制", "边界", "不必"], "♾️"),
    (["优先级", "选择", "取舍"], "📋"),
    # ── 小说/叙事 ──
    (["小说", "故事", "叙事", "蓝牙"], "📘"),
    (["失控", "时空"], "💫"),
    (["孤独", "独自", "一个人", "岛"], "🌃"),
    (["命运", "玩家", "游戏"], "🪐"),
    (["四季", "party", "high"], "🎼"),
    (["有趣", "好玩"], "🎮"),
    # ── 创作/方法 ──
    (["创作", "写作", "写", "笔墨"], "✍️"),
    (["方法", "引擎", "机制", "体系"], "⚙️"),
    (["结构", "层次", "四层"], "🏛️"),
    (["碰撞", "冲突", "会话", "对话"], "🧪"),
    (["手记", "记录", "日志", "创作手记"], "📓"),
    (["十天", "十日", "一剑"], "⚔️"),
    # ── 总结/结尾 ──
    (["结语", "总结", "结尾", "终点", "结语"], "🎯"),
    (["开始", "起点", "导言", "引言", "开篇"], "🚀"),
    (["贯通", "贯通", "融会", "打通", "连接"], "🔗"),
    (["桥梁", "桥面", "过渡", "翻转"], "🌉"),
    (["反照", "回望", "回望"], "🪞"),
    (["够用", "简单", "极简", "足够"], "✨"),
    (["问题", "挑战", "困难"], "❓"),
    (["方案", "解决", "路径", "方法"], "💡"),
    (["体系", "完成", "殿堂", "七篇"], "🏛️"),
    (["主干", "持守", "不变"], "🌳"),
]

DEFAULT_EMOJI = "📌"


def match_emoji(heading_text: str) -> str:
    text = heading_text.lower()
    for keywords, emoji in EMOJI_KEYWORDS:
        for kw in keywords:
            if kw.lower() in text:
                return emoji
    return DEFAULT_EMOJI


def collect_h2_map(text: str) -> dict[str, str]:
    """收集所有 h2 的 id → 纯文本映射。"""
    result: dict[str, str] = {}
    for m in re.finditer(r'<h2\s+id="([^"]+)"[^>]*>(.*?)</h2>', text, re.DOTALL):
        hid = m.group(1)
        raw = m.group(2)
        plain = re.sub(r"<[^>]+>", "", raw)
        plain = re.sub(r"\s+", " ", plain).strip()
        result[hid] = plain
    return result


def normalize_toc_text(t: str) -> str:
    """去除章节编号前缀以便匹配。"""
    t = re.sub(r"^[一二三四五六七八九十百千]+、\s*", "", t)
    t = re.sub(r"^第[一二三四五六七八九十\d]+[章节部分篇]\s*", "", t)
    t = re.sub(r"^\d+[\.\、]\s*", "", t)
    return t.strip()


def inject_toc_emoji(text: str, eol: str) -> str:
    """为 sidebar-toc 中的每个条目注入 emoji。"""
    toc_pat = re.compile(
        r'(?P<indent>^[ \t]*)<aside\s+class="sidebar-toc[^"]*">.*?</aside>',
        re.MULTILINE | re.DOTALL,
    )
    toc_m = toc_pat.search(text)
    if not toc_m:
        return text

    h2_map = collect_h2_map(text)
    toc_block = toc_m.group(0)
    base = toc_m.group("indent")
    u = "\t" if "\t" in toc_block else "    "

    # 提取现有 TOC 条目
    entries: list[tuple[str, str]] = []
    for em in re.finditer(
        r'<li>\s*<a\s+href="#([^"]+)"[^>]*>(.*?)</a>\s*</li>',
        toc_block,
        re.DOTALL,
    ):
        target = em.group(1)
        inner = em.group(2)
        plain = re.sub(r"<[^>]+>", "", inner)
        plain = re.sub(r"\s+", " ", plain).strip()
        entries.append((target, plain))

    if not entries:
        return text

    # 确定 TOC 标题
    h3_m = re.search(r"<h3[^>]*>(.*?)</h3>", toc_block, re.DOTALL)
    toc_title = re.sub(r"<[^>]+>", "", h3_m.group(1)).strip() if h3_m else "本章导览"

    # 构建新 TOC
    i1, i2, i3 = base + u, base + u + u, base + u + u + u
    lines = [
        f'{base}<aside class="sidebar-toc">',
        f"{i1}<h3>{toc_title}</h3>",
        f"{i1}<nav>",
        f"{i2}<ul>",
    ]
    for target, plain_text in entries:
        heading = h2_map.get(target, "")
        emoji = match_emoji(heading) if heading else match_emoji(plain_text)
        # 去除 plain_text 中所有已存在的前导 emoji（含变体选择符、ZWJ、空格），避免重复
        plain_text = re.sub(
            r'^(?:(?:[\U0001F000-\U0001FFFF\U00002600-\U000027BF][\ufe0f\u200d]*|[\ufe0f\u200d])\s*)+', '', plain_text
        ).strip()
        lines.append(f'{i3}<li><a href="#{target}">{emoji} {plain_text}</a></li>')
    lines.extend([
        f"{i2}</ul>",
        f"{i1}</nav>",
        f"{base}</aside>",
    ])

    new_toc = eol.join(lines)

    # 保留 TOC 后的换行
    after = toc_m.end()
    while after < len(text) and text[after] in "\r\n":
        after += 1
    trailing = text[toc_m.end():after]

    return text[: toc_m.start()] + new_toc + trailing + text[after:]


# ═══════════════════════════════════════════════════════════════════
#  文件处理
# ═══════════════════════════════════════════════════════════════════

def add_theme_class(text: str, current_file: str) -> str:
    """Add theme class to <body> for CSS scoping."""
    layer = find_l_layer(current_file)
    theme = "story" if layer else "tech"
    cls = f"site-theme-{theme}"

    # Already present?
    if cls in text:
        return text

    body_m = re.search(r'<body([^>]*)>', text)
    if not body_m:
        return text

    attrs = body_m.group(1)
    existing = re.search(r'class="([^"]*)"', attrs)
    if existing:
        new_cls = f'{existing.group(1)} {cls}'
        new_attrs = attrs.replace(f'class="{existing.group(1)}"', f'class="{new_cls}"')
    else:
        new_attrs = f'{attrs} class="{cls}"'

    text = text[:body_m.start()] + f'<body{new_attrs}>' + text[body_m.end():]
    return text


def detect_eol(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def sync_file(file_name: str) -> dict:
    path = ROOT / file_name
    if not path.exists():
        return {"status": "skip", "reason": "not found"}

    text = path.read_text(encoding="utf-8")
    eol = detect_eol(text)
    original = text

    text = fix_css_link(text, file_name, eol)
    text = replace_sidebar(text, file_name, eol)
    text = add_theme_class(text, file_name)
    text = inject_toc_emoji(text, eol)

    if text == original:
        return {"status": "unchanged"}

    path.write_text(text, encoding="utf-8", newline="")
    return {"status": "updated"}


def main() -> None:
    results: dict[str, list[str]] = {"updated": [], "unchanged": [], "skipped": [], "errors": []}

    for f in ALL_FILES:
        try:
            r = sync_file(f)
            if r["status"] == "updated":
                results["updated"].append(f)
            elif r["status"] == "unchanged":
                results["unchanged"].append(f)
            else:
                results["skipped"].append(f)
        except Exception as e:
            results["errors"].append(f"{f}: {e}")

    log_lines = []
    log_lines.append(f"Updated ({len(results['updated'])}):")
    for f in results["updated"]:
        log_lines.append(f"  - {f}")
    log_lines.append(f"\nUnchanged ({len(results['unchanged'])}):")
    for f in results["unchanged"]:
        log_lines.append(f"  - {f}")
    if results["skipped"]:
        log_lines.append(f"\nSkipped ({len(results['skipped'])}):")
        for f in results["skipped"]:
            log_lines.append(f"  - {f}")
    if results["errors"]:
        log_lines.append(f"\nErrors ({len(results['errors'])}):")
        for e in results["errors"]:
            log_lines.append(f"  - {e}")
    log_lines.append(f"\nTotal: {len(ALL_FILES)} files processed.")

    log_text = "\n".join(log_lines)
    print(log_text)
    (ROOT / "sync_result.log").write_text(log_text, encoding="utf-8")


if __name__ == "__main__":
    main()
