import fitz


def extract_text(pdf_file):

    text = ""

    pdf = fitz.open(
        stream=pdf_file,
        filetype="pdf"
    )

    for page in pdf:

        text += page.get_text()

    return text