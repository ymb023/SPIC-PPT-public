#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""回归评测套件：改 theme/components.css 后一键确认版式不退化、护栏仍灵敏。

把"改完 CSS 等人工渲染验收"变成"跑脚本自动判对错"。三个固定输入：
  1. sample-pages.html  （10 基础版式）→ 期望全过
  2. _layout-demo.html  （7 第二代版式）→ 期望全过
  3. _eval/stress-test.html（魔鬼样本）→ 期望按预定清单报特定违规
     （反向夹具：验证护栏真能抓到，而非只验正常页能过）

对每个输入跑 check_overflow（底部溢出）+ check_geometry（字号<8pt / 出血），
汇总成表，全部符合预期 exit 0；任一偏离 exit 1。

调用：python scripts/eval_suite.py
"""
from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_overflow import check_html          # type: ignore
from check_geometry import check_geometry      # type: ignore

try:
    sys.stdout.reconfigure(encoding="utf-8")    # type: ignore
except Exception:
    pass

SUPPORTS_COLOR = sys.stdout.isatty()
RED = "\033[31m" if SUPPORTS_COLOR else ""
GREEN = "\033[32m" if SUPPORTS_COLOR else ""
DIM = "\033[2m" if SUPPORTS_COLOR else ""
BOLD = "\033[1m" if SUPPORTS_COLOR else ""
RESET = "\033[0m" if SUPPORTS_COLOR else ""

SKILL_ROOT = Path(__file__).resolve().parent.parent
TPL = SKILL_ROOT / "template"

# 固定输入 + 期望。expect_clean=True：应全过；False：应触发违规（魔鬼样本）。
INPUTS = [
    {"path": TPL / "sample-pages.html", "expect_clean": True,
     "desc": "10 基础版式"},
    {"path": TPL / "_layout-demo.html", "expect_clean": True,
     "desc": "7 第二代版式"},
    {"path": TPL / "_eval" / "stress-test.html", "expect_clean": False,
     "desc": "魔鬼样本（反向夹具）"},
]


def _overflow_clean(html: Path) -> bool:
    """check_overflow 全过返回 True。吞掉它的打印，只取返回码。"""
    with contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        code = check_html(html, tolerance=2, json_output=True)
    return code == 0


def _geometry_clean(html: Path) -> bool:
    """check_geometry 全过返回 True。"""
    data = check_geometry(html, return_data=True)
    for p in data["pages"]:
        if p["fontTooSmall"] or p["bleed"]:
            return False
    return True


def main() -> int:
    print(f"\n{BOLD}SPIC-PPT 回归评测套件{RESET}")
    print("=" * 40)
    print(f"{DIM}改 theme/components.css 后跑此脚本，确认 17 版式不退化、护栏仍灵敏{RESET}\n")

    all_ok = True
    for item in INPUTS:
        html = item["path"]
        if not html.exists():
            print(f"  {RED}[缺失]{RESET} {html.name} — 跳过")
            all_ok = False
            continue

        ov = _overflow_clean(html)
        ge = _geometry_clean(html)
        actually_clean = ov and ge

        if item["expect_clean"]:
            ok = actually_clean
            verdict = "应全过" + ("✓" if ok else "✗ 退化了！")
        else:
            # 魔鬼样本：期望"不干净"（护栏抓到了东西）
            ok = not actually_clean
            verdict = "应报违规" + ("✓ 护栏抓到" if ok else "✗ 护栏失灵！")

        all_ok = all_ok and ok
        mark = f"{GREEN}[ ok ]{RESET}" if ok else f"{RED}[FAIL]{RESET}"
        oflag = "溢出✓" if ov else f"{RED}溢出✗{RESET}"
        gflag = "几何✓" if ge else f"{RED}几何✗{RESET}"
        print(f"  {mark} {html.name:<24} {DIM}{item['desc']}{RESET}")
        print(f"         {oflag}  {gflag}  → {verdict}")

    print()
    if all_ok:
        print(f"{GREEN}{BOLD}评测通过：版式未退化，护栏灵敏。{RESET}")
        return 0
    print(f"{RED}{BOLD}评测失败：上方 FAIL 项需排查。{RESET}")
    print(f"{DIM}样板退化→检查刚改的 CSS 破坏了哪个版式；"
          f"护栏失灵→检查 check_overflow/check_geometry 是否被改弱{RESET}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
