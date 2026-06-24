#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把装配好的 PPT HTML 的外部依赖内联，产出自包含单文件 HTML。

为什么要它：
    导出的 成品PPT.html 依赖 theme.css/components.css + 波浪条/logo/抽取图 等外部
    文件，脱离工作目录就是裸页，没法单独分享。本脚本把 CSS 内联进 <style>、把本地
    图片转 base64 data URI 内联进 <img>，产出一个文件——双击即开、可邮件直发，VI 与
    原版完全一致。

    字体不嵌入（决策）：依赖 font-family 回退链。交付环境基本是 Windows，微软雅黑必装。

用法：
    python scripts/inline_html.py deck.html                 # 产出 deck.standalone.html
    python scripts/inline_html.py deck.html -o single.html

也作为模块被 build_pdf.py 调用（导出 PDF 后顺带产单文件）。
"""
from __future__ import annotations

import argparse
import base64
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
except Exception:
    pass

MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
}


def _is_external(url: str) -> bool:
    """已是 data:/http(s):// 的资源——跳过（幂等）。"""
    u = url.strip().lower()
    return u.startswith(("data:", "http:", "https:", "//"))


def _to_data_uri(path: Path) -> str | None:
    mime = MIME.get(path.suffix.lower())
    if mime is None or not path.exists():
        return None
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _inline_css_urls(css_text: str, css_dir: Path) -> str:
    """把 CSS 里的 url(本地图) 替换为 data URI（背景图等）。"""
    def repl(m: "re.Match[str]") -> str:
        raw = m.group(1).strip().strip('"').strip("'")
        if _is_external(raw):
            return m.group(0)
        target = (css_dir / raw).resolve()
        uri = _to_data_uri(target)
        return f"url({uri})" if uri else m.group(0)

    return re.sub(r"url\(([^)]+)\)", repl, css_text)


def inline_html(src_html: Path, out_path: Path | None = None) -> Path:
    """把 src_html 的外部 CSS/图片依赖内联，产出自包含单文件。

    out_path 默认 <src_stem>.standalone.html（同目录）。返回产出路径。
    找不到的依赖：警告并跳过，不中断。已是 data:/http 的引用：跳过（幂等）。
    """
    # resolve()：相对路径 + 中文目录下，base_dir 锚到相对父目录会导致 CSS/图片
    # 解析失败（同 check_overflow 的中文路径坑）。转绝对路径自行消化。
    src_html = Path(src_html).resolve()
    base_dir = src_html.parent
    html = src_html.read_text(encoding="utf-8")
    warnings: list[str] = []

    # 1) 内联 <link rel="stylesheet" href="x.css"> → <style>...</style>
    def repl_link(m: "re.Match[str]") -> str:
        tag = m.group(0)
        href_m = re.search(r'href\s*=\s*["\']([^"\']+)["\']', tag)
        if not href_m:
            return tag
        href = href_m.group(1)
        if _is_external(href):
            return tag  # 远程样式表保留
        css_path = (base_dir / href).resolve()
        if not css_path.exists():
            warnings.append(f"CSS 找不到，跳过：{href}")
            return tag
        css = css_path.read_text(encoding="utf-8")
        css = _inline_css_urls(css, css_path.parent)
        return f"<style>\n{css}\n</style>"

    # 仅匹配 stylesheet 类型的 <link ...>
    html = re.sub(
        r'<link\b[^>]*\brel\s*=\s*["\']stylesheet["\'][^>]*>',
        repl_link, html, flags=re.IGNORECASE,
    )

    # 2) 内联 <img src="本地图"> → data URI（每图各自内联，不去重）
    #    曾试过 content:url() 去重重复图，但会绕过 <img> 的 CSS 尺寸约束（logo
    #    被巨幅拉伸破版，渲染验证抓出），故放弃去重——保 <img> 语义、零副作用。
    #    重复图的代价是体积略大（标准模板几张图，单文件约 1MB 量级，可接受）。
    def repl_img(m: "re.Match[str]") -> str:
        whole, src = m.group(0), m.group(1)
        if _is_external(src):
            return whole
        img_path = (base_dir / src).resolve()
        uri = _to_data_uri(img_path)
        if uri is None:
            warnings.append(f"图片找不到/不支持，跳过：{src}")
            return whole
        # 只替换 src 属性里的那个 url，保留 img 标签其余属性
        return whole.replace(f'"{src}"', f'"{uri}"').replace(f"'{src}'", f"'{uri}'")

    html = re.sub(r'<img\b[^>]*?\bsrc\s*=\s*["\']([^"\']+)["\'][^>]*>',
                  repl_img, html, flags=re.IGNORECASE)

    if out_path is None:
        out_path = src_html.with_name(src_html.stem + ".standalone.html")
    out_path = Path(out_path)
    out_path.write_text(html, encoding="utf-8")

    for w in warnings:
        print(f"  [warn] {w}", file=sys.stderr)
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path, help="装配好的 deck HTML")
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="输出路径（默认 <stem>.standalone.html）")
    args = ap.parse_args()
    if not args.html.exists():
        print(f"ERROR: 找不到 HTML：{args.html}", file=sys.stderr)
        sys.exit(2)
    out = inline_html(args.html, args.output)
    size_kb = round(out.stat().st_size / 1024)
    print(f"✓ 单文件已产出：{out}  ({size_kb} KB)")


if __name__ == "__main__":
    main()
