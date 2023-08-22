from glob2 import glob
from tqdm import tqdm
from os.path import basename
import pathlib
import requests
from bs4 import BeautifulSoup
import urllib


pathlib.Path("xl/pdf").mkdir(exist_ok=True)
pathlib.Path("xl/pdf_raw").mkdir(exist_ok=True)
pathlib.Path("xl/xml").mkdir(exist_ok=True)

url_ssoar = "https://www.ssoar.info/ssoar/handle/document/{}"
url_metadata = "https://www.ssoar.info/OAIHandler/request?verb=GetRecord&identifier=oai:gesis.izsoz.de:document/{}&metadataPrefix=oai_dc_de"
url_records_geography = "https://www.ssoar.info/OAIHandler/request?verb=ListIdentifiers&resumptionToken=oai_dc///ddc:900/{}"

for page in tqdm(range(200, 5000, 100)):
    response = requests.get(url_records_geography.format(str(page)))
    for ident in BeautifulSoup(response.content, features="xml").find_all('identifier'):
        doc = ident.getText()
        identifier = doc.rsplit('/', 1)[-1]
        if pathlib.Path(f"xl/pdf_raw/{identifier}.pdf").exists() and pathlib.Path(f"xl/xml/{identifier}.xml").exists():
            continue
        response = requests.get(url_ssoar.format(identifier))
        soup = BeautifulSoup(response.content, features="lxml")
        file_section = soup.find(id="file-section-entry")
        if not file_section:
            continue

        try:
            pdf_link = file_section.find("a").get('href')
            req = urllib.request.Request(pdf_link.replace(" ", "%20"), f"xl/pdf_raw/{identifier}.pdf", method='HEAD')
            flink = urllib.request.urlopen(req)
            content_length = flink.headers['Content-Length']
            size = int(content_length)/10e6
            if size > 5:
                print('long file')
                continue
            urllib.request.urlretrieve(pdf_link.replace(" ", "%20"), f"xl/pdf_raw/{identifier}.pdf")
            urllib.request.urlretrieve(url_metadata.format(identifier).replace(" ", "%20"), f"xl/xml/{identifier}.xml")
        except:
            print('uhoh')