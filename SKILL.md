---
name: spic-ppt
version: 4.11.0
description: >-
  Use when the user has an existing research report, outline, or written
  manuscript and wants to convert it into a polished HTML+PDF presentation deck
  (default output) following 国家电投 (SPIC) VI conventions. Triggers include
  "做演示文稿"、"做PPT"、"做汇报"、"出一份汇报材料"、"做成PPT"、
  "把这份报告做成幻灯片"、"经研院汇报"、"集团汇报"、"研究成果汇报"、
  "专题汇报"、"上级单位汇报"、"按工作流做PPT". This skill assumes the user has
  already completed the research/thinking phase and provides finished content;
  the AI's job is visual assembly, not content generation. Skip this skill when
  starting a new research project from scratch (use full-research instead),
  for simple one-page slides, or for party-political lectures (use the
  dedicated party-class workflow). If the user explicitly asks for a
  PowerPoint .pptx deliverable, switch to the pptx skill instead.
---

# 国家电投演示文稿设计制作工作流

## 核心定位（先想清楚）

**PPT 工作流是视觉装配流水线，不是内容生成器。**

```
研究阶段（用户做）→ 形成报告/大纲 → PPT 工作流（你做装配）
```

用户的核心价值在研究阶段已经发挥（形成判断和论点）。你在这里的核心价值是：**读懂成稿 → 结构化抽取 → 版式适配 → 标准模板装配**。

工作流的工时目标是 **40-60 分钟**（一份 20-30 页的标准汇报）。如果超过 90 分钟，说明流程跑错了。

---

## 启动检查清单

接到任务时，立即检查用户带了什么：

| 必须确认 | 形态 | 缺则要主动问 |
|---|---|---|
| **主输入** | 完整成稿（报告/大纲/.docx/.md） | 问"成稿在哪？" |
| **用途** | 宣讲/讲课/存底/审核/印刷 | 问"PPT 是用来现场宣讲、讲课培训、存底备查，还是上级单位审核？" |
| **时长** | XX 分钟 | 问"讲多长时间？" |
| **听众** | 谁、什么级别 | 问"听众是？" |
| **风格** | 标准汇报/学术分享/对外发布 | 问"按经研院标准汇报风格做？" |

**关键原则**：4 个约束一次问清，**不要分多轮问**（用 AskUserQuestion 一次提交多个问题）。

**用途差异（影响版式节奏）**：
- **汇报/审核**：信息密度高、重结论先行，单页可上双栏+数据墙，0.5-1 页/分钟。
- **讲课/培训**：重展开与节奏，单页只承载 1 个知识点，多用 `.center-y` 单图/单金句页，配图和示意图比例更高，节奏放慢到 1.5-2 页/分钟。讲课指业务/知识讲授；党课党建走专门工作流，不在此。

**反模式警告**：
- 不要让用户重新提炼论点——你应该自己读成稿
- 不要让用户画大纲——你应该从成稿抽取
- 不要让用户指定版式——你按内容性质推荐版式
- 不要让用户指定页数——按时长算（0.5-1 页/分钟）

---

## 工作流八阶段（完整执行）

### 第一阶段 · 接收任务 + 接收成稿
- 用 AskUserQuestion 一次问清 4 个约束（用途/时长/听众/风格）
- 接收成稿（用户给路径，你用 Read/Bash 工具读）
- 不必再问"讲者已有思路吗？"——成稿就是答案

### 第二阶段 · 读懂成稿 + 提取图片 + 权威文本补充

**核心原则**：原报告里的图是**潜在的素材库**，提取后让 AI 在第三阶段判断每张是否值得复用。

**子任务 A · 提取图片**（如成稿是 docx/pptx/pdf）：

```bash
python scripts/extract_images.py <成稿路径> _images/extracted
```

支持的格式：
- `.docx` / `.pptx` → 从 zip 包的 `word/media/` 或 `ppt/media/` 抽取
- `.pdf` → 用 PyMuPDF 提取内嵌图片（不处理矢量图表）（依赖 `pip install pymupdf`）

脚本输出：
- `_images/extracted/image_NN.png/.jpg/.jpeg` —— 所有可复用图片
- `_images/extracted/manifest.md` —— 图片清单（来源+尺寸+上下文）

**子任务 B · 通读成稿**：
- 识别三类内容：**判断/论点**、**支撑数据/引用**、**过渡内容**
- 同时建立"图片-内容映射"——哪张图配哪段文字（用 manifest.md 的上下文做线索）

**子任务 C · 权威文本补充**（如成稿引用党政文件）：
- 用 WebSearch + WebFetch 抓取权威原文做校对
- 权威源：news.cn（新华社）、gov.cn（中国政府网）、npc.gov.cn（人大网）、12371.cn（共产党员网）
- 输出 `_extracted/权威原文汇编.md`

**输出**：
- `_images/extracted/` —— 可复用图片+清单
- `_extracted/权威原文汇编.md` —— 如有引用
- 一份"我读到的成稿结构理解"让用户校对

### 第三阶段 · 结构化抽取 + 版式适配建议
**这是 v2 的核心阶段**。

写一份 `结构抽取_V1.md`，对每页给出：
- 页面标题（用户原文或抽取）
- 版式建议（从标准模板的 10 种版式中选）
- 核心论点（保留用户原文，不要替换措辞）
- 关键数据/引用
- **图片资源决策**：对每页需要图的位置做三选一决策：
   1. 复用原图：注明 `_images/extracted/image_NN.png`
   2. 重画/换图：注明"建议用 [CSS/SVG/Mermaid] 重做，或请用户提供新图"，并说明理由（原图分辨率低/风格不符/信息过时/需精简）
   3. 明确缺图：注明"此处需补图：[图的类型和内容描述]"——让用户在审定阶段决定如何补
- 建议略去的内容

同时给出整体取舍建议：
- 必讲：[报告第 X 章]
- 略讲：[报告第 Y 章]
- 不进 PPT：[附录、过渡章节]

**等用户审定**后再进入下一阶段。

### 第四阶段 · 技术选型
**默认 HTML+CSS+PDF**（覆盖 90% 场景，特别是经研院汇报）

例外：
- 后续需要 PowerPoint 协作修改 → 选 pptx
- 每月跑一次的数据驱动报表 → 选 python-pptx

### 第五阶段 · HTML 装配
**使用 `template/` 目录下的标准模板**。

装配步骤：
1. 复制 `template/template.html` 到项目目录作为骨架
2. 按结构抽取的页面顺序复制 `<section>` 块
3. 每页套用对应的主体版式（10 种版式见 sample-pages.html）
4. 关键论点用 `class="key-point"`（v4 hairline+左红条+小标签+图标）
5. 关键数据用 `<span class="accent">XX</span>` 染红
6. 含数据的页加 `<div class="data-source">数据来源：...</div>`
7. **按第三阶段决策装配图片**（不是一刀切复用，也不是一刀切重画）：
   - **复用原图**（最常见）：
     ```html
     <div class="chart-frame">
       <img src="_images/extracted/image_NN.png" style="width:100%;object-fit:contain;" alt="">
     </div>
     <div class="chart-caption">图表标题</div>
     ```
   - **重画/换图**：用 CSS/SVG/Mermaid 做简化版示意图；或在结构抽取里写明"建议用户提供 XX 新图"
   - **明确占位**：在结构抽取文档里**明确告诉用户**"P3 此处需补图：XX 类型"——不要在 HTML 里塞占位框假装完成

**铁律**：不要发明新版式。10 种现成版式已覆盖所有典型场景。
**铁律**：图片处理的判断逻辑——是复用、重画还是空着，要在第三阶段就明确告诉用户，不能装作完成了。

**视觉饱满**（撑满版面是你自带的能力，这里只给数值锚点）：下方留白 > 25% 即空洞，需撑满——主体用 `flex:1` + `justify-content:space-around` 铺满全高；卡片 `min-height:220-240px`、数据墙 `200px+`、列表项 `60pt+`；内容实在少时改用 `.center-y`（见下），不要靠"留白美学"糊弄。

**v4 视觉语言一句话**：纯白底 + hairline 边框 + 微阴影 + 大字号极细字重 + 品牌色 ≤20% 点缀；不要深色块/重底色（党政标语感）。完整设计要点（色值、字重、章节扉页、避免的旧版错误）见 **[references/visual-evolution.md](references/visual-evolution.md) · v4 视觉系统核心要点**——装配时若拿不准某个视觉细节，去那里查，不要在此重述。

---

### v4.x 视觉系统铁律 · 装配前必读

视觉系统演进与所有装配铁律详见 **[references/visual-evolution.md](references/visual-evolution.md)**

核心要点速查（装配 PPT 时一定要参照）：

| 维度 | 关键规则 | 详情 |
|---|---|---|
| **字号体系** | 投屏可读：正文 14pt / 标签 12pt / 来源 11pt 起步，禁止再缩 | v4.3 节 |
| **密集页救援** | 内容装不下 720px → 加 `class="slide compact"` | v4.3.1 节 |
| **稀疏页救援** | 目录/单引用等内容少于半页 → 加 `class="slide center-y"` | v4.3.3 节 |
| **双栏对齐** | 直接用 `<div class="body-grid">`（对齐已焊进 CSS：等高、底对齐，**不要再手写 grid**）；偏比例用 `.body-grid.cols-1-2` / `.cols-2-1` | v4.6 节 |
| **图表容器** | 图直接放 `<div class="chart-frame"><img></div>`（已焊 `max-height:100%`+`object-fit:contain`，竖高图不撑破、不变形） | v4.6 节 |
| **保留 vs 替换** | 字体/配色/装饰元素不能改；标题/正文/数据必须替换 demo | "v4 装配铁律" 节 |
| **不要现代化** | v4 视觉系统已稳定，不要主动"优化"模板（仅用户明确说才改） | "Don't modernize" 节 |

**核心规则速记**：
- 字号铁律：正文最小 13pt，投屏不可读 = 失败
- 装不下 → 加 `.compact`，不要缩字号；放不满 → 加 `.center-y`，不要拉伸
- 借鉴外部技巧前先问"它要解决什么问题"——我们用集团飘带+章节扉页+页码已经解决了 80% 的视觉问题

#### `.compact`（密集页）/ `.center-y`（稀疏页）何时加

**判断交给你自己**：内容明显塞不下 720px → 加 `class="slide compact"`；明显少于半页 → 加 `class="slide center-y"`。不必死记阈值——第七阶段 `check_overflow.py` 会实测兜底，真溢出了再补 `.compact` 也来得及。

经验阈值（拿不准时参考，非硬性）：
- `.compact`：编号点列 ≥5 项 / 时间线 ≥5 步 / key-point ≥80 字 / 单页 4+ 个组件块同框
- `.center-y`：目录页、单金句页、单大图、只有 1-2 个 metric 的数据墙

### 第六阶段 · 质量校验（双轨）

**校验 1 · AI 独立校验**（用 subagent）：
```
任务：把PPT中每条原文引用与权威原文汇编逐字比对
输出：差异清单 + 严重程度（高/中/低）
```

**校验 2 · 人工审定**——你提示用户检查：
- 政治表述合规性
- 内部口径（数字、表述）
- 保密边界

校验点清单：
- 党政文件引用完整准确（定语别漏，如"显著""基本""加快""全面"）
- 数字准确（百分比、亿元、装机量）
- 节选必须加省略号
- 引用归属清晰

### 第七阶段 · 导出闸门（自检已焊进导出）→ 反向验证

**步骤 1 · 用导出闸门导 PDF（不要再手敲 chrome 命令）**：
```bash
python scripts/build_pdf.py "C:\absolute\path\成品PPT.html"
```
- `build_pdf.py` **先跑溢出自检，任一页溢出就拒绝导出**并列出该改哪页；全过才导 PDF。
- 这把"自检"从"请 AI 记得跑"变成"结构上跳不过"——过去溢出反复交付的根因就是 AI 装配时忘了跑 check_overflow（实测：有成品 0 处 compact、带 2 页溢出直接交付）。
- 闸门用的就是 check_overflow（`.slide` 的 `overflow:hidden` 会把溢出静默裁掉，PNG 看不出来，所以必须实测 DOM）。

**若被拦截（按既定策略修，不要缩字号）**：
1. 未加 compact 的溢出页 → 加 `class="slide compact"`，重跑
2. 已是 compact 仍溢出 = 内容超量 → **保持一页、删掉最长项**（或拆两页，你定），重跑
3. **禁招**：缩字号——投屏会看不清
4. 确需带溢出交付 → 加 `--force` 显式放行（你看过提示后自己拍板）

> 单独跑自检（不导出）仍可用：`python scripts/check_overflow.py 成品PPT.html`
> 单页几何护栏（字号<8pt / 元素出血）：`python scripts/check_geometry.py 成品PPT.html`

> **维护者注**：改动 `theme.css` / `components.css` 后，跑 `python scripts/eval_suite.py` 做回归——它用三个固定输入（两样板覆盖 17 版式 + 魔鬼样本）自动确认"版式没退化、护栏仍灵敏"，把"改完靠人工渲染验收"变成"脚本判对错"。装配单份 PPT 时不需要跑它，这是维护 skill 本身时用的。

**步骤 3 · 反向验证（导 PNG 抽样肉眼检）**：
```python
import fitz
doc = fitz.open('output.pdf')
# 至少看：封面 + 章节扉页 + 任意 3 个内页 + 尾页
for idx in [0, len(doc)//4, len(doc)//2, 3*len(doc)//4, len(doc)-1]:
    pix = doc[idx].get_pixmap(matrix=fitz.Matrix(1.2, 1.2))
    pix.save(f'_preview/p{idx+1:02d}.png')
```
用 Read 工具看每张 PNG，检查字体显示、配色、对齐细节（溢出已在步骤 1 排除）。

### 第八阶段 · 归档与交付

```
项目目录/
├── 成品PPT.html              # 编辑用（依赖 css/图片）
├── 成品PPT.pdf               # 交付物①：打印/正式存档
├── 成品PPT.standalone.html   # 交付物②：自包含单文件（自动产出，见下）
├── 结构抽取_V2.md
├── _extracted/                # 权威原文汇编（如有）
├── _preview/                  # 抽样PNG（验证用）
└── _versions/                 # 历史版本快照（自动留底，见下）
```

**单文件交付（自动）**：`build_pdf.py` 导出 PDF 后会顺带产出 `成品PPT.standalone.html`——CSS 与图片全部内联（base64），**一个文件、双击即开、可邮件直发**，VI 与原版完全一致。发给别人/在线看用这一份；继续编辑仍用原 `成品PPT.html`（带依赖）。不需要时加 `--no-standalone` 跳过。注：单文件含 base64 图片，体积比原 HTML 大（标准模板约几 MB），属正常。

**版本留底（自动，无需操心）**：每次用 `build_pdf.py` 导出前，会自动把上一版 `成品PPT.html` 和 `成品PPT.pdf` 复制进 `_versions/`，命名带秒级时间戳（如 `成品PPT_20260605-143012.html`）。

**找回旧版**：直接打开 `_versions/` 里对应时间戳的文件（浏览器/WPS 看 HTML，双击看 PDF）。要把某旧版变回当前版，复制出来改回 `成品PPT.html` 即可。中间编辑不快照——只有"导出"才是一个值得留的版本。

---

## 五条铁律

1. **LOGO 绝不自制**——党徽、企业 LOGO 必须从 `shared/logos/` 调用，不能自己画 SVG
2. **党政文件引用必须从官方源抓取**——不能凭记忆、不能用二手解读
3. **AI 做减法不做加法**——保留用户核心表述原文，**绝不"补充新观点"**。模型越强越容易"热心帮忙"自动扩写论点、补数据、加案例——这恰恰是越界：用户的判断在研究阶段已定稿，你越权改的是他的研究结论。拿不准某句是否该精简时，宁可原样保留，让用户自己删。
4. **进入 PPT 工作流后不改研究内容**——发现研究问题→退回研究阶段重做
5. **图片处理要有判断力**——对每张图做三选一决策：
   - **复用**（默认）：原图合适 → 用 `<img src="_images/extracted/image_NN.png">` 引用
   - **重画/换图**：原图分辨率太低、风格不符、信息过时、需要为新听众精简 → 用 CSS/SVG 重做，或建议用户提供新图
   - **明确占位**：暂时没合适素材 → 用占位框 + 在结构抽取文档里**明确告诉用户"此处需补图"**
   - **禁止**：用 `[XX图表]` 这种空占位糊弄装完成

---

## 标准模板的 17 种版式

详见 `template/sample-pages.html`（01-10 基础版式）+ `template/_layout-demo.html`（11-17 第二代破三明治版式）：

**基础版式（01-10）**

| 编号 | 版式 | 适用场景 |
|---|---|---|
| 01 | 封面（集团固定款大波浪） | 标准开场 |
| 02 | 章节分隔页（大数字+章节标题） | 板块切换 |
| 03 | 双栏图表+表格 | 数据对比 |
| 04 | 全宽图表 | 单一核心趋势 |
| 05 | 编号点列 | 4 项要点论述 |
| 06 | 数据指标墙（4 个大数字） | 量化目标展示 |
| 07 | 三栏卡片（橙红绿编号） | 三大要点/三步走 |
| 08 | 时间线（带箭头） | 战略演进、规划路径 |
| 09 | 双栏文字结论 | 研究结论+启示对照 |
| 10 | 尾页（机构署名 + 飘带） | 标准收尾 |

**第二代版式（11-17 · 破三明治横向构图，class 见 components.css v4.10 段）**

| 编号 | 版式 | class | 适用场景 |
|---|---|---|---|
| 11 | 四宫格（2×2 等高卡，左色条+序号） | `.quad-grid`/`.quad-card` | 4 个并列要点，替代纵向列表 |
| 12 | 横向流程节点带（›箭头自动连接） | `.flow-row`/`.flow-node` | 多步流程/工作流（无时间属性，区别于时间线 08） |
| 13 | 验证对比+纯CSS条形图（删除线→真相） | `.verify-row`+`.mh-rows` | 前后对比、数据打假、趋势崩塌 |
| 14 | 红黄绿三栏（交通灯分级） | `.traffic`/`.tf` | 安全/风险/底线三档分级 |
| 15 | 组织架构（一行部门卡，.me 高亮自身） | `.dept-row`/`.dept` | 机构介绍从大到小、定位到我 |
| 16 | 外部机构 logo 墙 | `.logo-wall`/`.lw-grid` | 权威客户背书（比文字名单有力） |
| 17 | 产品截图框（浏览器chrome，cover铺满） | `.shot-frame` | 真实产品界面（区别于图表 chart-frame 的 contain） |

**标题区三件套**（`.head-block`：眉标+大标题+导语带 `.hl` 红高亮）是 11-17 的共享标题骨架，连续叙事场景比标准 title-row 更克制。

## 视觉系统速查

**配色**（来自 SPIC ETRC LOGO 双螺旋 + 集团参考PPT惯例；**真相源是 `template/theme.css` 的 CSS 变量**，下表仅为装配速查，若与 theme.css 不一致以 theme.css 为准）：
- 品牌深蓝 `#00005A` — 封面主标题
- 品牌红 `#D20000` — 章节大数字
- 品牌绿 `#3C961E` — 虚线框/边框
- 品牌橙 `#F07800` — 编号
- 品牌嫩绿 `#78B41E` — 装饰
- 关键强调红 `#C00000` — 文内关键数据染色
- 浅深蓝 `#1B3C6E` — 页面标题

**字体**：
- 中文：微软雅黑（VI 强制规范）
- 西文/数字：Arial

**LOGO 调用**：
- 标准汇报 → `shared/logos/etrc/etrc-logo.png`（封面 + 内页右上）
- 党课党建 → `shared/logos/party/` + `shared/logos/etrc/`
- 对外大场合 → 加 `shared/logos/spic/color/preferred-short-horizontal.png`

## 集团固定款波浪条（关键视觉元素）

**必用文件**：
- 封面：`template/_assets/wave-cover-plain.png`
- 内页标题下分割线：`template/_assets/wave-inner.png`

**铁律**：飘带是集团固定款，封面和内页都要保留，不能省。

---

## 详细工作流文档

更深入的解释见同目录下：
- [task-input-checklist.md](task-input-checklist.md) — 用户启动前应该做的准备
- [workflow-sop.md](workflow-sop.md) — 八阶段完整SOP

## 模板文档

- [template/README.md](template/README.md) — 标准模板的使用说明
- [shared/logos/README.md](shared/logos/README.md) — LOGO 选用决策树
