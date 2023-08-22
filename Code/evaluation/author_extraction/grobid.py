from glob2 import glob
from tqdm import tqdm
from os.path import basename
import pathlib
import requests

api_url = "http://localhost:8080/api/processHeaderDocument/"
path_list_pdf = glob("D:/Projects/Masterarbeit/evaluation/ssoar/xl/pdf/*.pdf")

params = {
    "consolidateHeader": 0,
    "includeRawAffiliations": 1,
}
for p in tqdm(path_list_pdf):
    identifier = basename(p).split(".")[0]
    if pathlib.Path(f"xl/grobid_dl/{identifier}.tei").exists():
        continue
    files = {'input': open(p, 'rb')}
    response = requests.post(api_url, params=params, files=files)
    if response.status_code == requests.status_codes.codes.OK:
        with open(f"xl/grobid_dl/{identifier}.tei", "w", encoding='utf-8') as f:
            f.write(response.text)