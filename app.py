import streamlit as st
import PyPDF2
import difflib
import os
from dotenv import load_dotenv
from pdf2image import convert_from_bytes
import pytesseract

# Load environment variables from .env file.
load_dotenv()

# Increase maximum upload size in config if needed.
# (See https://docs.streamlit.io/library/advanced-features/configuration for details.)

st.title("Universal Text Comparison Tool")
st.write(
    "Upload two files (PDFs or text). The tool will extract text (using OCR if scanned) and display differences. "
    "If the PDF is password-protected, check the box and provide the password."
)

def extract_text(file, password=None):
    """
    Extract text from a PDF file.
    - If the file is encrypted, it uses the provided password.
    - If no text is extracted (e.g., scanned PDF), it performs OCR.
    Returns a tuple (text, encryption_flag).
    """
    try:
        file.seek(0)  # reset file pointer
        pdf_reader = PyPDF2.PdfReader(file)
        if pdf_reader.is_encrypted:
            if password:
                pdf_reader.decrypt(password)
            else:
                st.warning("File appears to be encrypted. Please provide a password.")
                return None, True  # Indicate that the file is encrypted
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        # If no text found, assume it's scanned and use OCR
        if not text.strip():
            st.info("No digital text found. Attempting OCR on scanned document...")
            file.seek(0)
            images = convert_from_bytes(file.getvalue())
            for image in images:
                text += pytesseract.image_to_string(image) + "\n"
        return text, False
    except Exception as e:
        st.error(f"Error extracting text: {e}")
        return "", False

def generate_diff_html(text1, text2):
    """
    Uses difflib to create an HTML diff between two texts.
    - Additions: green background.
    - Deletions: red background.
    - Modification hints: yellow background.
    """
    diff = list(difflib.ndiff(text1.splitlines(), text2.splitlines()))
    html_diff = ""
    for line in diff:
        if line.startswith("+ "):
            html_diff += f'<span style="background-color: #d4fcbc;">{line[2:]}</span><br>'
        elif line.startswith("- "):
            html_diff += f'<span style="background-color: #fbb6c2;">{line[2:]}</span><br>'
        elif line.startswith("? "):
            html_diff += f'<span style="background-color: #fef3b7;">{line[2:]}</span><br>'
        else:
            html_diff += f'{line[2:]}<br>'
    return html_diff

# --- File 1 Upload ---
st.subheader("File 1")
file1 = st.file_uploader("Upload File 1", type=["pdf", "txt"])
password1 = None
if file1 is not None and file1.type == "application/pdf":
    if st.checkbox("File 1 is password protected?"):
        password1 = st.text_input("Enter password for File 1", type="password")

# --- File 2 Upload ---
st.subheader("File 2")
file2 = st.file_uploader("Upload File 2", type=["pdf", "txt"])
password2 = None
if file2 is not None and file2.type == "application/pdf":
    if st.checkbox("File 2 is password protected?"):
        password2 = st.text_input("Enter password for File 2", type="password")

if file1 and file2:
    # Extract text from File 1
    if file1.type == "application/pdf":
        text1, enc1 = extract_text(file1, password=password1)
    else:
        text1 = file1.getvalue().decode("utf-8")
        enc1 = False

    # Extract text from File 2
    if file2.type == "application/pdf":
        text2, enc2 = extract_text(file2, password=password2)
    else:
        text2 = file2.getvalue().decode("utf-8")
        enc2 = False

    # Warn user if a file is encrypted but no password was provided
    if enc1:
        st.info("File 1 is encrypted. Please provide a password above and re-upload the file.")
    if enc2:
        st.info("File 2 is encrypted. Please provide a password above and re-upload the file.")

    if text1 is not None and text2 is not None:
        st.subheader("Differences")
        diff_html = generate_diff_html(text1, text2)
        st.markdown(diff_html, unsafe_allow_html=True)
        
        st.subheader("Extracted Text from File 1")
        st.text_area("File 1 Text", text1, height=200)
        
        st.subheader("Extracted Text from File 2")
        st.text_area("File 2 Text", text2, height=200)
