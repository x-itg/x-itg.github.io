#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量优化技术文章HTML文件到100分标准
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# 需要优化的文件列表
FILES_TO_OPTIMIZE = [
    "true.html", "fwd.html", "exc.html", "in.html", "pcb.html", 
    "pt.html", "history.html", "ocd.html", "devs.html", "gmp.html", 
    "14.html", "13.html", "12.html", "py.html"
]

# 卡片CSS优化代码
CARD_CSS = """
        .card.accent-left { border-left: 4px solid var(--accent); }
        .card.philosophy { 
            border-left: 4px solid #8e44ad; 
            background: linear-gradient(135deg, #faf5ff 0%, #f5f0ff 100%);
        }
        .card.engineer { 
            border-left: 4px solid #2980b9; 
            background: linear-gradient(135deg, #f0f8ff 0%, #e8f4f8 100%);
        }
        .card.action { 
            border-left: 4px solid #27ae60; 
            background: linear-gradient(135deg, #f0fff4 0%, #e8f8ee 100%);
        }
        .card.vision { 
            border-left: 4px solid #3b82f6; 
            background: linear-gradient(135deg, #f0f8ff 0%, #e6f2ff 100%);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .card.vision:hover { 
            transform: translateY(-2px); 
            box-shadow: var(--shadow-md); 
        }
        .card {
            text-align: left;
        }
        .card p {
            text-align: left;
            margin: 0;
        }
        .card p:first-child {
            margin-top: 0;
        }
        .card p:last-child {
            margin-bottom: 0;
        }
        .card strong {
            display: block;
            color: var(--text);
            font-weight: 600;
            margin-bottom: 8px;
        }
        .card pre {
            text-align: left;
            margin: 12px 0 0;
            background: #1e293b;
            color: #e2e8f0;
            padding: 16px 20px;
            border-radius: 6px;
            font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", "SF Mono", "Consolas", monospace;
            font-size: 13px;
            line-height: 1.7;
            overflow-x: auto;
        }

        .insight-box {
            background: linear-gradient(135deg, #fef9e7 0%, #fef5d7 100%);
            border: 1px solid #f0d78c;
            border-left: 4px solid #f39c12;
            border-radius: var(--radius);
            padding: 20px 24px;
            margin: 24px 0;
            font-style: italic;
            color: #6b4c1e;
            text-align: left;
        }
        .insight-box strong {
            color: #4a340f;
            font-weight: 600;
        }
        .insight-box.decision { 
            background: linear-gradient(135deg, #e8f4f8 0%, #dceef5 100%);
            border-color: #a8d4e0; 
            border-left-color: #3498db;
            color: #1a5276; 
        }
        .insight-box.decision strong { 
            color: #0e3a57; 
        }
        .insight-box.warm { 
            background: linear-gradient(135deg, #fef9e7 0%, #fef5d7 100%);
            border-color: #f0d78c; 
            border-left-color: #f39c12;
            color: #6b4c1e; 
        }
        .insight-box.warm strong { 
            color: #4a340f; 
        }
        .insight-box.cool { 
            background: linear-gradient(135deg, #eaf2f8 0%, #dce8f2 100%);
            border-color: #a9cce3; 
            border-left-color: #2980b9;
            color: #1f4e79; 
        }
        .insight-box.cool strong { 
            color: #154360; 
        }
"""

def optimize_file(file_name):
    """优化单个HTML文件"""
    path = ROOT / file_name
    if not path.exists():
        print(f"⚠️  文件不存在: {file_name}")
        return False
    
    text = path.read_text(encoding="utf-8")
    original_text = text
    
    # 1. 添加卡片CSS（如果不存在）
    if ".card.philosophy" not in text:
        # 找到</style>标签前的位置
        style_end = text.rfind("</style>")
        if style_end != -1:
            # 在</style>前插入CSS
            text = text[:style_end] + CARD_CSS + "\n" + text[style_end:]
            print(f"✅ {file_name}: 添加卡片CSS")
    
    # 2. 优化series-nav的aria-label
    # 匹配 <a href="xxx.html">← 标题</a> 并添加aria-label
    series_nav_pattern = r'(<div class="series-nav">.*?</div>)'
    match = re.search(series_nav_pattern, text, re.DOTALL)
    if match:
        nav_block = match.group(1)
        # 为上一篇添加aria-label
        nav_block = re.sub(
            r'<a href="([^"]+)">←\s*([^<]+)</a>',
            r'<a href="\1" aria-label="上一篇：\2">← \2</a>',
            nav_block
        )
        # 为下一篇添加aria-label  
        nav_block = re.sub(
            r'<a href="([^"]+)">([^<]+)\s*→</a>',
            r'<a href="\1" aria-label="下一篇：\2">\2 →</a>',
            nav_block
        )
        text = text.replace(match.group(1), nav_block)
        print(f"✅ {file_name}: 优化series-nav无障碍访问")
    
    # 3. 优化quote-block（如果存在）
    if "quote-block" in text and "text-align: left" not in text:
        text = text.replace(
            "text-align: center;",
            "text-align: left;"
        )
        print(f"✅ {file_name}: 优化quote-block对齐")
    
    if text != original_text:
        path.write_text(text, encoding="utf-8", newline="")
        return True
    else:
        print(f"⏭️  {file_name}: 无需修改")
        return False

def main():
    print("🚀 开始批量优化技术文章...\n")
    
    success_count = 0
    for file_name in FILES_TO_OPTIMIZE:
        if optimize_file(file_name):
            success_count += 1
    
    print(f"\n✨ 优化完成！共处理 {success_count}/{len(FILES_TO_OPTIMIZE)} 个文件")

if __name__ == "__main__":
    main()
