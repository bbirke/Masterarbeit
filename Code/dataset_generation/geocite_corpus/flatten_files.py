from glob import glob
from pathlib import Path
import shutil


if __name__ == '__main__':
    pdf_files = glob('geocite_pdfs/**/*.pdf', recursive=True)
    for p in pdf_files:
        shutil.move(p, 'geocite_pdfs/' + Path(p).stem + '.pdf')
