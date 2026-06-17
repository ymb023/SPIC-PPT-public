#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""几何护栏：检测装配好的 PPT HTML 里两类可量化的版式违规。

  1. 字号 < 14pt（投屏铁律：正文/标题投屏不可读 = 失败）。说明性小字
     （page-no/data-source/标签/描述等）走白名单，不查。
  2. 元素出血：任何元素超出 slide 的左/右/上边界。
     （底部出血 = 内容溢出，由 check_overflow.py 负责，此处不重复。）

为什么是脚本而非人眼：这两类全部可用 getBoundingClientRect() + getComputedStyle()
精确判定，是"对错"不是"审美"——交给确定性脚本，把人眼留给真正的审美判断。
（学术背书：VLM-SlideEval 证明视觉模型在对齐/越界/字号上不可靠。）

调用：
    python scripts/check_geometry.py deck.html
    python scripts/check_geometry.py deck.html --json

退出码：0 = 全过 / 1 = 有违规 / 2 = 渲染失败
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from check_overflow import find_chrome  # 复用 Chrome 查找
except Exception as e:  # pragma: no cover
    print(f"ERROR: 无法导入 check_overflow.find_chrome: {e}", file=sys.stderr)
    sys.exit(2)

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
except Exception:
    pass

SUPPORTS_COLOR = sys.stdout.isatty()
RED = "\033[31m" if SUPPORTS_COLOR else ""
GREEN = "\033[32m" if SUPPORTS_COLOR else ""
DIM = "\033[2m" if SUPPORTS_COLOR else ""
BOLD = "\033[1m" if SUPPORTS_COLOR else ""
RESET = "\033[0m" if SUPPORTS_COLOR else ""

SLIDE_W = 1280
# 字号红线 = 8pt"真看不清"的绝对底线。
# 为什么不是 13/14pt：theme.css 字号是分级的——正文 14pt、小正文 13pt、
# 说明/标签 12pt、来源 11pt，全部合法。靠 class 名猜"是不是正文"永远猜不准，
# 会把大量合法小字误报成违规、沦为噪音。所以护栏只守一条谁都不争议的绝对红线：
# 任何文本 < 8pt = 真事故（缩字号缩过头/手误写了 6pt），投屏绝对看不清。
# 标签/说明/来源小字一律放过——它们的合规由人眼审美判断，不归几何护栏。
MIN_PT = 8.0
PT_TOL = 0.5
BLEED_TOL = 2          # 出血容差 px

# 字号白名单：8pt 以下本不该有合法文字，白名单基本是双保险。
FONT_WHITELIST = [
    "page-no", "page-num", "data-source", "footnote",
]

# 注入 JS：每页测字号过小 + 出血，写进隐藏 div。
CHECK_JS = """<script>
window.addEventListener("load", function() {
  setTimeout(function() {
    var WL = %s;
    var MIN_PT = %s, PT_TOL = %s, BLEED_TOL = %s, SLIDE_W = %s;
    function inWhitelist(el) {
      var n = el;
      while (n && n.nodeType === 1) {
        var cn = (n.className || "").toString();
        for (var k = 0; k < WL.length; k++) {
          if ((" " + cn + " ").indexOf(" " + WL[k] + " ") >= 0) return true;
        }
        n = n.parentElement;
      }
      return false;
    }
    function hasDirectText(el) {
      for (var i = 0; i < el.childNodes.length; i++) {
        var c = el.childNodes[i];
        if (c.nodeType === 3 && c.textContent.trim().length > 0) return true;
      }
      return false;
    }
    function label(el) {
      return (el.tagName || "") + "." +
             (el.className || "").toString().substring(0, 40);
    }
    var slides = document.querySelectorAll(".slide");
    var report = [];
    for (var i = 0; i < slides.length; i++) {
      var s = slides[i];
      var sRect = s.getBoundingClientRect();
      var all = s.querySelectorAll("*");
      var fontBad = [], bleed = [];
      for (var j = 0; j < all.length; j++) {
        var el = all[j];
        var cs = window.getComputedStyle(el);
        if (cs.display === "none" || cs.visibility === "hidden") continue;
        var rect = el.getBoundingClientRect();
        if (rect.width === 0 && rect.height === 0) continue;
        // --- 字号（只查有直接文本、非白名单的元素）---
        if (hasDirectText(el) && !inWhitelist(el)) {
          var px = parseFloat(cs.fontSize);
          var pt = px * 0.75;
          if (pt < MIN_PT - PT_TOL) {
            fontBad.push({ el: label(el), pt: Math.round(pt * 10) / 10 });
          }
        }
        // --- 出血（相对 slide 的左/右/上）---
        var pos = cs.position;
        if (pos === "fixed") continue;
        var left = rect.left - sRect.left;
        var right = rect.right - sRect.left;
        var top = rect.top - sRect.top;
        var dir = [];
        if (left < -BLEED_TOL) dir.push("左" + Math.round(left));
        if (right > SLIDE_W + BLEED_TOL) dir.push("右+" + Math.round(right - SLIDE_W));
        if (top < -BLEED_TOL) dir.push("上" + Math.round(top));
        if (dir.length) bleed.push({ el: label(el), dir: dir.join("/") });
      }
      report.push({ page: i + 1, fontTooSmall: fontBad, bleed: bleed });
    }
    var d = document.createElement("div");
    d.id = "__geometry_report__";
    d.style.display = "none";
    d.textContent = JSON.stringify(report);
    document.body.appendChild(d);
  }, 500);
});
</script>""" % (json.dumps(FONT_WHITELIST), MIN_PT, PT_TOL, BLEED_TOL, SLIDE_W)


def _render_report(html_path: Path) -> list:
    """渲染 HTML，注入检查脚本，取回每页几何报告。"""
    chrome = find_chrome()
    html_path = html_path.resolve()
    src = html_path.read_text(encoding="utf-8")
    if "</body>" not in src:
        raise RuntimeError("HTML 没有 </body> 标签")
    modified = src.replace("</body>", CHECK_JS + "</body>", 1)
    temp = html_path.parent / f"__geometry_check_{os.getpid()}.html"
    temp.write_text(modified, encoding="utf-8")
    try:
        url = "file:///" + str(temp).replace("\\", "/")
        result = subprocess.run(
            [chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
             "--virtual-time-budget=5000", "--dump-dom", url],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=60,
        )
    finally:
        try:
            temp.unlink()
        except OSError:
            pass
    m = re.search(r'id="__geometry_report__"[^>]*>(\[.*?\])</div>',
                  result.stdout, re.DOTALL)
    if not m:
        raise RuntimeError("没拿到几何报告——Chrome 渲染可能失败")
    return json.loads(m.group(1))


def check_geometry(html_path: Path, json_output: bool = False,
                   return_data: bool = False):
    """检测字号过小 + 元素出血。

    return_data=True 时返回 {"pages":[...]} 供测试/eval 调用；
    否则打印报告并返回 exit code（0/1）。
    """
    report = _render_report(html_path)
    data = {"html": str(html_path), "pages": report}

    flagged = [p for p in report
               if p["fontTooSmall"] or p["bleed"]]

    if return_data:
        return data

    if json_output:
        print(json.dumps({**data, "flagged_count": len(flagged)},
                         ensure_ascii=False, indent=2))
        return 1 if flagged else 0

    print(f"\n{BOLD}SPIC-PPT geometry check{RESET}")
    print("=" * 32)
    print(f"html: {html_path}")
    print(f"pages: {len(report)}   规则: 字号≥{MIN_PT}pt + 无左/右/上出血\n")
    for p in report:
        issues = []
        for f in p["fontTooSmall"]:
            issues.append(f"字号 {f['pt']}pt < {MIN_PT} ({f['el']})")
        for b in p["bleed"]:
            issues.append(f"出血 {b['dir']} ({b['el']})")
        if issues:
            print(f"  {RED}[FAIL]{RESET} p{p['page']:>2}  " +
                  f"\n           ".join(issues))
        else:
            print(f"  {GREEN}[ ok ]{RESET} p{p['page']:>2}")
    print()
    if flagged:
        print(f"{RED}{BOLD}Result: {len(flagged)}/{len(report)} 页有几何违规{RESET}")
        print(f"{DIM}字号修复：放大到 ≥14pt 或加 .compact（不要靠缩字号塞内容）"
              f"\n出血修复：检查负 margin / 绝对定位 / 宽度溢出{RESET}")
        return 1
    print(f"{GREEN}{BOLD}Result: 全部 {len(report)} 页几何合规{RESET}")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not args.html.exists():
        print(f"{RED}ERROR{RESET}: 找不到 HTML: {args.html}", file=sys.stderr)
        sys.exit(2)
    try:
        sys.exit(check_geometry(args.html, json_output=args.json))
    except RuntimeError as e:
        print(f"{RED}ERROR{RESET}: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
