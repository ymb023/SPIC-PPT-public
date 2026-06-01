# SPIC-PPT 视觉系统演进与铁律

本文件记录 v4 → v4.3.3 的设计语言迭代过程、借鉴反思、三大铁律（.compact / .center-y / 双栏底部对齐），以及装配时"保留 vs 替换"的二元清单。

主 SKILL.md 只保留运行时速查；本文档供需要理解"为什么这么做"的场景查阅。

---

## v4 视觉系统核心要点（精致现代风 · 2026.5.19 升级）

**不要**用深色块/重底色（党政标语感），**要**用以下手法撑视觉：

- **纯白底**（VI 惯例 `#FFFFFF`）—— 不要米色不要浅灰
- **hairline 边框**（`1px solid #E8E8E8`）+ 微阴影 `0 4px 12px rgba(0,0,0,0.04)` → 白卡浮起来
- **大字号 + 极细字重**：章节大数字 170pt × `font-weight:100`；卡片编号 46pt × `font-weight:200` —— 视觉重量足够但不沉重
- **顶部 3px 细色线**做卡片识别（橙/红/绿），不用大色块填充
- **小标签丝带**：`<span class="key-point-tag">核 心 判 断</span>` 浅红底 + 红字 + 字间距 0.2em
- **章节分隔页**：左侧超大数字 + hairline 竖线 + 右侧标题/量化指标 + 左下浅红光晕装饰
- **图标用 SVG 线条**（stroke 1.6pt），不用粗实心徽章
- **品牌色比例 ≤ 20%**：大部分白底+黑字，只在关键位置用品牌色点缀
- **避免的旧版本错误**：
  - 纯白卡片只有描边、无阴影（v1 老版，显空洞）
  - 深绿全屏背景、大色块（v2 备选版，党政标语感）
  - 米色暖底（v3 备选版，与集团 VI 惯例有偏差）

**v4 设计语言一句话总结**：在保留集团波浪条+经研院LOGO 的 VI 基础上，用**纯白+hairline+大字号+极细字重+微阴影**做精致现代风的视觉表达，参考调性接近 Stripe / Apple Newsroom / 麦肯锡现代报告。

---

## v4.1 P0 五件套升级（2026.5.19 借鉴 beautiful-html-templates 升级）

借鉴 zarazhangrui/beautiful-html-templates 的 Blue Professional / Editorial Forest / Cartesian / Emerald Editorial 四个模板的共识技巧。

### 1. Eyebrow Kicker · 谨慎使用（不是 P0 必备）

```html
<!-- CSS class 保留，但默认不用 -->
<div class="eyebrow-cn">趋 势 研 判</div>
```

**重要认知校正**：4 个外部模板都用 eyebrow，是因为它们没有"VI 视觉锚点"——我们有**集团红绿飘带**作为标题→正文的固定分割线，**eyebrow 是冗余的"装饰复制"**。

**借鉴时的核心错误**：把外部模板的"共识技巧"当作"必须借鉴"——但要先识别"它要解决什么问题"。如果我们没那个问题，就不需要那个技巧。

**何时该用 eyebrow**：
- 章节扉页（section-divider 没有飘带）
- 特殊版式（如全宽图表页，飘带很细的情况）
- 不要加在标题区——会跟飘带形成"双标题区"重复

**推荐文案**：保留 CSS class 以备特殊场景，文案可用 `趋 势 研 判` / `数 据 洞 察` / `战 略 抓 手` / `核 心 判 断` 等。

### 2. 品牌色透明度阶梯 · 半色层次

```css
/* 已在 theme.css 定义，AI 装配时直接用 */
background: var(--red-08);   /* 浅红底卡片 */
border-left: 4px solid var(--brand-red);
color: var(--brand-red);     /* 文字保持原品牌色 */
```

每个品牌色都有 04/08/15/20 四档透明度。**用法**：卡片底、强调引用块、半透明强调。

### 3. 暖中性灰 #8A8178 · 研究院气质

```css
color: var(--warm-taupe);    /* 暖中性灰 */
```

适用：装饰线、小字标签、页码、数据来源标注、eyebrow 西文版。替代当前的冷灰 `#888888`。

### 4. CSS counter 自动编号 · auto-list

```html
<ol class="auto-list">
  <li>
    <span class="lead">要点标题</span>
    <span class="desc">描述。<span class="text-red">关键数据</span>高亮。</span>
  </li>
  ...
</ol>
```

自动渲染 01/02/03/04，配橙红绿深蓝四色循环。**改顺序不用手动改号**。

### 5. 衬线只做"语义重音" · key-quote 组件

```html
<!-- 党政原文引用 / 领导金句 / 政策文本 -->
<div class="key-quote">
  能源行业正在经历的不是周期性波动，而是结构性变革——能否准确识变、科学应变、主动求变，决定了未来五年的行业排位。
  <span class="quote-source">—— 国家电投党组2026年3月研讨班讲话</span>
</div>
```

.key-quote 自带衬线字体（思源宋体），视觉重量比 .key-point 更突出。**用于党政文件原文、领导讲话引用、政策文本**。变体：`.key-quote.is-green / .is-orange`。

**衬线字体使用原则**（重要）：
- 用于：落款署名、金句引用、数字单位（"亿元""%"）、章节扉页副标题
- 不要：全文用衬线（丢失信息密度感）、正文用衬线、标题改成衬线（央企汇报需要无衬线的现代感）
- **一句话原则**：无衬线扛信息密度，衬线扛人格重量

**v4.1 的高级感来源**（叠加 v4 已有的）：
- v4 基础：细 + 冷 + 锐（科技精致）
- v4.1 新增：透明度阶梯 + 暖中性灰 + 衬线语义重音 = 研究院判断权威感

**实测验证**：sample-pages.html 的 P5（auto-list 自动编号 + 四色循环）+ data-source 暖中性灰已经体现 v4.1 效果。

---

## 借鉴反思（v4.2 验证后总结）

借鉴外部模板技巧时**已经发生 3 次错误**，全部源自"看到好就借鉴"：

**错误 1 · Eyebrow Kicker（v4.1）**：4 个模板都用，我也加了。但我们有集团飘带做语义分割，eyebrow 重复了。已移除。

**错误 2 · 封面 Masthead（v4.2）**：Emerald Editorial 的"出版物封面"做法。但我们封面已经"干净有重量"（飘带+LOGO+大标题+副标题+汇报人），加 masthead 是装饰过度。已移除。

**错误 3 · 内页右上 meta（v4.2）**：Editorial Forest 的"第 X 部分 · 0X"右上 meta。但章节信息已经通过"集团飘带 + 章节分隔页 + 页码"三处传达，右上再加是第四次重复，且贴 LOGO 显得像标签。已移除。

**沉淀的判断准则**：
1. **借鉴前问"它要解决什么问题"**——不是看"它有什么"
2. **判断我们是否有这个问题**——我们有飘带、LOGO、章节扉页这些已经存在的视觉锚点，很多技巧的"问题"已经被我们的固有结构解决了
3. **借鉴后验证不冗余**——肉眼检查"它替代了什么 / 重复了什么"
4. **宁可少不可多**——"干净有重量"比"装饰得好"更接近经研院汇报调性

## v4.2 实际生效的 P1 只剩 1 件

- **Double-rule 双线** 用在章节扉页 section-label（替代浅红底标签）
- ~~Masthead 报头~~（封面装饰过度，已移除）
- ~~左边框引言卡片~~（在 P0 .key-quote 已实现，跳过）

---

## v4.3 字号体系 · 投屏可读（2026.5.20 升级）

**核心原则**：默认按"会议室投屏 5-10m 视距"调字号，**不要按屏幕阅读调**。会议室投屏可读 ≥ 屏幕阅读舒服。

**theme.css 基准字号（已内置）**：

```
--fs-cover-title:   38pt   /* 封面主标题 */
--fs-cover-subtitle:20pt   /* 封面副标题 */
--fs-section-title: 34pt   /* 章节扉页标题 */
--fs-page-title:    24pt   /* 内页标题 */
--fs-page-subtitle: 16pt   /* 副标题 */
--fs-body:          14pt   /* 正文（投屏最小起点） */
--fs-body-sm:       13pt
--fs-caption:       12pt   /* 说明/标签 */
--fs-source:        11pt   /* 数据来源 */
```

**铁律**：
- 正文（描述性文字、列表项、卡片正文）**最小 13pt**，不要更小
- 标签/说明/数据来源 **最小 11pt**
- 大数字保持（46pt 卡片编号、56pt 数据墙、170pt 章节）
- 局部"装得下"问题**靠收紧 padding/gap 解决，不要靠缩字号**

**反模式警告**：以下场景常导致字号被压小，要警惕——
- 一页塞太多卡片/列表 → 减卡片数（4 → 3 → 2），不要缩字号
- 卡片高度不够装文字 → 加 min-height 或减点列数量，不要缩字号
- key-point 文字太长 → 让用户缩短措辞，不要缩字号
- "看起来更精致" → 投屏看不清才是最大的不精致

---

## v4.3.1 `.slide.compact` 密集页变体（解决长 deck 溢出 · 2026.5.20）

**问题**：v4.3 字号上调后，长 deck（25+ 页）或单页内容密集（双栏 + 6 列表项 + key-point + 图表）的页面，在 720px 高度内**装不下**。这是物理冲突：字号涨 18% → 高度需求涨 18%。

**反模式**：不要靠**降字号**救火（投屏会看不清）。

**正解**：用 `.slide.compact` 修饰类——已在 components.css 内置，**仅压 1-2pt 让所有内容统一收紧**。

**用法**：

```html
<!-- 普通页 -->
<section class="slide">...</section>

<!-- 密集页：自动使用更紧凑的字号体系 -->
<section class="slide compact">...</section>
```

**.compact 干了什么**（已内置在 components.css，AI 装配时只需加 class）：
- key-point 正文 15 → 13pt，列表 desc 13.5 → 12pt
- 三栏 card-title 17 → 15pt，正文 13.5 → 12pt
- 编号点列 lead 16 → 14pt，desc 13.5 → 12pt
- metric / mini-card / timeline 同步压缩
- 配套缩 padding（card 24→18pt、point-list 14→10pt）—**字号和间距同时压**，效果协调

**判断"何时该 compact"**：
- 内容性质：双栏 + 多列表 / 全宽长文字 / 多卡片+ key-point + chart 混排
- 试装一次没 compact 时，反向验证 PNG 看是否溢出 → 溢出就加 compact
- 单页有 3+ 个组件块（卡片组/点列/图表/key-point/quote）→ 默认加 compact

**铁律**：
- compact 只是"密集页救援"，不要**全 deck 默认加 compact**（会失去投屏字号的本意）
- 加 compact 前先问"是否能减一项内容"——结构性减载优先于字号收紧
- compact 后正文仍 ≥ 12pt（投屏底线），不要再单独缩

---

## v4.3.2 双栏底部对齐铁律（grid 行高陷阱 · 2026.5.20）

**问题**：用 `display: grid` 做双栏布局时，**两栏底部经常不对齐**。常见症状：右栏短一截、左栏盈余空白、被大图撑高溢出整页。

**根因（CSS Grid 陷阱）**：
- 默认 `grid-template-rows` 未指定 → 行高 = max-content（取最高子元素）
- 子元素内含大图时（如截图 1700×1000px），行高被强行撑大 → 整个 grid 容器溢出父容器
- `flex-direction: column` 的 flex 子项默认 `min-height: auto` → 不能被压缩到小于内容自然尺寸

**正解三件套（必须同时用）**：

```css
.body-grid {
  display: grid;
  grid-template-columns: 0.85fr 1.15fr;
  grid-template-rows: 1fr;     /* (1) 行高=容器高，不被内部撑大 */
  flex: 1;
  min-height: 0;               /* (2) 允许在 flex 列里被父容器压缩 */
}

/* 含图片的子容器 */
.preview-wrap {
  display: flex;
  flex-direction: column;
  min-height: 0;               /* (3) 允许内部图片以容器为准缩放 */
  overflow: hidden;
}
.preview-img-wrap {
  flex: 1 1 auto;
  min-height: 0;
  overflow: hidden;
}
.preview-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: contain;         /* 不要再用 max-height: 270px 这种硬编码 */
}
```

**铁律**：
- 双栏 grid 必须显式写 `grid-template-rows: 1fr`，**不要省略**
- flex 列里的 grid 子项必须加 `min-height: 0`
- 含图片的容器**禁用绝对 max-height**（如 `max-height: 270px`）——会破坏栏对齐
- 图片用 `width:100%; height:100%; object-fit: contain` 让它**适配容器**，不要让容器**适配它**

**反模式**：
- 错：`.preview-img-wrap { max-height: 280px; }` → 右栏永远比左栏短一截
- 错：给图片加 `max-width: 100%; max-height: 100%` 但不约束容器 → 大图把容器撑高
- 错：grid 不写 `grid-template-rows` → 行高随内容跳

**装配前自检 4 问**：
1. 双栏 grid 是否写了 `grid-template-rows: 1fr`？
2. body-grid 是否加了 `min-height: 0`？
3. 含图片的容器是否设了 `min-height: 0` + `overflow: hidden`？
4. 图片是否用 `width:100%; height:100%; object-fit: contain`？

---

## v4.3.3 稀疏页垂直居中（避免"头重脚轻" · 2026.5.20）

**问题**：单页内容显著少于半页时（目录页只有 3 个章节、单引用页只有 1 段文本、单图大版式等），默认 flex column 把内容压在飘带正下方 → 上半部分塞满、下半部分一片空白 → 视觉头重脚轻。

**正解**：用 `.slide.center-y` 修饰类——主体内容自动垂直居中到飘带下方的可用空间。

**用法（最简单）**：

```html
<section class="slide center-y">
  <div class="slide-body">
    <h2 class="page-title">目 录</h2>
    <div class="page-wave"><img src="..." alt=""></div>
    <ul class="toc">...</ul>   <!-- 自动垂直居中 -->
  </div>
</section>
```

**已支持的内容容器**（slide-body 直接子元素）：
`.toc / .auto-list / .point-list / .body-grid / .key-quote / .body-center / .chart-frame / .metric-wall / .three-cards / .mini-cards`

**多块内容一起居中** → 用 `.body-center` 包装器：

```html
<div class="slide-body">
  <h2 class="page-title">...</h2>
  <div class="page-wave">...</div>
  <div class="body-center">       <!-- 包多块 -->
    <ul class="toc">...</ul>
    <p class="footnote">注：...</p>
  </div>
</div>
```

**判断"何时该 center-y"**：
- 目录页 / 全书检索页（3-5 个章节）
- 单引言 / 单结论页（一段 key-quote）
- 单大图页 / 单大数据墙（只有 1-2 个 metric）
- 章节扉页变体（只有 title + 1 句副标题）
- 任何内容显著少于半页的稀疏页

**铁律**：
- center-y 是**稀疏页专用**，不要给内容密集的页加（会导致它和飘带挨太近）
- center-y 和 .compact 是**反向的两个修饰**：compact 救溢出，center-y 救空旷
- 不要既加 center-y 又加 compact——选错了模式说明该重新审视内容密度

---

## v4 装配铁律 · 保留 vs 替换二元清单

借鉴自 [zarazhangrui/beautiful-html-templates](https://github.com/zarazhangrui/beautiful-html-templates) 的设计哲学：**设计系统是模板的灵魂，必须严格保留；用户内容是模板的躯壳，必须完全替换**。

### 设计系统 · 必须保留（动一处都算改造模板）

**字体系统**：
- 中文：微软雅黑 / Microsoft YaHei / Noto Sans SC（VI 强制规范，不能换 Inter / Roboto / 思源宋体）
- 西文/数字：Arial / Helvetica（不能换无衬线字体如 Helvetica Neue / Inter）
- 字重梯度：超细 100 / 细 200 / 普通 400 / 中等 500 / 粗 700（不能新增字重）

**色彩系统**：
- 品牌四色：`#F07800` 橙 / `#D20000` 红 / `#3C961E` 绿 / `#78B41E` 嫩绿
- 品牌深蓝：`#00005A`（封面）/ `#1B3C6E`（页面标题）
- 关键强调：`#C00000`（红字）/ `#002060`（讲者署名）
- 灰阶：`#1A1A1A` / `#555555` / `#888888` / `#BBBBBB` / `#E8E8E8`（hairline）
- 软色：`#FCEFEC` / `#EEF5ED` / `#FCF1E5` / `#ECEFF3`（标签底）
- **不能新增其他颜色**——如果觉得不够用，是版式选错了，不是颜色不够

**视觉锚点**：
- 集团波浪条：封面用 `_assets/wave-cover-plain.png`，内页用 `_assets/wave-inner.png`
- 经研院LOGO：右上角，`shared/logos/etrc/etrc-logo.png`
- 顶部 3px 细色线（章节分隔页用）
- 卡片顶部 3px 色线（橙/红/绿三色识别）
- **位置和尺寸都不能改**

**组件结构**：
- `.key-point` 必须有：hairline 边 + 左 4px 红条 + 小标签 + 图标 + 内容
- `.three-cards .card` 必须有：顶部 3px 色线 + card-head（大数字+标题+英文小标）+ card-body + card-tags
- `.section-divider` 必须有：左侧大数字+section-num-label / 右侧 section-label+title+subtitle+meta
- **不能简化组件**（如去掉 card-tags 因为没标签内容——那就放空标签）

**装饰元素**：
- hairline 颜色 `#E8E8E8`、宽度 `1px`
- 阴影规格 `0 4px 12px rgba(0,0,0,0.04)`
- 圆角统一不用（除标签 12px、章节标签 2px）
- **不能加：渐变色块、深色背景、粗边框（>2px）、emoji 装饰**

### 用户内容 · 必须替换（不能用 demo 文本糊弄）

**封面**：
- `cover-title` → 用户的报告标题
- `cover-subtitle` → 用户的副标题（如"研究成果汇报"）
- `cover-author` → 真实汇报人姓名 + 日期

**章节分隔页**：
- `section-num` → 实际章节编号（01/02/03）
- `title` → 实际章节标题
- `subtitle` → 章节导读 1-2 句
- `meta` → 章节量化指标（从成稿抽取）

**内页**：
- `page-title` → 该页主标题
- `key-point` 内文字 → 该页核心论点（保留用户原文措辞）
- 各种 card / metric / point-list 的 → 具体内容
- `tag` 标签文字 → 该页关键词
- `data-source` → 真实数据来源
- `page-num` → 页码

**禁止**：
- 用 sample-pages.html 里的"双碳""能源行业三大转折"这种 demo 文本糊弄
- 用"标题1/标题2"这种占位文字交付
- 标签内容空着不填（要么填要么删整个 tag 区域）

---

## 新版式沿用清单（如果 10 种标准版式不够用时）

如果内容性质确实需要新版式（如 6 步流程、双层复合卡片、四栏对比等），新版式必须**严格沿用现有设计 token**：

| 沿用项 | 具体要求 |
|---|---|
| **字体** | 字体家族、字重、字距、行高都用现有变量 `var(--font-cn) / var(--font-en) / var(--fw-*)` |
| **配色** | 只能用 `:root` 里定义的 CSS 变量，不能新增颜色 |
| **装饰** | 沿用 hairline / 阴影 / 顶部 3px 色线等装饰元素 |
| **间距** | 沿用 `--space-*` 变量定义的间距节奏 |
| **组件语法** | 复用现有组件结构（卡片头-身-标签的三层结构、key-point 的图标-标签-内容） |
| **页面框架** | 标题区（title-row） + 飘带（page-wave） + 关键论点（key-point） + 主体 + 页码——这个框架不能变 |
| **导航行为** | 页码递增、章节切换的视觉延续性 |

**核心原则**：新版式应该让人**认不出是新版式**——它必须看起来像是 10 种标准版式中天然的第 11 种。

---

## Don't modernize · 不要"现代化"已稳定的模板

v4 视觉系统已经定稿（2026年5月19日）。这之后：
- **不要主动"优化"模板的视觉表达**（用户说要改才改）
- **不要换字体、换配色、加渐变、加动效**——稳定 > 持续优化
- **不要因为单次任务的特殊需求修改模板** —— 该用现有版式做减法适配
- 例外：用户明确说"换风格""不喜欢这版""做发布会风"等显式指令时才改

**为什么这条重要**：v1→v2→v3→v4 我们已经折腾了 4 轮才稳定，每次改动都意味着所有历史成品视觉不一致。**保持稳定比追求"更现代"更有价值**。
