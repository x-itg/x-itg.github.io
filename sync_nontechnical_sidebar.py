from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SHARED_CSS_ROOT = '<link rel="stylesheet" href="assets/site-sidebar.css">'
SHARED_CSS_CHILD = '<link rel="stylesheet" href="../assets/site-sidebar.css">'

VISIBLE_FLOW = [
    ("about.html", "我找到了一套法则", "law"),
    ("aboutmore/tk.html", "以不变应万变", "law"),
    ("aboutmore/fw.html", "工程魔法", "law"),
    ("aboutmore/sc.html", "调试AI，学会经营感情", "law"),
    ("aboutmore/wx.html", "乾坤大挪移心法 · 文章总览", "law"),
    ("aboutmore/itg.html", "爱婷哥", "persona"),
    ("aboutmore/forme.html", "写给自己", "persona"),
    ("aboutmore/pg.html", "家庭直播间", "persona"),
    ("aboutmore/m.html", "周一早上，梦见下班", "persona"),
    ("aboutmore/cc.html", "我可能哪里错了", "persona"),
    ("aboutmore/ll.html", "找个不懂的人聊聊", "persona"),
    ("aboutmore/ta.html", "不必全部收敛", "persona"),
    ("aboutmore/czy.html", "蓝牙：陆知意岛", "literature"),
    ("aboutmore/qp-chat.html", "失控时空·对话版", "literature"),
    ("aboutmore/jsxm.html", "失控时刻：有趣玩家", "literature"),
    ("aboutmore/czjs.html", "会话的碰撞", "meta"),
    ("aboutmore/fr.html", "四层结构：创作体系", "meta"),
]

FILES = [item[0] for item in VISIBLE_FLOW] + ["aboutmore/ff.html"]
FILE_TO_LAYER = {file_name: layer for file_name, _, layer in VISIBLE_FLOW}
FILE_TO_LAYER["aboutmore/ff.html"] = "special"

LAYER_META = {
    "law": ("法则与故事 · 法则层", "先解释法则怎么建立，再解释它为什么能走出工程。"),
    "persona": ("法则与故事 · 人格层", "法则落进家庭、关系、疲惫与自省，开始接受生活检验。"),
    "literature": ("法则与故事 · 文学层", "当法则遇到错配、感情与失控，它开始长出故事。"),
    "meta": ("法则与故事 · 元创作层", "这里公开引擎，解释这些作品如何被组织和生成。"),
    "special": ("法则与故事 · 特别页", "保留的隐藏实验，不放进公开流转顺序里。"),
}

LAYER_LABELS = {
    "law": "法则层",
    "persona": "人格层",
    "literature": "小说层",
    "meta": "体系层",
    "special": "特别页",
}

LAYER_SUMMARY_META = {
    "law": "法则主线与迁移起点",
    "persona": "日常、关系与自省现场",
    "literature": "小说、对话与失控实验",
    "meta": "体系说明与创作引擎",
    "special": "保留实验页",
}

LAYER_ITEM_META = {
    "law": ("当前法则文章", "法则相关文章"),
    "persona": ("当前人格文章", "人格相关文章"),
    "literature": ("当前小说作品", "小说与对话作品"),
    "meta": ("当前体系文章", "体系与引擎说明"),
    "special": ("保留实验页", "保留实验页"),
}

FILE_ICONS = {
    "about.html": "📖",
    "aboutmore/tk.html": "🧭",
    "aboutmore/fw.html": "🪄",
    "aboutmore/sc.html": "💞",
    "aboutmore/wx.html": "🗺️",
    "aboutmore/itg.html": "🌞",
    "aboutmore/forme.html": "📝",
    "aboutmore/pg.html": "🎤",
    "aboutmore/m.html": "🌙",
    "aboutmore/cc.html": "🪞",
    "aboutmore/ll.html": "💬",
    "aboutmore/ta.html": "♾️",
    "aboutmore/czy.html": "📘",
    "aboutmore/qp-chat.html": "💭",
    "aboutmore/jsxm.html": "🎮",
    "aboutmore/czjs.html": "🧪",
    "aboutmore/fr.html": "🏛️",
    "aboutmore/ff.html": "🕯️",
    "index.html": "🧭",
    "gd.html": "🌾",
}

VISIBLE_LAYERS = ["law", "persona", "literature", "meta"]

LAYER_GROUPS = {
    "law": [(file_name, title) for file_name, title, layer in VISIBLE_FLOW if layer == "law"],
    "persona": [(file_name, title) for file_name, title, layer in VISIBLE_FLOW if layer == "persona"],
    "literature": [(file_name, title) for file_name, title, layer in VISIBLE_FLOW if layer == "literature"],
    "meta": [(file_name, title) for file_name, title, layer in VISIBLE_FLOW if layer == "meta"],
    "special": [("aboutmore/ff.html", "隐藏页")],
}

TECH_SOURCE = [
    ("gd.html", "桥面 · 始于工程，服务生活", "从技术过桥，进入生活与叙事。"),
    ("aboutmore/wx.html", "总览 · 乾坤大挪移心法", "按地图理解技术与非技术的整体关系。"),
]


def detect_eol(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def detect_unit(indent: str) -> str:
    return "\t" if "\t" in indent else "    "


def href(current_file: str, target: str) -> str:
    prefix = "" if current_file == "about.html" else "../"
    return f"{prefix}{target}"


def ensure_shared_css(text: str, current_file: str, eol: str) -> str:
    expected = SHARED_CSS_ROOT if current_file == "about.html" else SHARED_CSS_CHILD
    if expected in text:
        return text
    other = SHARED_CSS_CHILD if expected == SHARED_CSS_ROOT else SHARED_CSS_ROOT
    if other in text:
        return text.replace(other, expected)
    head_end = text.find("</head>")
    if head_end == -1:
        raise ValueError("Could not find </head>")
    return text[:head_end] + expected + eol + text[head_end:]


def strip_css_rules(text: str, selectors: list[str]) -> str:
    updated = text
    for selector in selectors:
        pattern = re.compile(rf'^[ \t]*{re.escape(selector)}\s*\{{[^{{}}]*\}}\s*', re.MULTILINE)
        updated = pattern.sub("", updated)
    return updated


def remove_generated_sidebar_css(text: str, eol: str) -> str:
    anchors = [".site-sidebar", ".sidebar {", ".sidebar .logo", ".sidebar-intro"]
    start = -1
    for anchor in anchors:
        start = text.find(anchor)
        if start != -1:
            break
    end = text.find(".main-content", max(start, 0))
    if start == -1 or end == -1:
        return text
    line_start = text.rfind(eol, 0, start)
    line_start = 0 if line_start == -1 else line_start + len(eol)
    end_line_start = text.rfind(eol, 0, end)
    end_line_start = 0 if end_line_start == -1 else end_line_start + len(eol)
    updated = text[:line_start] + text[end_line_start:]
    return strip_css_rules(
        updated,
        [
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
            ".series-nav",
            ".series-nav a",
            ".series-nav a:hover",
            ".series-nav .placeholder",
        ],
    )


def build_link(indent: str, unit: str, title: str, desc: str, url: str, active: bool, eol: str, icon: str | None = None) -> str:
    active_class = " is-active" if active else ""
    if icon is not None:
        lines = [
            f'{indent}<li><a href="{url}" class="site-sidebar__link site-sidebar__article-link{active_class}">',
            f'{indent}{unit}<span class="site-sidebar__article-icon" aria-hidden="true">{icon}</span>',
            f'{indent}{unit}<span>',
            f'{indent}{unit}{unit}<span class="site-sidebar__link-title">{title}</span>',
            f'{indent}{unit}{unit}<span class="site-sidebar__link-meta">{desc}</span>',
            f"{indent}{unit}</span>",
            f"{indent}</a></li>",
        ]
        return eol.join(lines)
    lines = [
        f'{indent}<li><a href="{url}" class="site-sidebar__link{active_class}">',
        f'{indent}{unit}<span class="site-sidebar__link-title">{title}</span>',
        f'{indent}{unit}<span class="site-sidebar__link-meta">{desc}</span>',
        f"{indent}</a></li>",
    ]
    return eol.join(lines)


def build_group_summary(indent: str, unit: str, title: str, meta: str, eol: str) -> str:
    lines = [
        f"{indent}<summary>",
        f'{indent}{unit}<span class="site-sidebar__summary-text">{title}</span>',
        f'{indent}{unit}<span class="site-sidebar__summary-meta">{meta}</span>',
        f"{indent}</summary>",
    ]
    return eol.join(lines)


def build_sidebar(base_indent: str, current_file: str, eol: str) -> str:
    unit = detect_unit(base_indent)
    i1 = base_indent + unit
    i2 = i1 + unit
    i3 = i2 + unit
    i4 = i3 + unit
    layer = FILE_TO_LAYER[current_file]
    layer_title, layer_desc = LAYER_META[layer]
    lines = [
        f'{base_indent}<aside class="site-sidebar site-sidebar--story">',
        f'{i1}<div class="site-sidebar__brand"><a href="{href(current_file, "about.html")}"><i class="fas fa-feather-alt"></i> 法则与故事</a></div>',
        f'{i1}<div class="site-sidebar__intro">',
        f'{i2}<span class="site-sidebar__eyebrow">站点坐标</span>',
        f"{i2}<strong>{layer_title}</strong>",
        f"{i2}<p>{layer_desc}</p>",
        f"{i1}</div>",
    ]

    layers_to_render = [layer] if layer == "special" else VISIBLE_LAYERS
    for layer_name in layers_to_render:
        open_attr = " open" if layer_name == layer else ""
        current_desc, sibling_desc = LAYER_ITEM_META[layer_name]
        item_desc = current_desc if layer_name == layer else sibling_desc
        lines.extend([
            f'{i1}<details class="site-sidebar__group site-sidebar__group--{layer_name}"{open_attr}>',
            build_group_summary(i2, unit, LAYER_LABELS[layer_name], LAYER_SUMMARY_META[layer_name], eol),
            f'{i2}<div class="site-sidebar__group-body">',
            f"{i3}<ul>",
        ])
        for target, title in LAYER_GROUPS[layer_name]:
            lines.append(build_link(i4, unit, title, item_desc, href(current_file, target), current_file == target, eol, FILE_ICONS.get(target)))
        lines.extend([f"{i3}</ul>", f"{i2}</div>", f"{i1}</details>"])

    bridge_open = " open" if current_file == "aboutmore/wx.html" else ""
    lines.extend([
        f'{i1}<details class="site-sidebar__group"{bridge_open}>',
        build_group_summary(i2, unit, "技术源头", "从工程桥面回看整套法则的起点", eol),
        f'{i2}<div class="site-sidebar__group-body">',
        f"{i3}<ul>",
    ])
    for target, title, desc in TECH_SOURCE:
        lines.append(build_link(i4, unit, title, desc, href(current_file, target), False, eol, FILE_ICONS.get(target)))
    lines.extend([
        f"{i3}</ul>",
        f"{i2}</div>",
        f"{i1}</details>",
        f'{i1}<a href="{href(current_file, "index.html")}" class="site-sidebar__footer-link">← 返回首页</a>',
        f"{base_indent}</aside>",
    ])
    return eol.join(lines) + eol


def replace_sidebar(text: str, current_file: str, eol: str) -> str:
    start = text.find('<aside class="site-sidebar')
    if start == -1:
        start = text.find('<aside class="sidebar">')
    if start == -1:
        raise ValueError("Could not find story sidebar")
    end = text.find('<aside class="sidebar-toc">', start)
    if end == -1:
        end = text.find('<div class="main-content">', start)
    if end == -1:
        raise ValueError("Could not find story layout split")
    line_start = text.rfind(eol, 0, start)
    line_start = 0 if line_start == -1 else line_start + len(eol)
    end_line_start = text.rfind(eol, 0, end)
    end_line_start = 0 if end_line_start == -1 else end_line_start + len(eol)
    base_indent = text[line_start:start]
    return text[:line_start] + build_sidebar(base_indent, current_file, eol) + text[end_line_start:]


def clean_heading_text(content: str) -> str:
    text = re.sub(r"<[^>]+>", "", content)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def slugify_heading(title: str, used: set[str]) -> str:
    slug = title.lower()
    slug = re.sub(r"[^\w\u4e00-\u9fff\s-]", "", slug)
    slug = re.sub(r"[-\s]+", "-", slug).strip("-_")
    if not slug:
        slug = "section"
    candidate = slug
    counter = 2
    while candidate in used:
        candidate = f"{slug}-{counter}"
        counter += 1
    used.add(candidate)
    return candidate


def ensure_story_heading_ids(text: str) -> tuple[str, list[tuple[str, str]]]:
    main_start = text.find('<div class="main-content">')
    if main_start == -1:
        raise ValueError("Could not find main-content")
    main_end = text.find('</div>', main_start)
    footer_note = text.find('<div class="footer-note">', main_start)
    footer_badge = text.find('<div class="inland-security-footer">', main_start)
    if footer_note != -1:
        main_end = footer_note
    elif footer_badge != -1:
        main_end = footer_badge
    if main_end == -1:
        raise ValueError("Could not find end of main-content")

    segment = text[main_start:main_end]
    used_ids = set(re.findall(r'\bid="([^"]+)"', segment))
    toc_items: list[tuple[str, str]] = []
    heading_pattern = re.compile(r'<h2(?P<attrs>[^>]*)>(?P<body>.*?)</h2>', re.DOTALL)

    def repl(match: re.Match[str]) -> str:
        attrs = match.group("attrs")
        body = match.group("body")
        title = clean_heading_text(body)
        if not title:
            return match.group(0)
        id_match = re.search(r'\bid="([^"]+)"', attrs)
        if id_match:
            heading_id = id_match.group(1)
            used_ids.add(heading_id)
        else:
            heading_id = slugify_heading(title, used_ids)
            attrs = f'{attrs} id="{heading_id}"'
        toc_items.append((heading_id, title))
        return f'<h2{attrs}>{body}</h2>'

    updated_segment = heading_pattern.sub(repl, segment)
    return text[:main_start] + updated_segment + text[main_end:], toc_items


def build_toc(indent: str, current_file: str, toc_items: list[tuple[str, str]], eol: str) -> str:
    unit = detect_unit(indent)
    icon = FILE_ICONS.get(current_file, "🗂️")
    if not toc_items:
        toc_items = [("top", "返回开头")]
    lines = [
        f'{indent}<aside class="sidebar-toc sidebar-toc--story">',
        f'{indent}{unit}<h3><span class="sidebar-toc__icon" aria-hidden="true">{icon}</span> 本章导航</h3>',
        f'{indent}{unit}<nav>',
        f'{indent}{unit}{unit}<ul>',
    ]
    for target, title in toc_items:
        lines.append(f'{indent}{unit}{unit}{unit}<li><a href="#{target}">{title}</a></li>')
    lines.extend([
        f'{indent}{unit}{unit}</ul>',
        f'{indent}{unit}</nav>',
        f'{indent}</aside>',
    ])
    return eol.join(lines)


def replace_toc(text: str, current_file: str, toc_items: list[tuple[str, str]], eol: str) -> str:
    pattern = re.compile(r'(?P<indent>^[ \t]*)<aside class="sidebar-toc(?:[^"]*)">.*?</aside>\s*', re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    if match:
        toc = build_toc(match.group("indent"), current_file, toc_items, eol) + eol
        return text[: match.start()] + toc + text[match.end() :]

    main_content = text.find('<div class="main-content">')
    if main_content == -1:
        raise ValueError("Could not find main-content")
    line_start = text.rfind(eol, 0, main_content)
    line_start = 0 if line_start == -1 else line_start + len(eol)
    indent = text[line_start:main_content]
    toc = build_toc(indent, current_file, toc_items, eol) + eol
    return text[:main_content] + toc + text[main_content:]


def build_series_nav(indent: str, current_file: str, eol: str) -> str:
    unit = detect_unit(indent)
    flow_files = [item[0] for item in VISIBLE_FLOW]
    titles = {file_name: title for file_name, title, _ in VISIBLE_FLOW}
    index = flow_files.index(current_file)
    prev_target = ("gd.html", "⑯ 始于工程，服务生活") if index == 0 else (flow_files[index - 1], titles[flow_files[index - 1]])
    next_target = ("index.html", "五层进化") if index == len(flow_files) - 1 else (flow_files[index + 1], titles[flow_files[index + 1]])
    return eol.join([
        f'{indent}<div class="series-nav">',
        f'{indent}{unit}<a href="{href(current_file, prev_target[0])}">← {prev_target[1]}</a>',
        f'{indent}{unit}<a href="{href(current_file, next_target[0])}">{next_target[1]} →</a>',
        f"{indent}</div>",
    ])


def replace_series_nav(text: str, current_file: str, eol: str) -> str:
    if current_file == "aboutmore/ff.html":
        return text
    pattern = re.compile(r'(?P<indent>^[ \t]*)<div class="series-nav"[^>]*>.*?</div>\s*', re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    if match:
        nav = build_series_nav(match.group("indent"), current_file, eol) + eol
        return text[: match.start()] + nav + text[match.end() :]
    footer_note = text.find('<div class="footer-note">')
    if footer_note == -1:
        footer_note = text.find('<div class="inland-security-footer">')
    if footer_note == -1:
        raise ValueError("Could not find insertion point for series-nav")
    line_start = text.rfind(eol, 0, footer_note)
    line_start = 0 if line_start == -1 else line_start + len(eol)
    indent = text[line_start:footer_note]
    nav = build_series_nav(indent, current_file, eol) + eol
    return text[:footer_note] + nav + text[footer_note:]


def sync_file(file_name: str) -> bool:
    path = ROOT / file_name
    text = path.read_text(encoding="utf-8")
    eol = detect_eol(text)
    updated = ensure_shared_css(text, file_name, eol)
    updated = remove_generated_sidebar_css(updated, eol)
    updated = replace_sidebar(updated, file_name, eol)
    updated, toc_items = ensure_story_heading_ids(updated)
    updated = replace_toc(updated, file_name, toc_items, eol)
    updated = replace_series_nav(updated, file_name, eol)
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8", newline="")
    return True


def main() -> None:
    changed = []
    for file_name in FILES:
        if sync_file(file_name):
            changed.append(file_name)
    if changed:
        print("Updated nontechnical sidebars:")
        for file_name in changed:
            print(f"- {file_name}")
    else:
        print("No nontechnical sidebar changes were needed.")


if __name__ == "__main__":
    main()