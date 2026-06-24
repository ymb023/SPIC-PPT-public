#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPIC-PPT skill health check.

跑法：
    python scripts/health_check.py
    python scripts/health_check.py --skill-dir <path>

退出码：
    0  全部通过（可能含 WARNING）
    1  存在 FAIL
"""

import argparse
import os
import re
import sys
from pathlib import Path

try:
    import yaml  # PyYAML
except ImportError:
    sys.stderr.write(
        "ERROR: PyYAML not installed. Run: pip install pyyaml\n"
    )
    sys.exit(2)


# ---------- 输出编码 / 着色 ----------

# 在 Windows 控制台默认 GBK 编码下，✓ / ✗ / ⚠ 这类 Unicode 符号会触发
# UnicodeEncodeError。先尝试把 stdout/stderr 切到 UTF-8；切不动就降级到 ASCII。
def _force_utf8_stdio() -> bool:
    ok = True
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            ok = False
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            ok = False
    return ok


_UTF8_OK = _force_utf8_stdio()


def _supports_unicode_marks() -> bool:
    enc = (getattr(sys.stdout, "encoding", None) or "").lower()
    return _UTF8_OK or "utf" in enc


USE_UNICODE = _supports_unicode_marks()
USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

ANSI = {
    "green": "\033[32m",
    "red": "\033[31m",
    "yellow": "\033[33m",
    "gray": "\033[90m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}


def _c(text: str, color: str) -> str:
    if not USE_COLOR:
        return text
    return f"{ANSI.get(color, '')}{text}{ANSI['reset']}"


def mark_pass() -> str:
    return _c("[✓]" if USE_UNICODE else "[OK]  ", "green")


def mark_fail() -> str:
    return _c("[✗]" if USE_UNICODE else "[FAIL]", "red")


def mark_warn() -> str:
    return _c("[⚠]" if USE_UNICODE else "[WARN]", "yellow")


# ---------- 结果累计 ----------

class Report:
    def __init__(self) -> None:
        self.pass_count = 0
        self.fail_count = 0
        self.warn_count = 0

    def ok(self, msg: str) -> None:
        print(f"{mark_pass()} {msg}")
        self.pass_count += 1

    def fail(self, msg: str, detail: str | None = None) -> None:
        print(f"{mark_fail()} {_c(msg, 'red')}")
        if detail:
            for line in detail.splitlines():
                print(f"    {line}")
        self.fail_count += 1

    def warn(self, msg: str, detail: str | None = None) -> None:
        print(f"{mark_warn()} {_c(msg, 'yellow')}")
        if detail:
            for line in detail.splitlines():
                print(f"    {line}")
        self.warn_count += 1


# ---------- 检查项 ----------

FRONTMATTER_RE = re.compile(
    r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL
)
NAME_KEBAB_RE = re.compile(r"^[a-z][a-z0-9-]*$")

# 简易 <img ... src="..."> 提取（按行扫，方便给行号）
IMG_SRC_RE = re.compile(
    r"""<img\b[^>]*?\bsrc\s*=\s*(?P<q>['"])(?P<src>[^'"]+)(?P=q)""",
    re.IGNORECASE,
)

# 默认跳过的目录（递归扫描 HTML 时）
SKIP_DIRS = {"_preview", "_versions", "node_modules", ".git", "__pycache__"}


def check_frontmatter(skill_dir: Path, rpt: Report) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        rpt.fail(f"SKILL.md not found at {skill_md}")
        return

    text = skill_md.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        rpt.fail(
            "SKILL.md missing YAML frontmatter (--- ... --- block)",
            f"file: {skill_md}",
        )
        return

    raw = m.group(1)
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        rpt.fail(
            "SKILL.md frontmatter is NOT valid YAML",
            f"parser error: {e}\nfile: {skill_md}",
        )
        return

    rpt.ok("frontmatter YAML valid")

    if not isinstance(data, dict):
        rpt.fail(
            "frontmatter is not a YAML mapping",
            f"got type: {type(data).__name__}",
        )
        return

    # name 字段
    name = data.get("name")
    if not name:
        rpt.fail("frontmatter missing required field: name")
    elif not isinstance(name, str):
        rpt.fail(
            "frontmatter field 'name' is not a string",
            f"got: {name!r} (type {type(name).__name__})",
        )
    elif not NAME_KEBAB_RE.match(name):
        rpt.fail(
            f"frontmatter name is NOT kebab-case lowercase: {name!r}",
            "required regex: ^[a-z][a-z0-9-]*$\n"
            "fix: rename to e.g. 'spic-ppt'",
        )
    else:
        rpt.ok(f"frontmatter name is kebab-case lowercase: {name}")

    # description 字段
    desc = data.get("description")
    if desc is None:
        rpt.fail("frontmatter missing required field: description")
    elif not isinstance(desc, str):
        rpt.fail(
            "frontmatter field 'description' is not a string",
            f"got type: {type(desc).__name__}",
        )
    elif len(desc) < 50:
        rpt.fail(
            f"frontmatter description too short: {len(desc)} chars",
            "required: >= 50 chars",
        )
    else:
        rpt.ok(
            f"frontmatter description present ({len(desc)} chars)"
        )


def iter_html_files(skill_dir: Path):
    for root, dirs, files in os.walk(skill_dir):
        # 原地过滤要跳过的目录
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            low = fn.lower()
            # 跳过自包含单文件交付物（base64 内联，非源 HTML，不当成品扫）
            if low.endswith(".standalone.html"):
                continue
            if low.endswith(".html"):
                yield Path(root) / fn


HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def strip_html_comments(text: str) -> str:
    """把 <!-- ... --> 注释块替换为同长度的空白（保留行号）."""
    def repl(m):
        s = m.group(0)
        # 保留换行符以维持行号；其他字符替换为空格
        return "".join("\n" if c == "\n" else " " for c in s)
    return HTML_COMMENT_RE.sub(repl, text)


def check_logo_paths(skill_dir: Path, rpt: Report) -> None:
    html_files = list(iter_html_files(skill_dir))
    if not html_files:
        rpt.warn("no HTML files found under skill dir")
        return

    broken = []   # (html, lineno, src, resolved)
    checked = 0

    for html in html_files:
        try:
            raw = html.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            rpt.fail(
                f"cannot read HTML: {html.relative_to(skill_dir)}",
                str(e),
            )
            continue

        # 先剔除 HTML 注释中的占位 src，避免误报模板示例代码
        stripped = strip_html_comments(raw)
        lines = stripped.splitlines()

        for lineno, line in enumerate(lines, start=1):
            for m in IMG_SRC_RE.finditer(line):
                src = m.group("src").strip()
                checked += 1
                # 跳过外链 / data URI / 锚点
                if (
                    src.startswith(("http://", "https://", "//"))
                    or src.startswith("data:")
                    or src.startswith("#")
                ):
                    continue
                resolved = (html.parent / src).resolve()
                if not resolved.exists():
                    broken.append((html, lineno, src, resolved))

    if not broken:
        rpt.ok(
            f"all <img src> paths resolvable "
            f"({checked} refs across {len(html_files)} HTML files)"
        )
        return

    # 按文件聚合输出，但每个坏引用都算一次 FAIL
    for html, lineno, src, resolved in broken:
        rel_html = html.relative_to(skill_dir)
        rpt.fail(
            f"LOGO/asset path broken: {rel_html}:{lineno}",
            f'src="{src}"\n'
            f"expected at: {resolved}  (NOT FOUND)",
        )


def check_core_files(skill_dir: Path, rpt: Report) -> None:
    core_files = [
        "template/theme.css",
        "template/components.css",
        "template/sample-pages.html",
        "template/template.html",
        "template/_assets/wave-inner.png",
        "template/_assets/wave-cover-plain.png",
        "shared/logos/etrc/etrc-logo.png",
        "template/_layout-demo.html",
        "template/_eval/stress-test.html",
        "scripts/check_geometry.py",
        "scripts/eval_suite.py",
    ]
    for rel in core_files:
        target = skill_dir / rel
        if target.exists():
            rpt.ok(f"core file exists: {rel}")
        else:
            rpt.fail(
                f"core file MISSING: {rel}",
                f"expected at: {target}",
            )


def check_templates_double_track(skill_dir: Path, rpt: Report) -> None:
    legacy = skill_dir / "templates"
    if legacy.exists() and legacy.is_dir():
        rpt.warn(
            "legacy `templates/` directory still present",
            f"location: {legacy}\n"
            "suggestion: template/ is the canonical source; "
            "consider deleting templates/ to avoid double-track drift.",
        )
    else:
        rpt.ok("no legacy templates/ directory (single-track OK)")


def check_version_consistency(skill_dir: Path, rpt: Report) -> None:
    """版本号四处必须一致：VERSION / SKILL.md frontmatter / README 当前版本行 /
    components.css 顶注。

    历史教训：升版本时反复漏改某处（靠记得=必漏）——README 漏过、components.css
    顶注一度滞后到 v4.6.1。把一致性变成可检测的失败，焊进 health check。
    """
    versions: dict[str, str] = {}

    # 1) VERSION 文件
    vf = skill_dir / "VERSION"
    if vf.exists():
        versions["VERSION"] = vf.read_text(encoding="utf-8").strip()

    # 2) SKILL.md frontmatter version
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        m = FRONTMATTER_RE.match(skill_md.read_text(encoding="utf-8"))
        if m:
            try:
                data = yaml.safe_load(m.group(1))
                if isinstance(data, dict) and data.get("version") is not None:
                    versions["SKILL.md"] = str(data["version"]).strip()
            except yaml.YAMLError:
                pass

    # 3) README 当前版本行（当前版本：**vX.Y.Z**）
    readme = skill_dir / "README.md"
    if readme.exists():
        rm = re.search(
            r"当前版本[：:]\s*\*{0,2}v?([0-9]+\.[0-9]+\.[0-9]+)",
            readme.read_text(encoding="utf-8"),
        )
        if rm:
            versions["README.md"] = rm.group(1)

    # 4) components.css 顶注（SPIC-PPT 标准模板 vX.Y.Z · 通用组件）
    css = skill_dir / "template" / "components.css"
    if css.exists():
        cm = re.search(
            r"标准模板\s*v([0-9]+\.[0-9]+\.[0-9]+)",
            css.read_text(encoding="utf-8")[:400],
        )
        if cm:
            versions["components.css"] = cm.group(1)

    if len(versions) < 2:
        rpt.warn(
            "version consistency: 不足两处可比对",
            f"found: {versions}",
        )
        return

    # 归一化（去掉可能的前导 v）后比较
    norm = {k: v.lstrip("vV") for k, v in versions.items()}
    distinct = set(norm.values())
    if len(distinct) == 1:
        rpt.ok(
            f"version consistent across {len(versions)} sources: "
            f"v{next(iter(distinct))}"
        )
    else:
        detail = "\n".join(f"  {k}: {v}" for k, v in versions.items())
        rpt.fail(
            "version MISMATCH across sources (升版本时漏改了某处)",
            detail + "\nfix: 四处统一到同一版本号",
        )


def check_components_features(skill_dir: Path, rpt: Report) -> None:
    css = skill_dir / "template" / "components.css"
    if not css.exists():
        rpt.fail(
            "components.css missing — cannot verify v4.3 features",
            f"expected at: {css}",
        )
        return
    text = css.read_text(encoding="utf-8", errors="replace")
    required_tokens = [".slide.compact", ".slide.center-y", ".body-center"]
    missing = [tok for tok in required_tokens if tok not in text]
    if missing:
        rpt.fail(
            "components.css missing v4.3 modifier classes",
            "missing tokens: " + ", ".join(missing),
        )
    else:
        rpt.ok(
            "components.css has v4.3 modifier classes "
            "(.slide.compact / .slide.center-y / .body-center)"
        )


# ---------- 主入口 ----------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="SPIC-PPT skill health check"
    )
    default_skill_dir = Path(__file__).resolve().parent.parent
    ap.add_argument(
        "--skill-dir",
        type=Path,
        default=default_skill_dir,
        help=f"skill root dir (default: {default_skill_dir})",
    )
    args = ap.parse_args()
    skill_dir: Path = args.skill_dir.resolve()

    title = "SPIC-PPT skill health check"
    print(_c(title, "bold"))
    print("=" * len(title))
    print(_c(f"skill dir: {skill_dir}", "gray"))
    print()

    if not skill_dir.exists() or not skill_dir.is_dir():
        print(
            f"{mark_fail()} skill-dir does not exist or is not a directory: "
            f"{skill_dir}"
        )
        return 1

    rpt = Report()
    check_frontmatter(skill_dir, rpt)
    check_logo_paths(skill_dir, rpt)
    check_core_files(skill_dir, rpt)
    check_templates_double_track(skill_dir, rpt)
    check_components_features(skill_dir, rpt)
    check_version_consistency(skill_dir, rpt)

    print()
    summary = (
        f"Result: {rpt.pass_count} passed, "
        f"{rpt.fail_count} failed, "
        f"{rpt.warn_count} warning"
        + ("" if rpt.warn_count == 1 else "s")
    )
    if rpt.fail_count:
        print(_c(summary, "red"))
        return 1
    if rpt.warn_count:
        print(_c(summary + "  (warnings only — exit 0)", "yellow"))
        return 0
    print(_c(summary, "green"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
