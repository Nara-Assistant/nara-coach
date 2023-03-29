from PyPDF2 import PdfReader

def get_text(filename):
    pdf_reader = PdfReader(filename)
    res = ""

    for page in pdf_reader.pages:
        res += "\n" + page.extract_text()

    return res