from PIL import Image
from glob import glob
from pathlib import Path
import multiprocessing as mp


def resize_img(p):
    try:
        image = Image.open(p).convert("RGB")
        #w, h = image.size
        # resize image
        image = image.resize((size, size))
        image.save(path_resized_img + '/' + Path(p).stem + '_224.jpg')
    except:
        print(f'Error converting file: {Path(p).name}')
        with open(error_file, 'a', encoding='utf-8') as f:
            f.writelines(Path(p).name + '\n')


path_ori_img = 'D:/Projects/Masterarbeit/Data/DocBank_500K_ori_img'
path_resized_img = 'D:/Projects/Masterarbeit/Data/DocBank_500K_resized_img'
error_file = 'D:/Projects/Masterarbeit/Data/errors.log'
size = 224
start = 118800

path_list_ori_img = glob(path_ori_img + '/*')

if __name__ == '__main__':
    pool = mp.Pool(mp.cpu_count())
    pool.map(resize_img, path_list_ori_img[start:])
    pool.close()