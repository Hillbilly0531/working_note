import os
import re
from datetime import datetime
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

def convert_pdf_to_markdown_with_ocr(pdf_path, output_path, lang='chi_sim+eng'):
    """使用OCR将PDF转换为Markdown格式"""

    print(f"正在读取PDF: {pdf_path}")
    print("正在将PDF转换为图片（这可能需要一些时间）...")

    # 将PDF转换为图片
    images = convert_from_path(pdf_path, dpi=300)
    total_pages = len(images)
    print(f"PDF共 {total_pages} 页")

    markdown_content = []

    # 添加YAML frontmatter (Obsidian格式)
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    markdown_content.append("---")
    markdown_content.append(f"title: {filename}")
    markdown_content.append(f"created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    markdown_content.append("source: PDF文档(OCR识别)")
    markdown_content.append("tags:")
    markdown_content.append("  - 需求文档")
    markdown_content.append("  - PMS")
    markdown_content.append("---")
    markdown_content.append("")
    markdown_content.append(f"# {filename}")
    markdown_content.append("")
    markdown_content.append("> 注：本文档通过OCR技术从PDF图片中识别生成，可能存在识别误差。")
    markdown_content.append("")

    # 对每一页进行OCR识别
    for page_num, image in enumerate(images, 1):
        print(f"正在OCR识别第 {page_num}/{total_pages} 页...")

        # 使用Tesseract进行OCR识别（支持中英文）
        text = pytesseract.image_to_string(image, lang=lang)

        if text and text.strip():
            # 清理文本
            text = clean_text(text)

            # 添加页面分隔标记
            if page_num > 1:
                markdown_content.append(f"\n---\n")

            markdown_content.append(f"## 第 {page_num} 页")
            markdown_content.append("")

            # 处理文本内容
            lines = text.split('\n')
            formatted_lines = []
            prev_line_empty = False

            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    if not prev_line_empty:
                        formatted_lines.append('')
                        prev_line_empty = True
                    continue

                prev_line_empty = False
                formatted_lines.append(line)

            markdown_content.extend(formatted_lines)
            markdown_content.append("")

    # 保存Markdown文件
    full_content = '\n'.join(markdown_content)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)

    print(f"\n转换完成！已保存到: {output_path}")
    print(f"文件大小: {os.path.getsize(output_path)} 字节")
    return output_path

def clean_text(text):
    """清理文本中的特殊字符"""
    # 移除多余的空白字符
    text = re.sub(r'[ \t]+', ' ', text)
    # 移除多余的空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    # 移除页码标记
    text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
    return text.strip()

if __name__ == "__main__":
    pdf_path = r"d:\IdeaProjects\working_note\leyo\需求文档\pmsv28.28.0需求\需求文档原件.pdf"
    output_path = r"d:\IdeaProjects\working_note\leyo\需求文档\pmsv28.28.0需求\需求文档原件.md"

    convert_pdf_to_markdown_with_ocr(pdf_path, output_path)
