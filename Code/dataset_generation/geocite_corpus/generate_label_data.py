from glob import glob
import pandas as pd
import os
from pathlib import Path
from tqdm import tqdm
import json


if __name__ == '__main__':
    csv_files = glob('csv/*.csv')
    with open('labeled_texts_processed/batch_2.jsonl', 'w', encoding='utf-8') as f:
        for p in tqdm(csv_files):
            df = pd.read_csv(p, encoding='utf-8')
            token = df['token'].astype(str).tolist()
            txt = ' '.join(token)
            out_dict = {
                "text": f'### {os.path.basename(p)}\n'
                        + '### batch 2\n'
                        + f'### http://hyperion.bbirke.de/data/geocite/pdfs_2/{os.path.basename(p)[:-6]}\n\n'
                        + txt,
                "label": None
            }
            f.write(json.dumps(out_dict, ensure_ascii=False) + "\n")
