# scripts/ · 工作流辅助脚本

本目录放 SPIC-PPT skill 的辅助脚本。一律纯 Python，能在 Windows / macOS / Linux 上跑。

| 脚本 | 用途 | 何时跑 |
|---|---|---|
| `build_pdf.py` | **导出主入口**：溢出闸门→快照留底→导 PDF→顺带产单文件 standalone | **第七阶段导出用这个**，别手敲 chrome |
| `check_overflow.py` | 检测 .slide 内容是否超出 720px 边界（被 build_pdf 当闸门调用） | 单独自检；build_pdf 自动调 |
| `check_geometry.py` | 几何护栏：字号<8pt / 元素出血 / 页码连续性 | 单独自检；build_pdf 导出时只警告不阻断 |
| `eval_suite.py` | 回归评测：3 固定输入跑全套，确认 17 版式不退化、护栏灵敏 | **改 theme/components.css 后必跑** |
| `inline_html.py` | 把 HTML 的外部 CSS+图片内联成自包含单文件（被 build_pdf 调用） | build_pdf 自动调；一般不单独跑 |
| `extract_images.py` | 从 .docx / .pptx / .pdf 抽出可复用图片 | 接到用户成稿后的第二阶段 |
| `health_check.py` | 体检 skill 工程健康度（frontmatter、LOGO 路径、关键文件、CSS 关键类、版本四处一致） | fresh install 后、任何手动改动后、CI |

---

## health_check.py

一键健康检查脚本。检查 skill 在工程层面是否处于"可装配"状态。

### 用法

```bash
# 默认扫描脚本所在目录的父目录（= skill 根目录）
python scripts/health_check.py

# 指定 skill 目录
python scripts/health_check.py --skill-dir C:/path/to/SPIC-PPT
```

### 检查项

1. **frontmatter YAML 合法性**：SKILL.md 头部 `--- ... ---` 必须能被 `yaml.safe_load` 解析；必有 `name`、`description`；`name` 必须是 kebab-case 小写；`description` ≥ 50 字符。
2. **LOGO / 资源路径解析**：递归扫描所有 `.html`（跳过 `_preview/` 等），把 `<img src="...">` 当作相对该 HTML 的路径解析，校验目标文件是否存在。
3. **关键文件存在性**：`template/{theme.css, components.css, sample-pages.html, template.html, _layout-demo.html}`、`_assets/{wave-inner, wave-cover-plain}.png`、`shared/logos/etrc/etrc-logo.png`、`scripts/{check_geometry, eval_suite}.py`、`template/_eval/stress-test.html`。
4. **目录双轨检测**：如果 `templates/` 仍存在，告 WARNING（建议统一到 `template/`）。
5. **components.css 关键修饰类**：必须含 `.slide.compact`、`.slide.center-y`、`.body-center`。
6. **版本号四处一致**：VERSION / SKILL.md frontmatter / README 当前版本行 / components.css 顶注，不一致即 FAIL。

### 退出码

- `0` 全部通过（含仅 WARNING 的情况）
- `1` 存在任何 FAIL
- `2` 环境异常（如未安装 PyYAML）

### 依赖

- Python 3.9+（用了 PEP 604 联合类型）
- `pip install pyyaml`

### 输出示例

```
SPIC-PPT skill health check
============================
[✓] frontmatter YAML valid
[✗] frontmatter name is NOT kebab-case lowercase: 'SPIC-PPT'
    required regex: ^[a-z][a-z0-9-]*$
[✓] core file exists: template/theme.css
[⚠] legacy `templates/` directory still present
...

Result: 12 passed, 2 failed, 1 warning
```

---

## extract_images.py

从 .docx / .pptx / .pdf 中提取所有可复用图片，避免 AI 在 PPT 装配时重画占位框。

### 用法

```bash
python scripts/extract_images.py <输入文件> [输出目录]
```

默认输出目录：`_images/extracted/`

### 示例

```bash
# 从研究报告抽图
python scripts/extract_images.py 研究报告.docx

# 从历史 PPT 抽图（指定输出目录）
python scripts/extract_images.py 历史汇报.pptx my_project/_images/extracted

# 从 PDF 抽图
python scripts/extract_images.py 行业报告.pdf
```

### 输出

```
_images/extracted/
├── image_01.png       ← 第1张图
├── image_02.jpeg
├── ...
└── manifest.md        ← 图片清单（来源+尺寸+上下文，给 AI 用）
```

### 自动过滤

- 跳过小于 3KB 的文件（一般是图标/装饰元素）
- 跳过 `.wmf`、`.emf`（PPT 矢量元数据，HTML 用不了）
- 跳过 `Thumbs.db`、`.DS_Store`
- PDF 提取时跳过尺寸小于 70×70 像素的图

### 依赖

- **docx / pptx**：只需标准库 `zipfile`，零依赖
- **pdf**：`pip install pymupdf`

### 在工作流中的位置

属于 **第二阶段（读懂成稿）** 的子任务。

接到用户的成稿后，AI 应该立即：
1. 调用本脚本提取图片
2. 读取 `manifest.md` 了解可用图片资源
3. 在 **第三阶段（结构化抽取）** 时，对每页内容判断是否有匹配的原图
4. 在 **第五阶段（HTML 装配）** 时直接 `<img>` 引用，不要用占位框


---

## check_overflow.py

**装配的 PPT 是否真的装得下 720px？** 这个脚本用 Chrome headless 实测每张
`.slide` 内所有子元素的 `getBoundingClientRect().bottom` 是否超出 slide 底部。

### 为什么不能光靠"看 PNG"？

`.slide` 有 `overflow: hidden` + `height: 720px`，内容溢出后**会被静默裁掉**，
渲染出来的 PNG 看不见缺失内容——很多溢出 bug 就是这样在交付后才被发现的。
这个脚本绕过裁切，从 DOM 测量真实的内容高度。

### 用法

```bash
# 基本用法（推荐：装配完每个 deck 都跑一次）
python scripts/check_overflow.py path/to/deck.html

# 调宽容差（默认 +2px）
python scripts/check_overflow.py path/to/deck.html --tolerance 5

# 机器可读 JSON（用于 CI / 脚本集成）
python scripts/check_overflow.py path/to/deck.html --json
```

### 退出码

- `0` 全部 slide 在 720px 内
- `1` 至少一张 slide 溢出 → **必须修才能交付**
- `2` 环境异常（找不到 Chrome、HTML 不存在等）

### 输出示例

```
SPIC-PPT overflow check
================================
pages: 26   tolerance: +2px

  [ ok ] p 1  content_bottom=720px (slide=720)
  ...
  [FAIL] p20  溢出 +8px   content_bottom=728 deepest=UL.five-with-img
  [FAIL] p22  溢出 +57px  content_bottom=777 deepest=DIV.accent-line

Result: 2 / 26 pages overflow

建议修复（按优先级）：
  1. 先给溢出页加 'compact' 类：<section class="slide compact">
  2. 再次跑本脚本验证
  3. 仍 FAIL → 拆分该页 / 减列表项 / 减卡片数（结构性减载）
  4. 不要靠『再缩字号』——投屏会看不清
```

### 依赖

- Python 3.9+
- 已安装 Chrome 或 Edge（自动探测常见路径）
- 无需 pip 装额外包（不依赖 Playwright / Selenium）

### 集成到工作流

第七阶段直接用 `build_pdf.py`（已把溢出闸门焊进导出，不要再手敲 chrome 命令）：
```bash
python scripts/build_pdf.py 成品PPT.html
```
它先跑 check_overflow，任一页溢出即拒绝导出；过了才导 PDF + 顺带产单文件 standalone。
单独自检（不导出）仍可用 `python scripts/check_overflow.py 成品PPT.html`。

---

## build_pdf.py / check_geometry.py / eval_suite.py / inline_html.py

这四个脚本的用法与设计见 **SKILL.md 第七/八阶段**与 **CHANGELOG**（v4.6 导出闸门、v4.8 快照、v4.9 单文件、v4.11 评测套件+几何护栏）。要点：

- **build_pdf.py**：导出主入口。`--no-standalone` 跳过单文件、`--force` 跳过溢出闸门、`--tolerance N` 调容差、`-o` 指定输出。导出时顺带跑几何护栏（字号<8pt/出血/页码），只警告不阻断。
- **check_geometry.py**：`python scripts/check_geometry.py deck.html [--json]`。字号红线 8pt（"真看不清"绝对线，非 14pt）、元素出血、页码连续性。
- **eval_suite.py**：`python scripts/eval_suite.py`。改 theme/components.css 后跑，3 固定输入（两样板期望全过 + 魔鬼样本期望被抓）自动判版式是否退化、护栏是否失灵。
- **inline_html.py**：被 build_pdf 调用产 standalone，一般不单独跑。
