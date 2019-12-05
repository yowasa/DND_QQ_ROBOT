# 1.导入模块
from robobrowser import RoboBrowser
from filter import msg_route
import requests
import os
import random
from PIL import Image

from pixivpy3 import *

api = AppPixivAPI()

'''
ghs相关功能(未实现)
本周奶子 获取本周月曜日的丰满图片
更多奶子 获取之前一段时间的月曜日的丰满图片
随机色图 随机获取pixiv上排名靠前的图片
'''

env_dist = os.environ
cq_image_file = env_dist.get("cq_image_file")
if not cq_image_file:
    cq_image_file = 'F:\\workspace\\py\\CQP-xiaoi\\酷Q Pro\\data\\image\\'


@msg_route(r'本周奶子$')
def oppai_now(content):
    b = RoboBrowser(history=True)
    b.open('http://twitter.com/Strangestone/media')

    ls = b.find_all(class_='content')

    for each in ls:
        each_text = each.find(class_='TweetTextSize--normal')
        if '月曜日のたわわ' in each_text.text:
            pdiv = each.find(class_='AdaptiveMedia-photoContainer')
            print(pdiv.img.attrs.get('src'))
            return package_img(pdiv.img.attrs.get('src'))


@msg_route(r'更多奶子$')
def more_oppai(content):
    b = RoboBrowser(history=True)
    b.open('http://twitter.com/Strangestone/media')

    ls = b.find_all(class_='content')
    messagee = []
    for each in ls:
        each_text = each.find(class_='TweetTextSize--normal')
        if '月曜日のたわわ' in each_text.text:
            pdiv = each.find(class_='AdaptiveMedia-photoContainer')
            print(pdiv.img.attrs.get('src'))
            messagee.append(package_img(pdiv.img.attrs.get('src')))
    return ''.join(messagee)


@msg_route(r'\.ghs$')
def ghs_pixiv(content):
    try:
        # 没有数据从日排行前三十里随机取一张
        results = api.illust_ranking(mode='day_r18', date=None, offset=None)
        return package_pixiv_img(results.illusts[random.randint(0, 29)])
    except:
        api.login("2508488843@qq.com", "czqq872710284")


@msg_route(r'\.img')
def pixiv_search(content):
    cmd_msg = content.get('cmd_msg').strip()
    try:
        # 没有数据从日排行前三十里随机取一张
        if not cmd_msg:
            results = api.illust_ranking(mode='day', date=None, offset=None)
            return package_pixiv_img(results.illusts[random.randint(0, 29)])
        # 有数据以数据为tag进行搜索，第一页随机取一张展示（排行）
        illust = ten_page_search(cmd_msg)
        return package_pixiv_img(illust)
    except:
        api.login("2508488843@qq.com", "czqq872710284")



def package_img(url):
    name = url[url.rfind("/") + 1:]
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        open(cq_image_file + name, 'wb').write(r.content)
    return f'[CQ:image,file={name}]'


def package_pixiv_img(illust):
    url = illust.image_urls.large
    name = url[url.rfind("/") + 1:]
    api.download(url, path=cq_image_file,replace=True)
    name = trance_png(name,cq_image_file)
    return f'[CQ:image,file={name}]'

def trance_png(name,cq_image_file):
    im = Image.open(cq_image_file+name)
    name=name.replace("jpg","png")
    try:
        im.save(cq_image_file+name, "PNG")
    except IOError:
        pass
    return name


def ten_page_search(cmd_msg):
    illusts = []
    for i in range(0, 9):
        result = api.search_illust(cmd_msg, search_target='partial_match_for_tags', sort='date_desc', duration=None,
                                   offset=i * 30)
        illusts.extend(result.illusts)
    sorted(illusts, key=lambda v: v.total_bookmarks, reverse=True)
    fetch = random.randint(0, 29)
    return illusts[fetch]

