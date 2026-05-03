import os
import pandas as pd
from pypdf import PdfReader
from docx import Document
from langchain.tools import tool
import easyocr

# Initialize OCR reader (this might take a moment to load weights on first run)
# We use 'en' for English by default.
reader = None

def get_ocr_reader():
    global reader
    if reader is None:
        reader = easyocr.Reader(['en'])
    return reader

@tool
def read_file_content(file_path: str) -> str:
    """
    Reads the content of a file based on its extension (PDF, Word, Excel, Image, Text).
    Returns the extracted text content.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"

    ext = os.path.splitext(file_path)[1].lower()

    try:
        # 1. PDF
        if ext == ".pdf":
            pdf_reader = PdfReader(file_path)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text

        # 2. Word
        elif ext in [".docx", ".doc"]:
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])

        # 3. Excel
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
            return df.to_string()

        # 4. Images (OCR)
        elif ext in [".png", ".jpg", ".jpeg", ".bmp"]:
            ocr = get_ocr_reader()
            results = ocr.readtext(file_path, detail=0)
            return "\n".join(results)

        # 5. Text / CSV
        else:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()

    except Exception as e:
        return f"Error parsing {ext} file: {str(e)}"
