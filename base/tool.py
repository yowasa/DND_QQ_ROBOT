# 工具类


import random

import requests


# 获得属性加值
def get_check_plus(attr):
    attr = int(attr)
    if attr - 10 >= 0:
        return int((attr - 10) / 2)
    if attr - 10 < 0:
        return int((attr - 11) / 2)


# 通过request下载图片,返回图片名称
def requests_download_url(url, path):
    name = url[url.rfind("/") + 1:]
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        open(path + name, 'wb').write(r.content)
    return name


# 通过request下载图片,返回图片名称 列表操作
def requests_download_url_list(url_list, path):
    return [requests_download_url(url, path) for url in url_list]


# 得到正负10%的晃动比例，生成新size
def float_tenpercent_range(x, y):
    level = round(random.random() * 0.2 + 0.9, 2)
    return int(x * level), int(y * level)
