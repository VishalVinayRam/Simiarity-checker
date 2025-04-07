import streamlit as st
import PyPDF2
import difflib
import openai
import os

# Make sure to install openai: pip install openai
# Set your OpenAI API key as an environment variable before running the app.
openai.api_key = os.getenv("sk--25elGAnH0nP4Ku3Rab4Mg5BLY6wqMDflbkffwAYBpT3BlbkFJAfgIj8BGhKXLJl4At3ciqTdS4cnBH6W6x1-UcAi2YA")

def extract_text_from_pdf(file):
    """
    Extracts text from a PDF file using PyPDF2.
    If the PDF is scanned (image-based), text extraction may fail.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error("Failed to extract text. Ensure the PDF is not scanned or image-based.")
        raise e

def generate_diff_html(text1, text2):
    """
    Generates an HTML representation of the differences between two texts.
    - Added lines are highlighted in green.
    - Removed lines are highlighted in red.
    - Modification hint lines are highlighted in yellow.
    
    Returns the HTML string and counts of additions, deletions, and modifications.
    """
    diff = list(difflib.ndiff(text1.splitlines(), text2.splitlines()))
    html_diff = ""
    additions = deletions = modifications = 0
    
    for line in diff:
        # Lines starting with "+ " indicate additions.
        if line.startswith("+ "):
            html_diff += f'<span style="background-color: #d4fcbc;">{line[2:]}</span><br>'
            additions += 1
        # Lines starting with "- " indicate deletions.
        elif line.startswith("- "):
            html_diff += f'<span style="background-color: #fbb6c2;">{line[2:]}</span><br>'
            deletions += 1
        # Lines starting with "? " provide modification hints.
        elif line.startswith("? "):
            html_diff += f'<span style="background-color: #fef3b7;">{line[2:]}</span><br>'
            modifications += 1
        else:
            html_diff += f'{line[2:]}<br>'
    
    return html_diff, additions, deletions, modifications

def compare_texts_with_llm(text1, text2):
    """
    Uses the OpenAI API to semantically compare two texts.
    The prompt instructs the LLM to analyze the differences and provide
    a detailed summary highlighting additions, deletions, and modifications.
    """
    prompt = f"""
    You are an expert editor. Compare the following two documents and provide a detailed analysis of their differences.
    Highlight what has been added, removed, or modified in a clear and concise manner.

    --- Document 1 ---
    {text1}

    --- Document 2 ---
    {text2}

    Provide your analysis in bullet points.
    """
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # You can change this based on your requirements.
            prompt=prompt,
            max_tokens=500,
            temperature=0.5,
        )
        result = response.choices[0].text.strip()
        return result
    except Exception as e:
        return f"Error with LLM comparison: {e}"

# Streamlit UI
st.title("PDF Document Diff Tool with LLM Comparison")
st.write("Upload two PDF documents to visualize differences and get a semantic comparison from an LLM.")

# Allow users to upload two PDFs.
pdf_file1 = st.file_uploader("Upload PDF 1", type="pdf")
pdf_file2 = st.file_uploader("Upload PDF 2", type="pdf")

if pdf_file1 and pdf_file2:
    try:
        # Extract text from the uploaded PDFs.
        text1 = extract_text_from_pdf(pdf_file1)
        text2 = extract_text_from_pdf(pdf_file2)
        
        # Traditional diff using difflib.
        st.subheader("Traditional Diff")
        diff_html, additions, deletions, modifications = generate_diff_html(text1, text2)
        st.markdown(diff_html, unsafe_allow_html=True)
        
        st.subheader("Summary Report")
        st.write(f"**Additions:** {additions}")
        st.write(f"**Deletions:** {deletions}")
        st.write(f"**Modifications:** {modifications}")
        
        # Semantic comparison using LLM.
        st.subheader("LLM Semantic Comparison")
        llm_diff = compare_texts_with_llm(text1, text2)
        st.write(llm_diff)
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
