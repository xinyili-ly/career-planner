import pdfplumber
from docx import Document

def extract_text_from_pdf(file_path):
    # 目的：打开 PDF 并逐页拼接文字
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(file_path):
    # 目的：读取 Word 文档中的段落文字
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])