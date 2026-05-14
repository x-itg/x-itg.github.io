#!/usr/bin/env python3
"""为所有 10 篇文章源文件在 body 开头添加「关于作者」绿色链接卡片"""
import os, re

FILES = [
    "devs.html", "exc.html", "fwd.html", "gmp.html",
    "history.html", "index.html", "pcb.html", "pt.html",
    "test.html", "true.html",
]

BADGE = (
    '<div style="max-width:1400px;margin:0 auto;padding:8px 1rem 0;">'
    '<a href="about.html" style="display:inline-block;background:#22c55e;color:#fff;'
    'font-size:13px;font-weight:700;padding:4px 14px;border-radius:6px;'
    'text-decoration:none;">&#x1F446; 关于作者</a>'
    '</div>'
)

for fn in FILES:
    path = os.path.join(".", fn)
    if not os.path.exists(path):
        print(f"  !! 不存在: {fn}")
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 先移除之前误插在 <body> 后的卡片
    content = re.sub(
        r'<div style="max-width:1400px;margin:0 auto;padding:8px 1rem 0;">'
        r'<a href="about\.html" style="display:inline-block;background:#22c55e;color:#fff;'
        r'font-size:13px;font-weight:700;padding:4px 14px;border-radius:6px;'
        r'text-decoration:none;">&#x1F446; 关于作者</a></div>\s*',
        '', content, count=1
    )

    # 检查是否已有正确的卡片（在 <h1> 前）
    if '&#x1F446; 关于作者' in content:
        print(f"  -- 已存在正确位置，跳过: {fn}")
        continue

    # 在第一个 <h1> 前插入（标题上方）
    new = re.sub(
        r'(<h1\b[^>]*>)',
        lambda m: '\n' + BADGE + '\n' + m.group(0),
        content, count=1
    )
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new)
    print(f"  + 已更新: {fn}")

print("\n完成！")
