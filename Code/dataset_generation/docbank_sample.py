import numpy as np
from glob import glob
import os
import shutil
from pathlib import Path

import pandas as pd

docs_authors = []
with open('authors.txt', 'r') as f:
    for line in f.readlines():
        docs_authors.append(line.strip())

docs_none = []
with open('none.txt', 'r') as f:
    for line in f.readlines():
        docs_none.append(line.strip())

docs_ref = []
with open('refs.txt', 'r') as f:
    for line in f.readlines():
        docs_ref.append(line.strip())

np.random.seed(33)
sample_authors = np.random.choice(docs_authors, 500, replace=False).tolist()
sample_none = np.random.choice(docs_none, 500, replace=False).tolist()
sample_ref = np.random.choice(docs_ref, 500, replace=False).tolist()

samples_docbank = sample_authors + sample_none + sample_ref

path_docbank_txt = 'D:/Projects/Masterarbeit/Data/DocBank_500K_txt/'
path_docbank_img = 'D:/Projects/Masterarbeit/Data/DocBank_500K_resized_img/'

pairs = []

columns = ['token', 'x0', 'y0', 'x1', 'y1', 'r', 'g', 'b', 'font', 'label']
for sample in samples_docbank:
    df = pd.read_csv(path_docbank_txt + sample, names=columns, header=None, sep='\t', quotechar=' ')
    df[['token', 'x0', 'y0', 'x1', 'y1', 'label']].to_csv('txt/' + os.path.basename(sample)[:-4] + '_docbank.csv', index=False)
    shutil.copy(path_docbank_img + sample[:-4] + '_ori_224.jpg', 'img/' + sample[:-4] + '_docbank.jpg')
    pairs.append((os.path.basename(sample)[:-4] + '_docbank.csv', sample[:-4] + '_docbank.jpg'))
    #print(sample[:-4])
    #break

geocite_samples = glob('../geocite/csv_label/*.csv')
print(len(geocite_samples))
path_train_txt = Path('train/txt/')
path_train_txt.mkdir(parents=True)
path_train_img = Path('train/img/')
path_train_img.mkdir(parents=True)
path_test_txt = Path('test/txt/')
path_test_txt.mkdir(parents=True)
path_test_img = Path('test/img/')
path_test_img.mkdir(parents=True)

for sample in geocite_samples:
    shutil.copy(sample, 'txt/' + os.path.basename(sample[:-4]) + '_geocite.csv')
    shutil.copy('../geocite/img/' + os.path.basename(sample[:-4]) + '.jpg', 'img/' + os.path.basename(sample[:-4]) + '_geocite.jpg')
    pairs.append((sample[:-4] + '_geocite.csv', os.path.basename(sample[:-4]) + '_geocite.jpg'))
    #print(sample)
    #break

ratio = .1
indices = range(len(pairs))
test_set_indices = np.random.choice(indices, int(ratio * len(pairs)), replace=False).tolist()
test_set = [pairs[i] for i in test_set_indices]
train_set = [x for x in pairs if x not in test_set]

for txt, img in train_set:
    shutil.copy('txt/' + os.path.basename(txt), 'train/txt/')
    shutil.copy('img/' + img, 'train/img/')

for txt, img in test_set:
    shutil.copy('txt/' + os.path.basename(txt), 'test/txt/')
    shutil.copy('img/' + img, 'test/img/')
#print(len(sample_authors + sample_none))