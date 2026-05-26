from __future__ import annotations

import re
from pathlib import Path

import sync_nontechnical_sidebar
import sync_technical_sidebar


ROOT = Path(__file__).resolve().parent
FILES = sync_technical_sidebar.TECH_FILES + sync_nontechnical_sidebar.FILES
FOOTER_URL = "https://x-itg.github.io/about.html"


def detect_eol(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def detect_unit(indent: str) -> str:
    return "\t" if "\t" in indent else "    "


def strip_css_rules(text: str, selectors: list[str]) -> str:
    updated = text
    for selector in selectors:
        pattern = re.compile(rf'^[ \t]*{re.escape(selector)}\s*\{{[^{{}}]*\}}\s*', re.MULTILINE)
        updated = pattern.sub("", updated)
    return updated


def remove_footer_css(text: str) -> str:
    updated = strip_css_rules(
        text,
        [
            ".inland-security-footer",
            ".tooltip-container",
            ".trigger-content",
            ".x-itg-link",
            ".x-itg-link:visited",
            ".x-itg-link:hover",
            ".tooltip-content",
            ".tooltip-content::after",
            ".tooltip-container:hover .tooltip-content",
            ".tooltip-container:focus-within .tooltip-content",
            ".info-section",
        ],
    )
    media_pattern = re.compile(
        r'^[ \t]*@media\s*\(max-width:\s*640px\)\s*\{[^{}]*\.inland-security-footer[^{}]*\.x-itg-link[^{}]*\}\s*',
        re.MULTILINE,
    )
    updated = media_pattern.sub("", updated)
    style_pattern = re.compile(r'<style>\s*(?:(?:(?!</style>).)*(?:inland-security-footer|x-itg-link|tooltip-content|tooltip-container|trigger-content|info-section).*)?</style>\s*', re.DOTALL)
    updated = style_pattern.sub("", updated)
    empty_style_pattern = re.compile(r'<style>\s*</style>\s*', re.DOTALL)
    updated = empty_style_pattern.sub("", updated)
    dangling_closers_pattern = re.compile(r'(?P<footer></div>\s*</div>\s*</div>)(?:\s*</div>\s*</div>)+(?=\s*</body>)', re.DOTALL)
    return dangling_closers_pattern.sub(lambda match: match.group("footer"), updated)


def build_footer(indent: str, eol: str) -> str:
    unit = detect_unit(indent)
    i1 = indent + unit
    i2 = i1 + unit
    i3 = i2 + unit
    return eol.join(
        [
            f'{indent}<div class="inland-security-footer">',
            f'{i1}<div class="tooltip-container">',
            f'{i2}<div class="trigger-content">',
            f'{i3}<a href="{FOOTER_URL}" target="_blank" rel="noreferrer" class="x-itg-link">',
            f'{i3}{unit}<span>itg · -lvgl-</span>',
            f"{i3}</a>",
            f"{i2}</div>",
            f'{i2}<div class="tooltip-content">',
            f'{i3}<section class="info-section"><span>itg</span></section>',
            f'{i3}<section class="info-section"><span>微信号: -lvgl-</span></section>',
            f"{i2}</div>",
            f"{i1}</div>",
            f"{indent}</div>",
        ]
    )


def replace_footer(text: str, eol: str) -> str:
    body_end = text.find("</body>")
    if body_end == -1:
        raise ValueError("Could not find </body> for footer insertion")
    footer_start = text.rfind('<div class="inland-security-footer">', 0, body_end)
    if footer_start != -1:
        line_start = text.rfind(eol, 0, footer_start)
        line_start = 0 if line_start == -1 else line_start + len(eol)
        indent = text[line_start:footer_start]
        footer_html = build_footer(indent, eol) + eol
        return text[:line_start] + footer_html + text[body_end:]

    line_start = text.rfind(eol, 0, body_end)
    indent = "" if line_start == -1 else text[line_start + len(eol) : body_end]
    footer_html = build_footer(indent, eol) + eol
    return text[:body_end] + footer_html + text[body_end:]


def sync_file(file_name: str) -> bool:
    path = ROOT / file_name
    text = path.read_text(encoding="utf-8")
    eol = detect_eol(text)
    updated = remove_footer_css(text)
    updated = replace_footer(updated, eol)
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
        print("Updated footer badges:")
        for file_name in changed:
            print(f"- {file_name}")
    else:
        print("No footer badge changes were needed.")


if __name__ == "__main__":
    main()