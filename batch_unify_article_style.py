#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
batch_unify_article_style.py
=============================
Unify article styles and fold long code blocks across all
technical / humanities articles (excluding novels and index).

Usage:
    python batch_unify_article_style.py
"""

import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Article classification
# ---------------------------------------------------------------------------

TECH_FILES = [
    "in.html", "true.html", "test.html", "fwd.html", "exc.html",
    "pcb.html", "pt.html", "history.html", "ocd.html", "devs.html",
    "gmp.html", "hg.html", "12.html", "py.html", "13.html", "14.html",
    "gd.html", "lj.html",
]

# about.html lives in root; all others live in aboutmore/
HUMANITIES_ROOT = ["about.html"]

HUMANITIES_ABOUTMORE = [
    # L1
    "tk.html", "fw.html", "sc.html", "wx.html",
    # L2
    "itg.html", "forme.html", "pg.html", "m.html", "cc.html",
    "ll.html", "ta.html",
    # L4
    "czjs.html", "fr.html", "jg.html", "sryj.html", "gc.html",
]

# Excluded: L3 novels (czy, qp-chat, gary, alone, mywj, party-high, jsxm)
#           and index.html

# Files that should get the CSS link but NOT be modified by code-folding etc.
# (test.html was explicitly excluded by the user)
SKIP_PROCESSING = {"test.html"}

# ---------------------------------------------------------------------------
# CSS cleanup patterns
# ---------------------------------------------------------------------------

# Full-block patterns: remove these CSS rule blocks from inline <style>
# because article-base.css now provides them.
SELECTORS_TO_REMOVE = [
    # Card variants
    r'\.card\.accent-left\s*\{[^}]*\}',
    r'\.card\.philosophy\s*\{[^}]*\}',
    r'\.card\.philosopher\s*\{[^}]*\}',
    r'\.card\.engineer\s*\{[^}]*\}',
    r'\.card\.action\s*\{[^}]*\}',
    r'\.card\.vision\s*\{[^}]*\}',
    r'\.card\.vision:hover\s*\{[^}]*\}',
    r'\.card\.tip\s*\{[^}]*\}',
    r'\.card\.green-left\s*\{[^}]*\}',
    r'\.card\.blue-left\s*\{[^}]*\}',
    r'\.card\.purple-left\s*\{[^}]*\}',
    # Insight box variants
    r'\.insight-box\.decision\s*\{[^}]*\}',
    r'\.insight-box\.decision\s+strong\s*\{[^}]*\}',
    r'\.insight-box\.warm\s*\{[^}]*\}',
    r'\.insight-box\.warm\s+strong\s*\{[^}]*\}',
    r'\.insight-box\.cool\s*\{[^}]*\}',
    r'\.insight-box\.cool\s+strong\s*\{[^}]*\}',
    # Layer tags
    r'\.layer-tag\.level1\s*\{[^}]*\}',
    r'\.layer-tag\.level2\s*\{[^}]*\}',
    r'\.layer-tag\.level3\s*\{[^}]*\}',
]

# Single-line CSS rules to remove (compact format used in humanities articles)
COMPACT_PATTERNS_TO_REMOVE = [
    # Insight box (compact single-line)
    r'\.insight-box\s*\{[^}]*border-left:[^}]*\}',
    r'\.insight-box\s+strong\s*\{[^}]*\}',
    # Quote block (compact single-line with text-align:center)
    r'\.quote-block\s*\{[^}]*text-align:center[^}]*\}',
    # Code font (compact single-line)
    r'\bcode\s*\{\s*font-family:[^}]*\}',
    r'\bp\s+code,\s*li\s+code\s*\{[^}]*\}',
]


def detect_eol(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


# ---------------------------------------------------------------------------
# CSS link injection
# ---------------------------------------------------------------------------

def ensure_article_css_link(text: str, is_aboutmore: bool, eol: str) -> str:
    """Insert <link rel="stylesheet" href="...article-base.css"> if missing."""
    href = "../assets/article-base.css" if is_aboutmore else "assets/article-base.css"
    link_tag = f'<link rel="stylesheet" href="{href}">'

    if "article-base.css" in text:
        return text

    # Insert before </head>
    head_end = text.find("</head>")
    if head_end == -1:
        return text

    return text[:head_end] + link_tag + eol + text[head_end:]


# ---------------------------------------------------------------------------
# CSS cleanup
# ---------------------------------------------------------------------------

def clean_inline_css(text: str) -> str:
    """Remove redundant inline CSS rules now covered by article-base.css."""

    # 1. Remove full-block patterns
    for pattern in SELECTORS_TO_REMOVE:
        text = re.sub(pattern, '', text, flags=re.DOTALL)

    # 2. Remove compact single-line patterns
    for pattern in COMPACT_PATTERNS_TO_REMOVE:
        text = re.sub(pattern, '', text)

    # 3. Fix quote-block text-align:center -> text-align:left
    text = re.sub(
        r'(\.quote-block\s*\{[^}]*)text-align:\s*center',
        r'\1text-align: left',
        text,
    )

    # 4. Remove inline style="" on <pre> tags
    text = re.sub(
        r'<pre\s+style="[^"]*">',
        '<pre>',
        text,
    )

    # 5. Clean up multiple blank lines inside <style> blocks
    text = re.sub(r'(\n\s*){3,}', '\n\n', text)

    return text


# ---------------------------------------------------------------------------
# Code folding
# ---------------------------------------------------------------------------

CODE_FOLD_THRESHOLD = 30  # lines


def count_code_lines(block_content: str) -> int:
    """Count the number of lines in a code block's content."""
    # Strip HTML tags for counting purposes
    stripped = re.sub(r'<[^>]+>', '', block_content)
    lines = stripped.strip().split('\n')
    return len(lines)


def wrap_in_details(pre_match: re.Match, line_count: int) -> str:
    """Wrap a <pre>...</pre> or <div class="code-block">...</div> in <details>."""
    full_block = pre_match.group(0)

    # Determine indent from the line before the match
    start = pre_match.start()
    # Find the start of the line containing the match
    line_start = full_block[:full_block.find('<')].rfind('\n')
    if line_start == -1:
        indent = ''
    else:
        indent = full_block[:line_start + 1]

    summary_text = f"展开代码 ({line_count} 行)"
    wrapper = (
        f'<details class="code-collapse">\n'
        f'{indent}<summary>{summary_text}'
        f'<span class="line-count">{line_count} lines</span></summary>\n'
        f'{indent}{full_block}\n'
        f'{indent}</details>'
    )
    return wrapper


def fold_long_code_blocks(text: str) -> str:
    """Find <pre> and .code-block elements exceeding threshold and wrap them.

    Processing order:
      1. <div class="code-block">...</div>  (balanced div matching)
      2. Standalone <pre>...</pre>           (skip if already inside code-collapse)
    """

    # ------------------------------------------------------------------
    # Pass 1: Fold <div class="code-block">...</div> (balanced divs)
    # ------------------------------------------------------------------
    cb_open_re = re.compile(r'<div\s+class="code-block"[^>]*>')

    def find_balanced_div_close(text: str, start: int) -> int:
        """From `start` (just after the opening <div ...>), find the matching </div>."""
        depth = 1
        pos = start
        while depth > 0 and pos < len(text):
            next_open = text.find('<div', pos)
            next_close = text.find('</div>', pos)
            if next_close == -1:
                return -1
            if next_open != -1 and next_open < next_close:
                depth += 1
                pos = next_open + 4
            else:
                depth -= 1
                if depth == 0:
                    return next_close + len('</div>')
                pos = next_close + len('</div>')
        return -1

    offset = 0
    for m in cb_open_re.finditer(text):
        adj_start = m.start() + offset
        inner_start = m.end() + offset
        end = find_balanced_div_close(text, inner_start)
        if end == -1:
            continue
        block = text[adj_start:end]
        if 'code-collapse' in block:
            continue
        lines = count_code_lines(block)
        if lines <= CODE_FOLD_THRESHOLD:
            continue
        # Detect indent
        line_start = text.rfind('\n', 0, adj_start)
        indent = text[line_start + 1:adj_start] if line_start != -1 else ''
        summary = f"展开代码 ({lines} 行)"
        wrapper = (
            f'<details class="code-collapse">\n'
            f'{indent}<summary>{summary}'
            f'<span class="line-count">{lines} lines</span></summary>\n'
            f'{indent}{block}\n'
            f'{indent}</details>'
        )
        old_len = end - adj_start
        text = text[:adj_start] + wrapper + text[end:]
        offset += len(wrapper) - old_len

    # ------------------------------------------------------------------
    # Pass 2: Fold standalone <pre>...</pre> (not inside code-collapse)
    # ------------------------------------------------------------------
    pre_pattern = re.compile(r'<pre[^>]*>.*?</pre>', re.DOTALL)

    def replace_pre(m):
        block = m.group(0)
        # Check context: skip if already inside a code-collapse
        context_start = max(0, m.start() - 500)
        context = text[context_start:m.start()]
        if '<details class="code-collapse">' in context and '</details>' not in context[context.find('<details class="code-collapse">'):]:
            return block
        lines = count_code_lines(block)
        if lines > CODE_FOLD_THRESHOLD:
            line_start = block[:block.find('<')].rfind('\n')
            indent = block[:line_start + 1] if line_start != -1 else ''
            summary = f"展开代码 ({lines} 行)"
            return (
                f'<details class="code-collapse">\n'
                f'{indent}<summary>{summary}'
                f'<span class="line-count">{lines} lines</span></summary>\n'
                f'{indent}{block}\n'
                f'{indent}</details>'
            )
        return block

    text = pre_pattern.sub(replace_pre, text)

    return text


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

def process_file(file_path: Path, is_aboutmore: bool) -> bool:
    """Process a single HTML file. Returns True if modified."""
    if not file_path.exists():
        print(f"  [SKIP] Not found: {file_path.name}")
        return False

    text = file_path.read_text(encoding="utf-8")
    original = text
    eol = detect_eol(text)

    # 1. Inject shared CSS link
    text = ensure_article_css_link(text, is_aboutmore, eol)

    # 2. Clean redundant inline CSS
    text = clean_inline_css(text)

    # 3. Fold long code blocks (skip for excluded files)
    if file_path.name not in SKIP_PROCESSING:
        text = fold_long_code_blocks(text)

    if text == original:
        return False

    file_path.write_text(text, encoding="utf-8", newline="")
    return True


def main():
    print("=" * 60)
    print("  Article Style Unification & Code Folding")
    print("=" * 60)
    print()

    modified = []
    skipped = []

    # Process root-level technical articles
    print("[T] Technical articles (root):")
    for fname in TECH_FILES:
        fp = ROOT / fname
        if process_file(fp, is_aboutmore=False):
            modified.append(fname)
            print(f"  [OK]   {fname}")
        else:
            skipped.append(fname)
            print(f"  [--]   {fname} (no changes)")

    # Process root-level humanities articles
    print()
    print("[L] Humanities articles (root):")
    for fname in HUMANITIES_ROOT:
        fp = ROOT / fname
        if process_file(fp, is_aboutmore=False):
            modified.append(fname)
            print(f"  [OK]   {fname}")
        else:
            skipped.append(fname)
            print(f"  [--]   {fname} (no changes)")

    # Process aboutmore/ humanities articles
    print()
    print("[L] Humanities articles (aboutmore/):")
    for fname in HUMANITIES_ABOUTMORE:
        fp = ROOT / "aboutmore" / fname
        if process_file(fp, is_aboutmore=True):
            modified.append(f"aboutmore/{fname}")
            print(f"  [OK]   aboutmore/{fname}")
        else:
            skipped.append(f"aboutmore/{fname}")
            print(f"  [--]   aboutmore/{fname} (no changes)")

    # Summary
    total = len(TECH_FILES) + len(HUMANITIES_ROOT) + len(HUMANITIES_ABOUTMORE)
    print()
    print("-" * 60)
    print(f"  Total: {total} files")
    print(f"  Modified: {len(modified)}")
    print(f"  Unchanged: {len(skipped)}")
    print("-" * 60)

    # Verify novels were not touched
    novels = ["czy.html", "qp-chat.html", "gary.html", "alone.html",
              "mywj.html", "party-high.html", "jsxm.html"]
    print()
    print("[X] Excluded novels (should not be modified):")
    for fname in novels:
        fp = ROOT / "aboutmore" / fname
        if fp.exists():
            content = fp.read_text(encoding="utf-8")
            if "article-base.css" in content:
                print(f"  [!!]   aboutmore/{fname} — UNEXPECTED modification!")
            else:
                print(f"  [OK]   aboutmore/{fname} — untouched")

    print()
    print("Done.")


if __name__ == "__main__":
    main()
