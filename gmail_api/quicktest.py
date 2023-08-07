import PyPDF2

def reset_eof_of_pdf_return_stream(pdf_stream_in:list):
    # find the line position of the EOF
    x: bytes = pdf_stream_in[-1]
    xs = x.decode()
    xs += '%%EOF'
    pdf_stream_in[-1] = xs.encode()
    # return the list up to that point

    return pdf_stream_in

with open('adjuntos/URSULINA DE LA CONCEPCION DELGADO DE GARZON BASAL.pdf', 'rb') as p:
   txt = (p.readlines())

# get the new list terminating correctly
txtx = reset_eof_of_pdf_return_stream(txt)

# write to new pdf
with open('URSULINA DE LA CONCEPCION DELGADO DE GARZON BASAL.pdf', 'wb') as f:
   f.writelines(txtx)

fixed_pdf = PyPDF2.PdfReader('URSULINA DE LA CONCEPCION DELGADO DE GARZON BASAL.pdf')
