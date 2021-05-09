# 1.导入模块
import os
import random
import json
import requests
from PIL import Image
from pixivpy3 import *
from robobrowser import RoboBrowser
import re
from base import cq_code_formate as cq_tool
from base import tool
from filter import msg_route
from tool.dnd_db import PixivCache

api = AppPixivAPI()
# api = ByPassSniApi()
# api.require_appapi_hosts(
#     hostname="public-api.secure.pixiv.net"
# )
# api.set_accept_language('en_us')
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
    cq_image_file = 'D:\\workspace\\mcl\\data\\OneBot\\image\\'

pixiv_user_name = env_dist.get("pixiv_user_name")
pixiv_password = env_dist.get("pixiv_password")

def web_pixiv_login():
    token = get_token()
    web_api.set_auth(access_token=token['access_token'], refresh_token=token['refresh_token'])
    web_api.auth(refresh_token=token['refresh_token'])
    token['refresh_token'] = web_api.refresh_token
    write_refresh_token(token)

def pixiv_login():
    token=get_token()
    api.set_auth(access_token=token['access_token'],refresh_token=token['refresh_token'])
    api.auth(refresh_token=token['refresh_token'])
    token['refresh_token']=api.refresh_token
    write_refresh_token(token)


def get_token():
    with open('../../token', 'r') as f:
        result = json.load(f)
    return result

def write_refresh_token(token):
    with open('../../token', 'w') as f:
        json.dump(token, fp=f)

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

@msg_route(r'(\.|。)search')
def img_search(content):
    cmd_msg = content.get('cmd_msg').strip()
    matchObj=re.match(r'\[CQ:image,file=(.*),url=(.*)\]', cmd_msg, re.M|re.I)
    if matchObj:
        img_url=matchObj.group(2)
        url = f'https://saucenao.com/search.php?output_type=2&testmode=1&api_key=53f99bec6827ad0b6b728c063be1c84c20d40f20&numres=16&url={img_url}'

        result = requests.get(url)
        if result.status_code != 200:
            return '请求异常'
        content = json.loads(result.content)
        if content['header']['status']!=0:
            if content['header']['status']==-2:
                return '搜索过于频繁'
            else:
                return '搜索超过限制'
        result_list=content['results']
        # 相似度大于90的列表
        uper_90= list(filter(lambda n: float(n['header']['similarity']) > float(90), result_list))
        if len(uper_90)>0:
            pixiv_list=list(filter(lambda n: n['header']['index_id'] in (5,6), uper_90))
            if len(pixiv_list)==0:
                select = result_list[0]
            else:
                select=pixiv_list[0]
        else:
            select=result_list[0]
        return package_search_result(select)

    else:
        return '未识别到图片'

def package_search_result(select):
    index_id= select['header']['index_id']
    similarity=select['header']['similarity']
    thumbnail = select['header'][ 'thumbnail']
    ext_url=select['data'].get('source')
    if not ext_url:
        ext_url=select['data']['ext_urls'][0]
    if index_id == 5 or index_id == 6:
        # 5->pixiv 6->pixiv historical
        service_name = 'pixiv'
        illust_id = select['data']['pixiv_id']
        content={'cmd_msg':str(illust_id)}
    elif index_id == 8:
        # 8->nico nico seiga
        service_name = 'seiga'
    elif index_id == 9:
        # 8->nico nico seiga
        service_name = 'Twitter'
    elif index_id == 10:
        # 10->drawr
        service_name = 'drawr'
    elif index_id == 11:
        # 11->nijie
        service_name = 'nijie'
    elif index_id == 34:
        # 34->da
        service_name = 'da'
    else:
        service_name = '未知'
    if index_id == 5 or index_id == 6:
        other_msg = '\n' + get_by_id(content, need_info=True)
    else:
        url_list=[]
        url_list.append(thumbnail)
        name_list = tool.requests_download_url_list(url_list, cq_image_file)
        other_msg='\n'+ cq_tool.package_img_2_cq_code_list(name_list)
    return f'图片来源:{service_name}\n相似度:{similarity}\n原图地址:{ext_url}{other_msg}'


@msg_route(r'(\.|。)tag$')
def pixiv_tag(content):
    try:
        result = api.trending_tags_illust()
        if result.get('error'):
            if True != content.get("retry"):
                pixiv_login()
                content["retry"] = True
                return pixiv_tag(content)
            else:
                return "Pixiv登陆异常"
        randomNumber = random.randint(0, len(result.get('trend_tags')) - 1)
        return result.get('trend_tags')[randomNumber].get('tag')
    except PixivError as pe:
        if True != content.get("retry"):
            pixiv_login()
            content["retry"] = True
            return pixiv_tag(content)
        else:
            return "Pixiv登陆异常"
    except Exception as ex:
        return "未知异常"


@msg_route(r'(\.|。)gimg',need_user=True)
def group_pixiv_search(content):
    return pixiv_search_common(content, group=True)


@msg_route(r'(\.|。)img',need_user=True)
def pixiv_search(content):
    return pixiv_search_common(content)


@msg_route(r'(\.|。)gghs',need_user=True)
def group_ghs_pixiv(content):
    content['call_back'] = True
    return ghs_pixiv_common(content, group=True)


@msg_route(r'(\.|。)ghs',need_user=True)
def ghs_pixiv(content):
    content['call_back'] = True
    return ghs_pixiv_common(content)


@msg_route(r'(\.|。)ill',need_user=True)
def ill(content):
    if not content.get('cmd_msg').strip():
        content['cmd_msg'] = '1000users'
    return pixiv_web_search_common(content)


@msg_route(r'(\.|。)ero',need_user=True)
def ero(content):
    content['call_back'] = True
    if not content.get('cmd_msg').strip():
        content['cmd_msg'] = '1000users'
    return pixiv_web_search_common(content, r18=True)


@msg_route(r'(\.|。)manga',need_user=True)
def manga(content):
    if not content.get('cmd_msg').strip():
        content['cmd_msg'] = '1000users'
    return pixiv_web_search_common(content, type='manga')


@msg_route(r'(\.|。)eman',need_user=True)
def eromanga(content):
    content['call_back'] = True
    if not content.get('cmd_msg').strip():
        content['cmd_msg'] = '1000users'
    return pixiv_web_search_common(content, r18=True, type='manga')


@msg_route(r'(\.|。)gif',need_user=True)
def gif(content):
    if not content.get('cmd_msg').strip():
        content['cmd_msg'] = '1000users'
    return pixiv_web_search_common(content, type='ugoira')

@msg_route(r'(\.|。)hgif',need_user=True)
def gif(content):
    content['call_back'] = True
    if not content.get('cmd_msg').strip():
        content['cmd_msg'] = '1000users'
    return pixiv_web_search_common(content,r18=True, type='ugoira')

@msg_route(r'(\.|。)pid',need_user=True)
def pid(content):
    return get_by_id(content,need_info=content.get('sys_user').pixiv_switch)


def get_by_id(content,retry=True,need_info=False):
    cmd_msg=content.get('cmd_msg').strip()
    if not cmd_msg:
        return '请指定作品id'
    if not cmd_msg.isdigit():
        return '请指定作品id'
    try:
        result=api.illust_detail(int(cmd_msg))
        # result = web_api.works(int(cmd_msg))
        if result.get('error') :
            return "未查询到作品"
            # if retry:
            #     pixiv_login()
            #     return get_by_id(content, retry=False,need_info=need_info)
        # illusts = result.get('response')
        illust=result.get('illust')
        # if len(illusts) == 0:
        #     return "未查询到作品"
        if not illust.get('sanity_level') < 6:
            content['call_back'] = True
        return combine_app_result(illust,group=True,need_info=need_info)
    except PixivError as pe:
        if retry:
            pixiv_login()
            return get_by_id(content, retry=False,need_info=need_info)
        else:
            return "Pixiv登陆异常"
    except Exception as ex:
        return "未知异常"



def ghs_pixiv_common(content, group=False):
    cmd_msg = content.get('cmd_msg').strip()
    try:
        if not cmd_msg:
            results = api.illust_ranking(mode='day_r18', date=None, offset=None)
            if results.get('error'):
                if True != content.get("retry"):
                    pixiv_login()
                    content["retry"] = True
                    return ghs_pixiv_common(content, group=group,need_info=content.get('sys_user').pixiv_switch)
                else:
                    return "Pixiv登陆异常"
            # 没有数据从日排行前三十里随机取一张
            illust = results.illusts[random.randint(0, len(results.illusts) - 1)]
            return combine_app_result(illust, group=group,need_info=content.get('sys_user').pixiv_switch)
        else:
            illust = ten_page_search(cmd_msg, r18=True)
            if not illust:
                return "搜索不到结果"
            return combine_app_result(illust, group=group,need_info=content.get('sys_user').pixiv_switch)
    except Exception as pe:
        if True != content.get("retry"):
            pixiv_login()
            content["retry"] = True
            return ghs_pixiv_common(content)
        else:
            return "Pixiv登陆异常"
    # except Exception as ex:
    #     return "未知异常"


def pixiv_search_common(content, group=False):
    cmd_msg = content.get('cmd_msg').strip()
    try:
        # 没有数据从日排行前三十里随机取一张
        if not cmd_msg:
            results = api.illust_ranking(mode='day', date=None, offset=None)
            if results.get('error'):
                if True != content.get("retry"):
                    pixiv_login()
                    content["retry"] = True
                    return pixiv_search_common(content, group=group,need_info=content.get('sys_user').pixiv_switch)
                else:
                    return "Pixiv登陆异常"
            if len(results.illusts) == 0:
                return "搜索不到结果"
            illust = results.illusts[random.randint(0, len(results.illusts) - 1)]
            return combine_app_result(illust, group=group,need_info=content.get('sys_user').pixiv_switch)
        # 有数据以数据为tag进行搜索，第一页随机取一张展示（排行）
        illust = ten_page_search(cmd_msg)
        if not illust:
            return "搜索不到结果"
        return combine_app_result(illust, group=group,need_info=content.get('sys_user').pixiv_switch)
    except Exception as pe:
        if True != content.get("retry"):
            pixiv_login()
            content["retry"] = True
            return pixiv_search_common(content, group=group)
        else:
            return "Pixiv登陆异常"
    # except Exception as ex:
    #     return "未知异常"


# 组装app端的查询结果
def combine_app_result(illust, group=False,need_info=False):
    cq_img = package_pixiv_img(illust, group=group)
    if need_info:
        return f'pixivID:{illust.get("id")}\n标题:{illust.get("title")}\n作者:{illust.get("user").get("name")}({illust.get("user").get("id")})\nTags:{" ".join([x.get("name") for x in illust.get("tags")])}\n{cq_img}'
    else:
        return cq_img

# 组装web端的查询结果
def combine_web_result(illust, type='illustration',need_info=False):
    cq_img = web_package_pixiv_img(illust, type)
    if need_info:
        return f'pixivID:{illust.get("id")}\n标题:{illust.get("title")}\n作者:{illust.get("user").get("name")}({illust.get("user").get("id")})\nTags:{" ".join([x for x in illust.get("tags")])}\n{cq_img}'
    else:
        return cq_img


# Web版本搜索
def pixiv_web_search_common(content, r18=False, type='illustration'):
    cmd_msg = content.get('cmd_msg').strip()
    try:
        illust = web_ten_page_search(cmd_msg, r18=r18, type=type)
        if not illust:
            return "搜索不到结果"
        return combine_web_result(illust, type,need_info=content.get('sys_user').pixiv_switch)
    except PixivError as pe:
        if True != content.get("retry"):
            web_pixiv_login()
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


def gen_gif_response(ill_id, retry=True):
    try:
        result = api.ugoira_metadata(ill_id)
        if result.get('error'):
            if retry:
                pixiv_login()
                return gen_gif_response(ill_id, retry=False)
            else:
                return "Pixiv登陆异常"
        url = result.get('ugoira_metadata').get('zip_urls').get('medium')
        delay = result.get('ugoira_metadata').get('frames')[0].get('delay')
        fps = int(1000 / delay)
        zip_name = url[url.rfind("/") + 1:]
        name = zip_name.replace('.zip', '')
        path = cq_image_file + name + '/'
        gif_name = name + '.gif'
        target_name = cq_image_file + gif_name
        if not os.path.exists(target_name):
            api.download(url, path=cq_image_file, replace=True)
            tool.unzip_single(cq_image_file + zip_name, path)
            filenames = sorted((path + fn for fn in os.listdir(path)))
            tool.package_2_gif(filenames, target_name, fps=fps)
        return f'[CQ:image,file={gif_name}]'

    except PixivError as pe:
        if retry:
            pixiv_login()
            return gen_gif_response(ill_id, retry=False)
        else:
            return "Pixiv登陆异常"
    except Exception as ex:
        return "未知异常"


def package_pixiv_img(illust, group=False):
    url = illust.meta_single_page.get('original_image_url')
    cache = PixivCache.get_or_none((PixivCache.pixiv_id == illust.get('id')) &(PixivCache.group==group) )
    if cache:
        
        return cache.message
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
            result = ''.join(img_list)
        else:
            ##一组图随机取一个
            length = len(urls)
            randomNumber = random.randint(0, length - 1)
            uurl = urls[randomNumber]
            name = uurl[uurl.rfind("/") + 1:]
            api.download(uurl, path=cq_image_file, replace=True)
            name = trance_png(name, cq_image_file)
            result = f'[CQ:image,file={name}]'
    else:
        if 'gif' not in url:
            url = illust.image_urls.get('large')
        name = url[url.rfind("/") + 1:]
        api.download(url, path=cq_image_file, replace=True)
        name = trance_png(name, cq_image_file)
        result = f'[CQ:image,file={name}]'
    new_cache = PixivCache()
    new_cache.pixiv_id = illust.get('id')
    new_cache.group = group
    new_cache.message=result
    new_cache.save()
    return result


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
    result = web_api.search_works(cmd_msg, mode="tag", types=[type], include_sanity_level=r18, per_page=500)
    if result.get('status') == "failure":
        raise PixivError('search error')
    illusts = result.get('response')
    if len(illusts) == 0:
        return None
    if not r18:
        illusts = list(filter(lambda n: n.sanity_level == 'white', illusts))
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
