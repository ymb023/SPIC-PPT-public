# LOGO 资源库

> 来源：国家电投官方VI资源包
> 用途：所有演示文稿模板共享调用

---

## 目录结构

```
shared/logos/
├── spic/                     # 国家电投集团官方LOGO
│   ├── source/               # 矢量源文件（AI + JPG预览）
│   ├── color/                # 彩色标准版（白色或浅色背景用）
│   ├── reversed/             # 反白版（深色背景用，整体反白）
│   └── text_reversed/        # 字体反白版（图标彩色保留，文字白色）
├── etrc/                     # 经研院 LOGO（咨询公司）
└── party/                    # 中国共产党党徽（共产党员网官方版）
```

---

## 选用决策树

### 第一步：选用哪个 LOGO？

| 场景 | 用 LOGO |
|---|---|
| 集团内部汇报、研究报告发布、对外讲座 | spic + etrc |
| 党课、党建主题、巡视整改 | party + etrc |
| 学术分享、专家讲座 | etrc 单独 或 不用 |
| 对外大型发布会、行业大会 | spic（突出集团身份） |
| 涉党涉政（必须严肃场合） | party + spic + etrc 三者 |

### 第二步：选用哪种版本？

#### SPIC LOGO 四个版本如何选

| 版本目录 | 适用背景 | 视觉效果 |
|---|---|---|
| `color/` | 白色/浅色背景 | 标准彩色（绿+橙+红双螺旋 + 深蓝文字） |
| `reversed/` | 深色背景 | 整体反白（图案文字都白色） |
| `text_reversed/` | 深色背景 + 想保留品牌色 | 图案保留彩色，文字白色 |
| `source/` | 印刷品、放大使用 | AI矢量源，可无限放大 |

#### SPIC 每个版本又分多种组合

| 组合 | 内容 | 适用 |
|---|---|---|
| **首选简称组合-横式** | "国家电投" 横排 | **最推荐** — 角标、页眉默认用这个 |
| **首选简称组合-竖式** | "国家电投" 竖排 | 侧边装饰 |
| **中文简称组合-横/竖** | "国家电投"（无英文） | 纯中文场景 |
| **英文简称组合-横/竖** | "SPIC"（无中文） | 国际化场景 |
| **中文全称组合-横/竖** | "国家电力投资集团有限公司" | 正式文件首页 |
| **中英文全称组合-横/竖** | 中文全称 + "STATE POWER INVESTMENT CORPORATION" | 对外正式场合 |

**默认推荐**：90% 场景用 `spic/color/preferred-short-horizontal.png`

### 第三步：经研院 LOGO

只有一个版本（含图案+"国家电投经研院"中文+"SPIC ETRC"英文）：
- `etrc/etrc-logo.png` — 直接用
- `etrc/etrc-logo.pdf` — 印刷品用矢量
- `etrc/etrc-logo.jpg` — 备用

### 第四步：党徽

- `party/party-emblem-gold.png` — 用于深色背景（如党课PPT封面红底）
- `party/party-emblem-red.png` — 用于浅色背景（如内页白底）
- 来源：共产党员网（12371.cn）受权发布的标准版

---

## HTML 引用示例

### 集团汇报模板的封面（标准用法）

```html
<!-- 封面：SPIC LOGO + 经研院LOGO 双标识 -->
<div class="cover-logos">
  <img src="../shared/logos/spic/color/preferred-short-horizontal.png" alt="国家电投">
  <span class="divider"></span>
  <img src="../shared/logos/etrc/etrc-logo.png" alt="经研院">
</div>
```

### 内页角标（只放经研院）

```html
<div class="corner-logo">
  <img src="../shared/logos/etrc/etrc-logo.png" alt="经研院">
</div>
```

### 党课PPT（朱红底）的角标

```html
<div class="corner-emblem">
  <img src="../shared/logos/party/party-emblem-red.png" alt="党徽">
</div>
<div class="corner-enterprise">
  <img src="../shared/logos/etrc/etrc-logo.png" alt="经研院">
</div>
```

### 发布会模板的深色背景

```html
<!-- 反白版用于深色背景 -->
<img src="../shared/logos/spic/reversed/preferred-short-horizontal.png" alt="国家电投">
```

---

## 使用规范

### 必须遵守

1. **不能裁剪、变形、调色**——官方LOGO是注册商标，不能改造
2. **保持比例**——缩放时用CSS `object-fit: contain;` 而非 `cover`
3. **保留呼吸空间**——LOGO周围至少留有LOGO高度1/3的留白
4. **避免低对比度**——浅色LOGO不能放在浅色背景（用反白版替代）

### 建议规范

1. **角标默认尺寸**：高度 28-36px（按 1280×720 画布计算）
2. **封面LOGO尺寸**：高度 60-90px
3. **优先用 PNG**（自带透明背景）；矢量印刷用 AI/PDF

---

## 文件清单

### SPIC（国家电投）

**矢量源**（3个）：
- spic-logo-combo.ai（1.5MB，AI源文件）
- spic-logo-combo-01.jpg（605KB，预览）
- spic-logo-combo-02.jpg（372KB，预览）

**彩色 color/**（13个 PNG/JPG）：
覆盖所有组合×横竖式，外加"综合智慧零碳电厂"特殊LOGO

**反白 reversed/**（11个 PNG）：
覆盖所有组合×横竖式

**字体反白 text_reversed/**（9个 PNG）：
覆盖主要组合×横竖式

### ETRC（经研院）

- etrc-logo.png（206KB）— 含三种组合（"经研院ETRC"小、"国家电投经研院SPIC ETRC"横+竖排）
- etrc-logo.pdf（225KB）— 矢量版
- etrc-logo.jpg（381KB）— JPG版

### 党徽

- party-emblem-gold.png（35KB）— 1024×1024，深色背景用
- party-emblem-red.png（15KB）— 1024×1024，浅色背景用

---

## 引用归属

- 国家电投LOGO：国家电力投资集团有限公司官方VI（注册商标）
- 经研院LOGO：国家电投集团经济技术研究咨询有限公司官方VI
- 党徽：共产党员网（12371.cn）受权发布的标准版本，源自《中国共产党党徽党旗条例》
