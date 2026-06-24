#!/usr/bin/env python3
"""把装配好的 PPT HTML 导出为 PDF —— 但先过"溢出闸门"。

为什么要这个脚本（而不是直接 chrome --print-to-pdf）：
    过去溢出之所以反复交付，根因是"溢出自检靠 AI 记得跑"，而 AI 经常不跑
    （实测：中海油 deck 0 处 compact、带 2 页溢出直接交付 = 自检从没跑过）。
    本脚本把自检**焊进导出流程**：不过闸就不给 PDF。想交付就必须先把溢出修掉，
    绕不开。这是把"请记得检查"换成"结构上无法跳过"。

闸门逻辑：
    1. 先跑 check_overflow（复用，不重复造检测轮子）
    2. 任一页溢出 → 拒绝导出，打印每页该怎么改（加 compact / 删内容），exit 1
    3. 全部通过 → 调 Chrome headless 导 PDF

内容超量页（compact 也救不了）的策略：
    脚本不自动拆页、不自动缩字号（投屏会看不清）。它列出溢出页让你**手动删减**，
    删完重跑即可。确实要带溢出交付时，用 --force 显式放行（你看过提示后自己拍板）。

用法：
    python scripts/build_pdf.py deck.html                  # 默认输出同名 .pdf
    python scripts/build_pdf.py deck.html -o out.pdf
    python scripts/build_pdf.py deck.html --tolerance 5
    python scripts/build_pdf.py deck.html --force          # 跳过闸门强行导出

退出码：
    0 = 导出成功
    1 = 溢出被拦截（未导出）
    2 = 其它错误（找不到文件 / Chrome / 渲染失败）
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 历史版本快照目录名（与成品 HTML 同级）
VERSIONS_DIR = "_versions"

# 复用 check_overflow 的检测逻辑与 Chrome 查找——不重复造轮子
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from check_overflow import check_html, find_chrome  # type: ignore
except Exception as e:  # pragma: no cover
    print(f"ERROR: 无法导入 check_overflow.py（应与本脚本同目录）: {e}",
          file=sys.stderr)
    sys.exit(2)

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
except Exception:
    pass

SUPPORTS_COLOR = sys.stdout.isatty()
RED = "\033[31m" if SUPPORTS_COLOR else ""
GREEN = "\033[32m" if SUPPORTS_COLOR else ""
YELLOW = "\033[33m" if SUPPORTS_COLOR else ""
BOLD = "\033[1m" if SUPPORTS_COLOR else ""
RESET = "\033[0m" if SUPPORTS_COLOR else ""


def snapshot_before_overwrite(*paths: Path) -> int:
    """覆盖前把已存在的成品文件快照进 _versions/。

    每个传入路径若已存在，复制一份带秒级时间戳的副本到同级 _versions/，
    命名 <basename>_<YYYYMMDD-HHMMSS>.<ext>。不存在的路径静默跳过（首次导出）。
    返回实际快照的文件数。

    这是版本留底机制：每次导出前自动留旧版，绕不开、不靠记得。
    恢复时直接打开 _versions/ 里的文件即可。
    """
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    count = 0
    for p in paths:
        if not p.exists():
            continue
        vdir = p.parent / VERSIONS_DIR
        vdir.mkdir(exist_ok=True)
        dest = vdir / f"{p.stem}_{stamp}{p.suffix}"
        shutil.copy2(p, dest)
        count += 1
    return count


def export_pdf(html_path: Path, pdf_path: Path) -> int:
    """调 Chrome headless 导 PDF。返回 exit code。"""
    chrome = find_chrome()
    url = "file:///" + str(html_path.resolve()).replace("\\", "/")
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--no-sandbox",
        "--virtual-time-budget=15000",
        f"--print-to-pdf={pdf_path.resolve()}",
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=120)
    if not pdf_path.exists():
        print(f"{RED}ERROR{RESET}: Chrome 未生成 PDF。stderr 尾部：",
              file=sys.stderr)
        print((result.stderr or "")[-400:], file=sys.stderr)
        return 2
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("html", type=Path, help="装配好的 deck HTML（绝对路径最稳）")
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="输出 PDF 路径（默认同名 .pdf）")
    ap.add_argument("--tolerance", type=int, default=2,
                    help="溢出容差 px（默认 2）")
    ap.add_argument("--no-standalone", action="store_true",
                    help="不顺带生成自包含单文件 HTML（默认生成）")
    ap.add_argument("--force", action="store_true",
                    help="跳过溢出闸门强行导出（你已看过提示并决定带溢出交付）")
    args = ap.parse_args()

    if not args.html.exists():
        print(f"{RED}ERROR{RESET}: 找不到 HTML：{args.html}", file=sys.stderr)
        sys.exit(2)

    pdf_path = args.output or args.html.with_suffix(".pdf")

    # ---- 闸门：先自检溢出 ----
    if not args.force:
        print(f"{BOLD}[1/2] 溢出自检（闸门）…{RESET}")
        code = check_html(args.html, tolerance=args.tolerance, json_output=False)
        if code != 0:
            print()
            print(f"{RED}{BOLD}✗ 导出被拦截：上面列出的页存在溢出。{RESET}")
            print("处理方式（按你的策略：保持一页 + 手动删减，不自动拆/缩）：")
            print("  · 未加 compact 的溢出页 → 先加 "
                  "<section class=\"slide compact\">，重跑本脚本")
            print("  · 已是 compact 仍溢出 → 该页内容超量，"
                  "删掉提示的最长项 / 拆成两页（你定），再重跑")
            print(f"  · 确需带溢出交付 → 加 {BOLD}--force{RESET} 显式放行")
            sys.exit(1)
        print(f"{GREEN}✓ 全部页面在界内{RESET}\n")
    else:
        print(f"{RED}[!] --force：跳过溢出闸门{RESET}\n")

    # ---- 几何护栏：字号<8pt / 元素出血（只警告，不阻断导出）----
    # 溢出是零误报的硬红线 → 拒绝导出；几何护栏对某些合法装饰定位可能误报，
    # 故只提示不拦，把判断权留给你（真事故你会看到，误报不会卡住交付）。
    try:
        from check_geometry import check_geometry  # 同目录
        gdata = check_geometry(args.html, return_data=True)
        gissues = []
        for p in gdata["pages"]:
            for f in p["fontTooSmall"]:
                gissues.append(f"p{p['page']} 字号 {f['pt']}pt<8 ({f['el']})")
            for b in p["bleed"]:
                gissues.append(f"p{p['page']} 出血 {b['dir']} ({b['el']})")
        for it in gdata.get("pageNoIssues", []):
            gissues.append(f"页码 {it}")
        if gissues:
            print(f"{YELLOW}[geom warn]{RESET} 几何护栏发现 "
                  f"{len(gissues)} 处（不阻断导出，请自行判断）：")
            for it in gissues[:8]:
                print(f"    · {it}")
            if len(gissues) > 8:
                print(f"    … 余 {len(gissues) - 8} 处，"
                      f"详见 python scripts/check_geometry.py")
            print()
    except Exception as e:  # 护栏失败绝不影响主交付
        print(f"{YELLOW}[warn]{RESET} 几何护栏跳过（不影响导出）：{e}",
              file=sys.stderr)

    # ---- 覆盖前留底：把上一版 HTML+PDF 快照进 _versions/ ----
    n = snapshot_before_overwrite(args.html, pdf_path)
    if n:
        print(f"{GREEN}✓ 已留底上一版 {n} 个文件 → "
              f"{args.html.parent / VERSIONS_DIR}{RESET}")

    # ---- 导出 ----
    print(f"{BOLD}[2/2] 导出 PDF…{RESET}")
    code = export_pdf(args.html, pdf_path)
    if code == 0:
        print(f"{GREEN}{BOLD}✓ 已导出：{RESET}{pdf_path}")
        print(f"  找回旧版：打开 {args.html.parent / VERSIONS_DIR}/ 里带时间戳的文件")

        # ---- 顺带产出自包含单文件 HTML（CSS/图片内联，可邮件直发/双击即开）----
        if not args.no_standalone:
            try:
                from inline_html import inline_html  # 同目录
                sa = inline_html(args.html)
                sa_kb = round(sa.stat().st_size / 1024)
                print(f"{GREEN}✓ 单文件已产出：{RESET}{sa} ({sa_kb} KB)")
                print("  这一份自包含，发给别人/在线看用它；继续编辑用原 HTML")
            except Exception as e:  # 单文件失败不影响 PDF 主交付
                print(f"{YELLOW}[warn]{RESET} 单文件 HTML 生成失败（不影响 PDF）：{e}",
                      file=sys.stderr)
    sys.exit(code)


if __name__ == "__main__":
    main()
