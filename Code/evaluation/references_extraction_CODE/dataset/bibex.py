from glob import glob
from tqdm import tqdm
from os.path import basename
import pathlib
import requests
import json
from PyPDF2 import PdfWriter, PdfReader

api_url = "https://hyperion.bbirke.de/api/process/extract/document/"
path_list_pdf = glob("D:/Projects/Masterarbeit/evaluation/references_extraction_DATA/PDF_papers/*.pdf")

params = {
    "ocr": "false",
    "ocr_lang": "deu",
    "return_tokens": "false",
    "title_page": 0,
}

pdf2delete = {
    "AGR-BIO-SCI_1": [5, 6],
    "EAR-PLA-SCI_20": [3]
}

for p in tqdm(path_list_pdf):
    identifier = basename(p).split(".")[0]
    if pathlib.Path(f"bibex/{identifier}.json").exists():
        continue

    # if identifier in pdf2delete:
    #
    #     infile = PdfReader(pathlib.Path(p))
    #     output = PdfWriter()
    #
    #     for i in range(len(infile.pages)):
    #         if i not in pdf2delete[identifier]:
    #             p = infile.pages[i]
    #             output.add_page(p)
    #
    #     with open(identifier + '.pdf', 'wb') as f:
    #         output.write(f)
    files = {'file': open(p, 'rb')}
    response = requests.post(api_url, params=params, files=files)
    if response.status_code == requests.status_codes.codes.OK:
        with open(f"bibex/{identifier}.json", "w") as f:
            f.write(json.dumps(json.loads(response.text), indent=4))