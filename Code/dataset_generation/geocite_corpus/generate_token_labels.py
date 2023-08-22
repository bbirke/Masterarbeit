from glob import glob
import pandas as pd
import os
from pathlib import Path
import json
from tqdm import tqdm
from collections import Counter


labels = ['other', 'abstract', 'author', 'caption', 'date', 'equation', 'figure', 'footer', 'list', 'paragraph', 'reference',
          'section', 'table', 'title', ]
id2label = {k: v for k, v in enumerate(labels)}
label2id = {v: k for k, v in enumerate(labels)}


def most_frequent(occurence_list):
    occurence_count = Counter(occurence_list)
    return occurence_count.most_common(1)[0][0]


if __name__ == '__main__':
    json_files = []
    with open('labeled_finished/all.jsonl', 'r', encoding='utf-8') as f:
        contents = f.readlines()
        for line in tqdm(contents):
            labels = []
            j = json.loads(line)
            splits = j['text'].split('\n')
            comment = j['Comments']
            if comment:
                continue
            csv_file = splits[0][4:]
            txt = splits[-1]
            offset = len(splits[0]) + len(splits[1]) + len(splits[2]) + len(splits[3]) + 4
            mask = ['paragraph'] * len(txt)
            #print(len(mask))
            for start, end, label in j['label']:
                #print(start, end)
                mask[start - offset:end - offset] = [label.replace('\'', '')] * (end - start)
            # print(j['text'])
            token = []
            label = []
            for c, m in zip([c for c in txt], mask):
                #print(c, m)
                if not token:
                    if c == ' ':
                        continue
                    token.append(c)
                    label.append(m)
                    continue

                if c == ' ':
                    labels.append(most_frequent(label))
                    token = []
                    label = []
                else:
                    token.append(c)
            if token:
                labels.append(most_frequent(label))
            #print(labels)

            df = pd.read_csv('csv/' + csv_file)
            if len(labels) != len(df):
                print(csv_file)
                break
            df['label'] = labels
            df.to_csv('csv_label/' + csv_file, index=False)
            #print(df)
            #break

            #print(len(mask))
            #print(mask)
            # print(j['label'])
            # print(start)
            # print(end)
            # print(label)