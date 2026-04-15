import fitz  # PyMuPDF
import os
import re
from datetime import datetime

def convert_pdf_to_markdown_with_ocr(pdf_path, output_path):
    """使用PyMuPDF的OCR功能将PDF转换为Markdown格式"""

    print(f"正在读取PDF: {pdf_path}")

    # 打开PDF
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"PDF共 {total_pages} 页")

    markdown_content = []

    # 添加YAML frontmatter (Obsidian格式)
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    markdown_content.append("---")
    markdown_content.append(f"title: {filename}")
    markdown_content.append(f"created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    markdown_content.append("source: PDF文档(OCR)")
    markdown_content.append("tags:")
    markdown_content.append("  - 需求文档")
    markdown_content.append("  - PMS")
    markdown_content.append("---")
    markdown_content.append("")
    markdown_content.append(f"# {filename}")
    markdown_content.append("")

    # 处理每一页
    for page_num in range(total_pages):
        page = doc[page_num]
        page_number = page_num + 1
        print(f"正在处理第 {page_number}/{total_pages} 页...")

        # 添加页面分隔
        if page_num > 0:
            markdown_content.append(f"\n---\n")

        markdown_content.append(f"## 第 {page_number} 页")
        markdown_content.append("")

        # 1. 尝试提取文本（包括OCR）
        # PyMuPDF 1.23.0+ 支持 get_text() 的 OCR 功能
        text = page.get_text("text")

        # 如果文本很少，尝试使用OCR
        if not text or len(text.strip()) < 50:
            print(f"  文本内容较少，尝试OCR识别...")
            # 将页面转换为图片然后OCR
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x缩放提高OCR精度
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(pix.tobytes("png")))

            # 使用pytesseract进行OCR
            try:
                import pytesseract
                text = pytesseract.image_to_string(img, lang='chi_sim+eng')
                print(f"  OCR识别完成，识别到 {len(text)} 字符")
            except Exception as e:
                print(f"  OCR识别失败: {e}")
                text = ""

        if text and text.strip():
            text = clean_text(text)
            # 处理文本内容
            lines = text.split('\n')
            formatted_lines = []
            prev_line_empty = False

            for line in lines:
                line = line.strip()
                if not line:
                    if not prev_line_empty:
                        formatted_lines.append('')
                        prev_line_empty = True
                    continue

                prev_line_empty = False

                # 检测标题
                if is_likely_title(line):
                    formatted_lines.append(f"### {line}")
                else:
                    formatted_lines.append(line)

            markdown_content.extend(formatted_lines)
            markdown_content.append("")
        else:
            markdown_content.append("*该页未识别到文字内容*")
            markdown_content.append("")

        # 2. 提取图片
        image_list = page.get_images()
        if image_list:
            print(f"  发现 {len(image_list)} 张图片")

    doc.close()

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

def is_likely_title(line):
    """判断一行是否可能是标题"""
    if len(line) < 50 and len(line) > 3:
        # 检查是否是章节编号
        if re.match(r'^[\d一二三四五六七八九十]+[\.\、\s]', line):
            return True
        if re.match(r'^第[\d一二三四五六七八九十]+章', line):
            return True
        # 检查关键词
        title_keywords = ['需求', '功能', '说明', '概述', '简介', '背景', '目标', '范围', '流程', '设计', '实现', '测试', '验收', '附录', '目录', '总结']
        for keyword in title_keywords:
            if keyword in line and len(line) < 30:
                return True
    return False

if __name__ == "__main__":
    pdf_path = r"d:\IdeaProjects\working_note\leyo\需求文档\pmsv28.28.0需求\需求文档原件.pdf"
    output_path = r"d:\IdeaProjects\working_note\leyo\需求文档\pmsv28.28.0需求\需求文档原件_ocr.md"

    convert_pdf_to_markdown_with_ocr(pdf_path, output_path)
