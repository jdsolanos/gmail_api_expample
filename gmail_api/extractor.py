import PyPDF2
import os
import csv
from datetime import datetime

def get_value(page_text, key, ending_block_signs):
    doc_index = page_text.index(key) + len(key)
    print(page_text[doc_index])
    value = ""

    while page_text[doc_index] in ending_block_signs:
        doc_index+=1

    while page_text[doc_index] not in ending_block_signs and doc_index!=len(page_text)-1:
        value+=page_text[doc_index]
        doc_index+=1

    if doc_index==len(page_text)-1:
        value+=page_text[doc_index]
    return value
 
def reset_eof_of_pdf_return_stream(pdf_stream_in:list):
    # find the line position of the EOF
    for i, x in enumerate(pdf_stream_in):
        if b'%%EOF' in x:
            actual_line = len(pdf_stream_in)-i
            print(f'EOF found at line position {-i} = actual {actual_line}, with value {x}')
            break

    # return the list up to that point
    return pdf_stream_in[:actual_line]

enfermedades = ["arritmia",
                "cardio", 
                "ductus",
                "arterio",
                "ECV",
                "ACV",
                "cerebro",
                "hiperten",
                "HTA",
                "infarto",
                "isque",
                "transitorio",
                "ictus",
                "fibrilac",
                "fluter"
                ]

lista_adjuntos = os.listdir("adjuntos")
lista_pdfs = [file_name for file_name  in lista_adjuntos if ".pdf" in file_name]
ending_block_signs= ["\n","\t"," ",")"]
hoja_excel = [
    ["documento","comorbilidades", "IAH","fecha_estudio","fecha_correo","nombre_archivo"]
]
error_excel = [
    ["archivo","error"]
]
for file_name in lista_pdfs:
    pdf_file_obj = open(f'adjuntos/{file_name}', 'rb')
    splited_file_name = file_name.split("_fecha_")
    real_file_name = splited_file_name[0]+".pdf"
    mail_date = splited_file_name[1].replace(".pdf","")
    try:
        mail_date =  datetime.fromtimestamp(int(mail_date)/1000).strftime('%Y-%m-%d') 
    except Exception as e:
        print("error en", file_name)
        error_excel.append([file_name,e])
        continue
    print(mail_date)
    print(file_name)
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
    except Exception as e:
        print("error en", file_name)
        error_excel.append([file_name,e])
        continue
    document = ""
    special_words = "NO"
    iah = "N/A"
    studio_date = ""

    for page in pdf_reader.pages:
        try:
            page_text = page.extract_text()
        except Exception as e:
            error_excel.append([file_name,e])
            continue
        if "D.I. No."  in page_text:
            document = get_value(page_text, "D.I. No.", ending_block_signs)
            break
        if "Documento:" in page_text:
            document = get_value(page_text, "Documento:", ending_block_signs)
            break
        if "DOCUMENTO:" in page_text:
            document = get_value(page_text, "DOCUMENTO:", ending_block_signs)
            break
        if "d.I. No."  in page_text:
            document = get_value(page_text, "d.I. No.", ending_block_signs)
            break
        if "documento:" in page_text:
            document = get_value(page_text, "documento:", ending_block_signs)
            break

    if document == "":
        print("otra forma de documento")
        error_excel.append([file_name,"no hay documento"])
        continue
    
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if "Fecha del estudio:" in page_text:
            studio_date = get_value(page_text, "Fecha del estudio:", ending_block_signs)
            break
        if "Fecha:" in page_text:
            studio_date = get_value(page_text, "Fecha:", ending_block_signs)
            break

    if studio_date =="":
        error_excel.append([file_name,"no hay fecha de estudio"])
        continue
    
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if "IAH:" in page_text:
            iah = get_value(page_text, "IAH:", ending_block_signs)
            break
    
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        for word in enfermedades:
            if word in page_text:
                special_words = "YES"
                break
    hoja_excel.append([document, special_words, iah, studio_date, mail_date, real_file_name])
    print(f"documento: {document}, palabras especiales: {special_words}, IAH: {iah}")
    
    pdf_file_obj.close()


with open('datos_totales.csv', mode='w') as employee_file:
    employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for row in hoja_excel:
        employee_writer.writerow(row)

with open('errores_totales.csv', mode='w') as employee_file:
    employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for row in error_excel:
        employee_writer.writerow(row)