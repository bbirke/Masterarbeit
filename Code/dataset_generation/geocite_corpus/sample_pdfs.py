from glob import glob
import numpy as np
import shutil
from tqdm import tqdm

np.random.seed(42)
path_pdfs = glob("P:/II Zitationsdatenerhebung/Digitalisate/*/*_rdy/*.pdf")
selected = np.random.choice(path_pdfs, size=200, replace=False)
for s in tqdm(selected):
    shutil.copy(s, "pdf/")
