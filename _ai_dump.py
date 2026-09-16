# -*- coding: utf-8 -*-
"""导出全站 AI 味否定/对仗句式的原文片段（含标签），供批量替换使用。"""
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent

PATTERNS = [
    re.compile(r"不是[^。！？；\n]{0,40}?而是"),
    re.compile(r"并非[^。！？；\n]{0,40}?而是"),
    re.compile(r"不[在是][^。！？；\n]{0,40}?而[在是]"),
    re.compile(r"与其[^。！？；\n]{0,50}?不如"),
    re.compile(r"不只是[^。！？；\n]{0,40}?[更也]是"),
    re.compile(r"不再是[^。！？；\n]{0,40}?而是"),
    re.compile(r"没有[^。！？；\n]{0,30}?只有"),
    re.compile(r"不是[^。！？；\n]{0,30}?，是"),
    re.compile(r"不[是能会][^。！？；\n]{0,30}?，[这那]是"),
    re.compile(r"不[是能会][^。！？；\n]{0,20}?，?只是"),
    re.compile(r"不[追选][^。！？；\n]{0,22}?而[在追选]"),
]

SCRIPT = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE)

out = []
for fp in sorted(ROOT.rglob("*.html")):
    if fp.name in {"bundle.html", "google54a4d9b75b7c0938.html"}:
        continue
    if "node_modules" in fp.parts:
        continue
    raw = fp.read_text(encoding="utf-8", errors="replace")
    raw = SCRIPT.sub(lambda m: "\n" * m.group(0).count("\n"), raw)
    for i, line in enumerate(raw.split("\n"), 1):
        spans = []
        for pat in PATTERNS:
            for m in pat.finditer(line):
                spans.append((m.start(), m.end()))
        # 合并重叠
        spans.sort()
        merged = []
        for s, e in spans:
            if merged and s <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], e))
            else:
                merged.append((s, e))
        for s, e in merged:
            before = line[max(0, s - 22):s]
            mid = line[s:e]
            after = line[e:e + 22]
            out.append("%s|%d|%s[[[%s]]]%s" % (fp.relative_to(ROOT).as_posix(), i, before, mid, after))

(ROOT / "_ai_dump.txt").write_text("\n".join(out), encoding="utf-8")
print("导出条目：", len(out))
print("已写入 _ai_dump.txt")
