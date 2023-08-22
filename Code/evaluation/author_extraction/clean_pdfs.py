from PyPDF2 import PdfWriter, PdfReader
import os
from glob2 import glob
from tqdm import tqdm
from os.path import basename

path_list_pdf_raw = glob("xl/pdf_raw/*.pdf")
for p in tqdm(path_list_pdf_raw):
    kbyte = os.stat(p).st_size / 1024
    mbyte = os.stat(p).st_size / 1024 ** 2
    if kbyte < 200 or mbyte > 5:
        continue
    infile = PdfReader(p, 'rb')
    output = PdfWriter()
    for i in range(1, len(infile.pages)):
        page = infile.pages[i]
        output.add_page(page)

        with open(f'xl/pdf/{basename(p)}', 'wb') as f:
            output.write(f)