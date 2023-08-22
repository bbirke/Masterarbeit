from glob2 import glob
from tqdm import tqdm
from os.path import basename
import pathlib
import requests
from bs4 import BeautifulSoup
from Levenshtein import distance

import unicodedata
import re

normalized_char_dict = {
    "Ä": "AE",
    "Ü": "UE",
    "Ö": "OE",
    "ä": "ae",
    "ü": "ue",
    "ö": "oe",
    #"ß": "ss"
}


def remove_accented_chars(text:str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    return text


def strip_umlauts(text: str) -> str:
    for umlaut, replacement in normalized_char_dict.items():
        text = text.replace(umlaut, replacement)
    return text


def remove_punctuation(text: str) -> str:
    return text.replace('.', '')


path_list_tei = glob("D:/Projects/Masterarbeit/evaluation/ssoar/xl/grobid/*.tei")

n_true_authors = 0
n_pred_authors = 0
tp = 0
tn = 0
fp = 0
fn = 0
all_matches = 0
for p in tqdm(path_list_tei):

    p_xml = "xl/xml/" + basename(p).split(".")[0] + ".xml"

    with open(p_xml, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'xml')

    results = soup.find_all('dc:creator')
    if not results:
        continue
    true_authors = []
    for item in results:
        true_authors.append(remove_punctuation(remove_accented_chars(strip_umlauts(item.getText())).lower()))
    n_true_authors += len(true_authors)

    with open(p, encoding='utf-8') as filep:
        bs = BeautifulSoup(filep, "lxml")
    # print(bs.find_all('author'))
    authors = bs.find_all('author')
    pred_authors = []
    for author in authors:
        persnames = author.find_all('persname')
        for persname in persnames:
            first_name = ''
            middle_name = ''
            forenames = persname.find_all('forename')
            #print(forenames)
            for forename in forenames:
                if forename['type'] == 'first':
                    first_name = forename.getText()
                if forename['type'] == 'middle':
                    middle_name = forename.getText()
            surnames = persname.find_all('surname')
            if len(surnames) > 1:
                print('Multiple surnames detected.')

            surname = surnames[0].getText() if surnames else ''
            pred_author = surname + ", " + first_name + " " + middle_name
            pred_author = re.sub(r"\s*[.]\s*", ".",
            remove_punctuation(remove_accented_chars(strip_umlauts(pred_author.strip().lower()))).replace("dr.", ""))
            pred_author = ''.join([i for i in pred_author if not i.isdigit()])
            pred_authors.append(pred_author)

    n_pred_authors += len(pred_authors)

    matches = 0
    for true in true_authors:
        for pred in pred_authors:
            if distance(true, pred) <= 1:
            #if true == pred:
                matches += 1
                continue
    fn += len(true_authors) - matches
    fp += len(pred_authors) - matches
    all_matches += matches

    if matches == 0:
        print(f"No matches found in {basename(p).split('.')[0]}.")
        print("True authors:")
        print(true_authors)
        print("Pred authors:")
        print(pred_authors)
        print("*" * 20)
        print()

    elif matches < len(true_authors) and matches != 0:
        print(f"Partly matches found in {basename(p).split('.')[0]}.")
        print("True authors:")
        print(true_authors)
        print("Pred authors:")
        print(pred_authors)
        print("*" * 20)
        print()

    elif len(pred_authors) - matches > 0:
        print(f"FP found in {basename(p).split('.')[0]}.")
        print("True authors:")
        print(true_authors)
        print("Pred authors:")
        print(pred_authors)
        print("*" * 20)
        print()

    elif len(true_authors) - matches > 0:
        print(f"FN found in {basename(p).split('.')[0]}.")
        print("True authors:")
        print(true_authors)
        print("Pred authors:")
        print(pred_authors)
        print("*" * 20)
        print()


print('All matches ' + str(all_matches))
print('True authors ' + str(n_true_authors))
print('Predicted authors ' + str(n_pred_authors))
print('False positives ' + str(fp))
print('False negatives ' + str(fn))

precicion = all_matches/(all_matches+fp)
recall = all_matches/(all_matches+fn)

print('Precision ' + str(precicion))
print('Recall ' + str(recall))

f1 = (2*all_matches)/((2*all_matches) + fp + fn)

print('F1 ' + str(f1))

    # identifier = basename(p).split(".")[0]
    # if pathlib.Path(f"grobid/{identifier}.tei").exists():
    #     continue
    # files = {'input': open(p, 'rb')}
    # response = requests.post(api_url, params=params, files=files)
    # if response.status_code == requests.status_codes.codes.OK:
    #     with open(f"grobid/{identifier}.tei", "w") as f:
    #         f.write(response.text)