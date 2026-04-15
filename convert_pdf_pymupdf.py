import fitz  # PyMuPDF
import os
import re
from datetime import datetime
from PIL import Image
import io

def convert_pdf_to_markdown(pdf_path, output_path):
    """使用PyMuPDF将PDF转换为Markdown格式"""

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
    markdown_content.append("source: PDF文档")
    markdown_content.append("tags:")
    markdown_content.append("  - 需求文档")
    markdown_content.append("  - PMS")
    markdown_content.append("---")
    markdown_content.append("")
    markdown_content.append(f"# {filename}")
    markdown_content.append("")

    # 创建附件目录
    attachments_dir = os.path.join(os.path.dirname(output_path), "attachments")
    os.makedirs(attachments_dir, exist_ok=True)

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

        # 1. 尝试提取文本
        text = page.get_text()

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
                formatted_lines.append(line)

            markdown_content.extend(formatted_lines)
            markdown_content.append("")

        # 2. 提取图片
        image_list = page.get_images()
        if image_list:
            print(f"  发现 {len(image_list)} 张图片")
            for img_index, img in enumerate(image_list, 1):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                # 保存图片
                image_filename = f"page{page_number}_img{img_index}.{image_ext}"
                image_path = os.path.join(attachments_dir, image_filename)

                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)

                # 在Markdown中引用图片
                rel_path = f"attachments/{image_filename}"
                markdown_content.append(f"![图片-{page_number}-{img_index}]({rel_path})")
                markdown_content.append("")

        # 3. 提取表格
        tables = page.find_tables()
        if tables and tables.tables:
            print(f"  发现 {len(tables.tables)} 个表格")
            for table_idx, table in enumerate(tables.tables, 1):
                markdown_content.append(f"\n**表格 {table_idx}**\n")
                df = table.to_pandas()
                markdown_content.append(df.to_markdown(index=False))
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
    # 移除页码标记
    text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
    return text.strip()

if __name__ == "__main__":
    pdf_path = r"d:\IdeaProjects\working_note\leyo\需求文档\pmsv28.28.0需求\需求文档原件.pdf"
    output_path = r"d:\IdeaProjects\working_note\leyo\需求文档\pmsv28.28.0需求\需求文档原件.md"

    convert_pdf_to_markdown(pdf_path, output_path)
