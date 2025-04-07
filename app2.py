import streamlit as st
import PyPDF2
import difflib
import openai
import os
from pdf2image import convert_from_bytes
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()  # This loads variables from .env into os.environ
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable in your .env file")
openai.api_key = openai_api_key

@st.cache_resource
def load_caption_model():
    # This function loads the image captioning model once.
    return pipeline("image-to-text")

# Now, the pipeline is available as "pipeline" from the transformers package.
captioner = load_caption_model()

def extract_text_from_pdf(file):
    """
    Extracts text from a PDF file using PyPDF2.
    Attempts to decrypt if necessary.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        if pdf_reader.is_encrypted:
            try:
                pdf_reader.decrypt('')
            except Exception as de:
                st.error("Failed to decrypt PDF. It might be password protected.")
                raise de
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
    Generates an HTML representation of differences between two texts.
    Highlights:
    - Additions in green
    - Deletions in red
    - Modification hints in yellow
    Returns the HTML string and counts.
    """
    diff = list(difflib.ndiff(text1.splitlines(), text2.splitlines()))
    html_diff = ""
    additions = deletions = modifications = 0
    
    for line in diff:
        if line.startswith("+ "):
            html_diff += f'<span style="background-color: #d4fcbc;">{line[2:]}</span><br>'
            additions += 1
        elif line.startswith("- "):
            html_diff += f'<span style="background-color: #fbb6c2;">{line[2:]}</span><br>'
            deletions += 1
        elif line.startswith("? "):
            html_diff += f'<span style="background-color: #fef3b7;">{line[2:]}</span><br>'
            modifications += 1
        else:
            html_diff += f'{line[2:]}<br>'
    
    return html_diff, additions, deletions, modifications

def compare_texts_with_llm(text1, text2):
    """
    Uses the OpenAI ChatCompletion API to semantically compare two texts.
    """
    prompt = f"""
    Compare the following two documents and provide a detailed analysis of their differences.
    Highlight what has been added, removed, or modified in a clear and concise manner.

    --- Document 1 ---
    {text1}

    --- Document 2 ---
    {text2}

    Provide your analysis in bullet points.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert editor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.5,
        )
        result = response.choices[0].message["content"].strip()
        return result
    except Exception as e:
        return f"Error with LLM comparison: {e}"

def extract_images_from_pdf(file):
    """
    Converts PDF pages into images using pdf2image.
    Ensure you have poppler installed on your system.
    """
    try:
        images = convert_from_bytes(file.getvalue())
        return images
    except Exception as e:
        st.error("Failed to extract images from PDF.")
        raise e

def generate_image_captions(images):
    """
    Generates a caption for each image using a Hugging Face image captioning model.
    """
    captions = []
    for i, image in enumerate(images):
        caption = captioner(image)[0]['generated_text']
        captions.append(f"Page {i+1}: {caption}")
    return "\n".join(captions)

def compare_image_captions_with_llm(captions1, captions2):
    """
    Uses the OpenAI ChatCompletion API to compare image captions from two PDFs.
    """
    prompt = f"""
    Compare the following two sets of image descriptions generated from PDF documents.
    Provide a detailed analysis of differences between the images in each document, highlighting any changes in content, layout, or style.

    --- PDF Document 1 Image Descriptions ---
    {captions1}

    --- PDF Document 2 Image Descriptions ---
    {captions2}

    Provide your analysis in bullet points.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert image analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.5,
        )
        result = response.choices[0].message["content"].strip()
        return result
    except Exception as e:
        return f"Error with LLM image comparison: {e}"

# Streamlit UI
st.title("PDF Diff Tool with LLM for Text and Image Comparison")
st.write("Upload two PDF documents to visualize text differences and compare images using LLM.")

# File upload widgets for two PDFs.
pdf_file1 = st.file_uploader("Upload PDF 1", type="pdf")
pdf_file2 = st.file_uploader("Upload PDF 2", type="pdf")

if pdf_file1 and pdf_file2:
    try:
        # Text extraction and diff
        text1 = extract_text_from_pdf(pdf_file1)
        text2 = extract_text_from_pdf(pdf_file2)
        
        st.subheader("Traditional Text Diff")
        diff_html, additions, deletions, modifications = generate_diff_html(text1, text2)
        st.markdown(diff_html, unsafe_allow_html=True)
        
        st.subheader("Text Summary Report")
        st.write(f"**Additions:** {additions}")
        st.write(f"**Deletions:** {deletions}")
        st.write(f"**Modifications:** {modifications}")
        
        st.subheader("LLM Semantic Text Comparison")
        llm_diff = compare_texts_with_llm(text1, text2)
        st.write(llm_diff)
        
        # Image extraction and comparison
        st.subheader("Image Comparison")
        images1 = extract_images_from_pdf(pdf_file1)
        images2 = extract_images_from_pdf(pdf_file2)
        
        if images1 and images2:
            st.write("Generating captions for PDF 1 images...")
            captions1 = generate_image_captions(images1)
            st.write(captions1)
            
            st.write("Generating captions for PDF 2 images...")
            captions2 = generate_image_captions(images2)
            st.write(captions2)
            
            st.subheader("LLM Semantic Image Comparison")
            llm_image_diff = compare_image_captions_with_llm(captions1, captions2)
            st.write(llm_image_diff)
        else:
            st.info("No images found in one or both PDFs.")
        
    except Exception as e:
        st.error(f"An error occurred: {e}")