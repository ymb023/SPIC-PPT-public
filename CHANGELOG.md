# Changelog

所有重要的版本变更记录于此。版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

---

## [4.8.2] — 2026-06-05 · SKILL.md 瘦身：reference 内容下沉（context engineering）

依据 Anthropic《Lessons from building Claude Code: How we use skills》#02——SKILL.md 应是导航页，详细说明下沉到 references/，渐进暴露。

### Changed
- **删 SKILL.md 重复段**：「v4 视觉系统核心要点」整段（色值/字重/旧版错误，约 16 行）与 `references/visual-evolution.md` 一字不差重复，删除并替换为一句视觉语言概括 + 指针。零信息损失，装配时拿不准的视觉细节去 reference 查。
- **色值表标注真相源**：SKILL.md 配色速查表注明「真相源是 `template/theme.css` 的 CSS 变量」，降低多处文档色值漂移风险（不加检查脚本——色值不像版本号频繁变，theme.css 是事实源，避免过度工程化）。

### Notes
- 保留判断：色值/字体/LOGO 路径/飘带文件名是装配高频锚点（每页要查），留在导航页符合 #02，不下沉。区分标准是查阅频率：每页用 → 留；历史考据 → 下沉。

## [4.8.1] — 2026-06-05 · 修复 README 版本漏更 + 版本一致性焊进 health_check

用户发现：GitHub 主页 README"当前版本"行一直停在 v4.6.1——升版本时反复漏改 README 这一处（4.7.0、4.8.0 两次都漏）。根因是"六处同步"靠记得，又掉进本 skill 一路在批判的"靠 AI 记得"坑。

### Fixed
- **README"当前版本"行**：v4.6.1 → v4.8.1，与 VERSION / SKILL.md frontmatter 对齐。

### Added
- **`health_check.py` 版本一致性检查**：比对 VERSION / SKILL.md frontmatter / README"当前版本"行三处，不一致即 FAIL。把"升版本漏改某处"从"事后被用户发现"变成"health_check 立即报错"——同本 skill"焊进结构、不靠记得"的根治哲学。负向测试验证：改坏 README → exit 1。

## [4.8.0] — 2026-06-05 · 版本快照（导出自动留底，可找回旧版）

用户反馈：制作 PPT 时常需找回旧版，但成品 HTML/PDF 每次都原地覆盖——根因是压根没有版本控制。

### 设计判断
- 不用 git：恢复场景是"拿回那一版文件"，非合并/diff；HTML diff 噪音大、PDF 是黑盒，git 价值发挥不出。
- 焊进导出闸门：`build_pdf.py` 已是强制必经卡点，加快照不引入新纪律（同"溢出自检焊进导出"的根治哲学）。
- 粒度=每次导出：只有"导出"才是值得找回的版本，中间编辑不快照（有意选择）。

### Added
- **`build_pdf.py` 导出前自动留底**：覆盖前把上一版 `成品PPT.html` + `成品PPT.pdf` 复制进 `_versions/`，命名带秒级时间戳 `<basename>_<YYYYMMDD-HHMMSS>.<ext>`。首次导出（无旧版）不报错、无快照。
- **找回旧版**：直接打开 `_versions/` 里对应时间戳文件即可，零工具、零心智。

### Changed
- **`SKILL.md` 第八阶段**：归档目录加 `_versions/`，附"版本留底"与"找回旧版"说明。
- **`health_check.py`**：`SKIP_DIRS` 加 `_versions`，避免把历史快照当成品扫。
- **`.gitignore`**：加 `_versions/`（本地产物，不进 git，同 `_preview/`）。

### Engineering Notes
- TDD：先建 RED（`snapshot_before_overwrite` 不存在→导入失败）→ 实现 → GREEN（7/7：已有旧版产快照、首次不报错、二次累计、命名格式、时间戳唯一）。
- `check_overflow.py` 只接单文件不扫目录，无需改（spec 中该条为防御性，实际不触发）。

## [4.7.0] — 2026-05-29 · 讲课听众 + 文件名全英文 + 封底改八字

三项用户反馈一次落地。

### Added
- **用途新增"讲课/培训"一类**（SKILL.md 启动清单）：补"用途差异（影响版式节奏）"——汇报/审核走高密度结论先行（0.5-1 页/分钟）；讲课/培训走单页单知识点、多 `.center-y`、慢节奏（1.5-2 页/分钟）。讲课指业务/知识讲授，党课党建仍走专门工作流。

### Changed
- **文件名全部英文化**：65 个中文文件名 + 2 个中文目录（`标准模板/`→`template/`、`产品案例页/`→`product-case/`）改为英文；HTML/CSS/脚本里的功能性引用同步更新（17 个文本文件）。git 识别为 rename（保留历史）。资产/LOGO 用语义化英文名（如 `集团波浪条-内页.png`→`wave-inner.png`、`经研院LOGO.png`→`etrc-logo.png`、`首选简称组合横式.png`→`preferred-short-horizontal.png`）。
- **封底改八字**（template.html + sample-pages.html 尾页）：去掉"恳请各位领导批评指正"+机构署名，改为单行 40pt「风光无限　国家电投」，"风"染品牌绿、"光"染品牌红（双关新能源底色），保留飘带+LOGO。
- **health_check.py** 内部 `components.css` 路径同步改 `template/`。

### Verified
- health_check 13/13、overflow 10/10、封底渲染肉眼核验（飘带高清不变形）。

## [4.6.1] — 2026-05-29 · 内页波浪分割线换高清版（资产升级）

纯资产升级。内页波浪分割线 `wave-inner.png` 换高清版，所有新 deck 自动套用，无需每次手动换图。

### 根因（实测，非代码缺陷）
- Chrome 实测：所有 wave 渲染 distortion=1.000，CSS（`.page-wave img { height:auto }`）从未拉伸。
- "拉伸变形"来自资产本身——旧版 1544×48（32:1）细条铺满 1160px 后波形被摊平，是分辨率/比例问题。

### Changed
- `template/_assets/wave-inner.png`：1544×48（32:1，10KB）→ 12000×200（60:1，579KB）。
- 文件名与 CSS 不变，纯资产替换；新版更扁、更精致，投屏更清晰。

## [4.6.0] — 2026-05-29 · 根治溢出+对齐：从"靠AI记得"到"结构上做对"

系统化调试。根因不是"提醒不够"，而是架构：把"正确布局"写成了 AI 装配时要手动记得套的约定，而非组件自带默认行为。改 3 次（v4.3.1/v4.5.0/v4.5.3）仍复发 = 架构问题，停止打补丁。

### 证据（真实成品取证）
- 中海油成品 `.compact` 用 **0 次**、带 2 页溢出直接交付 = 溢出自检脚本**从没跑过**。
- 集团月报加了 11 次 compact 仍漏 p6/p9/p16（deepest 全是 `.three-cards`）= AI 手动加，记得 11 次漏 3 次。
- `.body-grid` 被 SKILL 文档使用、被成品用 15–48 次，但 **components.css 里零定义** = 每次装配都靠 AI 手写 grid+对齐，经常漏 → 两栏底部不齐。
- 连 skill 自己的样板 `sample-pages.html` P5 都带 +19px 溢出——参考模板本身就是坏的。

### Added
- **`.body-grid` 双栏布局基类**（components.css）：对齐焊进 CSS——`flex:1`+`min-height:0`+`align-items:stretch`，两栏等高、底部自动对齐；`.cols-1-2`/`.cols-2-1` 调比例；`> * { min-width:0 }` 防长内容撑破。装配直接用类，不再手写。RED 夹具验证：双栏含竖图 +580px → 0。
- **`.chart-frame` 图片 containment**：`max-height:100%`+`object-fit:contain`+flex 列容器。竖高图在等高栏内被封顶、不撑破、不变形；纯 block 上下文退化为不约束（向后兼容）。RED 夹具：全宽竖图 +1772px → 0。
- **`scripts/build_pdf.py` 导出闸门**：导 PDF 前强制跑溢出自检，**任一页溢出即拒绝导出**并列出改法，过了才导。把"自检"从"请 AI 记得跑"变成"结构上跳不过"。双向测试通过：溢出 deck 被拒不产 PDF / 干净 deck 放行产 409KB PDF。

### Fixed
- **`sample-pages.html` P5** 给编号点列页加 `.compact`，消除样板自带的 +19px 溢出。现 10/10 页全过。

### Changed (SKILL.md)
- 第七阶段导出：`python scripts/build_pdf.py deck.html` 取代手敲 chrome 命令（闸门内置自检）。
- 速查表"双栏对齐"铁律：从"手写 grid 三件套"改为"直接用 `.body-grid`"；新增"图表容器"行。

### Engineering Notes
- 内容超量页（compact 也救不了）策略：保持一页 + 删减最长项（不自动拆/缩字号——投屏底线），`--force` 可显式放行。
- TDD 回归保护起作用：先建 RED 夹具看其 FAIL（+580/+1772）再改 CSS；改后回归 sample-pages 发现 P5 仍 FAIL → 核对确认是**既有 bug**非本次引入（chart-frame 改与 auto-list 页无关），避免了误判与瞎改。

---

## [4.5.3] — 2026-05-29 · 模型升级重审 · 瘦身/脱敏/边界加固

随主模型升级到 Opus 4.8 重新审视 skill：区分"为弱模型搭的脚手架"（可瘦身）与"模型再强也替代不了的"（必留）。

### 设计判断
- **确定性工具全留**：`check_overflow.py` / `extract_images.py` / Chrome 导 PDF——模型再强也"看不见"被 `overflow:hidden` 裁掉的溢出，这是结构性需要，非能力问题。
- **判断类散文瘦身**：强模型自带疏密判断与版面感，弱模型时代的硬阈值拐杖可降级。
- **专属审美与域规矩必留**：纯白 / hairline / 极细字重 / 不要党政标语感 / 集团飘带必用——强模型猜不到，必须写死。

### Changed（瘦身）
- **`.compact` / `.center-y` 触发清单降级**：从"必加硬阈值表"改为"判断交给模型 + `check_overflow.py` 兜底 + 经验阈值参考"。
- **"视觉饱满"散文压缩**：6 行 → 1 段，只保留数值锚点（留白 >25%、卡片 `min-height` 等）。

### Added（针对强模型的新风险）
- **"做减法不做加法"边界加固**：模型越强越易"热心扩写"论点/补数据，明确这是越界——用户判断在研究阶段已定稿。

### Fixed（脱敏 + 缺陷）
- **清除残留人名**（7 处 / 5 文件）：补做脱敏，清除上轮遗漏的内部人名。
- **frontmatter 版本回填**：`4.5.1` → `4.5.3`（修正 4.5.2 时漏更 SKILL.md 版本字段）。
- **SKILL.md 定位去"经研院"**：标题与 description 改为"国家电投 (SPIC)"，与 README 脱敏保持一致（触发词"经研院汇报"保留）。
- **`design-spec-summary.md` 加过时归档警示**：标明其色值（电投蓝绿）已被 v4 LOGO 四色取代，勿用于装配。

---

## [4.5.2] — 2026-05-25 · 封底去掉 THANK YOU

用户反馈：封底的"THANK YOU"大字在央企汇报语境下显得突兀。

### Changed
- **`template/template.html`**（尾页）：移除 84pt "THANK YOU" h1，改为以"恳请各位领导批评指正"（20pt，字距 0.4em）为主视觉，hairline 细线分隔机构署名 + 日期，整体垂直居中。
- **`template/sample-pages.html`**（P10 尾页）：同步修改。
- **`SKILL.md`** 版式表：`尾页（THANK YOU + 飘带）` → `尾页（机构署名 + 飘带）`。

### Design rationale
"THANK YOU" 源自英文商业 PPT 惯例，在中文正式汇报（尤其是向领导层汇报）中与语境不符。
去掉后由"恳请各位领导批评指正"承担结尾语义，letter-spacing 拉开、hairline 收底，整体更正式克制。

---

## [4.5.1] — 2026-05-20 · 红绿飘带视觉精修

用户反馈："红绿色飘带感觉很生硬在贴图，还有裁切的边框"。

### Root cause（两点）
1. **PNG 半透明像素过多**：原始 `wave-inner.png` 平均 alpha 仅 47%
   （RGBA mode，大量边缘半透明），白底上看就像褪色。
2. **PNG 左右是硬切边**：飘带形状直接到 PNG 边界结束，无渐变过渡，
   全宽显示时形成明显矩形框感。

### Fixed
- **PNG alpha 增强**（`scripts/` 一次性处理）：
  - 原 772×24 → alpha 阈值化（>20 → 255）→ Bicubic 升 1544×48
    → 二次阈值（>80 → 255，20-80 → ×2 加深）
  - 最终 mean alpha 47 → **133**（+183%），opaque 像素 32% → **51%**
- **两侧 4% 渐隐**（components.css `.page-wave::before/::after` 伪元素）：
  - 左：linear-gradient `#FFF` → transparent，覆盖宽度 4%
  - 右：linear-gradient transparent → `#FFF`，覆盖宽度 4%
  - Chrome `--print-to-pdf` 兼容（CSS `mask-image` 在打印模式不稳）
- 颜色现在饱满清晰、两侧自然融入纸面、无"贴图感"

### Files changed
- `template/_assets/wave-inner.png`（1544×48，alpha 增强版）
- `template/components.css`（`.page-wave::before/::after` 渐隐伪元素）
- 备份保留：`wave-inner-original-772x24.png`

---

## [4.5.0] — 2026-05-20 · 根治装配溢出

用户反馈：v4.3.x 加了 `.compact / .center-y` 修饰类后，AI 装配 PPT 时**仍经常出现
页面溢出**。根因：规则定义有，但 AI 不知道何时该用、且不主动检测。

### Added (核心交付)
- **`scripts/check_overflow.py`**（240 行）：用 Chrome headless + 注入 JS 实测每张
  `.slide` 内所有元素的 `getBoundingClientRect().bottom`，与 slide 底部比较。
  比"渲染 PDF 看 PNG"准确得多（`.slide` 的 `overflow:hidden` 会把溢出内容静默
  裁掉，PNG 上看不出来）。
  - 默认容差 +2px；可 `--tolerance N` 调宽
  - `--json` 输出机器可读
  - exit 1 if any overflow → 阻断"溢出版本被交付"
  - 无外部依赖（不要 Playwright / Selenium）

### Changed (SKILL.md)
- **第七阶段重命名**为 "溢出自检 → PDF 导出 → 反向验证"
  - 强制步骤 1：跑 check_overflow.py，FAIL 不准导 PDF
  - 步骤 2 才是 PDF 导出
  - 步骤 3 抽样验证（重点看字体/配色，溢出已在步骤 1 排除）
- **新增 `.compact` 必加触发清单**（v4.x 铁律节）：
  - 编号点列 ≥ 5 项
  - 三栏卡片 + key-point + chart 三块同框
  - 双栏每栏 ≥ 3 条
  - 时间线 ≥ 5 步
  - key-point ≥ 80 字
  - 数据墙 + key-point + 额外文本
  - 单页含 4+ 个组件块
- 新增反向 `.center-y` 必加清单（稀疏页）

### Engineering Notes
之前的失败模式：SKILL.md 说"密集页用 .compact"，但 AI 主观判断"密集"，常判错；
SKILL.md 说"反向验证 PNG"，但 AI 经常跳过，或只看几页且看不出溢出。
v4.5 把"AI 凭感觉判断 + 用户事后发现"换成"装配时按清单加 .compact + 强制自检"。

实测：在中海油 deck（26 页）上脚本准确发现 p20 (+8px) 和 p22 (+57px) 溢出。

---

## [4.4.0] — 2026-05-20 · 工程化大清理

按 Codex 工程诊断修复 5 个 fatal skill 安装坑 + 2 个自查盲点。
**Breaking** 变更：目录结构调整。fresh install 健康检查 13/13 通过。

### Fixed (P0)
- **frontmatter YAML 不合法**——`description` 中未加引号的 `NOT for:` 导致 YAML 解析失败。重写为 block scalar (`>-`) 折叠样式，把 `NOT for:` 改成 `Skip this skill when` 去掉冒号。
- **`name` 字段大小写**——`SPIC-PPT` → `spic-ppt`（kebab-case lowercase，符合 OpenAI/Codex agent 规范）。
- **LOGO 路径全坏**——31 处 HTML 引用 `../_shared/logos/...` 但 skill 实际目录是 `shared/logos/...`。批量修了 16 个 HTML、82 处路径引用。
- **`templates/` vs `template/` 双轨**——删除整个 `templates/`（05-19 旧版，无 v4.3 功能）。SKILL.md 中 7 处引用全替换为 `template/`。
- **`extract_images.py` PDF 措辞错**——"PyMuPDF 渲染" → "PyMuPDF 提取内嵌图片（不处理矢量图表）"。函数 docstring 加局限性说明 + 整页渲染 fallback 提示。

### Changed
- **SKILL.md 瘦身**：658 → 320 行（-51%）。v4 视觉系统、v4.1 五件套、v4.2 P1、v4.3.x 三件套、装配铁律、"Don't modernize" 全部外置到 `references/visual-evolution.md`。
- **`product-case/`**：移到 `references/examples/product-case/`，明确是参考案例非 skill 资产。修了相对路径深度（多上跳 2 层）。

### Added
- **`scripts/health_check.py`** (379 行)：13 项检查（frontmatter YAML、name 规范、LOGO 路径解析、核心文件存在、`templates/` 是否清掉、components.css 关键 class）。支持 ANSI 颜色 + Windows GBK 自动降级。`exit 1` if any FAIL。
- **`references/visual-evolution.md`** (401 行)：完整视觉系统演进史。
- **`references/examples/README.md`**：说明 examples/ 用途。
- **`scripts/README.md`**：脚本索引。
- **`VERSION`** 文件 + **`CHANGELOG.md`**：版本号文件级可见。

### Engineering Notes
根本原因：之前每次都从含完整 `_shared/` 的工作目录运行，从没把 skill 当作"fresh install 要能跑"测试。本版加 `health_check.py` 后未来不会再翻车。

---

## [4.3.3] — 2026-05-20 · 稀疏页垂直居中

### Added
- **`.slide.center-y`** 修饰类：单页内容显著少于半页时（目录/单引用/单图大版式），自动垂直居中到飘带下方可用空间。
- **`.body-center`** 包装器：多块内容一起居中。
- **`template/demo-toc-center.html`**：可运行参考。

与 `.compact` 形成反向对称（compact 救溢出 / center-y 救空旷）。

---

## [4.3.2] — 2026-05-20 · 双栏对齐铁律

### Fixed
双栏 grid 布局两栏底部不对齐，含大图时反向把整个 grid 撑高溢出。根因：默认 `grid-template-rows: max-content`。

### Required (装配规范)
- `grid-template-rows: 1fr`（行高 = 容器高）
- `min-height: 0`（允许在 flex 父里压缩）
- 图片用 `width:100%; height:100%; object-fit: contain`，禁用绝对 `max-height`

---

## [4.3.1] — 2026-05-20 · 密集页变体

### Added
- **`.slide.compact`** 修饰类：长 deck（25+ 页）或密集单页装不下 720px 时使用。字号统一压 1-2pt（key-point 15→13、卡片正文 13.5→12 等），同步缩 padding。投屏底线保持（最小 12pt）。

---

## [4.3.0] — 2026-05-20 · 字号体系投屏可读

### Changed
- **theme.css 字号体系整体上调**（按"会议室投屏 5-10m 视距"标准）：
  - 正文 12pt → **14pt** (+17%)
  - 卡片正文 11pt → **13pt** (+18%)
  - 说明/标签 10pt → **12pt** (+20%)
  - 数据来源 9pt → **11pt** (+22%)
  - 页面标题 22pt → **24pt**
  - 章节标题 32pt → **34pt**
  - 封面标题 36pt → **38pt**
- components.css 同步所有硬编码 pt 值。
- 大数字（46/56/170pt）保持。

### Fixed
- 红绿飘带拉伸掉色（移除 `.page-wave opacity: 0.6` + 内页 PNG Lanczos 上采样到 2400×75）。

---

## [4.2.0] — 2026-05-19 · P1 局部升级

### Added
- **Double-rule 双线装饰**（用于章节扉页 section-label）。

### Removed
- 封面 masthead（装饰过度）
- 内页右上 meta（与飘带/章节扉页/页码重复）

---

## [4.1.0] — 2026-05-19 · P0 五件套（借鉴反思）

### Added
- 品牌色透明度阶梯（16 变量：`--red-04 / --red-08 / --red-15 / --red-20` 等）
- 暖中性灰 `--warm-taupe: #8A8178`
- 衬线字体栈（`--font-cn-editorial`），仅用于落款/金句/数字单位的"语义重音"
- **`.auto-list`** CSS counter 自动编号（橙红绿深蓝四色循环）
- **`.key-quote`** 关键引言卡片（衬线 + 半透明品牌底）

### Removed
- Eyebrow Kicker 默认使用（与集团飘带重复）

---

## [4.0.0] — 2026-05-19 · 视觉系统重构

### Changed
- 整体设计语言：纯白底 + hairline + 大字号 + 极细字重 + 微阴影
- 取消米色背景、深绿色块等"党政标语感"装饰
- 参考调性：Stripe / Apple Newsroom / 麦肯锡现代报告
