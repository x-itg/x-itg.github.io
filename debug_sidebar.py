import re
from pathlib import Path

out = Path('c:/z/x-itg.github.io/debug_out.txt')
text = Path('c:/z/x-itg.github.io/index.html').read_text(encoding='utf-8')
lines = []
lines.append(f"File length: {len(text)}")

# Test sidebar regex
pat = re.compile(r'(?P<indent>^[ \t]*)<aside\s+class="(?:site-sidebar|sidebar-series|sidebar)[^"]*"', re.MULTILINE)
m = pat.search(text)
if m:
    lines.append(f"Sidebar found at {m.start()}: {m.group(0)!r}")
else:
    lines.append("Sidebar NOT found")
    idx = text.find('site-sidebar')
    lines.append(f"site-sidebar string at pos {idx}")
    if idx > 0:
        lines.append(f"Context: {text[max(0,idx-50):idx+80]!r}")

bm = re.search(r'<body([^>]*)>', text)
if bm:
    lines.append(f"Body tag: <body{bm.group(1)}>")
else:
    lines.append("Body tag NOT found")

toc = text.find('sidebar-toc')
lines.append(f"sidebar-toc at pos: {toc}")
lines.append(f"Has site-theme-tech: {'site-theme-tech' in text}")

out.write_text('\n'.join(lines), encoding='utf-8')
print('Done')
