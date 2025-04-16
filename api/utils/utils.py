import io
import PyPDF2
from docx import Document
from fastapi import HTTPException
import asyncio

# Aync version of extract_text_from_docx_sync
async def extract_text_from_docx(file_content : str) -> str:
    """
    Extract text from a DOCX file.
    """
    return await asyncio.to_thread(extract_text_from_docx_sync, file_content)

def extract_text_from_docx_sync(file_content : str) -> str:
    """
    Extract text from a DOCX file (blocking version).
    """
    doc = Document(io.BytesIO(file_content))
    extracted_text = ""
    for para in doc.paragraphs:
        extracted_text += para.text + "\n"
    return extracted_text

# Aync version of extract_text_from_pdf_sync
async def extract_text_from_pdf(file_content : str) -> str:
    """
    Extract text from a PDF file.
    """
    return await asyncio.to_thread(extract_text_from_pdf_sync, file_content)

def extract_text_from_pdf_sync(file_content : str) -> str:
    """
    Extract text from a PDF file (blocking version).
    """
    content = ""
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
    num_pages = len(pdf_reader.pages)

    for i in range(num_pages):
        page = pdf_reader.pages[i]
        content += page.extract_text() 
    
    return content

# Aync version of extract_text_from_txt_sync
async def extract_text_from_txt(file_content : str) -> str:
    """
    Extract text from a TXT file.
    """
    return await asyncio.to_thread(extract_text_from_txt_sync, file_content)

def extract_text_from_txt_sync(file_content : str) -> str:
    """
    Extract text from a TXT file (blocking version).
    """
    return file_content.decode("utf-8")

async def extract_text_from_file(file_content : str, file_type : str) -> str:
    """
    Extract text from a file based on its type.
    """
    if file_type == "docx":
        return await extract_text_from_docx(file_content)
    elif file_type == "pdf":
        return await extract_text_from_pdf(file_content)
    elif file_type == "txt":
        return await extract_text_from_txt(file_content)
    else:
        raise HTTPException(status_code=400, detail="Unsuported file type")