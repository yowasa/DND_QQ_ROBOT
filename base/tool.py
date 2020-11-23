# 工具类


import random

import hashlib
import requests

import zipfile

import imageio
from pygifsicle import optimize
from PIL import Image
import os

# 获得属性加值
def get_check_plus(attr):
    attr = int(attr)
    if attr - 10 >= 0:
        return int((attr - 10) / 2)
    if attr - 10 < 0:
        return int((attr - 11) / 2)

def md5(str):
    m = hashlib.md5()
    m.update(str.encode("utf8"))
    print(m.hexdigest())
    return m.hexdigest()

# 通过request下载图片,返回图片名称
def requests_download_url(url, path):
    name = url[url.rfind("/") + 1:]
    hash_name=md5(name)+'.jpg'
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        open(path + hash_name, 'wb').write(r.content)
    return hash_name


# 通过request下载图片,返回图片名称 列表操作
def requests_download_url_list(url_list, path):
    return [requests_download_url(url, path) for url in url_list]


# 得到正负10%的晃动比例，生成新size
def float_tenpercent_range(x, y):
    level = round(random.random() * 0.2 + 0.9, 2)
    return int(x * level), int(y * level)


# 解压单个文件 src_file:文件目录,dest_dir:目标目录
def unzip_single(src_file, dest_dir):
    zf = zipfile.ZipFile(src_file)
    try:
        zf.extractall(path=dest_dir)
    except RuntimeError as e:
        print(e)
    zf.close()


def package_2_gif(filenames, target_file,fps=12):
    images = []
    for filename in filenames:
        images.append(imageio.imread(filename))
    imageio.mimsave(target_file, images, fps=fps)
    optimize(target_file, options=["--lossy"], colors=64)
    optimize_gif(target_file)


def optimize_gif(target_file):
    size=os.path.getsize(target_file) / (1024 * 1024)
    if size < 6:
        return
    ratio=size/5
    im = Image.open(target_file)
    w, h = im.size
    w_s, h_s = int(w/ratio),int(h/ratio)
    optimize(target_file, options=["--lossy",f'--resize-width={w_s}',f'--resize-width={h_s}'], colors=64)
