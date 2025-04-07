# Universal Text Comparison Tool Documentation

## Prerequisites
- **Python 3.8 or later**
- **Pip** (Python's package installer)
- **Tesseract OCR:**
  - **Windows:** Download and install from [Tesseract OCR](https://github.com/tesseract-ocr/tesseract/wiki)
  - **macOS:** `brew install tesseract`
  - **Linux:** `sudo apt-get install tesseract-ocr`
- **Poppler:**
  - **Windows:** Download from [Poppler Windows](http://blog.alivate.com.au/poppler-windows/)
  - **macOS:** `brew install poppler`
  - **Linux:** `sudo apt-get install poppler-utils`

## Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone https://github.com/VishalVinayRam/Simiarity-checker.git
   cd Simiarity-checker
Create a virtual environment (recommended):
   
      **python -m venv venv
      On Windows:**
      
      **venv\Scripts\activate
      On macOS/Linux:**
      
      source venv/bin/activate
      Install dependencies:
      
      pip install streamlit PyPDF2 pdf2image pytesseract openai python-dotenv fpdf
      (Optional: For Chatbot) Create a .env file in your project folder with:
      
      OPENAI_API_KEY=your_openai_api_key_here
   **Run the app:**
      
      ```bash
       streamlit run app.py
       Then open http://localhost:8501 in your browser.


**Feature**
Usage Instructions
Text Comparison
Upload two files (PDF or text).

For encrypted PDFs, check the box and enter the password.

The tool extracts text (using OCR if needed) and shows differences.

View differences inline or side-by-side.

Chatbot Assistant
Click "Open Chatbot" to start a conversation.

Ask questions or request a summary.

The chatbot uses OpenAI's API to answer and summarize.

**Technical Details**
Text Extraction:
Uses PyPDF2 to extract text from PDFs. If no text is found (e.g., in scanned PDFs), it falls back to OCR using pdf2image and pytesseract.

**Text Comparison:**
Uses Python's difflib to compare texts, with both inline and side-by-side views.

**Chatbot:**
Uses OpenAI's API to provide a Q&A and summarization assistant.

Other Libraries:
Streamlit for the UI, python-dotenv for managing environment variables, and fpdf for generating PDF documentation.

**Future Improvements**
Improve OCR accuracy.

Add support for image-based comparison.

Enhance the chatbot functionality.
Attach a web search module (web rag) to the chatbot to fetch and answer questions based on internet data.
Further improve the UI.
