# SPIC-PPT 版本快照设计（v4.8.0）

## 问题

制作演示文稿时常需找回旧版，但当前流程对成品 HTML/PDF 是**原地覆盖**——每次 AI 改稿都把上一版物理抹掉。根因不是版本控制坏了，而是压根没有版本控制。

## 目标

每次成功导出都自动留底，旧版可随时找回，不依赖 AI 或人"记得另存"。

## 设计决策（已与用户确认）

| 维度 | 决策 | 理由 |
|---|---|---|
| 触发时机 | 每次覆盖前自动快照 | 结构上跳不过，不靠记得 |
| 恢复方式 | 直接打开文件 | 零心智成本，用户本就在 Windows 翻文件 |
| 快照内容 | HTML + PDF 都存 | HTML 可改，PDF 可直接发/看 |
| 不用 git | 时间戳快照 | 恢复场景是"拿回那一版文件"，非合并/diff；HTML diff 噪音大、PDF 是黑盒，git 价值发挥不出 |

## 机制

把快照焊进 `build_pdf.py` 导出闸门——它已是 skill 强制必经的导出卡点，不引入新纪律。

`build_pdf.py` 执行顺序：
1. 跑溢出自检（已有）；不过则拒绝导出（已有）
2. **新增**：自检通过后、写新 PDF 前，若同名成品 HTML 已存在 → 复制旧 HTML 进 `_versions/`，命名 `<basename>_<YYYYMMDD-HHMMSS>.html`
3. 写新 PDF（已有）
4. **新增**：新 PDF 也复制一份同名时间戳进 `_versions/`
5. 首次导出（无旧版）→ 只产出当前结果，不报错

```
项目目录/
├── 成品PPT.html                          ← 当前版（始终最新）
├── 成品PPT.pdf
└── _versions/
    ├── 成品PPT_20260605-143012.html       ← 历史快照
    ├── 成品PPT_20260605-143012.pdf
    ├── 成品PPT_20260605-161533.html
    └── 成品PPT_20260605-161533.pdf
```

## 恢复

无需工具。`_versions/` 里是完整文件，双击 HTML 用浏览器/WPS 看，双击 PDF 直接看。要把旧版变回当前版：复制出来改名，或让 AI 做。

## 关键细节

- **时间戳**：脚本运行时本地时间，精确到秒（`YYYYMMDD-HHMMSS`），避免同分钟两次导出撞名。
- **不污染自检**：`check_overflow.py`、`health_check.py` 需忽略 `_versions/`，避免把历史版本当成品扫。
- **`.gitignore`**：`_versions/` 加入忽略（本地产物，不进 git，同 `_preview/`）。
- **不动 Edit/Write 流程**：中间编辑不快照——只有"导出"才是值得找回的版本，这是有意的粒度选择。
- **不加手动标签**：纯自动，YAGNI。

## 改动范围

| 文件 | 改动 |
|---|---|
| `scripts/build_pdf.py` | 加快照逻辑（导出前 HTML、导出后 PDF） |
| `scripts/check_overflow.py` | 忽略 `_versions/`（防误扫，若其会扫目录） |
| `scripts/health_check.py` | 忽略 `_versions/` |
| `SKILL.md` | 第八阶段归档目录加 `_versions/` 说明 + 找回旧版指引 |
| `.gitignore` | 加 `_versions/` |
| VERSION / CHANGELOG / 文件头 | 4.7.0 → 4.8.0 |

## 测试（TDD）

1. **RED**：临时目录含旧 `成品PPT.html`，跑 build_pdf → 验证 `_versions/` 出现带时间戳的旧 HTML 副本
2. 首次导出（无旧版）→ 不报错，正常导出
3. 二次导出 → `_versions/` 累计两份，时间戳不同
4. 回归：check_overflow 不把 `_versions/` 文件算进溢出报告

## 同步

改完按既定流程同步四处：Claude skill 目录、private GitHub、public GitHub（注意脱敏）、桌面 ZIP、qclaw 副本。
