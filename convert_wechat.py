#!/usr/bin/env python3
"""
将7篇嵌入式AI工程化HTML文章转换为微信公众号编辑器可识别的格式。
输出到 ./wechat/ 目录，每个文件可直接复制粘贴到公众号编辑器。
关键策略：先保护 <pre> 代码块，再执行所有清理/转换，最后恢复 <pre> 并加内联样式。
"""
import re
import os

OUT_DIR = "wechat"
os.makedirs(OUT_DIR, exist_ok=True)

ARTICLES = [
    ("index.html", 1, "五层进化", "AI编程调试的五层架构"),
    ("true.html",  2, "实践项目模板", "高可复用嵌入式AI编程骨架"),
    ("test.html",  3, "自主修复闭环", "AI双轨收敛 . 需求螺旋闭合"),
    ("pcb.html",   4, "电路图分析器", "PDF原理图转AI可读描述"),
    ("exc.html",   5, "共生演化", "规格-实现知识一致性"),
    ("history.html",6, "历史的包袱", "遗留工程与AI迁移策略"),
    ("pt.html",    7, "最后的拼图：Skills", "规则感知型即时方法"),
]

# ======================== <pre>/<code> 保护机制 ========================

PRE_PLACEHOLDER = "___PRE_BLOCK_{}___"

def protect_code_blocks(html):
    """用占位符替换所有 <pre>...</pre> 和 .code-block 内的 <code>...</code> 块。
    保留独立的单行 <code> 作为行内代码。返回 (处理后的html, 替换列表)"""
    blocks = []

    def dedent_text(text):
        """去除代码文本的公共前导缩进（类似 textwrap.dedent）
        第一行常与 <pre> 平齐无缩进，从第二行开始计算最小缩进。"""
        lines = text.split('\n')
        if len(lines) <= 1:
            return text
        # 从第二行开始找非空行的最小缩进
        indent_sizes = [len(line) - len(line.lstrip()) for line in lines[1:] if line.strip()]
        min_indent = min(indent_sizes) if indent_sizes else 0
        if min_indent:
            # 只去掉前导空白（空格/制表符），不碰内容字符
            stripped = []
            for line in lines:
                if len(line) >= min_indent and line[:min_indent].strip() == '':
                    stripped.append(line[min_indent:])
                else:
                    stripped.append(line)
            lines = stripped
        return '\n'.join(lines)

    def save(m, tag_open='<pre', tag_close='</pre>'):
        idx = len(blocks)
        content = m.group(0)
        content = re.sub(rf'{tag_open}[^>]*>', '<pre>', content, count=1)
        content = content.replace(tag_close, '</pre>')
        content = re.sub(r'(?<=<pre>)(.*?)(?=</pre>)', lambda m2: dedent_text(m2.group(1)), content, flags=re.DOTALL)
        blocks.append(content)
        return PRE_PLACEHOLDER.format(idx)

    def pre_replacer(m): return save(m, '<pre', '</pre>')
    html = re.sub(r'<pre[^>]*>.*?</pre>', pre_replacer, html, flags=re.DOTALL)

    def code_block_replacer(m):
        code_match = re.search(r'<code[^>]*>(.*?)</code>', m.group(0), re.DOTALL)
        if code_match:
            idx = len(blocks)
            raw_code = code_match.group(1)
            raw_code = dedent_text(raw_code)
            content = '<pre>' + raw_code + '</pre>'
            blocks.append(content)
            return '<div>' + PRE_PLACEHOLDER.format(idx) + '</div>'
        return m.group(0)
    html = re.sub(r'<div[^>]*class="code-block"[^>]*>.*?</div>', code_block_replacer, html, flags=re.DOTALL)

    return html, blocks

def restore_code_blocks(html, blocks):
    span_styles = {
        'keyword': 'color:#c792ea;',
        'string': 'color:#c3e88d;',
        'comment': 'color:#546e7a;font-style:italic;',
        'func': 'color:#82aaff;',
        'type': 'color:#ffcb6b;',
        'dir': 'color:#7dd3fc;',
        'file': 'color:#a5b4fc;',
        'layer-tag': 'display:inline-block;background:#1a1a2e;color:#fff;font-size:11px;padding:2px 10px;border-radius:3px;font-weight:600;',
    }
    pre_style = ('<pre style="'
        'background:#1e293b;'
        'color:#e2e8f0;'
        'padding:16px 20px;'
        'border-radius:6px;'
        'font-family:Consolas,monospace;'
        'font-size:13px;'
        'line-height:1.7;'
        'margin:16px 0;'
        'overflow-x:auto;'
        'white-space:pre-wrap;'
    '">')
    for idx, block in enumerate(blocks):
        block = re.sub(r'<pre[^>]*>', pre_style, block, count=1)
        for cls, style in span_styles.items():
            block = re.sub(rf'<span[^>]*class="{cls}"[^>]*>', f'<span style="{style}">', block)
        m = re.match(r'(<pre[^>]*>)(.*)(</pre>)', block, re.DOTALL)
        if m:
            lines_raw = m.group(2).split('\n')
            wrapped = []
            for line in lines_raw:
                if line.strip() == '':
                    wrapped.append('<span style="display:block;"><br></span>')
                else:
                    wrapped.append(f'<span style="display:block;">{line}</span>')
            block = m.group(1) + ''.join(wrapped) + m.group(3)
        html = html.replace(PRE_PLACEHOLDER.format(idx), block)
    return html

# ======================== 导航生成 ========================

def build_nav(current_num):
    lines = ['<div style="background:#f8f9fa;border:1px solid #e0e4e8;border-radius:8px;padding:16px 20px;margin:0 0 32px 0;font-size:14px;line-height:1.8;">']
    lines.append('<strong style="color:#1a1a2e;font-size:15px;">[嵌入式AI工程化系列]</strong><br>')
    for fn, num, title, desc in ARTICLES:
        if num == current_num:
            lines.append(f'<span style="display:inline-block;background:#c0392b;color:#fff;padding:1px 8px;border-radius:3px;font-weight:700;margin:2px 0;">第{num}篇</span> <strong>{title}</strong> <span style="color:#8896a4;font-size:13px;">-- {desc}</span><br>')
        else:
            lines.append(f'<span style="display:inline-block;background:#f0f3f6;color:#4a5568;padding:1px 8px;border-radius:3px;margin:2px 0;">第{num}篇</span> {title} <span style="color:#8896a4;font-size:13px;">-- {desc}</span><br>')
    lines.append('</div>')
    return '\n'.join(lines)

def build_footer_nav(current_num):
    prev_link = ""
    next_link = ""
    for fn, num, title, desc in ARTICLES:
        if num == current_num - 1:
            prev_fn = fn
            prev_link = f'<a href="{prev_fn}" style="color:#2980b9;">&lt; 上一篇：{title}</a>'
        if num == current_num + 1:
            next_fn = fn
            next_link = f'<a href="{next_fn}" style="color:#2980b9;">下一篇：{title} &gt;</a>'
    parts = ['<div style="margin-top:40px;padding-top:20px;border-top:2px solid #e0e4e8;font-size:14px;text-align:center;line-height:2.2;">']
    if prev_link:
        parts.append(f'<span style="margin-right:20px;">{prev_link}</span>')
    if next_link:
        parts.append(f'<span>{next_link}</span>')
    parts.append('<br><a href="index.html" style="color:#2980b9;">[返回系列首页]</a>')
    parts.append('</div>')
    return '\n'.join(parts)

# ======================== 清理与转换 ========================

def clean_html_safe(raw):
    raw = re.sub(r'<style[^>]*>.*?</style>', '', raw, flags=re.DOTALL)
    raw = re.sub(r'<link[^>]*>', '', raw)
    raw = re.sub(r'<script[^>]*>.*?</script>', '', raw, flags=re.DOTALL)
    raw = re.sub(r'<svg[^>]*>.*?</svg>', '', raw, flags=re.DOTALL)
    raw = re.sub(r'<i[^>]*class="[^"]*fa[^"]*"[^>]*>.*?</i>', '', raw, flags=re.DOTALL)
    raw = re.sub(r'<i[^>]*>\s*</i>', '', raw)
    raw = re.sub(r'<nav[^>]*class="(?:top-nav|page-nav)"[^>]*>.*?</nav>', '', raw, flags=re.DOTALL)
    raw = re.sub(r'<aside[^>]*class="sidebar"[^>]*>.*?</aside>', '', raw, flags=re.DOTALL)
    raw = re.sub(r'<div[^>]*class="layout"[^>]*>', '', raw)
    raw = re.sub(r'<div[^>]*class="main-content"[^>]*>', '', raw)
    raw = re.sub(r'<div[^>]*class="sidebar-utility"[^>]*>.*?</div>', '', raw, flags=re.DOTALL)
    raw = re.sub(r'<div[^>]*class="section-nav"[^>]*>.*?</div>', '', raw, flags=re.DOTALL)
    raw = re.sub(r'<div[^>]*class="article-series"[^>]*>.*?</div>', '', raw, flags=re.DOTALL)
    raw = re.sub(r'<a[^>]*class="back-link"[^>]*>.*?</a>', '', raw)
    raw = re.sub(r'<span[^>]*class="sep"[^>]*>.*?</span>', '', raw)
    raw = re.sub(r'<span[^>]*class="choice[^"]*"[^>]*>', '<strong style="color:#c0392b;">', raw)
    raw = raw.replace('</figure>', '')
    raw = re.sub(r'<div[^>]*class="step-content"[^>]*>', '', raw)
    return raw

def convert_classes_to_inline(html):
    rules = [
        (r'<div[^>]*class="container"[^>]*>', '<div style="max-width:780px;margin:0 auto;">'),
        (r'<div[^>]*class="hero"[^>]*>', '<div style="background:linear-gradient(135deg,#ffffff,#f0f6ff);border-radius:16px;padding:24px;margin-bottom:24px;border:1px solid #e2edf5;">'),
        (r'<div[^>]*class="sub"[^>]*>', '<div style="font-size:17px;color:#2c4f7c;border-left:3px solid #3b82f6;padding-left:16px;margin-bottom:16px;">'),
        (r'<header[^>]*class="article-header"[^>]*>', '<div style="margin-bottom:40px;">'),
        (r'</header>', '</div>'),
        (r'<span[^>]*class="series-tag"[^>]*>', '<span style="display:inline-block;background:#c0392b;color:#fff;font-size:13px;font-weight:700;padding:4px 12px;border-radius:3px;margin-bottom:16px;">'),
        (r'<p[^>]*class="subtitle"[^>]*>', '<p style="font-size:17px;color:#5a6c7d;font-weight:400;margin-bottom:20px;border-left:3px solid #3b82f6;padding-left:16px;">'),
        (r'<p[^>]*class="meta"[^>]*>', '<p style="font-size:13px;color:#8896a4;">'),
        (r'<h1[^>]*>', '<h1 style="font-size:26px;font-weight:700;line-height:1.35;margin-bottom:12px;">'),
        (r'<h2[^>]*>', '<h2 style="font-size:24px;font-weight:700;margin:48px 0 16px;padding-top:20px;border-top:2px solid #e0e4e8;">'),
        (r'<h3[^>]*>', '<h3 style="font-size:19px;font-weight:600;margin:32px 0 12px;color:#1a1a2e;">'),
        (r'<h4[^>]*>', '<h4 style="font-size:16px;font-weight:600;margin:24px 0 8px;color:#1a1a2e;">'),
        (r'<p[^>]*>', '<p style="margin:14px 0;line-height:1.8;">'),
        (r'<ul[^>]*>', '<ul style="margin:14px 0 14px 20px;line-height:1.8;">'),
        (r'<ol[^>]*>', '<ol style="margin:14px 0 14px 20px;line-height:1.8;">'),
        (r'<li[^>]*>', '<li style="margin:6px 0;">'),
        (r'<code[^>]*>', '<code style="background:#eef1f5;padding:2px 6px;border-radius:3px;color:#c0392b;font-size:13px;font-family:Consolas,monospace;">'),
        (r'<table[^>]*>', '<table style="width:100%;border-collapse:collapse;margin:20px 0;font-size:14px;">'),
        (r'<th[^>]*>', '<th style="padding:10px 14px;text-align:left;border:1px solid #d0dbe6;background:#f5f7fa;font-weight:700;font-size:13px;">'),
        (r'<td[^>]*>', '<td style="padding:10px 14px;text-align:left;border:1px solid #d0dbe6;">'),
        (r'<div[^>]*class="(?:card|merged-section)"[^>]*accent-left[^>]*>', '<div style="background:#ffffff;border:1px solid #e0e4e8;border-radius:8px;padding:24px 28px;margin:24px 0;border-left:4px solid #c0392b;">'),
        (r'<div[^>]*class="card"[^>]*warning[^>]*>', '<div style="background:#fffdf7;border:1px solid #f0e5c0;border-radius:8px;padding:24px 28px;margin:24px 0;">'),
        (r'<div[^>]*class="card"[^>]*>', '<div style="background:#ffffff;border:1px solid #e0e4e8;border-radius:8px;padding:24px 28px;margin:24px 0;">'),
        (r'<div[^>]*class="card-light"[^>]*>', '<div style="background:#f8fafc;border-radius:8px;padding:14px 18px;border:1px solid #e5e7eb;">'),
        (r'<div[^>]*class="merged-section"[^>]*>', '<div style="background:linear-gradient(105deg,#ffffff,#f8fcff);border-top:4px solid #3b82f6;padding:24px;border-radius:12px;">'),
        (r'<div[^>]*class="insight-box"[^>]*>', '<div style="background:#fef9e7;border:1px solid #f0d78c;border-radius:6px;padding:18px 22px;margin:20px 0;color:#6b4c1e;line-height:1.7;">'),
        (r'<div[^>]*class="highlight"[^>]*>', '<div style="background:#eef9ff;border-left:4px solid #3b82f6;padding:14px 20px;border-radius:8px;margin:16px 0;">'),
        (r'<div[^>]*class="quote"[^>]*>', '<div style="border-left:3px solid #8b5cf6;background:#faf5ff;padding:14px 20px;border-radius:8px;margin:16px 0;">'),
        (r'<div[^>]*class="key-takeaway"[^>]*>', '<div style="background:linear-gradient(135deg,#ecfdf5,#d1fae5);border-radius:8px;padding:16px 20px;margin:14px 0;border:2px solid #10b981;">'),
        (r'<div[^>]*class="principle-card"[^>]*>', '<div style="background:linear-gradient(135deg,#fef3c7,#fde68a);border-radius:8px;padding:14px 18px;margin:12px 0;border-left:4px solid #f59e0b;">'),
        (r'<div[^>]*class="case-study"[^>]*>', '<div style="background:#f0fdf4;border-radius:8px;padding:16px 20px;margin:14px 0;border:1px solid #bbf7d0;">'),
        (r'<div[^>]*class="technique-card"[^>]*>', '<div style="background:white;border-radius:8px;padding:14px 18px;border:1px solid #e5e7eb;margin:12px 0;">'),
        (r'<div[^>]*class="report-block"[^>]*>', '<div style="background:#fafcfd;border:1px solid #d0dbe6;border-radius:6px;padding:18px 20px;margin:18px 0;font-size:14px;line-height:1.7;">'),
        (r'<div[^>]*class="report-label"[^>]*>', '<div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#8896a4;font-weight:700;margin-bottom:8px;">'),
        (r'<div[^>]*class="workflow-step"[^>]*>', '<div style="padding:14px;background:#f8fafc;border:1px solid #e0e4e8;border-radius:8px;margin:8px 0;">'),
        (r'<div[^>]*class="step-number"[^>]*>', '<div style="display:inline-block;width:32px;height:32px;background:#3b82f6;color:white;border-radius:50%;text-align:center;line-height:32px;font-weight:700;float:left;margin-right:12px;">'),
        (r'<div[^>]*class="step-num"[^>]*>', '<div style="display:inline-block;width:32px;height:32px;background:#3b82f6;color:white;border-radius:50%;text-align:center;line-height:32px;font-weight:700;float:left;margin-right:12px;">'),
        (r'<span[^>]*class="step-num"[^>]*>', '<span style="display:inline-block;width:32px;height:32px;background:#3b82f6;color:white;border-radius:50%;text-align:center;line-height:32px;font-weight:700;float:left;margin-right:12px;">'),
        (r'<div[^>]*class="phase-card"[^>]*>', '<div style="background:#ffffff;border:1px solid #e0e4e8;border-radius:8px;padding:24px 26px;margin:20px 0;">'),
        (r'<span[^>]*class="phase-number"[^>]*>', '<span style="display:inline-block;background:#1a1a2e;color:#fff;font-size:12px;font-weight:700;padding:3px 12px;border-radius:20px;margin-bottom:10px;">'),
        (r'<span[^>]*class="mechanism-label"[^>]*>', '<span style="display:inline-block;background:#f0f3f6;color:#4a5568;font-size:11px;font-weight:600;padding:3px 8px;border-radius:3px;margin-bottom:10px;">'),
        (r'<div[^>]*class="level-badge"[^>]*>', '<div style="display:inline-block;background:#eef3ff;padding:4px 14px;border-radius:30px;font-family:monospace;font-weight:600;font-size:13px;margin-bottom:14px;color:#1e3a8a;">'),
        (r'<div[^>]*class="badge"[^>]*>', '<div style="display:inline-block;background:#e8f0fe;border-radius:30px;padding:4px 14px;font-size:13px;font-weight:500;color:#1f598a;margin-bottom:12px;">'),
        (r'<span[^>]*class="innovation-tag"[^>]*>', '<span style="background:#8b5cf6;color:white;font-size:11px;padding:2px 8px;border-radius:12px;margin-left:6px;vertical-align:middle;">'),
        (r'<span[^>]*class="layer-tag"[^>]*>', '<span style="display:inline-block;background:#1a1a2e;color:#fff;font-size:11px;padding:2px 10px;border-radius:3px;font-weight:600;">'),
        (r'<span[^>]*class="vs-tag"[^>]*>', '<span style="display:inline-block;background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:4px;font-size:12px;margin-right:4px;">'),
        (r'<span[^>]*class="our-tag"[^>]*>', '<span style="display:inline-block;background:#dbeafe;color:#1e40af;padding:2px 8px;border-radius:4px;font-size:12px;">'),
        (r'<div[^>]*class="stats-grid"[^>]*>', '<div>'),
        (r'<div[^>]*class="stat-item"[^>]*>', '<div style="display:inline-block;width:48%;text-align:center;padding:12px;background:#f8fafc;border:1px solid #e0e4e8;border-radius:8px;margin:4px 1%;vertical-align:top;">'),
        (r'<div[^>]*class="stat-value"[^>]*>', '<div style="font-size:22px;font-weight:700;color:#3b82f6;">'),
        (r'<div[^>]*class="grid-2"[^>]*>', '<div style="margin:14px 0;">'),
        (r'<div[^>]*class="grid-3"[^>]*>', '<div style="margin:14px 0;">'),
        (r'<div[^>]*class="term-grid"[^>]*>', '<div style="margin:14px 0;">'),
        (r'<div[^>]*class="concept-table"[^>]*>', '<div>'),
        (r'<div[^>]*class="paradigm-list"[^>]*>', '<ul style="margin:14px 0;line-height:1.8;">'),
        (r'<div[^>]*class="dir-tree"[^>]*>', '<pre style="background:#1e2937;color:#e2e8f0;padding:14px 18px;border-radius:8px;font-family:Consolas,monospace;font-size:13px;line-height:1.8;margin:14px 0;overflow-x:auto;">'),
        (r'<div[^>]*class="ui-mockup"[^>]*>', '<div style="background:#1e2937;border-radius:8px;padding:14px;margin:14px 0;">'),
        (r'<div[^>]*class="ui-panel"[^>]*>', '<div style="background:#334155;border-radius:6px;padding:12px 10px;margin:8px 0;">'),
        (r'<div[^>]*class="ui-pdf-view"[^>]*>', '<div style="background:#f8fafc;border-radius:6px;text-align:center;color:#64748b;font-size:13px;padding:20px;margin:6px 0;">'),
        (r'<span[^>]*class="keyword"[^>]*>', '<span style="color:#c792ea;">'),
        (r'<span[^>]*class="string"[^>]*>', '<span style="color:#c3e88d;">'),
        (r'<span[^>]*class="comment"[^>]*>', '<span style="color:#546e7a;font-style:italic;">'),
        (r'<span[^>]*class="func"[^>]*>', '<span style="color:#82aaff;">'),
        (r'<span[^>]*class="type"[^>]*>', '<span style="color:#ffcb6b;">'),
        (r'<span[^>]*class="dir"[^>]*>', '<span style="color:#7dd3fc;">'),
        (r'<span[^>]*class="file"[^>]*>', '<span style="color:#a5b4fc;">'),
        (r'<figure[^>]*class="figure"[^>]*>', '<div style="margin:24px 0;text-align:center;">'),
        (r'<p[^>]*class="caption"[^>]*>', '<p style="font-size:12px;color:#8896a4;margin-top:8px;text-align:center;">'),
        (r'<div[^>]*class="footnote-section"[^>]*>', '<div style="margin-top:48px;padding-top:20px;border-top:1px solid #e0e4e8;">'),
        (r'<div[^>]*class="term-card"[^>]*>', '<div style="background:white;border-radius:8px;padding:14px;border:1px solid #e5e7eb;">'),
        (r'<div[^>]*class="phase-grid"[^>]*>', '<div style="margin:24px 0;">'),
    ]
    for pattern, replacement in rules:
        html = re.sub(pattern, replacement, html)
    html = re.sub(r'\sclass="[^"]*"', '', html)
    return html

# ======================== 卡片/步骤/统计 -> 表格 ========================

def convert_workflow_to_table(html):
    def replace_steps(m):
        block = m.group(0)
        steps = re.findall(
            r'<div style="padding:14px;background:#f8fafc;border:1px solid #e0e4e8;[^"]*"[^>]*>'
            r'\s*<(?:div|span) style="display:inline-block;width:32px;height:32px;background:#3b82f6;color:white;border-radius:50%;text-align:center;line-height:32px;font-weight:700;float:left;margin-right:12px;">(\d+)</(?:div|span)>'
            r'(?:\s*<div[^>]*>)?'
            r'\s*<h4[^>]*>([^<]+)</h4>'
            r'\s*<p[^>]*>([^<]*)</p>'
            r'(?:\s*</div>)?'
            r'\s*</div>'
            r'(?:</div>)?',
            block, re.DOTALL
        )
        if not steps or len(steps) < 2:
            return block
        rows = ['<table style="width:100%;border-collapse:collapse;margin:16px 0;border:1px solid #d0dbe6;">']
        for num, title, body in steps:
            rows.append('<tr>')
            rows.append('<td style="width:50px;text-align:center;vertical-align:middle;background:#f0f4fa;border:1px solid #d0dbe6;padding:14px 8px;">')
            rows.append(f'<div style="display:inline-block;width:36px;height:36px;background:#3b82f6;color:white;border-radius:50%;text-align:center;line-height:36px;font-weight:700;font-size:16px;">{num}</div>')
            rows.append('</td>')
            rows.append('<td style="padding:14px 18px;vertical-align:middle;background:#ffffff;border:1px solid #d0dbe6;">')
            rows.append(f'<div style="font-size:16px;font-weight:600;color:#1a1a2e;margin-bottom:4px;">{title}</div>')
            rows.append(f'<div style="font-size:14px;line-height:1.7;color:#4a5568;">{body}</div>')
            rows.append('</td>')
            rows.append('</tr>')
        rows.append('</table>')
        return '\n'.join(rows)

    step_div = (
        r'<div style="padding:14px;background:#f8fafc;border:1px solid #e0e4e8;[^"]*"[^>]*>'
        r'\s*<(?:div|span) style="display:inline-block;width:32px;height:32px;background:#3b82f6;color:white;border-radius:50%;text-align:center;line-height:32px;font-weight:700;float:left;margin-right:12px;">\d+</(?:div|span)>'
        r'(?:\s*<div[^>]*>)?'  # 可选的孤儿包装 div
        r'\s*<h4[^>]*>[^<]+</h4>'
        r'\s*<p[^>]*>[^<]*</p>'
        r'(?:\s*</div>)?'  # 可选的孤儿包装 div 闭合
        r'\s*</div>'
        r'(?:</div>)?'
    )
    pattern = rf'(?:{step_div}\s*){{2,6}}'
    html = re.sub(pattern, replace_steps, html, flags=re.DOTALL)
    return html

def convert_cards_to_table(html):
    def replace_cards(m):
        block = m.group(0)
        cards = re.findall(
            r'<div style="(?=[^"]*background:white)(?=[^"]*border:1px solid #e5e7eb)(?=[^"]*padding:\d+px)[^"]*"[^>]*>'
            r'<h4[^>]*>([^<]+)</h4>'
            r'(?:\s*<p[^>]*>([^<]*)</p>)?'
            r'\s*</div>',
            block, re.DOTALL
        )
        if not cards or len(cards) < 2:
            return block
        rows = ['<table style="width:100%;border-collapse:collapse;margin:16px 0;">']
        for i in range(0, len(cards), 2):
            rows.append('<tr>')
            for j in range(2):
                if i + j < len(cards):
                    title_text, body_text = cards[i + j]
                    body_text = body_text.strip()
                    rows.append('<td style="width:50%;padding:16px 18px;vertical-align:top;background:#ffffff;border:1px solid #d0dbe6;">')
                    rows.append(f'<div style="border-left:4px solid #3b82f6;padding-left:12px;margin-bottom:8px;font-size:16px;font-weight:600;color:#1a1a2e;">{title_text}</div>')
                    if body_text:
                        rows.append(f'<div style="font-size:14px;line-height:1.7;color:#4a5568;padding-left:4px;">{body_text}</div>')
                    rows.append('</td>')
            rows.append('</tr>')
        rows.append('</table>')
        return '\n'.join(rows)

    card_div = (
        r'<div style="(?=[^"]*background:white)(?=[^"]*border:1px solid #e5e7eb)(?=[^"]*padding:\d+px)[^"]*"[^>]*>'
        r'<h4[^>]*>[^<]+</h4>'
        r'(?:\s*<p[^>]*>[^<]*</p>)?'
        r'\s*</div>'
    )
    pattern = rf'<div[^>]*>(?:\s*{card_div}\s*){{2,6}}</div>'
    html = re.sub(pattern, replace_cards, html, flags=re.DOTALL)
    return html

def convert_stats_to_table(html):
    def replace_with_table(m):
        content = m.group(0)
        items = re.findall(
            r'<div style="display:inline-block;width:48%;[^"]*">'
            r'<div style="font-size:22px;font-weight:700;color:#3b82f6;">([^<]+)</div>'
            r'<div>([^<]+)</div>'
            r'</div>',
            content
        )
        if len(items) < 2:
            return m.group(0)
        rows = ['<table style="width:100%;border-collapse:collapse;margin:14px 0;border:1px solid #e0e4e8;">']
        for i in range(0, len(items), 2):
            rows.append('<tr>')
            for j in range(2):
                if i + j < len(items):
                    val, label = items[i + j]
                    rows.append('<td style="width:50%;padding:16px 12px;text-align:center;background:#f8fafc;border:1px solid #e0e4e8;vertical-align:top;">')
                    rows.append(f'<div style="font-size:22px;font-weight:700;color:#3b82f6;">{val}</div>')
                    rows.append(f'<div style="font-size:13px;color:#4a5568;margin-top:4px;">{label}</div>')
                    rows.append('</td>')
            rows.append('</tr>')
        rows.append('</table>')
        return ''.join(rows)

    item_pattern = (
        r'<div style="display:inline-block;width:48%;[^"]*">'
        r'<div style="font-size:22px;font-weight:700;color:#3b82f6;">[^<]+</div>'
        r'<div>[^<]+</div>'
        r'</div>'
    )
    pattern = rf'<div[^>]*>(?:\s*{item_pattern}\s*){{2,8}}</div>'
    html = re.sub(pattern, replace_with_table, html, flags=re.DOTALL)
    return html

def convert_highlight_cards_to_table(html):
    def replace_hl(m):
        block = m.group(0)
        items = re.findall(
            r'<div style="[^"]*(?:linear-gradient|#[a-f0-9]{6})[^"]*(?:border-left|border).*?"[^>]*>'
            r'\s*<h4[^>]*>([^<]+)</h4>'
            r'\s*<p[^>]*>([^<]*)</p>'
            r'\s*</div>',
            block, re.DOTALL
        )
        if not items or len(items) < 2:
            return block
        rows = ['<table style="width:100%;border-collapse:collapse;margin:16px 0;border:1px solid #d0dbe6;">']
        for title, body in items:
            body = body.strip()
            rows.append('<tr>')
            rows.append('<td style="width:6px;padding:0;background:#f59e0b;border:1px solid #d0dbe6;"></td>')
            rows.append(f'<td style="padding:14px 18px;vertical-align:top;background:#fffdf7;border:1px solid #d0dbe6;">')
            rows.append(f'<div style="font-size:16px;font-weight:600;color:#92400e;margin-bottom:6px;">{title}</div>')
            if body:
                rows.append(f'<div style="font-size:14px;line-height:1.7;color:#5a4a3a;">{body}</div>')
            rows.append('</td>')
            rows.append('</tr>')
        rows.append('</table>')
        return '\n'.join(rows)

    card_pat = (
        r'<div style="[^"]*(?:linear-gradient|#[a-f0-9]{6})[^"]*(?:border-left|border).*?"[^>]*>'
        r'\s*<h4[^>]*>[^<]+</h4>'
        r'\s*<p[^>]*>[^<]*</p>'
        r'\s*</div>'
    )
    pattern = rf'<div[^>]*>(?:\s*{card_pat}\s*){{2,6}}</div>'
    html = re.sub(pattern, replace_hl, html, flags=re.DOTALL)

    def replace_single(m):
        block = m.group(0)
        title_m = re.search(r'<h4[^>]*>([^<]+)</h4>', block)
        if not title_m:
            return block
        title = title_m.group(1).strip()
        rest = block[title_m.end():].strip()
        if rest.endswith('</div>'):
            rest = rest[:-6].rstrip()
        rows = ['<table style="width:100%;border-collapse:collapse;margin:16px 0;border:1px solid #a3d9a5;">',
                '<tr>',
                '<td style="width:6px;padding:0;background:#22c55e;border:1px solid #a3d9a5;"></td>',
                '<td style="padding:16px 20px;vertical-align:top;background:#f0fdf4;border:1px solid #a3d9a5;">',
                f'<div style="font-size:16px;font-weight:600;color:#166534;margin-bottom:6px;">{title}</div>',
                f'<div style="font-size:14px;line-height:1.7;color:#2d6a4f;">{rest}</div>',
                '</td>',
                '</tr>',
                '</table>']
        return '\n'.join(rows)

    single_pat = (
        r'<div style="[^"]*(?:background:#f0fdf4|background:#fffdf7|border-left:4px solid #(?:c0392b|3b82f6))[^"]*"[^>]*>'
        r'.*'
        r'</div>'
    )
    html = re.sub(single_pat, replace_single, html, flags=re.DOTALL)
    return html

def flatten_nested_lists(html):
    def flat_li(m):
        before_ul = m.group(1)
        inner_items = re.findall(r'<li[^>]*>(.*?)</li>', m.group(2), re.DOTALL)
        parts = [before_ul]
        for item in inner_items:
            item_clean = re.sub(r'<[^>]+>', '', item).strip()
            if item_clean:
                parts.append(f'<br>&nbsp;&nbsp;&nbsp;&bull; {item_clean}')
        return '<li style="margin:6px 0;">' + ''.join(parts) + '</li>'

    for _ in range(5):
        new_html = re.sub(
            r'<li[^>]*>(.*?)<ul[^>]*>(.*?)</ul>\s*</li>',
            flat_li, html, flags=re.DOTALL
        )
        if new_html == html:
            break
        html = new_html
    return html

# ======================== 主转换流程 ========================

TITLES_MAP = {
    "五层进化": ("结构化日志 . 负日志 . CLI闭环 . Vibe+Verify 完整工程", "五层进化 . 核心架构"),
    "实践项目模板": ("基于「五层进化」方法论的真实项目骨架", "五层进化 . 工程落地"),
    "自主修复闭环": ("AI在每一轮迭代中同步完善代码和测试，螺旋逼近需求目标", "五层进化 . 闭环方法论"),
    "电路图分析器": ("将PDF电路图转化为结构化描述，建立元件与代码的快速跳转通道", "五层进化 . 硬件工具链"),
    "共生演化": ("当agents.md与代码彼此背离时，AI应成为持续追踪分歧的忠诚管家", "五层进化 . 深度扩展"),
    "历史的包袱": ("被Keil/IAR钉死在Windows上的老项目，如何成为AI能对话的资产", "五层进化 . 环境维度"),
    "最后的拼图：Skills": ("规则感知型即时方法，5分钟解决一个具体问题", "五层进化 . 应用层"),
}

def add_header_and_footer(body_html, article_num, article_title, article_subtitle, article_tag):
    nav = build_nav(article_num)
    footer_nav = build_footer_nav(article_num)
    lines = [
        '<section style="max-width:680px;margin:0 auto;padding:20px 0;font-family:-apple-system,BlinkMacSystemFont,Microsoft YaHei,PingFang SC,sans-serif;color:#2c3e50;line-height:1.8;">',
        f'<div style="margin-bottom:40px;">',
        f'<span style="display:inline-block;background:#c0392b;color:#fff;font-size:13px;font-weight:700;padding:4px 14px;border-radius:3px;margin-bottom:14px;">{article_tag}</span>',
        f'<h1 style="font-size:30px;font-weight:700;line-height:1.35;margin-bottom:12px;letter-spacing:-0.3px;">{article_title}</h1>',
    ]
    if article_subtitle:
        lines.append(f'<p style="font-size:17px;color:#5a6c7d;font-weight:400;margin-bottom:10px;border-left:3px solid #3b82f6;padding-left:16px;">{article_subtitle}</p>')
    lines.append(f'<p style="font-size:13px;color:#8896a4;">itg &middot; 嵌入式AI工程化系列</p>')
    lines.append('</div>')
    lines.append(nav)
    lines.append(body_html)
    lines.append(footer_nav)
    lines.append('</section>')
    return '\n'.join(lines)

def convert_one(src_file, article_num, article_title, article_desc):
    print(f"  [{article_num}/7] {article_title}...")
    with open(src_file, 'r', encoding='utf-8') as f:
        raw = f.read()

    m = re.search(r'<body[^>]*>(.*?)</body>', raw, re.DOTALL)
    body = m.group(1) if m else raw

    body, pre_blocks = protect_code_blocks(body)
    body = clean_html_safe(body)
    body = convert_classes_to_inline(body)

    body = re.sub(r'\n\s*\n\s*\n', '\n\n', body)
    body = re.sub(r'<div[^>]*>\s*</div>', '', body)

    body = restore_code_blocks(body, pre_blocks)

    body = convert_stats_to_table(body)
    body = convert_cards_to_table(body)
    body = convert_workflow_to_table(body)
    body = convert_highlight_cards_to_table(body)
    body = flatten_nested_lists(body)

    # 把 report-block 包裹进 <table>（一次性，用贪婪 .* 匹配到最后一个 </div>）
    def wrap_report(m):
        return ('<table style="width:100%;border-collapse:collapse;margin:18px 0;border:1px solid #d0dbe6;">'
                '<tr><td style="padding:18px 20px;background:#fafcfd;border:none;font-size:14px;line-height:1.7;">'
                + m.group(1) +
                '</td></tr></table>')
    body = re.sub(
        r'<div style="background:#fafcfd;border:1px solid #d0dbe6;border-radius:6px;padding:18px 20px;margin:18px 0;font-size:14px;line-height:1.7;">(.*)</div>',
        wrap_report, body, flags=re.DOTALL
    )

    body = re.sub(r'<div[^>]*class="article-header"[^>]*>.*?</div>', '', body, flags=re.DOTALL)
    body = re.sub(r'<header[^>]*>.*?</header>', '', body, flags=re.DOTALL)
    body = re.sub(r'<footer[^>]*>.*?</footer>', '', body, flags=re.DOTALL)
    body = re.sub(r'<div[^>]*class="footnote-section"[^>]*>.*?(?=<div style="margin-top:48px)', '', body, flags=re.DOTALL)

    subtitle, tag = TITLES_MAP.get(article_title, ("", "嵌入式AI工程化"))

    full_html = add_header_and_footer(body, article_num, article_title, subtitle, tag)

    out_fn = f"w-{article_num:02d}-{article_title.replace('：','-').replace(' ','')}.html"
    out_path = os.path.join(OUT_DIR, out_fn)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"    -> {out_path}")

def main():
    print("开始转换7篇文章为公众号格式...\n")
    for fn, num, title, desc in ARTICLES:
        src = os.path.join(".", fn)
        if not os.path.exists(src):
            print(f"  !! 文件不存在: {src}")
            continue
        convert_one(src, num, title, desc)
    print(f"\n=== 全部完成！7个文件已输出到 ./{OUT_DIR}/ 目录 ===")

if __name__ == "__main__":
    main()
