# 1.导入模块
import os
import random

import requests
from PIL import Image
from pixivpy3 import *
from robobrowser import RoboBrowser

from filter import msg_route

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
    cq_image_file = 'F:\\workspace\\py\\CQP-xiaoi2\\酷Q Pro\\data\\image\\'

pixiv_user_name = env_dist.get("pixiv_user_name")
pixiv_password = env_dist.get("pixiv_password")


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


@msg_route(r'(\.|。)gimg')
def group_pixiv_search(content):
    return pixiv_search_common(content, group=True)


@msg_route(r'(\.|。)img')
def pixiv_search(content):
    return pixiv_search_common(content)


@msg_route(r'(\.|。)gghs', need_user=True)
def group_ghs_pixiv(content):
    return ghs_pixiv_common(content, group=True)


@msg_route(r'(\.|。)ghs', need_user=True)
def ghs_pixiv(content):
    return ghs_pixiv_common(content)


def ghs_pixiv_common(content, group=False):
    opt = content.get('sys_user')
    if opt.level < 10:
        return '仅管理员可以使用ghs'
    cmd_msg = content.get('cmd_msg').strip()
    try:
        if not cmd_msg:
            results = api.illust_ranking(mode='day_r18', date=None, offset=None)
            if results.get('error'):
                if True != content.get("retry"):
                    api.login(pixiv_user_name, pixiv_password)
                    content["retry"] = True
                    return ghs_pixiv_common(content, group=group)
                else:
                    return "Pixiv登陆异常"
            # 没有数据从日排行前三十里随机取一张
            return package_pixiv_img(results.illusts[random.randint(0, len(results.illusts) - 1)], group=group)
        else:
            illust = ten_page_search(cmd_msg, r18=True)
            if not illust:
                return "搜索不到结果"
            return package_pixiv_img(illust, group=group)
    except PixivError as pe:
        if True != content.get("retry"):
            api.login(pixiv_user_name, pixiv_password)
            content["retry"] = True
            return ghs_pixiv_common(content)
        else:
            return "Pixiv登陆异常"
    except Exception as ex:
        return "未知异常"


def pixiv_search_common(content, group=False):
    cmd_msg = content.get('cmd_msg').strip()
    try:
        # 没有数据从日排行前三十里随机取一张
        if not cmd_msg:
            results = api.illust_ranking(mode='day', date=None, offset=None)
            if results.get('error'):
                if True != content.get("retry"):
                    api.login(pixiv_user_name, pixiv_password)
                    content["retry"] = True
                    return pixiv_search_common(content, group=group)
                else:
                    return "Pixiv登陆异常"
            if len(results.illusts) == 0:
                return "搜索不到结果"
            return package_pixiv_img(results.illusts[random.randint(0, len(results.illusts) - 1)], group=group)
        # 有数据以数据为tag进行搜索，第一页随机取一张展示（排行）
        illust = ten_page_search(cmd_msg)
        if not illust:
            return "搜索不到结果"
        return package_pixiv_img(illust, group=group)
    except PixivError as pe:
        if True != content.get("retry"):
            api.login(pixiv_user_name, pixiv_password)
            content["retry"] = True
            return pixiv_search_common(content, group=group)
        else:
            return "Pixiv登陆异常"
    except Exception as ex:
        return "未知异常"


def package_img(url):
    name = url[url.rfind("/") + 1:]
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        open(cq_image_file + name, 'wb').write(r.content)
    return f'[CQ:image,file={name}]'


def package_pixiv_img(illust, group=False):
    url = illust.meta_single_page.get('original_image_url')
    if not url:
        urls = []
        for i in illust.meta_pages:
            uu = i.get('image_urls').get('large')
            if uu:
                urls.append(uu)
        ##一组图取全部
        if group:
            img_list = []
            for uurl in urls:
                name = uurl[uurl.rfind("/") + 1:]
                api.download(uurl, path=cq_image_file, replace=True)
                name = trance_png(name, cq_image_file)
                img_list.append(f'[CQ:image,file={name}]')
            return ''.join(img_list)
        else:
            ##一组图随机取一个
            length = len(urls)
            randomNumber = random.randint(0, length - 1)
            uurl = urls[randomNumber]
            name = uurl[uurl.rfind("/") + 1:]
            api.download(uurl, path=cq_image_file, replace=True)
            name = trance_png(name, cq_image_file)
            return f'[CQ:image,file={name}]'
    else:
        if 'gif' not in url:
            url = illust.image_urls.get('large')
        name = url[url.rfind("/") + 1:]
        api.download(url, path=cq_image_file, replace=True)
        name = trance_png(name, cq_image_file)
        return f'[CQ:image,file={name}]'


def trance_png(name, cq_image_file):
    im = Image.open(cq_image_file + name)
    if im.format == 'WEBP':
        name = name.replace("jpg", "png")
        try:
            w, h = im.size
            w_s, h_s = float_range(w, h)
            im = im.resize((w_s, h_s))
            im.save(cq_image_file + name, "PNG")
        except IOError:
            pass
        return name
    elif im.format in ['JPEG', 'PNG']:
        try:
            w, h = im.size
            w_s, h_s = float_range(w, h)
            im = im.resize((w_s, h_s))
            im.save(cq_image_file + name)
        except IOError:
            pass
        return name
    else:
        return name


def ten_page_search(cmd_msg, r18=False):
    illusts = []
    for i in range(0, 9):
        if r18:
            cmd_msg=cmd_msg+' R-18'
        result = api.search_illust(cmd_msg, search_target='partial_match_for_tags', sort='date_desc', duration=None,
                                   offset=i * 30, req_auth=True)
        if result.get('error'):
            raise PixivError('search error')
        if len(result.illusts) == 0:
            break
        result_filter = []
        for r in result.illusts:
            if 'R-18' not in [tg.name for tg in r.tags] and not r18:
                result_filter.append(r)
            if 'R-18' in [tg.name for tg in r.tags] and r18:
                result_filter.append(r)
        illusts.extend(result_filter)
    if len(illusts) == 0:
        return None
    illusts_sorted = sorted(illusts, key=lambda v: v.total_bookmarks, reverse=True)
    fetch = 29
    if fetch > len(illusts_sorted) - 1:
        fetch = len(illusts_sorted) - 1
    fetch = random.randint(0, fetch)
    return illusts_sorted[fetch]


# 得到正负10%的晃动比例，生成新size
def float_range(x, y):
    level = round(random.random() * 0.2 + 0.9, 2)
    return int(x * level), int(y * level)
