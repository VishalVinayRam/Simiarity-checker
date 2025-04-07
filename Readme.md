Installation and Usage Instructions

Prerequisites:
- Python 3.8 or later
- Pip (Python's package installer)
- Tesseract OCR:
    * Windows: Download and install from https://github.com/tesseract-ocr/tesseract/wiki
    * macOS: brew install tesseract
    * Linux: sudo apt-get install tesseract-ocr
- Poppler:
    * Windows: Download from http://blog.alivate.com.au/poppler-windows/
    * macOS: brew install poppler
    * Linux: sudo apt-get install poppler-utils

Setup Instructions:
1. Clone the repository:
   git clone https://github.com/VishalVinayRam/Simiarity-checker.git

2. Create a virtual environment (recommended):
   python -m venv venv
   - On Windows: venv\\Scripts\\activate
   - On macOS/Linux: source venv/bin/activate

3. Install dependencies:
   pip install streamlit PyPDF2 pdf2image pytesseract openai python-dotenv fpdf


(Optional and needed only when you want to use the chatbot)
4. Create a .env file in your project folder with:
   OPENAI_API_KEY=your_openai_api_key_here

5. Run the app:
   streamlit run app.py
   Then open http://localhost:8501 in your browser.

Usage Instructions:
- Text Comparison:
   * Upload two files (PDF or text).
   * For encrypted PDFs, check the box and enter the password.
   * The tool extracts text (using OCR if needed) and shows differences.
   * View differences inline or side-by-side.

- Chatbot Assistant:
   * Click "Open Chatbot" to chat.
   * Ask questions or request a summary.
   * The chatbot uses OpenAI's API to answer and summarize.

Technical Details:
- Uses PyPDF2 for PDF text extraction.
- Uses OCR (pytesseract) when no text is found.
- Compares texts with difflib.
- Chatbot uses OpenAI's API.
- Libraries: Streamlit, PyPDF2, pdf2image, pytesseract, OpenAI API, python-dotenv, fpdf.

Future improvement:
- Improve OCR accuracy.
- Adding image support 
- Making chatbot more functional
- Attach a web rag to chatbot to get information based on the text and answere question based on the internet 
- Improve the UI
