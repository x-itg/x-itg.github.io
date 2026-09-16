# -*- coding: utf-8 -*-
"""全站扫描 AI 味否定句 / 对仗句"""
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent

PATTERNS = [
    ("不是A而是B", re.compile(r"不是[^。！？；\n]{0,40}?而是")),
    ("并非A而是B", re.compile(r"并非[^。！？；\n]{0,40}?而是")),
    ("不在A而在B", re.compile(r"不[在是][^。！？；\n]{0,40}?而[在是]")),
    ("与其说A不如说B", re.compile(r"与其[^。！？；\n]{0,50}?不如")),
    ("不只是A更是B", re.compile(r"不只是[^。！？；\n]{0,40}?[更也]是")),
    ("不再是A而是B", re.compile(r"不再是[^。！？；\n]{0,40}?而是")),
    ("没有A只有B", re.compile(r"没有[^。！？；\n]{0,30}?只有")),
    ("不是A是B", re.compile(r"不是[^。！？；\n]{0,30}?，是")),
    ("不是A这是B", re.compile(r"不[是能会][^。！？；\n]{0,30}?，[这那]是")),
    ("不…只是…", re.compile(r"不[是能会][^。！？；\n]{0,20}?，?只是")),
]

TAG = re.compile(r"<[^>]+>")
SCRIPT = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE)

hits = {}
total = 0
for fp in sorted(ROOT.rglob("*.html")):
    if fp.name in {"bundle.html", "google54a4d9b75b7c0938.html"}:
        continue
    if "node_modules" in fp.parts:
        continue
    raw = fp.read_text(encoding="utf-8", errors="replace")
    # 用等量换行替换 script/style，保持原始行号不变
    raw = SCRIPT.sub(lambda m: "\n" * m.group(0).count("\n"), raw)
    lines = raw.split("\n")
    for i, line in enumerate(lines, 1):
        text = TAG.sub("", line)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        for name, pat in PATTERNS:
            if pat.search(text):
                hits.setdefault(name, []).append((fp.relative_to(ROOT).as_posix(), i, text))
                total += 1
                break

print("=" * 70)
print("总命中：", total)
for name, _ in PATTERNS:
    print("  %-14s %d" % (name, len(hits.get(name, []))))
print("=" * 70)

by_file = {}
for name, items in hits.items():
    for f, ln, t in items:
        by_file.setdefault(f, []).append((ln, name, t))

rank = sorted(by_file.items(), key=lambda kv: -len(kv[1]))
print("\n【按文件排序 Top 20】")
for f, items in rank[:20]:
    print("  %-32s %d" % (f, len(items)))

show = sys.argv[1] if len(sys.argv) > 1 else None
if show:
    print("\n" + "=" * 70)
    for f, items in rank:
        if show not in f:
            continue
        for ln, name, t in sorted(items):
            print("[%s:%d] %s" % (f, ln, name))
            print("    " + t[:180])
