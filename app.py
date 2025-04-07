import streamlit as st
import PyPDF2
import difflib
import os
from dotenv import load_dotenv
from pdf2image import convert_from_bytes
import pytesseract
import openai
from openai import ChatCompletion


# Load environment variables from .env file.
load_dotenv()

# Set OpenAI API key from environment variable.
if not openai_api_key:
    st.error("Please set the OPENAI_API_KEY environment variable in your .env file.")
openai.api_key = openai_api_key

# =====================================
# Existing Text Comparison Code
# =====================================


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
file1 = st.file_uploader("Upload File 1", type=["pdf", "txt"], key="file1")
password1 = None
if file1 is not None and file1.type == "application/pdf":
    if st.checkbox("File 1 is password protected?", key="pw1"):
        password1 = st.text_input("Enter password for File 1", type="password", key="pass1")

# --- File 2 Upload ---
st.subheader("File 2")
file2 = st.file_uploader("Upload File 2", type=["pdf", "txt"], key="file2")
password2 = None
if file2 is not None and file2.type == "application/pdf":
    if st.checkbox("File 2 is password protected?", key="pw2"):
        password2 = st.text_input("Enter password for File 2", type="password", key="pass2")

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

# =====================================
# New Chatbot Code
# =====================================

st.markdown("---")
st.header("Chatbot Assistant")

# Initialize session state for chatbot if not already present.
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chatbot_open" not in st.session_state:
    st.session_state.chatbot_open = False

# Button to toggle the chatbot window.
if st.button("Open Chatbot"):
    st.session_state.chatbot_open = not st.session_state.chatbot_open

# Chatbot Interface
if st.session_state.chatbot_open:
    st.subheader("Chatbot")
    
    # Display chat history.
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Bot:** {msg['content']}")

    # Input area for new messages.
    user_input = st.text_input("Ask a question or type your message here...", key="chat_input")
    if st.button("Send", key="send_button") and user_input:
        # Append the user's message to the history.
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Prepare messages for OpenAI including a system prompt.
        messages = [{"role": "system", "content": "You are a helpful assistant that can answer questions and summarize conversations."}]
        messages.extend(st.session_state.chat_history)
        
        # Get the bot's response using the new interface.
        try:
            response = ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.7,
            )
            answer = response.choices[0].message["content"].strip()
        except Exception as e:
            answer = f"Error: {e}"
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.experimental_rerun()
    
    # Button to summarize the conversation.
    if st.button("Summarize Conversation"):
        conversation_text = "\n".join([f'{msg["role"].capitalize()}: {msg["content"]}' for msg in st.session_state.chat_history])
        summary_prompt = f"Summarize the following conversation in a few bullet points:\n\n{conversation_text}"
        try:
            summary_response = ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert summarization assistant."},
                    {"role": "user", "content": summary_prompt}
                ],
                max_tokens=100,
                temperature=0.5,
            )
            summary = summary_response.choices[0].message["content"].strip()
        except Exception as e:
            summary = f"Error: {e}"
        st.markdown("### Conversation Summary")
        st.write(summary)