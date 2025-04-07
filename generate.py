from reportlab.pdfgen import canvas

def create_pdf(filename, content):
    c = canvas.Canvas(filename)
    # Starting position on the page
    x, y = 50, 750
    for line in content.splitlines():
        c.drawString(x, y, line)
        y -= 20  # Move to the next line
    c.save()

# Content for the first PDF
content1 = """Hello, this is sample PDF 1.
This document contains some example text.
Line unique to PDF 1: Welcome to our demo!"""

# Content for the second PDF
content2 = """Hello, this is sample PDF 2.
This document contains some example text.
Line unique to PDF 2: Enjoy exploring the differences!"""

create_pdf("sample1.pdf", content1)
create_pdf("sample2.pdf", content2)

print("Sample PDFs created: sample1.pdf and sample2.pdf")