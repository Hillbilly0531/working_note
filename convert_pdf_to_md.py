import pdfplumber
import os
import re
from datetime import datetime

def convert_pdf_to_markdown(pdf_path, output_path):
    """将PDF转换为Markdown格式"""

    print(f"正在读取PDF: {pdf_path}")

    with pdfplumber.open(pdf_path) as pdf:
        markdown_content = []
        total_pages = len(pdf.pages)
        print(f"PDF共 {total_pages} 页")

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

        # 提取每一页的文本
        for page_num, page in enumerate(pdf.pages, 1):
            print(f"正在处理第 {page_num}/{total_pages} 页...")

            # 尝试提取文本
            text = page.extract_text()

            # 如果直接提取失败，尝试使用其他方法
            if not text or text.strip() == '':
                # 尝试提取表格
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        text = table_to_markdown(table)
                        markdown_content.append(text)
                        markdown_content.append("")
                continue

            # 清理文本
            text = clean_text(text)

            if text:
                # 添加页面分隔标记
                if page_num > 1:
                    markdown_content.append(f"\n---\n")
                    markdown_content.append(f"*第 {page_num} 页*\n")

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

                    # 检测可能的标题
                    if is_likely_title(line, i, lines):
                        formatted_lines.append(f"## {line}")
                    else:
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

def table_to_markdown(table):
    """将表格转换为Markdown格式"""
    if not table or len(table) == 0:
        return ""

    md_lines = []

    # 表头
    header = table[0]
    md_lines.append("| " + " | ".join(str(cell) if cell else "" for cell in header) + " |")

    # 分隔符
    md_lines.append("| " + " | ".join(["---"] * len(header)) + " |")

    # 数据行
    for row in table[1:]:
        md_lines.append("| " + " | ".join(str(cell) if cell else "" for cell in row) + " |")

    return '\n'.join(md_lines)

def clean_text(text):
    """清理文本中的特殊字符"""
    # 移除多余的空白字符
    text = re.sub(r'[ \t]+', ' ', text)
    # 移除多余的空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def is_likely_title(line, index, all_lines):
    """判断一行是否可能是标题"""
    # 如果行很短且包含关键词
    if len(line) < 50 and len(line) > 3:
        # 检查是否是章节编号（如 "1." 或 "1.1" 或 "一、"）
        if re.match(r'^[\d一二三四五六七八九十]+[\.\、\s]', line):
            return True
        if re.match(r'^第[\d一二三四五六七八九十]+章', line):
            return True
        # 检查是否包含关键词
        title_keywords = ['需求', '功能', '说明', '概述', '简介', '背景', '目标', '范围', '流程', '设计', '实现', '测试', '验收', '附录', '目录', '总结']
        for keyword in title_keywords:
            if keyword in line and len(line) < 30:
                return True
    return False

if __name__ == "__main__":
    pdf_path = r"d:\IdeaProjects\working_note\leyo\需求文档\pmsv28.28.0需求\需求文档原件.pdf"
    output_path = r"d:\IdeaProjects\working_note\leyo\需求文档\pmsv28.28.0需求\需求文档原件.md"

    convert_pdf_to_markdown(pdf_path, output_path)
