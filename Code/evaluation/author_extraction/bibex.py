from glob2 import glob
from tqdm import tqdm
from os.path import basename
import pathlib
import requests
import json
import PyPDF2

api_url = "https://hyperion.bbirke.de/api/process/pdf/"
path_list_pdf = glob("D:/Projects/Masterarbeit/evaluation/ssoar/xl/pdf/*.pdf")

params = {
    "ocr": "false",
    "ocr_lang": "deu",
    "return_tokens": "false",
    "title_page": 0,
}
for p in tqdm(path_list_pdf[1468:]):
    identifier = basename(p).split(".")[0]
    if pathlib.Path(f"xl/bibex/{identifier}.json").exists():
        continue
    with open(p, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        if len(reader.pages) > 15:
            print('large pdf')
            continue
    files = {'file': open(p, 'rb')}
    response = requests.post(api_url, params=params, files=files)
    if response.status_code == requests.status_codes.codes.OK:
        with open(f"xl/bibex/{identifier}.json", "w", encoding='utf-8') as f:
            f.write(json.dumps(json.loads(response.text), indent=4))

