#!/usr/bin/env python3
"""检测装配好的 PPT HTML 中哪些 .slide 的内容溢出了 720px 边界。

原理：用 Chrome headless 渲染 HTML，注入 JS 测量每张 .slide 内所有子元素的
getBoundingClientRect().bottom，与 slide 自身底部比较。任何子元素超出 slide
底部 = 该页溢出。

这是真测量，比"反向验证 PNG"准确得多（因为 .slide 的 overflow:hidden 会把
溢出内容裁掉，PNG 看不出来）。

调用：
    python scripts/check_overflow.py path/to/deck.html
    python scripts/check_overflow.py path/to/deck.html --tolerance 5
    python scripts/check_overflow.py path/to/deck.html --json

退出码：
    0 = 所有页通过
    1 = 至少一页溢出
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# -------- 颜色 --------
SUPPORTS_COLOR = sys.stdout.isatty()
RED = "\033[31m" if SUPPORTS_COLOR else ""
GREEN = "\033[32m" if SUPPORTS_COLOR else ""
YELLOW = "\033[33m" if SUPPORTS_COLOR else ""
DIM = "\033[2m" if SUPPORTS_COLOR else ""
BOLD = "\033[1m" if SUPPORTS_COLOR else ""
RESET = "\033[0m" if SUPPORTS_COLOR else ""

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
except Exception:
    pass


def find_chrome() -> str:
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(
            r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
        ),
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise RuntimeError(
        "找不到 Chrome/Edge 可执行文件。请安装 Chrome 或 Edge。"
    )


# 注入 JS：测量每张 slide 内所有元素，找最深 bottom，对比 slide 底部
CHECK_JS = """<script>
window.addEventListener("load", function() {
  setTimeout(function() {
    var slides = document.querySelectorAll(".slide");
    var report = [];
    for (var i = 0; i < slides.length; i++) {
      var s = slides[i];
      var slideRect = s.getBoundingClientRect();
      var slideBottom = slideRect.bottom;
      var maxBottom = 0;
      var deepestEl = "";
      var all = s.querySelectorAll("*");
      for (var j = 0; j < all.length; j++) {
        var el = all[j];
        // 跳过 absolute / fixed 定位（如 page-footer 在 bottom:16px 是设计内的）
        var pos = window.getComputedStyle(el).position;
        if (pos === "absolute" || pos === "fixed") continue;
        var rect = el.getBoundingClientRect();
        if (rect.bottom > maxBottom) {
          maxBottom = rect.bottom;
          deepestEl = (el.tagName || "") + "." + (el.className || "").toString().substring(0, 50);
        }
      }
      report.push({
        page: i + 1,
        slideHeight: Math.round(slideRect.height),
        contentBottom: Math.round(maxBottom - slideRect.top),
        overflowsBy: Math.round(maxBottom - slideBottom),
        deepestEl: deepestEl
      });
    }
    var d = document.createElement("div");
    d.id = "__overflow_report__";
    d.style.display = "none";
    d.textContent = JSON.stringify(report);
    document.body.appendChild(d);
  }, 500);
});
</script>"""


def check_html(
    html_path: Path,
    tolerance: int = 2,
    json_output: bool = False,
) -> int:
    """检测 HTML 中每张 slide 是否溢出。返回 exit code。"""
    chrome = find_chrome()

    # 转绝对路径——否则中文相对路径下 Chrome headless 解析 file:/// URL 失败，
    # 闸门误报"找不到文件/溢出"（主目录 D:/工作文件夹/... 是中文路径，命中率极高）。
    html_path = html_path.resolve()

    # 读源 HTML，临时插入 check 脚本到 </body> 前
    src = html_path.read_text(encoding="utf-8")
    if "</body>" not in src:
        if not json_output:
            print(f"{RED}ERROR{RESET}: HTML 没有 </body> 标签", file=sys.stderr)
        return 2

    modified = src.replace("</body>", CHECK_JS + "</body>", 1)
    # 临时文件必须放在源 HTML 同目录（保留相对路径正确）
    temp = html_path.parent / f"__overflow_check_{os.getpid()}.html"
    temp.write_text(modified, encoding="utf-8")

    try:
        url = "file:///" + str(temp).replace("\\", "/")
        result = subprocess.run(
            [
                chrome,
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                "--virtual-time-budget=5000",
                "--dump-dom",
                url,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
    finally:
        try:
            temp.unlink()
        except OSError:
            pass

    # 提取报告
    m = re.search(
        r'id="__overflow_report__"[^>]*>(\[.*?\])</div>',
        result.stdout,
        re.DOTALL,
    )
    if not m:
        if json_output:
            print(json.dumps({"error": "no overflow report in dump"}))
        else:
            print(
                f"{RED}ERROR{RESET}: 没拿到溢出报告——Chrome 渲染可能失败",
                file=sys.stderr,
            )
            print("stdout tail:", result.stdout[-300:], file=sys.stderr)
        return 2

    report = json.loads(m.group(1))
    flagged = [p for p in report if p["overflowsBy"] > tolerance]

    if json_output:
        print(json.dumps({
            "html": str(html_path),
            "tolerance": tolerance,
            "total_pages": len(report),
            "flagged_count": len(flagged),
            "pages": report,
        }, ensure_ascii=False, indent=2))
        return 1 if flagged else 0

    # 人类可读输出
    print(f"\n{BOLD}SPIC-PPT overflow check{RESET}")
    print("=" * 32)
    print(f"html: {html_path}")
    print(f"pages: {len(report)}   tolerance: +{tolerance}px\n")

    for p in report:
        ov = p["overflowsBy"]
        if ov > tolerance:
            print(
                f"  {RED}[FAIL]{RESET} p{p['page']:>2}  "
                f"溢出 {RED}{ov:+}px{RESET}  "
                f"{DIM}content_bottom={p['contentBottom']} "
                f"deepest={p['deepestEl']}{RESET}"
            )
        else:
            print(
                f"  {GREEN}[ ok ]{RESET} p{p['page']:>2}  "
                f"{DIM}content_bottom={p['contentBottom']}px (slide=720){RESET}"
            )

    print()
    if flagged:
        print(
            f"{RED}{BOLD}Result: {len(flagged)} / {len(report)} pages "
            f"overflow{RESET}"
        )
        print()
        print(f"{BOLD}建议修复（按优先级）：{RESET}")
        print(
            f"  1. 先给溢出页加 'compact' 类："
            f"<section class=\"slide{BOLD} compact{RESET}\">"
        )
        print(f"  2. 再次跑本脚本验证")
        print(f"  3. 仍 FAIL → 拆分该页 / 减列表项 / 减卡片数（结构性减载）")
        print(f"  4. 不要靠『再缩字号』——投屏会看不清")
        return 1
    else:
        print(
            f"{GREEN}{BOLD}Result: all {len(report)} pages fit "
            f"within slide bounds{RESET}"
        )
        return 0


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("html", type=Path, help="path to deck HTML")
    ap.add_argument(
        "--tolerance",
        type=int,
        default=2,
        help="px tolerance (default 2; content overflowing by more is FAIL)",
    )
    ap.add_argument(
        "--json",
        action="store_true",
        help="output machine-readable JSON",
    )
    args = ap.parse_args()

    if not args.html.exists():
        print(f"{RED}ERROR{RESET}: HTML not found: {args.html}", file=sys.stderr)
        sys.exit(2)

    sys.exit(check_html(args.html, args.tolerance, args.json))


if __name__ == "__main__":
    main()
