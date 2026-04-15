import pdfplumber

pdf_path = r"d:\IdeaProjects\working_note\leyo\需求文档\pmsv28.28.0需求\需求文档原件.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"PDF共 {len(pdf.pages)} 页\n")

    for page_num, page in enumerate(pdf.pages, 1):
        print(f"=== 第 {page_num} 页 ===")

        # 提取文本
        text = page.extract_text()
        if text:
            print(f"文本长度: {len(text)}")
            print(f"文本前200字符:\n{text[:200]}")
        else:
            print("未提取到文本")

        # 检查是否有图片
        images = page.images
        print(f"图片数量: {len(images)}")

        # 检查是否有表格
        tables = page.extract_tables()
        print(f"表格数量: {len(tables)}")

        # 检查页面尺寸
        print(f"页面尺寸: {page.width} x {page.height}")
        print()
