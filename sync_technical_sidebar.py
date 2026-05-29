from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SHARED_CSS = '<link rel="stylesheet" href="assets/site-sidebar.css">'

TECH_ITEMS = [
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
    ("gmp.html", "📜", "合规验证与AI编程", '专业延伸 · 从"事后补文档"到"事前建法则"'),
    ("hg.html", "🎯", "回归现实：单Agent实践框架", "综合实战 · 将完整法则体系落地为可立即上手的工程实践"),
    ("12.html", "⚔️", "AI编程的利刃", "工程利器 · 同步生成测试脚本让AI自我调试"),
    ("py.html", "🐍", "批量修改，先问该不该用脚本", "工程利器 · 先判断模式，再把批量改造交给脚本执行"),
    ("13.html", "🧵", "拆解与整合", "工程心法 · 驾驭复杂系统的完整工程法则"),
    ("14.html", "⚖️", "AI谄媚与专利", "专业延伸 · 在拿证与保护之间切换审查模式"),
    ("gd.html", "🌾", "始于工程，服务生活", "内核反照 · 工程法则从技术补丁长成生活工具"),
]

TECH_FILES = [item[0] for item in TECH_ITEMS]
ITEM_BY_FILE = {item[0]: item for item in TECH_ITEMS}
TITLE_BY_FILE = {file_name: title for file_name, _, title, _ in TECH_ITEMS}

GROUPS = [
    ("总纲", [TECH_ITEMS[0]]),
    ("核心主线", TECH_ITEMS[1:5]),
    ("根系能力", TECH_ITEMS[5:7]),
    ("专业延伸", [TECH_ITEMS[7], TECH_ITEMS[8], TECH_ITEMS[9], TECH_ITEMS[10], TECH_ITEMS[15]]),
    ("实战与心法", TECH_ITEMS[11:15]),
    ("内核反照", [TECH_ITEMS[16]]),
]

BRIDGES = [
    ("about.html", "总序 · 我找到了一套法则", "从技术回到整站总叙事。"),
    ("aboutmore/wx.html", "总览 · 乾坤大挪移心法", "从技术、生活到文学的一张路线图。"),
]

SECTION_META = {
    "in.html": ("T · 嵌入式AI工程化", "定义体系坐标，后续所有工程法则都从这里分叉。"),
    "index.html": ("T · 嵌入式AI工程化", "从这里进入技术主线，再决定是先读总纲还是先看整张地图。"),
    "true.html": ("T · 嵌入式AI工程化", "把方法论压成可复用的工程骨架。"),
    "test.html": ("T · 嵌入式AI工程化", "双轨收敛让系统能自检自修。"),
    "fwd.html": ("T · 嵌入式AI工程化", "引入性格制衡与决策切换。"),
    "exc.html": ("T · 嵌入式AI工程化", "让知识资产具备健康度与唤醒机制。"),
    "pcb.html": ("T · 嵌入式AI工程化", "这里补齐感知与支撑，让体系能真正接入物理世界。"),
    "pt.html": ("T · 嵌入式AI工程化", "这里补齐感知与支撑，让体系能真正接入物理世界。"),
    "history.html": ("T · 嵌入式AI工程化", "法则进入遗留工程、设备身份与合规场景。"),
    "ocd.html": ("T · 嵌入式AI工程化", "把开源工具链、硬件状态和AI执行闭环接到同一条命令线上。"),
    "devs.html": ("T · 嵌入式AI工程化", "法则进入遗留工程、设备身份与合规场景。"),
    "gmp.html": ("T · 嵌入式AI工程化", "法则进入遗留工程、设备身份与合规场景。"),
    "hg.html": ("T · 嵌入式AI工程化", "完整法则压进真实工作流，验证能否长期落地。"),
    "12.html": ("T · 嵌入式AI工程化", "完整法则压进真实工作流，验证能否长期落地。"),
    "py.html": ("T · 嵌入式AI工程化", "完整法则压进真实工作流，验证能否长期落地。"),
    "13.html": ("T · 嵌入式AI工程化", "完整法则压进真实工作流，验证能否长期落地。"),
    "14.html": ("T · 嵌入式AI工程化", "这里开始守关，要求法则不仅会借力，也会刹车。"),
    "gd.html": ("T · 嵌入式AI工程化", "这是从技术翻回生活的桥面，后面的非技术文章都从这里接上。"),
}

def detect_eol(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def detect_unit(indent: str) -> str:
    return "\t" if "\t" in indent else "    "


def ensure_shared_css(text: str, eol: str) -> str:
    if SHARED_CSS in text:
        return text
    head_end = text.find("</head>")
    if head_end == -1:
        raise ValueError("Could not find </head>")
    return text[:head_end] + SHARED_CSS + eol + text[head_end:]


def strip_css_rules(text: str, selectors: list[str]) -> str:
    updated = text
    for selector in selectors:
        pattern = re.compile(rf'^[ \t]*{re.escape(selector)}\s*\{{[^{{}}]*\}}\s*', re.MULTILINE)
        updated = pattern.sub("", updated)
    return updated


def remove_generated_sidebar_css(text: str, eol: str) -> str:
    cleaned = strip_css_rules(
        text,
        [
            ".site-sidebar",
            ".site-sidebar__brand",
            ".site-sidebar__brand a",
            ".site-sidebar__intro",
            ".site-sidebar__eyebrow",
            ".site-sidebar__group",
            ".site-sidebar__group summary",
            ".site-sidebar__group summary::-webkit-details-marker",
            ".site-sidebar__group summary::after",
            ".site-sidebar__group[open] summary::after",
            ".site-sidebar__group-body",
            ".site-sidebar__group-body ul",
            ".site-sidebar__link",
            ".site-sidebar__link:hover",
            ".site-sidebar__link.is-active",
            ".site-sidebar__link-title",
            ".site-sidebar__link-meta",
            ".site-sidebar__article-link",
            ".site-sidebar__article-num",
            ".site-sidebar__footer-link",
            ".site-sidebar__footer-link:hover",
            ".sidebar-series",
            ".sidebar-series nav ul",
            ".sidebar-series nav li",
            ".sidebar-series nav a",
            ".sidebar-series nav a:hover",
            ".sidebar-series nav a.active",
            ".sidebar-series nav a i",
            ".sidebar-series::-webkit-scrollbar",
            ".sidebar-series::-webkit-scrollbar-track",
            ".sidebar-series::-webkit-scrollbar-thumb",
            ".sidebar-overview",
            ".sidebar-kicker",
            ".sidebar-overview strong",
            ".sidebar-overview p",
            ".article-series",
            ".article-series h3",
            ".series-group",
            ".series-group summary",
            ".series-group summary::-webkit-details-marker",
            ".series-group summary::after",
            ".series-group[open] summary::after",
            ".series-group-body",
            ".series-group-body ul",
            ".series-group-body li",
            ".sidebar-bridge",
            ".sidebar-bridge h3",
            ".sidebar-bridge ul",
            ".sidebar-bridge a",
            ".sidebar-bridge a:hover",
            ".sidebar-bridge a.active",
            ".sidebar-bridge strong",
            ".sidebar-bridge span",
            ".article-link",
            ".article-link .article-num",
            ".article-link.active .article-num",
            ".article-link .article-info",
            ".article-link .article-title",
            ".article-link .article-desc",
            ".article-link.active",
            ".article-link.active .article-desc",
            ".series-nav",
            ".series-nav a",
            ".series-nav a:hover",
            ".sidebar-toc",
            ".sidebar-toc h3",
            ".sidebar-toc nav ul",
            ".sidebar-toc nav li",
            ".sidebar-toc nav a",
            ".sidebar-toc nav a:hover",
            ".sidebar-toc nav a i",
            ".sidebar-toc::-webkit-scrollbar",
            ".sidebar-toc::-webkit-scrollbar-track",
            ".sidebar-toc::-webkit-scrollbar-thumb",
        ],
    )
    return remove_sidebar_media_blocks(cleaned)


def remove_sidebar_media_blocks(text: str) -> str:
    media_start = re.compile(r"@media[^\{]*\{", re.MULTILINE)
    sidebar_tokens = (".sidebar-toc", ".site-sidebar", ".sidebar-series")
    allowed_selectors = (
        ".layout",
        ".sidebar-toc",
        ".sidebar-toc h3",
        ".sidebar-toc nav ul",
        ".sidebar-toc nav li",
        ".sidebar-toc nav a",
        ".sidebar-toc nav a:hover",
        ".sidebar-toc nav a i",
        ".site-sidebar",
        ".sidebar-series",
    )
    out: list[str] = []
    cursor = 0

    for match in media_start.finditer(text):
        start = match.start()
        if start < cursor:
            continue

        i = match.end() - 1
        depth = 0
        end = None
        while i < len(text):
            ch = text[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
            i += 1

        if end is None:
            break

        block = text[start:end]
        selectors = re.findall(r"(^|\})\s*([^@][^\{]+)\{", block, re.MULTILINE)
        normalized_selectors = []
        for _, selector_group in selectors:
            for selector in selector_group.split(","):
                normalized = " ".join(selector.split())
                if normalized:
                    normalized_selectors.append(normalized)

        is_sidebar_block = (
            any(token in block for token in sidebar_tokens)
            and normalized_selectors
            and all(selector in allowed_selectors for selector in normalized_selectors)
        )
        if is_sidebar_block:
            out.append(text[cursor:start])
            cursor = end

    out.append(text[cursor:])
    return "".join(out)


def build_article_link(indent: str, unit: str, item: tuple[str, str, str, str], active_file: str, eol: str) -> str:
    file_name, icon, title, desc = item
    active_class = " is-active" if file_name == active_file else ""
    lines = [
        f'{indent}<li><a href="{file_name}" class="site-sidebar__link site-sidebar__article-link{active_class}">',
        f'{indent}{unit}<span class="site-sidebar__article-icon" aria-hidden="true">{icon}</span>',
        f'{indent}{unit}<span>',
        f'{indent}{unit}{unit}<span class="site-sidebar__link-title">{title}</span>',
        f'{indent}{unit}{unit}<span class="site-sidebar__link-meta">{desc}</span>',
        f"{indent}{unit}</span>",
        f"{indent}</a></li>",
    ]
    return eol.join(lines)


def build_text_link(indent: str, unit: str, href: str, title: str, desc: str, eol: str) -> str:
    lines = [
        f'{indent}<li><a href="{href}" class="site-sidebar__link">',
        f'{indent}{unit}<span class="site-sidebar__link-title">{title}</span>',
        f'{indent}{unit}<span class="site-sidebar__link-meta">{desc}</span>',
        f"{indent}</a></li>",
    ]
    return eol.join(lines)


def build_sidebar(base_indent: str, active_file: str, eol: str) -> str:
    unit = detect_unit(base_indent)
    i1 = base_indent + unit
    i2 = i1 + unit
    i3 = i2 + unit
    i4 = i3 + unit
    title, desc = SECTION_META[active_file]
    lines = [
        f'{base_indent}<aside class="site-sidebar site-sidebar--tech">',
        f'{i1}<div class="site-sidebar__brand"><a href="index.html"><i class="fas fa-sun"></i> T · 嵌入式AI工程化</a></div>',
        f'{i1}<div class="site-sidebar__intro">',
        f'{i2}<span class="site-sidebar__eyebrow">当前支线</span>',
        f"{i2}<strong>{title}</strong>",
        f"{i2}<p>{desc}</p>",
        f"{i1}</div>",
        f'{i1}<div class="site-sidebar__quick-links">',
        f'{i2}<a href="index.html" class="site-sidebar__quick-link site-sidebar__quick-link--primary"><i class="fas fa-house"></i><span>首页入口</span></a>',
        f'{i2}<a href="aboutmore/wx.html" class="site-sidebar__quick-link"><i class="fas fa-map"></i><span>站点总览</span></a>',
        f"{i1}</div>",
    ]
    for group_title, items in GROUPS:
        open_attr = " open" if any(item[0] == active_file for item in items) else ""
        lines.extend([
            f'{i1}<details class="site-sidebar__group"{open_attr}>',
            f"{i2}<summary>{group_title}</summary>",
            f'{i2}<div class="site-sidebar__group-body">',
            f"{i3}<ul>",
        ])
        for item in items:
            lines.append(build_article_link(i4, unit, item, active_file, eol))
        lines.extend([f"{i3}</ul>", f"{i2}</div>", f"{i1}</details>"])
    bridge_open = " open" if active_file == "gd.html" else ""
    lines.extend([
        f'{i1}<details class="site-sidebar__group"{bridge_open}>',
        f"{i2}<summary>走出技术</summary>",
        f'{i2}<div class="site-sidebar__group-body">',
        f"{i3}<ul>",
    ])
    for href, link_title, link_desc in BRIDGES:
        lines.append(build_text_link(i4, unit, href, link_title, link_desc, eol))
    lines.extend([
        f"{i3}</ul>",
        f"{i2}</div>",
        f"{i1}</details>",
        f'{i1}<a href="about.html" class="site-sidebar__footer-link">→ 关于作者</a>',
        f"{base_indent}</aside>",
    ])
    return eol.join(lines) + eol


def replace_sidebar(text: str, active_file: str, eol: str) -> str:
    start = text.find('<aside class="site-sidebar')
    if start == -1:
        start = text.find('<aside class="sidebar-series">')
    if start == -1:
        raise ValueError("Could not find technical sidebar")
    end = text.find('<aside class="sidebar-toc">', start)
    if end == -1:
        raise ValueError("Could not find sidebar-toc")
    line_start = text.rfind(eol, 0, start)
    line_start = 0 if line_start == -1 else line_start + len(eol)
    end_line_start = text.rfind(eol, 0, end)
    end_line_start = 0 if end_line_start == -1 else end_line_start + len(eol)
    base_indent = text[line_start:start]
    return text[:line_start] + build_sidebar(base_indent, active_file, eol) + text[end_line_start:]


def build_series_nav(indent: str, active_file: str, eol: str) -> str:
    unit = detect_unit(indent)
    index = TECH_FILES.index(active_file)
    prev_target = ("aboutmore/wx.html", "乾坤大挪移心法总览") if index == 0 else (TECH_FILES[index - 1], TITLE_BY_FILE[TECH_FILES[index - 1]])
    next_target = ("aboutmore/wx.html", "乾坤大挪移心法总览") if index == len(TECH_FILES) - 1 else (TECH_FILES[index + 1], TITLE_BY_FILE[TECH_FILES[index + 1]])
    return eol.join([
        f'{indent}<div class="series-nav">',
        f'{indent}{unit}<a href="{prev_target[0]}">← {prev_target[1]}</a>',
        f'{indent}{unit}<a href="{next_target[0]}">{next_target[1]} →</a>',
        f"{indent}</div>",
    ])


def build_bottom_series_links(indent: str, eol: str) -> str:
    parts = []
    for file_name, _, title, _ in TECH_ITEMS:
        parts.append(f'<a href="{file_name}">{title}</a>')
    joined = f" ·{eol}{indent}    ".join(parts)
    lines = [
        f'{indent}<div class="bottom-series-links" style="margin-top:48px;padding-top:24px;border-top:1px solid var(--border);font-size:14px;line-height:1.9;color:#5a6c7d;">',
        f"{indent}    <strong>系列导航：</strong>",
        f"{indent}    {joined}",
        f"{indent}</div>",
    ]
    return eol.join(lines)


def replace_bottom_series_links(text: str, eol: str) -> str:
    pattern = re.compile(r'(?P<indent>^[ \t]*)<div class="bottom-series-links"[^>]*>.*?</div>\s*', re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    if match:
        block = build_bottom_series_links(match.group("indent"), eol) + eol + eol
        return text[: match.start()] + block + text[match.end() :]
    series_nav = re.search(r'(?P<indent>^[ \t]*)<div class="series-nav"[^>]*>', text, re.MULTILINE)
    if series_nav:
        block = build_bottom_series_links(series_nav.group("indent"), eol) + eol + eol
        return text[: series_nav.start()] + block + text[series_nav.start() :]
    return text


def replace_series_nav(text: str, active_file: str, eol: str) -> str:
    pattern = re.compile(r'(?P<indent>^[ \t]*)<div class="series-nav"[^>]*>.*?</div>\s*', re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    if match:
        nav = build_series_nav(match.group("indent"), active_file, eol) + eol
        return text[: match.start()] + nav + text[match.end() :]
    bottom_links = re.search(r'(?P<indent>^[ \t]*)<div class="bottom-series-links"[^>]*>.*?</div>', text, re.MULTILINE | re.DOTALL)
    if bottom_links:
        nav = eol + eol + build_series_nav(bottom_links.group("indent"), active_file, eol)
        return text[: bottom_links.end()] + nav + text[bottom_links.end() :]
    footer_at = text.find("<footer>")
    if footer_at == -1:
        footer_at = text.find('<div class="inland-security-footer">')
    if footer_at == -1:
        raise ValueError("Could not find insertion point for series-nav")
    line_start = text.rfind(eol, 0, footer_at)
    line_start = 0 if line_start == -1 else line_start + len(eol)
    indent = text[line_start:footer_at]
    nav = build_series_nav(indent, active_file, eol) + eol
    return text[:footer_at] + nav + text[footer_at:]


def sync_file(file_name: str) -> bool:
    path = ROOT / file_name
    text = path.read_text(encoding="utf-8")
    eol = detect_eol(text)
    updated = ensure_shared_css(text, eol)
    updated = remove_generated_sidebar_css(updated, eol)
    updated = replace_sidebar(updated, file_name, eol)
    updated = replace_bottom_series_links(updated, eol)
    updated = replace_series_nav(updated, file_name, eol)
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8", newline="")
    return True


def main() -> None:
    changed = []
    for file_name in TECH_FILES:
        if sync_file(file_name):
            changed.append(file_name)
    if changed:
        print("Updated technical sidebars:")
        for file_name in changed:
            print(f"- {file_name}")
    else:
        print("No technical sidebar changes were needed.")


if __name__ == "__main__":
    main()