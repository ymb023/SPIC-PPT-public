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


# 三态：渲染失败(error)必须与"护栏抓到违规"(dirty)区分——否则魔鬼样本会因
# Chrome 没渲染成功而 false-green（exit 2 被当成"护栏抓到了"）。
CLEAN, DIRTY, ERROR = "clean", "dirty", "error"


def _overflow_state(html: Path) -> str:
    """check_overflow：0=clean / 1=dirty(有溢出) / 2=error(渲染失败)。"""
    with contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        try:
            code = check_html(html, tolerance=2, json_output=True)
        except Exception:
            return ERROR
    if code == 2:
        return ERROR
    return CLEAN if code == 0 else DIRTY


def _geometry_state(html: Path) -> str:
    """check_geometry：渲染失败抛 RuntimeError → error；否则按违规判 clean/dirty。"""
    try:
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            data = check_geometry(html, return_data=True)
    except Exception:
        return ERROR
    if data.get("pageNoIssues"):
        return DIRTY
    for p in data["pages"]:
        if p["fontTooSmall"] or p["bleed"]:
            return DIRTY
    return CLEAN


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

        ov = _overflow_state(html)
        ge = _geometry_state(html)

        if ov == ERROR or ge == ERROR:
            # 渲染失败：既不是"全过"也不是"护栏抓到"，是硬错误，绝不算 PASS
            ok = False
            verdict = f"{RED}渲染失败（Chrome 没跑成）—— 无法判定{RESET}"
        elif item["expect_clean"]:
            ok = (ov == CLEAN and ge == CLEAN)
            verdict = "应全过" + ("✓" if ok else "✗ 退化了！")
        else:
            # 魔鬼样本：期望至少一项 dirty（护栏真抓到违规，而非渲染失败）
            ok = (ov == DIRTY or ge == DIRTY)
            verdict = "应报违规" + ("✓ 护栏抓到" if ok else "✗ 护栏失灵！")

        all_ok = all_ok and ok
        mark = f"{GREEN}[ ok ]{RESET}" if ok else f"{RED}[FAIL]{RESET}"
        def flag(name, st):
            if st == CLEAN: return f"{name}✓"
            if st == DIRTY: return f"{name}！"
            return f"{RED}{name}ERR{RESET}"
        print(f"  {mark} {html.name:<24} {DIM}{item['desc']}{RESET}")
        print(f"         {flag('溢出',ov)}  {flag('几何',ge)}  → {verdict}")

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
