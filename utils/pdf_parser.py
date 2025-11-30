
from PyPDF2 import PdfReader

def extract_text_from_pdf(file) -> str:
    """
    Accepts a file-like object (Streamlit uploaded file) or path.
    Returns concatenated text from all pages.
    """
    try:
        reader = PdfReader(file)
        all_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                all_text.append(text)
        return "\n\n".join(all_text)
    except Exception as e:
     return""