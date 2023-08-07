import PyPDF2
import os

pdf_file_obj = open(f'ACUÑA ACUÑA MARIA CRISTINA BASAL.pdf', 'rb')

pdf_reader = PyPDF2.PdfReader(pdf_file_obj)

for page in pdf_reader.pages:
    print(page.extract_text())