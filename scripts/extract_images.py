"""
从 docx / pptx / pdf 中提取所有图片，供 PPT 装配阶段复用

用途：避免 AI 在 PPT 装配时"重画"原报告里已有的图表/示意图/照片

Usage:
    python extract_images.py <input_file> [output_dir]

示例：
    python extract_images.py 研究报告.docx
    python extract_images.py 历史汇报.pptx _images/extracted
    python extract_images.py 行业报告.pdf

输出：
    _images/extracted/
    ├── image_01.png / .jpg / .jpeg
    ├── image_02.png
    ├── ...
    └── manifest.md   # 每张图的来源信息，AI 用这份清单判断哪张图放在 PPT 哪页

依赖：
    - docx/pptx: 仅需标准库 zipfile（任何 Python 都能跑）
    - pdf: PyMuPDF（pip install pymupdf）
"""

import sys
import os
import zipfile
import shutil
from pathlib import Path


# 过滤规则
MIN_FILE_SIZE = 3000   # < 3KB 通常是图标、装饰元素
SKIP_NAMES = {'thumbs.db', '.ds_store'}  # 系统垃圾文件
SKIP_EXTENSIONS = {'.wmf', '.emf'}        # PPT 矢量元数据（无法在 HTML 用）


def is_useful_image(name: str, size: int) -> bool:
    """判断是否值得保留"""
    base = os.path.basename(name).lower()
    if base in SKIP_NAMES:
        return False
    ext = os.path.splitext(base)[1].lower()
    if ext in SKIP_EXTENSIONS:
        return False
    if size < MIN_FILE_SIZE:
        return False
    return True


def extract_from_zip(input_path: str, output_dir: str, media_prefix: str):
    """docx / pptx 都是 zip 包，图片在 word/media/ 或 ppt/media/"""
    os.makedirs(output_dir, exist_ok=True)
    extracted = []

    with zipfile.ZipFile(input_path) as z:
        # 列出所有 media 文件并按原始名称自然排序（image1, image2, ..., image10）
        import re
        def natural_key(info):
            # 提取文件名末尾的数字用于自然排序
            base = os.path.basename(info.filename)
            m = re.search(r'(\d+)', base)
            return (int(m.group(1)) if m else 0, base)

        media_items = sorted(
            [info for info in z.infolist()
             if info.filename.startswith(media_prefix)
             and not info.is_dir()
             and is_useful_image(info.filename, info.file_size)],
            key=natural_key
        )

        for i, info in enumerate(media_items, 1):
            original_name = os.path.basename(info.filename)
            ext = os.path.splitext(original_name)[1].lower()
            out_name = f"image_{i:02d}{ext}"
            out_path = os.path.join(output_dir, out_name)

            with z.open(info) as src, open(out_path, 'wb') as dst:
                shutil.copyfileobj(src, dst)

            extracted.append({
                'out_name': out_name,
                'original_name': original_name,
                'source_location': f'内嵌资源（原名: {original_name}）',
                'size_kb': round(info.file_size / 1024, 1),
            })

    return extracted


def extract_from_pdf(input_path: str, output_dir: str):
    """PDF 用 PyMuPDF 提取内嵌的栅格（raster）图片。

    注意 · 局限性：
    - 本函数只提取 PDF 中以 image XObject 形式嵌入的栅格图（PNG/JPG 等）。
    - **不处理矢量图表**（如 PDF 里用 vector path 绘制的折线图、柱状图）。
    - 如需把矢量图表当作图片复用，可改用整页渲染：
        page.get_pixmap(matrix=fitz.Matrix(2, 2)).save(...)
      但整页渲染会带上背景/标题等周边元素，需自行裁剪。
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("ERROR: 需要安装 PyMuPDF: pip install pymupdf", file=sys.stderr)
        sys.exit(2)

    os.makedirs(output_dir, exist_ok=True)
    extracted = []
    counter = 0
    seen_xrefs = set()   # 同一张图可能在多页出现，去重

    doc = fitz.open(input_path)
    for page_num, page in enumerate(doc, 1):
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)

            try:
                pix = fitz.Pixmap(doc, xref)
                # CMYK → RGB
                if pix.n - pix.alpha > 3:
                    pix = fitz.Pixmap(fitz.csRGB, pix)

                # 过滤太小的图片
                if pix.width * pix.height < 5000:  # < 70x70 像素
                    pix = None
                    continue

                counter += 1
                out_name = f"image_{counter:02d}.png"
                out_path = os.path.join(output_dir, out_name)
                pix.save(out_path)
                size_kb = round(os.path.getsize(out_path) / 1024, 1)

                # 提取该图所在页的上下文文字（前150字）
                page_text = page.get_text()
                context = page_text[:150].replace('\n', ' ').strip()

                extracted.append({
                    'out_name': out_name,
                    'original_name': f'xref={xref}',
                    'source_location': f'PDF 第 {page_num} 页',
                    'size_kb': size_kb,
                    'dimensions': f'{pix.width}x{pix.height}',
                    'context': context,
                })
                pix = None
            except Exception as e:
                print(f"  跳过 xref={xref}（{e}）", file=sys.stderr)

    doc.close()
    return extracted


def write_manifest(input_path: str, output_dir: str, extracted: list):
    """写 manifest.md：AI 装配 PPT 时用此清单决定每页用哪张图"""
    manifest_path = os.path.join(output_dir, 'manifest.md')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write("# 图片资源清单\n\n")
        f.write(f"**源文件**：`{input_path}`\n\n")
        f.write(f"**共提取 {len(extracted)} 张图片**\n\n")
        f.write("---\n\n")
        f.write("## 使用指引（给 AI）\n\n")
        f.write("在 PPT 结构化抽取阶段，对每页内容判断是否有匹配的图片。如有：\n")
        f.write("- HTML 装配时用 `<img src=\"_images/extracted/image_NN.xxx\">` 引用\n")
        f.write("- **不要重画占位框**，直接用原图\n")
        f.write("- 图片保持原比例（CSS `object-fit: contain`）\n")
        f.write("- 图片外层套 `<div class=\"chart-frame\">` 保留绿色边框\n\n")
        f.write("---\n\n")
        f.write("## 图片清单\n\n")
        for item in extracted:
            f.write(f"### {item['out_name']}\n\n")
            f.write(f"- **来源**：{item['source_location']}\n")
            f.write(f"- **文件大小**：{item['size_kb']} KB\n")
            if 'dimensions' in item:
                f.write(f"- **尺寸**：{item['dimensions']}\n")
            if 'context' in item:
                f.write(f"- **所在页上下文**：> {item['context']}\n")
            f.write(f"- **HTML 引用**：`<img src=\"_images/extracted/{item['out_name']}\">`\n\n")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print(f"ERROR: 文件不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = sys.argv[2] if len(sys.argv) > 2 else '_images/extracted'

    ext = os.path.splitext(input_path)[1].lower()
    print(f"提取来源: {input_path}")
    print(f"输出目录: {output_dir}")
    print(f"文件类型: {ext}")
    print()

    if ext == '.docx':
        extracted = extract_from_zip(input_path, output_dir, 'word/media/')
    elif ext == '.pptx':
        extracted = extract_from_zip(input_path, output_dir, 'ppt/media/')
    elif ext == '.pdf':
        extracted = extract_from_pdf(input_path, output_dir)
    else:
        print(f"ERROR: 不支持的格式 {ext}（支持 .docx / .pptx / .pdf）", file=sys.stderr)
        sys.exit(1)

    if not extracted:
        print("没有提取到可复用图片（可能源文件不含图片，或图片都太小被过滤）")
        sys.exit(0)

    write_manifest(input_path, output_dir, extracted)

    print(f"完成。提取 {len(extracted)} 张图片：")
    for item in extracted[:10]:
        print(f"  - {item['out_name']} ({item['size_kb']} KB, {item['source_location']})")
    if len(extracted) > 10:
        print(f"  ... 还有 {len(extracted) - 10} 张")
    print()
    print(f"清单文件: {os.path.join(output_dir, 'manifest.md')}")


if __name__ == '__main__':
    main()
