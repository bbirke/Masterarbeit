from pathlib import Path
from glob import glob
from tqdm import tqdm
import zipfile
import numpy as np
import os


path_resized_img = 'D:/Projects/Masterarbeit/Data/DocBank_500K_resized_img'
path_txt = 'D:/Projects/Masterarbeit/Data/DocBank_500K_txt'
path_chunks = 'D:/Projects/Masterarbeit/Data/chunks'
error_file = 'D:/Projects/Masterarbeit/Data/errors_chunks.log'
seed = 33
chunk_size = 50000


if __name__ == '__main__':
    path_list_resized_img = glob(path_resized_img + '/*')
    np.random.seed(seed)
    random_list = np.random.choice(path_list_resized_img, size=2000, replace=False)
    validation_list = random_list[1000:]
    test_list = random_list[:1000]
    zip_file_val = zipfile.ZipFile(path_chunks + f'/docbank_validation.zip', 'w')
    for p in validation_list:
        p_txt = path_txt + '/' + Path(p).stem[:-8] + '.txt'
        zip_file_val.write(p, 'DocBank_500K_resized_img_val/' + os.path.basename(p), compress_type=zipfile.ZIP_DEFLATED)
        zip_file_val.write(p_txt, 'DocBank_500K_txt_val/' + os.path.basename(p_txt), compress_type=zipfile.ZIP_DEFLATED)
    zip_file_val.close()
    zip_file_test = zipfile.ZipFile(path_chunks + f'/docbank_test.zip', 'w')
    for p in test_list:
        p_txt = path_txt + '/' + Path(p).stem[:-8] + '.txt'
        zip_file_test.write(p, 'DocBank_500K_resized_img_test/' + os.path.basename(p), compress_type=zipfile.ZIP_DEFLATED)
        zip_file_test.write(p_txt, 'DocBank_500K_txt_test/' + os.path.basename(p_txt), compress_type=zipfile.ZIP_DEFLATED)
    zip_file_test.close()
    # for chunk_id, index in tqdm(enumerate(range(0, len(path_list_resized_img), chunk_size))):
    #     paths_chunk = path_list_resized_img[index:index + chunk_size]
    #     zip_file = zipfile.ZipFile(path_chunks + f'/docbank_{chunk_id}.zip', 'w')
    #     for p in tqdm(paths_chunk):
    #         if p in random_list:
    #             continue
    #         p_txt = path_txt + '/' + Path(p).stem[:-8] + '.txt'
    #         zip_file.write(p, 'DocBank_500K_resized_img/' + os.path.basename(p), compress_type=zipfile.ZIP_DEFLATED)
    #         zip_file.write(p_txt, 'DocBank_500K_txt/' + os.path.basename(p_txt), compress_type=zipfile.ZIP_DEFLATED)
    #     zip_file.close()
