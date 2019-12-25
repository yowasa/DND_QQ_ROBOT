# 1.导入模块
import os
import random

import requests
from PIL import Image
from pixivpy3 import *
from robobrowser import RoboBrowser

from base import cq_code_formate as cq_tool
from base import tool
from filter import msg_route

api = AppPixivAPI()
web_api = PixivAPI()

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
            name = tool.requests_download_url(pdiv.img.attrs.get('src'), cq_image_file)
            return cq_tool.package_img_2_cq_code(name)


@msg_route(r'更多奶子$')
def more_oppai(content):
    b = RoboBrowser(history=True)
    b.open('http://twitter.com/Strangestone/media')

    ls = b.find_all(class_='content')
    url_list = []
    for each in ls:
        each_text = each.find(class_='TweetTextSize--normal')
        if '月曜日のたわわ' in each_text.text:
            pdiv = each.find(class_='AdaptiveMedia-photoContainer')
            url_list.append(pdiv.img.attrs.get('src'))
    name_list = tool.requests_download_url_list(url_list, cq_image_file)
    return cq_tool.package_img_2_cq_code_list(name_list)


@msg_route(r'(\.|。)tag$')
def pixiv_tag(content):
    try:
        result = api.trending_tags_illust()
        if result.get('error'):
            if True != content.get("retry"):
                api.login(pixiv_user_name, pixiv_password)
                content["retry"] = True
                return pixiv_tag(content)
            else:
                return "Pixiv登陆异常"
        randomNumber = random.randint(0, len(result.get('trend_tags')) - 1)
        return result.get('trend_tags')[randomNumber].get('tag')
    except PixivError as pe:
        if True != content.get("retry"):
            api.login(pixiv_user_name, pixiv_password)
            content["retry"] = True
            return pixiv_tag(content)
        else:
            return "Pixiv登陆异常"
    except Exception as ex:
        return "未知异常"


@msg_route(r'(\.|。)gimg')
def group_pixiv_search(content):
    return pixiv_search_common(content, group=True)


@msg_route(r'(\.|。)img')
def pixiv_search(content):
    return pixiv_search_common(content)


@msg_route(r'(\.|。)gghs')
def group_ghs_pixiv(content):
    content['call_back'] = True
    return ghs_pixiv_common(content, group=True)


@msg_route(r'(\.|。)ghs')
def ghs_pixiv(content):
    content['call_back']=True
    return ghs_pixiv_common(content)


@msg_route(r'(\.|。)ill')
def ill(content):
    if not content.get('cmd_msg').strip():
        content['cmd_msg'] = '1000users'
    return pixiv_web_search_common(content)


@msg_route(r'(\.|。)ero')
def ero(content):
    content['call_back'] = True
    if not content.get('cmd_msg').strip():
        content['cmd_msg'] = '1000users'
    return pixiv_web_search_common(content, r18=True)


@msg_route(r'(\.|。)manga')
def manga(content):
    if not content.get('cmd_msg').strip():
        content['cmd_msg'] = '1000users'
    return pixiv_web_search_common(content, type='manga')


@msg_route(r'(\.|。)eman')
def eromanga(content):
    content['call_back'] = True
    if not content.get('cmd_msg').strip():
        content['cmd_msg'] = '1000users'
    return pixiv_web_search_common(content, r18=True, type='manga')

@msg_route(r'(\.|。)gif')
def gif(content):
    content['call_back'] = True
    if not content.get('cmd_msg').strip():
        content['cmd_msg'] = '1000users'
    return pixiv_web_search_common(content, type='ugoira')

def ghs_pixiv_common(content, group=False):
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


# Web版本搜索
def pixiv_web_search_common(content, r18=False, type='illustration'):
    cmd_msg = content.get('cmd_msg').strip()
    try:
        illust = web_ten_page_search(cmd_msg, r18=r18, type=type)
        if not illust:
            return "搜索不到结果"
        return web_package_pixiv_img(illust, type)
    except PixivError as pe:
        if True != content.get("retry"):
            web_api.login(pixiv_user_name, pixiv_password)
            content["retry"] = True
            return pixiv_web_search_common(content, r18=r18, type=type)
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


def web_package_pixiv_img(illust, type='illustration'):
    if type == 'manga':
        pages = web_api.works(illust.get('id')).get('response')[0].get('metadata').get('pages')
        urls = [p.get('image_urls').get('large') for p in pages]
        img_list = []
        for uurl in urls:
            name = uurl[uurl.rfind("/") + 1:]
            web_api.download(uurl, path=cq_image_file, replace=True)
            name = trance_png(name, cq_image_file)
            img_list.append(f'[CQ:image,file={name}]')
        return ''.join(img_list)
    if type == 'illustration':
        url = illust.get('image_urls').get('large')
        name = url[url.rfind("/") + 1:]
        web_api.download(url, path=cq_image_file, replace=True)
        name = trance_png(name, cq_image_file)
        return f'[CQ:image,file={name}]'
    if type == 'ugoira':
        return gen_gif_response(illust.get('id'))


def gen_gif_response(ill_id,retry=True):
    try:
        result=api.ugoira_metadata(ill_id)
        if result.get('error'):
            if retry:
                api.login(pixiv_user_name, pixiv_password)
                return gen_gif_response(ill_id, retry=False)
            else:
                return "Pixiv登陆异常"
        url = result.get('ugoira_metadata').get('zip_urls').get('medium')
        zip_name = url[url.rfind("/") + 1:]
        name=zip_name.replace('.zip', '')
        path=cq_image_file+name+'/'
        gif_name=name+'.gif'
        target_name=cq_image_file+gif_name
        if not os.path.exists(target_name):
            api.download(url, path=cq_image_file, replace=True)
            tool.unzip_single(cq_image_file+zip_name,path)
            filenames = sorted((path+fn for fn in os.listdir(path)))
            tool.package_2_gif(filenames,target_name)
        return f'[CQ:image,file={gif_name}]'

    except PixivError as pe:
        if retry:
            api.login(pixiv_user_name, pixiv_password)
            return gen_gif_response(ill_id,retry=False)
        else:
            return "Pixiv登陆异常"
    except Exception as ex:
        return "未知异常"


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
            w_s, h_s = tool.float_tenpercent_range(w, h)
            im = im.resize((w_s, h_s))
            im.save(cq_image_file + name, "PNG")
        except IOError:
            pass
        return name
    elif im.format in ['JPEG', 'PNG']:
        try:
            w, h = im.size
            w_s, h_s = tool.float_tenpercent_range(w, h)
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
            cmd_msg = cmd_msg + ' R-18'
        result = api.search_illust(cmd_msg, search_target='partial_match_for_tags', sort='date_desc', duration=None,
                                   offset=i * 30, req_auth=True)
        if result.get('error'):
            raise PixivError('search error')
        if len(result.illusts) == 0:
            break
        illusts.extend(result.illusts)
    if len(illusts) == 0:
        return None
    if not r18:
        illusts = list(filter(lambda n: n.sanity_level < 6, illusts))
    if len(illusts) == 0:
        return None
    illusts_sorted = sorted(illusts, key=lambda v: v.total_bookmarks, reverse=True)
    fetch = 29
    if fetch > len(illusts_sorted) - 1:
        fetch = len(illusts_sorted) - 1
    fetch = random.randint(0, fetch)
    return illusts_sorted[fetch]


def web_ten_page_search(cmd_msg, r18=False, type='illustration'):
    if r18:
        cmd_msg = cmd_msg + ' R-18'
    result = web_api.search_works(cmd_msg, mode="tag", types=[type], include_sanity_level=r18, per_page=300)
    if result.get('status') == "failure":
        raise PixivError('search error')
    illusts = result.get('response')
    if len(illusts) == 0:
        return None
    illusts_sorted = sorted(illusts,
                            key=lambda v: v.get('stats').get('favorited_count').get('public') + v.get('stats').get(
                                'favorited_count').get('private'), reverse=True)
    fetch = 29
    if fetch > len(illusts_sorted) - 1:
        fetch = len(illusts_sorted) - 1
    fetch = random.randint(0, fetch)
    return illusts_sorted[fetch]
