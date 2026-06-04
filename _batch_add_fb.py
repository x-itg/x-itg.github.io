#!/usr/bin/env python3
"""批量在底部系列导航中添加 fb.html 链接。"""
import re
from pathlib import Path

files = [f for f in Path('.').rglob('*.html')
         if f.name not in ('fb.html', 'index.html')]

# Pattern: lj.html link · newline+spaces · 14.html link
pat = re.compile(
    r'(<a href="lj\.html">[^<]+</a>\s*\u00b7\s*\n)(\s*)(<a href="14\.html">)',
    re.MULTILINE
)

count = 0
for f in files:
    text = f.read_text(encoding='utf-8')
    if 'bottom-series-links' not in text:
        continue
    bsl_start = text.find('bottom-series-links')
    bsl_end = text.find('</div>', bsl_start)
    bsl_chunk = text[bsl_start:bsl_end] if bsl_end > bsl_start else ''
    if 'fb.html' in bsl_chunk:
        print(f'Already has fb in nav: {f}')
        continue
    m = pat.search(text, bsl_start)
    if m and (bsl_end < 0 or m.start() < bsl_end):
        indent = m.group(2)
        fb_link = f'<a href="fb.html">\u522b\u628aAI\u7528\u6210\u4ed8\u8d39\u4e0a\u73ed</a> \u00b7\n{indent}'
        new_text = text[:m.end(1)] + indent + fb_link + text[m.start(3):]
        f.write_text(new_text, encoding='utf-8')
        count += 1
        print(f'Updated: {f}')
    else:
        print(f'SKIP (no match): {f}')
print(f'\nTotal updated: {count}')
