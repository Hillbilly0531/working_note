import fitz  # PyMuPDF
import os
import re
import io
import numpy as np
from datetime import datetime
from PIL import Image

def convert_pdf_to_markdown_with_easyocr(pdf_path, output_path):
    """使用EasyOCR将PDF转换为Markdown格式"""

    print(f"正在读取PDF: {pdf_path}")

    # 初始化EasyOCR（首次运行会下载模型）
    print("正在初始化EasyOCR（首次运行需要下载模型，请稍候）...")
    import easyocr
    reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
    print("EasyOCR初始化完成！")

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
    markdown_content.append("source: PDF文档(EasyOCR识别)")
    markdown_content.append("tags:")
    markdown_content.append("  - 需求文档")
    markdown_content.append("  - PMS")
    markdown_content.append("---")
    markdown_content.append("")
    markdown_content.append(f"# {filename}")
    markdown_content.append("")
    markdown_content.append("> 注：本文档通过EasyOCR技术从PDF图片中识别生成，可能存在识别误差。")
    markdown_content.append("")

    # 处理每一页
    for page_num in range(total_pages):
        page = doc[page_num]
        page_number = page_num + 1
        print(f"\n正在处理第 {page_number}/{total_pages} 页...")

        # 添加页面分隔
        if page_num > 0:
            markdown_content.append(f"\n---\n")

        markdown_content.append(f"## 第 {page_number} 页")
        markdown_content.append("")

        # 1. 尝试直接提取文本
        text = page.get_text("text")

        # 如果文本很少，使用OCR
        if not text or len(text.strip()) < 100:
            print(f"  使用EasyOCR识别图片文字...")

            # 将页面转换为图片
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x缩放提高OCR精度
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            img_array = np.array(img)

            # 使用EasyOCR识别
            results = reader.readtext(img_array)

            if results:
                # 按Y坐标分组，组织成段落
                lines = []
                current_y = None
                current_line = []

                for (bbox, detected_text, conf) in results:
                    y_coord = (bbox[0][1] + bbox[2][1]) / 2  # 计算中心Y坐标

                    if current_y is None or abs(y_coord - current_y) < 20:
                        current_line.append(detected_text)
                        current_y = y_coord
                    else:
                        lines.append(' '.join(current_line))
                        current_line = [detected_text]
                        current_y = y_coord

                if current_line:
                    lines.append(' '.join(current_line))

                text = '\n'.join(lines)
                print(f"  识别到 {len(results)} 个文本块")
            else:
                text = ""
                print(f"  未识别到文字")

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
    output_path = r"d:\IdeaProjects\working_note\leyo\需求文档\pmsv28.28.0需求\需求文档原件.md"

    convert_pdf_to_markdown_with_easyocr(pdf_path, output_path)
