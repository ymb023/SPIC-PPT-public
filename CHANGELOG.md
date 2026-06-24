# Changelog

所有重要的版本变更记录于此。版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

---

## [4.11.3] — 2026-06-22 · 架构清理（/simplify 四维审查后）

4 个并行 agent 按 reuse/simplification/efficiency/altitude 审了 skill 架构。采纳低风险高确定项，验证后剔除多个 agent 误报，最大的重构项明确推迟。

### Removed / Cleaned
- 删 `template/visual-upgrade-demo.html`（1072 行，0 引用，v4.2 废弃的设计预览迭代）。
- 删 components.css 里孤儿 `.title-row .meta` 规则——其唯一用法已在 v4.11.2 禁止（会盖右上 LOGO），留着 CSS 等于为禁用模式保留样式、误导维护。换成一行说明注释。

### Changed
- **版本一致性检查扩到 4 处**：health_check 的 `check_version_consistency` 加 components.css 顶注（原只查 VERSION/SKILL.md/README 三处）。上线即抓出真漂移——css 顶注停在 v4.11.0、落后 skill 两个版本。这正是该检查的价值：人工维护的注释版本号必漏，焊进自检才可靠。

### 审查结论（剔除的误报 + 推迟项，记录判断）
- **剔除（验证为误报/会破坏）**：删 design-spec-summary.md（被 2 个 README 引用，删=文档漂移）；删 .eyebrow/.eyebrow-cn（visual-evolution 明确"保留备特殊场景"）；抽 ANSI 颜色到共享模块（28 行永不变的常量，新增依赖不值）。
- **推迟（价值最高但太重，留待专门 TDD）**：统一 check_overflow/check_geometry 的 Chrome 渲染骨架 + build_pdf 合并两次 Chrome 启动为一次（reuse/efficiency/altitude 三个 agent 都指向它，省每次导出 2-4 秒）。它动的是所有检查依赖的核心，不能在无人值守的清理 pass 里盲改——需独立 RED/GREEN。已记为下一个候选。

## [4.11.2] — 2026-06-22 · 复用旧页三连：默认保留 + 页码检查 + 内页 meta 修复

一份真实拼装+重绘成品（算电协同，旧页粘进来风格不一致、重绘后图文混排乱）暴露的三个问题，依次解决。第 1 个是机制升级（探讨认可后实现），2/3 是确定性修复。

### Added
- **复用旧 PPT 页：先诊断、默认保留（换皮不换骨）**（SKILL.md 第三阶段新增专节）。核心是翻转默认姿态——**旧页往往精心排过，不默认整页重绘**。复用旧页必须先出"旧页诊断"（原布局/排版评价/图性质/建议动作三选一+理由）给用户审定，再动手。三档动作：最小换皮（只改 VI 层，布局原样）/ 保骨换图（布局留、数据图重画）/ 真重绘（排版不行才用标准版式）。皮=配色字体LOGO飘带，骨=图文结构布局，非必要不动骨。解决"复用旧页重绘排版乱、丢原布局"的根因：AI 跳过了"先理解旧页值不值得保留"直接重绘。
- **页码连续性检查**（焊进 check_geometry）：采集每页 `.page-no/.page-num/.page-footer` 数字，验证有页码的页序列严格 +1，抓重号/跳号/串号（插页后高发）。封面/扉页无页码不强求。纯函数 `page_number_issues` 单测 5/5。eval_suite 的 geometry 判定纳入页码项。

### Fixed
- **内页模板右上 meta 盖 LOGO**：`template.html` 内页模板 title-row 残留 `<div class="meta">第 X 部分 · 02</div>`——visual-evolution.md 早写明 v4.2 已移除（会贴 LOGO、是章节信息第四次重复），但模板没删干净。删除该行+同步注释。章节扉页 `.section-divider .section-right .meta`（右侧量化指标墙，不碰 logo）合法保留。

### Engineering Notes
- 设计纪律复盘：第 1 个问题（旧页诊断）经"brainstorm 探讨 → 用户认可设计 → 才实现"全流程，未在探讨阶段擅自动手。
- 回归：页码单测 5/5、两样板 check_geometry 全过（含页码项）、eval_suite/health_check 全绿、无 SyntaxWarning。

## [4.11.1] — 2026-06-17 · 外部审计修正（Codex 审计 · 采纳真 bug、剔除平台错位）

Codex 审计了一次，跑通 health_check(18/18) 和 eval_suite。其结论"能力内核强、改进空间在包装一致性"基本属实，但有**平台错位**：它拿 Codex 规范量这个 Claude Code skill（要求挪 version 字段、改平台中性口径、统一到 .codex/skills）——这些对 Codex 对、对我们不对，**未采纳**（我们运行时就是 Claude Code）。采纳了三条与平台无关的真 bug：

### Fixed
- **README 断链**：`templates/sample-preview.pdf` → `template/sample-preview.pdf`（少个目录名错，markdown 链接检查的唯一断链）。顺带修目录树里的 `templates/` 旧名、补 `_layout-demo.html`/`_eval/` 条目、版式数 10→17。
- **check_geometry.py 头部文档与代码矛盾**：文档头还写"字号<14pt"，实际阈值 `MIN_PT=8.0`（上一版降阈值时漏改头部）。同步成 8pt 逻辑，避免维护误判。

### Changed
- **几何护栏焊进 build_pdf 导出闸门（只警告不阻断）**：导出时顺带跑 check_geometry，字号<8pt/出血打印 `[geom warn]` 但不拒绝导出。理由：溢出是零误报硬红线→拒绝导出；几何护栏对某些合法装饰定位可能误报→只提示、判断权留人。把护栏从"记得单独跑"挂进主流程，又不会因误报卡住真实交付。验证：魔鬼样本导出时正确警告 2 处（6pt+右出血）且仍成功导出。

### 未采纳（平台错位，记录备查）
- "version 不是合法 frontmatter 字段"=Codex 规范，Claude Code 无此限制；version 留 frontmatter 与 VERSION/README 三处一致（health_check 已守此一致性）。
- "统一到 .codex/skills/、改平台中性口径、清理 deck-craft 别名"=按 Codex 个人 skill 管的思路；我们主线是 Claude Code skill，SKILL.md 用 Claude 工具名（AskUserQuestion/Read/Bash）是正确的。deck-craft 是 Codex 侧自装别名，非本仓库产物。

## [4.11.0] — 2026-06-17 · 机器评测套件：把"人工渲染验收"变成"脚本判对错"

竞品调研（2026-06-17）的落地。调研结论：SPIC-PPT 在"工程闸门"和"路线判断"上已领先同类（reveal.js 承认垂直溢出无法自动解决、frontend-slides 等同类无任何质检），落后的不是方向是"密度"——确定性脚本管可量化项这条路只做了"溢出"一个点。本版把它从一个点铺成一张网。

### Added
- **`check_geometry.py` 几何护栏**：在溢出检查之外新增两项可量化检查——① 字号<8pt（投屏"真看不清"绝对红线）② 元素出血（左/右/上越界）。复用 check_overflow 的 Chrome headless 注入机制，零新依赖。
- **`eval_suite.py` 回归评测套件**：三个固定输入（sample-pages 10版式 + _layout-demo 7版式 + 魔鬼样本）一键跑全套。两样板期望全过（版式不退化），魔鬼样本期望按预定报违规（护栏灵敏）。**改 theme/components.css 后跑一次，自动确认 17 版式没退化、护栏没失灵**——这是 Anthropic 官方"可重放评测是 skill 有效性唯一真相来源"的落地。
- **`template/_eval/stress-test.html` 魔鬼样本**：护栏的"反向夹具"，三页各故意触发一类违规（底部溢出/字号6pt/右出血），验证护栏真能抓到。

### 关键设计判断
- **字号红线定 8pt 不是 14pt**：theme.css 字号是分级的（正文14/小正文13/标签12/来源11，全合法）。靠 class 名猜"是不是正文"永远猜不准、会把合法小字误报成违规沦为噪音。所以只守"任何文本<8pt=真事故"这条谁都不争议的绝对线，标签/说明小字的合规交回人眼审美。**宁可少而准，不要多而嘘**——这是调研里"误报多了就会被忽略"教训的直接应用。
- **不做 SSIM 渲染基线比对**：变化检测≠对错判定，任何有意改版式都会让 SSIM 漂移→沦为噪音。护栏（对错）+ 魔鬼样本（灵敏度）已够。
- **明确不学的陷阱**：AI 端到端生成内容、引入框架、整页自适应缩放、跨 runtime 通用化、VLM 审美打分、开放模板生态——全是为"让任意人生成任意风格"设计，与我们"锁定央企VI+只装配不创作"方向相反，跟了就自废武功。

### Changed
- `health_check.py`：core_files 登记 4 个新文件（check_geometry/eval_suite/_layout-demo/stress-test）。
- `SKILL.md` 第七阶段：加 check_geometry 单独用法 + 维护者注（改 CSS 后跑 eval_suite）。
- `components.css` 顶注 v4.10.0 → v4.11.0。

### Engineering Notes
- TDD：check_geometry 先 RED（导入失败）→ 实现 → GREEN（7/7：字号/出血/白名单/正常各向）。
- 评测发现的真问题：初版字号线定 14pt，跑 sample-pages 报 9/10 页"违规"——评测自己抓出了"阈值定错"的设计 bug，降到 8pt 后两样板全过、魔鬼样本仍被抓。**评测上线第一件事就是证明了自己有用。**

## [4.10.0] — 2026-06-15 · 第二代版式扩容：10 种 → 17 种（破三明治）

用户最初痛点"单页排版太拥挤、太刻板的三明治结构"的正面解药。从苏州讲坛成品逆向提炼 7 种横向/网格构图，渲染样张经用户审美验收后焊入。规则劝不动结构，新版式才能换掉结构。

### Added（components.css v4.10 段，7 个新版式 + 标题区三件套）
- **11 四宫格** `.quad-grid`：2×2 等高卡、左色条+四色序号，替代纵向列表流水账（最高频）。
- **12 横向流程** `.flow-row`：N 节点等宽、伪元素 `›` 自动连接，表线性流程（无时间属性，区别于时间线 08）。
- **13 验证对比** `.verify-row`+`.mh-rows`：AI初判删除线 → 纯 CSS 逐年条形图，"断崖式可视化 >> 糊截图"。
- **14 红黄绿三栏** `.traffic`：交通灯圆点分级，表安全/风险/底线三档。
- **15 组织架构** `.dept-row`：一行部门卡、`.me` 红框高亮自身，机构介绍从大到小定位到我。
- **16 logo 墙** `.logo-wall`：外部机构背书，比文字客户名单有力。
- **17 产品截图框** `.shot-frame`：浏览器 chrome 窗口 + `object-fit:cover` 铺满，真实界面"真在用"证据。**与 `.chart-frame`（contain，数据图不裁切）双轨并存，按图性质二选一**。
- **标题区三件套** `.head-block`（眉标+大标题+导语带 `.hl` 红高亮）：11-17 共享标题骨架，连续叙事比 title-row 更克制。

### Changed
- `SKILL.md` 版式表 10 种 → 17 种，第二代版式标注 class 与适用场景。
- `template/_layout-demo.html`：7 版式的范例 demo（供装配参考）。
- `components.css` 顶注版本回填 v4.6.1 → v4.10.0（修历史脱节）。

### 质量纪律
- 全部只用 `:root` 现有变量（橙红绿蓝四色、`--fw-*`、`--font-*`），零新增色值——受 visual-evolution「新版式沿用清单」约束，让人认不出是新版式。
- 均为新增类、不改既有组件——符合「Don't modernize」（属"内容性质确需新版式"的正当扩充，连续叙事场景 10 种覆盖不到）。
- **眼见为实验收**：7 版式做成 demo 渲染 PNG 经用户逐张审美确认后才焊；焊后又脱离内联 CSS 独立渲染回归（6/6 界内），证明 components.css 焊接正确。

## [4.9.0] — 2026-06-15 · 单文件 HTML 交付（导出顺带产自包含 standalone）

用户痛点：导出的 HTML 依赖一堆外部文件（css/波浪条/logo/抽取图），脱离工作目录就是裸页，没法单独分享。交付一份 PPT，对方该收到一个文件不是一个文件夹。

### Added
- **`scripts/inline_html.py`**：把 HTML 的外部 CSS（→`<style>`）和本地图片（→base64 data URI）全部内联，产出自包含单文件 `<stem>.standalone.html`，双击即开、可邮件直发、VI 与原版一致。CSS 内 `url()` 一并内联；远程/已 data 引用幂等跳过；缺失图警告不崩。
- **接入 build_pdf 导出闸门**：导出 PDF 成功后顺带产出 standalone（`--no-standalone` 可跳过）；单文件失败不影响 PDF 主交付。一次导出得两种交付格式——PDF 打印存档、单文件分享在线看。
- **字体**：不嵌入，靠 font-family 回退链（交付环境基本 Windows，雅黑必装）。

### Changed
- `SKILL.md` 第八阶段归档目录加 `成品PPT.standalone.html` + 单文件交付说明。
- `health_check.py`：`iter_html_files` 跳过 `*.standalone.html`（交付物非源，不当成品扫）。

### Engineering Notes
- TDD：RED（inline_html 不存在）→ 实现 → GREEN（5/5：CSS内联/图base64/幂等/缺图不崩/重复图各自内联）。
- **眼见为实抓出真 bug**：曾试 `content:url()` 去重重复图（578KB 飘带×7次→省体积），测试 9/9 全过，但渲染验证发现 logo 被巨幅拉伸破版——`content:url()` 绕过 `<img>` 的 CSS 尺寸约束。**否决去重，保 `<img>` 语义零副作用**。这正是 skill 自身"渲染验证"铁律的价值：纯单测会放过这种 bug。
- 体积：不去重不换图，标准模板单文件约 6MB（高清飘带 base64×多次）；能邮件发（未超 25MB），用户选择不优化、保高清。

## [4.8.3] — 2026-06-15 · check_overflow 相对路径修复（苏州经验反哺·唯一进 skill 的一条）

苏州发改委讲坛积累了一份《通用工作手册》（266 行）+ 44 页成品。用两个 workflow 逐条比对手册 vs skill（36 条候选反哺），但工程上严格过滤——**只有 AI 真不知道、真踩坑、且属"装配层"的才进 skill，其余留手册**。最终只一条够格，且它是代码 bug 不是规则。

### Fixed
- **`check_overflow.py` 入口 `html_path.resolve()`**：相对路径 + 中文目录下，Chrome headless 解析 `file:///` URL 失败，导致闸门误报"找不到文件/溢出"（主目录 `D:/工作文件夹/...` 是中文路径，命中率极高）。脚本入口转绝对路径自行消化——**用 1 行代码消灭这个坑，而非在 SKILL.md 写"请记得用绝对路径"**（能用代码消灭的 gotcha 不留成规则）。
- 回归：相对/绝对路径均 exit 0；health_check 14/14；build_pdf import 正常。

### 反哺取舍（记录工程判断，避免 skill 越堆越臭长）
- **砍掉不进 skill**：屏=判断/口语回逐字稿、政治话语暗线、机构介绍从大到小、复用成熟金句、合规红线（绝对化/攀附/数字三要素）——这些是**讲者/内容层**经验，留《通用工作手册》，不污染装配层 skill。
- **防 subagent 注入**：评估后砍——skill 的 WebFetch 只抓政府官网（news.cn/gov.cn）核对引文，注入面极低，手册那条源自爬商业网页场景，不适用。
- **砍三明治/版式扩容**：留待后续版本，靠新增横向构图版式（quad-grid/flow-row 等）从结构上化解"刻板三明治"，而非加规则劝阻——规则劝不动结构，组件才能换结构。需渲样张确认观感后再焊。

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
