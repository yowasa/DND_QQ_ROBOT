from hoshino import R, Service, priv
import hoshino
from functools import partial
import random
import json
from PIL import Image
import asyncio
from pixivpy3 import *
from .CacheCounter import *
import zipfile
import imageio
from pygifsicle import optimize
import math
from .PixivCounter import PixivCounter
from hoshino.typing import CQEvent

"""
Pixiv相关功能
"""

sv_img = Service('pixiv功能', enable_on_default=True, bundle='图片功能', help_=
'''[img]{标签} pixiv搜索图片 不加标签则会随机抽取日榜图片
[gimg]{标签} pixiv搜索图片 会返回图组 不加标签则会随机抽取日榜图片
[pid]{图片id} pixiv搜索指定id图片
[启用图片详情] 搜tag出图会显示作品详情 个人设置
[关闭图片详情] 搜tag出图会显示作品详情 个人设置 默认为关闭
[订阅] {作者id} 为本群订阅指定作者的作品 管理员可操作，对群组设置
[取消订阅] {作者id} 为本群取消订阅指定作者的作品 管理员可操作，对群组设置
[订阅列表] 查看订阅的信息
[自动订阅] 批量订阅和订阅日榜 再次输入指令取消 管理员可操作，对群组设置
[热门标签] pixiv搜索最近热门的标签
[抓取订阅] 从扫描订阅的图片中手动抓取未发送过的图片
''')

sv_ghs = Service('搞黄色', enable_on_default=False, bundle='图片功能', help_=
'''[ghs]{标签} pixiv搜索图片（R18版本）不加标签则会随机抽取日榜图片
[gghs]{标签} pixiv搜索图片（R18版本） 会返回图组 不加标签则会随机抽取日榜图片
[启用自动撤回] 开启r18图片自动撤回 仅管理员可用，对群组设置
[关闭自动撤回] 关闭r18图片自动撤回 仅管理员可用，对群组设置
''')

# 缓存图片文件
CACHE_FILE = 'ghs/cache/'
# 缓存大图文件
CACHE_FULL_FILE = 'ghs/full/'

api = AppPixivAPI()
api.set_accept_language('zh-cn')  # zh-cn


@sv_ghs.on_fullmatch(['启用自动撤回', '开启自动撤回'])
async def pixiv_detail_open(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能设置自动撤回哦。', at_sender=True)
    set_auto_delete(ev.group_id, True)
    await bot.send(ev, "启用自动撤回成功")


@sv_ghs.on_fullmatch(['关闭自动撤回'])
async def pixiv_detail_close(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能设置自动撤回哦。', at_sender=True)
    set_auto_delete(ev.group_id, False)
    await bot.send(ev, "关闭自动撤回成功")


@sv_img.on_fullmatch(['启用图片详情', '开启图片详情'])
async def pixiv_detail_open(bot, ev: CQEvent):
    set_need_detail(ev.user_id, True)
    await bot.send(ev, "启用图片详情成功")


@sv_img.on_fullmatch(['关闭图片详情'])
async def pixiv_detail_close(bot, ev: CQEvent):
    set_need_detail(ev.user_id, False)
    await bot.send(ev, "关闭图片详情成功")


@sv_img.on_prefix(['热门标签', 'tag'])
async def pixiv_tag(bot, ev: CQEvent):
    for i in range(3):
        try:
            result = api.trending_tags_illust()
            if result.get('error'):
                pixiv_login()
            else:
                tags = [t.get('tag') for t in result.get('trend_tags')]
                await bot.send(ev, "最近热门标签列表:\n" + " ".join(tags))
                return
        except Exception as ex:
            pixiv_login()
    await bot.send(ev, "Pixiv登陆异常 请稍后再试")


@sv_img.on_prefix(["img"])
async def pixiv_search(bot, ev: CQEvent):
    msg = await img_search(ev, group=False, r18=False)
    await bot.send(ev, msg)


@sv_img.on_prefix(["gimg"])
async def group_pixiv_search(bot, ev: CQEvent):
    msg = await img_search(ev, group=True, r18=False)
    await bot.send(ev, msg)


@sv_ghs.on_prefix(["ghs", "搞黄色"])
async def group_pixiv_search(bot, ev: CQEvent):
    msg = await img_search(ev, group=False, r18=True)
    data = await bot.send(ev, msg)
    if get_auto_delete(ev.group_id):
        await asyncio.sleep(30)
        await bot.delete_msg(self_id=ev.self_id, message_id=data['message_id'])


@sv_ghs.on_prefix(["gghs"])
async def group_pixiv_search(bot, ev: CQEvent):
    msg = await img_search(ev, group=True, r18=True)
    data = await bot.send(ev, msg)
    if get_auto_delete(ev.group_id):
        await asyncio.sleep(30)
        await bot.delete_msg(self_id=ev.self_id, message_id=data['message_id'])


@sv_img.on_prefix(["pid"])
async def pid(bot, ev: CQEvent):
    cmd_msg = str(ev.message).strip()
    if not cmd_msg:
        await bot.send(ev, '请指定作品id')
        return
    if not cmd_msg.isdecimal():
        await bot.send(ev, '输入数字')
        return
    for i in range(3):
        try:
            result = api.illust_detail(int(cmd_msg))
            illust = result.get('illust')
            msg = await combine_app_result(illust, group=True, need_detail=get_need_detail(ev.user_id))
            data = await bot.send(ev, msg)
            if not illust.get('sanity_level') < 6:
                if get_auto_delete(ev.group_id):
                    await asyncio.sleep(30)
                    await bot.delete_msg(self_id=ev.self_id, message_id=data['message_id'])
            return
        except Exception as ex:
            pixiv_login()


# 为个人或群开启自动ghs功能
@sv_img.on_prefix(['自动订阅'])
async def open_auto_ghs(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能设置自动订阅。', at_sender=True)
    msg = str(ev.message).strip()
    if msg == '日榜':
        msg = add_subscribe(ev, 'day')
    elif msg == 'r18日榜':
        msg = add_subscribe(ev, 'day_r18')
    elif msg == '默认列表':
        msg = add_subscribe(ev, 'public')
    elif msg == 'r18默认列表':
        msg = add_subscribe(ev, 'private')
    else:
        msg = '无此指令 请输入:日榜 默认列表'
    await bot.send(ev, msg)


@sv_img.on_prefix(['订阅'])
async def subscribe(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能设置订阅。', at_sender=True)
    msg = str(ev.message).strip()
    result = add_subscribe(ev, 'user', Auth_User=msg)
    await bot.send(ev, result)


# .checksub  <作者id>:检查是否订阅某作者作品
@sv_img.on_prefix(['检查订阅'])
async def checksub(bot, ev: CQEvent):
    comm = str(ev.message).strip()
    msg = ev.detail_type
    if msg == 'group':
        user_id = ev.group_id
    elif msg == 'private':
        user_id = ev.user_id
    elif msg == 'discuss':
        user_id = ev.discuss_id
    else:
        bot.finish(ev, '不支持群/私聊/讨论组以外的订阅方式')
    pc = PixivCounter()
    old = pc._get_subscribe_id(user_id, msg, 'pixiv', 'user', comm)
    if not old:
        result = '未订阅'
    else:
        result = '订阅中'
    await bot.send(ev, result)


def trancetype(msg):
    if msg == 'day':
        return '日榜'
    elif msg == 'day_r18':
        return 'r18日榜'
    elif msg == 'public':
        return '默认列表'
    elif msg == 'private':
        return 'r18默认列表'


@sv_img.on_prefix(['订阅列表'])
async def sublist(bot, ev: CQEvent):
    msg = ev.detail_type
    if msg == 'group':
        user_id = ev.group_id
    elif msg == 'private':
        user_id = ev.user_id
    elif msg == 'discuss':
        user_id = ev.discuss_id
    else:
        await bot.finish(ev, '不支持群/私聊/讨论组以外的订阅方式')
    pc = PixivCounter()

    pack_info = [trancetype(str(sub[0])) for sub in pc._select_no_user_type(user_id, msg, 'pixiv')]
    user_infos = [str(sub[0]) for sub in pc._select_user_type(user_id, msg, 'pixiv')]
    return_msg = ''
    if pack_info:
        return_msg += '套餐\n' + '\n'.join(pack_info) + '\n\n'

    if user_infos:
        return_msg += '画师id\n' + '\n'.join(user_infos)
    await bot.send(ev, return_msg)


@sv_img.on_prefix(['取消订阅'])
async def unsubscribe(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能设置订阅。', at_sender=True)
    comm = str(ev.message).strip()
    msg = ev.detail_type
    if msg == 'group':
        user_id = ev.group_id
    elif msg == 'private':
        user_id = ev.user_id
    elif msg == 'discuss':
        user_id = ev.discuss_id
    else:
        await bot.finish(ev, '不支持群/私聊/讨论组以外的订阅方式')
    pc = PixivCounter()
    old = pc._get_subscribe_id(user_id, msg, 'pixiv', 'user', comm)
    if not old:
        await bot.send(ev, '未订阅过该作者作品')
    else:
        pc._del_by_subscribe_id(old)
        await bot.send(ev, '取消订阅成功')


@sv_img.on_prefix(['测试扫描'])
async def unsubscribe(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '测试用 勿扰。', at_sender=True)
    await scan_job()
    print("测试成功")


@sv_img.on_prefix(['测试投放'])
async def unsubscribe(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '测试用 勿扰。', at_sender=True)
    await send_job()
    print("测试成功")


@sv_img.scheduled_job('cron', hour='*/4', minute='10', second='30')
async def scan_job():
    sv_img.logger.info("开始扫描订阅信息")
    try:
        pixiv_login()
        sv_img.logger.info("pixiv登录成功")
        # 每日前三十
        results = api.illust_ranking(mode='day', date=None, offset=None)
        sv_img.logger.info("抓取日榜信息成功")
        results_r18 = api.illust_ranking(mode='day_r18', date=None, offset=None)
        sv_img.logger.info("抓取r18日榜信息成功")
        result_public = api.illust_follow(restrict='public')
        sv_img.logger.info("抓取公开收藏夹信息成功")
        result_private = api.illust_follow(restrict='private')
        sv_img.logger.info("抓取私人收藏夹信息成功")
        # query = Subscribe.select().where(Subscribe.clazz == 'pixiv')
        pc = PixivCounter()
        query = pc._select_all_subinfo_by_class('pixiv')
        u_map = {}
        for each in query:
            if each.type == 'day':
                await build_result(each, results.illusts)
                sv_img.logger.info("存储日榜信息成功")
            if each.type == 'day_r18':
                await build_result(each, results_r18.illusts)
                sv_img.logger.info("存储r18日榜信息成功")
            if each.type == 'private':
                await build_result(each, result_private.illusts)
                sv_img.logger.info("存储私人收藏夹信息成功")
            if each.type == 'public':
                await build_result(each, result_public.illusts)
                sv_img.logger.info("存储公开收藏夹信息成功")
            if each.type == 'user':
                if u_map.get(each.type_user):
                    results_users = u_map.get(each.type_user)
                else:
                    sv_img.logger.info(f"开始扫描画师{each.type_user}作品信息")
                    results_users = await asyncio.get_event_loop().run_in_executor(
                        None, partial(api.user_illusts, each.type_user))
                    if results == None or results_users.illusts == None:
                        sv_img.logger.error(f"扫描画师{each.type_user}作品信息失败")
                        await asyncio.sleep(300)
                        results_users = await asyncio.get_event_loop().run_in_executor(
                            None, partial(api.user_illusts, each.type_user))
                    u_map[each.type_user] = results_users
                sv_img.logger.info(f"扫描画师{each.type_user}作品信息成功 准备存储")
                await build_result(each, results_users.illusts)
                sv_img.logger.info(f"存储指定画师{each.type_user}作品信息成功")
        sv_img.logger.info("扫描结束")
        return
    except Exception as e:
        sv_img.logger.info(f"扫描失败{e}")
        return


@sv_img.on_prefix(['抓取订阅'])
async def fetch_sub(bot, ev: CQEvent):
    msg = str(ev.message).strip()
    type = ev.detail_type
    limit = 1
    if msg:
        if msg.isdecimal():
            if int(msg) > 5 or int(msg) < 1:
                bot.finish(ev, "请输入1-5的数字")
            else:
                limit = int(msg)
        else:
            bot.finish(ev, "请输入1-5的数字")
    pc = PixivCounter()
    query = pc.select_sendlog_limit(ev.group_id, type, 0, limit)
    if not query:
        await bot.finish(ev, "已经一滴也没有了")
    for e in query:
        await bot.send(ev, e.message_info)
        pc.set_sendlog_flag(e.id)
        await asyncio.sleep(3)


@sv_img.scheduled_job('cron', minute='2,17,32,47', second='30')
async def send_job():
    sv_img.logger.info("开始投放订阅图片")
    try:
        need_send_list = send_list()
        for each in need_send_list:
            context = each.get('content')
            user_type = context['message_type']
            if not context:
                continue
            message = each.get('message')
            for sid in hoshino.get_self_ids():
                if user_type == 'group':
                    await sv_img.bot.send_group_msg(self_id=sid, group_id=context['group_id'], message=message)
                elif user_type == 'private':
                    await sv_img.bot.send_private_msg(self_id=sid, user_id=context['user_id'], message=message)
                elif user_type == 'discuss':
                    await sv_img.bot.send_discuss_msg(self_id=sid, discuss_id=context['discuss_id'], message=message)
        sv_img.logger.info("发送完成")
        return
    except Exception as e:
        sv_img.logger.info(f"发送失败{e}")
        return


def get_auto_delete(group_id):
    pc = PixivCounter()
    return pc._get_group_auto_delete(group_id)


def set_auto_delete(group_id, switch):
    pc = PixivCounter()
    auto = 1 if switch else 0
    pc._save_group_auto_delete(group_id, auto)


def get_need_detail(qq_number):
    pc = PixivCounter()
    return pc._get_user_need_detail(qq_number)


def set_need_detail(qq_number, switch):
    pc = PixivCounter()
    need = 1 if switch else 0
    pc._save_user_need_detail(qq_number, need)


async def img_search(ev: CQEvent, group=False, r18=False):
    msg = str(ev.message)
    need_detail = get_need_detail(ev.user_id)
    for i in range(3):
        try:
            if not msg:
                if r18:
                    results = api.illust_ranking(mode='day_r18', date=None, offset=None)
                else:
                    results = api.illust_ranking(mode='day', date=None, offset=None)
                if results.get('error'):
                    pixiv_login()
                illust = results.illusts[random.randint(0, len(results.illusts) - 1)]
                sv_img.logger.info(f"解析的图片id为{illust.get('id')}")
                return await combine_app_result(illust, group=group, need_detail=need_detail)
            else:
                # 多页搜索
                illust = page_search(msg, r18=r18)
                if not illust:
                    return "未搜索到结果"
                sv_img.logger.info(f"解析的图片id为{illust.get('id')}")
                return await combine_app_result(illust, group=group, need_detail=need_detail)
        except Exception as pe:
            pixiv_login()
    return "Pixiv登陆异常 请稍后再试"


# 多页搜索
def page_search(cmd_msg, r18=False):
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


# 组装app端的查询结果
async def combine_app_result(illust, group=False, need_detail=False):
    cq_img = await asyncio.get_event_loop().run_in_executor(
        None, partial(package_pixiv_img, illust, group))
    if need_detail:
        return f'pixivID:{illust.get("id")}\n标题:{illust.get("title")}\n作者:{illust.get("user").get("name")}({illust.get("user").get("id")})\nTags:{" ".join([x.get("name") for x in illust.get("tags")])}\n{cq_img}'
    else:
        return cq_img


# 将查询到的illust对象缓存并转化为cq码
def package_pixiv_img(illust, group=False):
    url = illust.meta_single_page.get('original_image_url')
    cache = CacheCounter()
    message = cache._get_cache(illust.get('id'), group)
    if message:
        return message
    if illust.get('type') == "ugoira":
        result = gen_gif_response(illust.get('id'))
        try:
            cache._set_cache(illust.get('id'), group, str(result))
        except Exception as e:
            sv_img.logger.error("存储p站缓存失败")
        return result
    if not url:
        urls = []
        for i in illust.meta_pages:
            uu = i.get('image_urls').get('large')
            if uu:
                urls.append(uu)
        ##一组图取全部(太多了刷屏 至多取前5)
        if group:
            img_list = []
            if len(urls) > 5:
                for i in range(5):
                    uurl = urls[i]
                    name = uurl[uurl.rfind("/") + 1:]
                    api.download(uurl, path=R.img(CACHE_FILE).path, replace=True)
                    name = trance_png(name, R.img(CACHE_FILE).path)
                    img_list.append(str(R.img(CACHE_FILE + name).cqcode))
                result = ''.join(img_list)
            else:
                for uurl in urls:
                    name = uurl[uurl.rfind("/") + 1:]
                    api.download(uurl, path=R.img(CACHE_FILE).path, replace=True)
                    name = trance_png(name, R.img(CACHE_FILE).path)
                    img_list.append(str(R.img(CACHE_FILE + name).cqcode))
                result = ''.join(img_list)
        else:
            #一组图随机取一个
            length = len(urls)
            randomNumber = random.randint(0, length - 1)
            uurl = urls[randomNumber]
            name = uurl[uurl.rfind("/") + 1:]
            api.download(uurl, path=R.img(CACHE_FILE).path, replace=True)
            name = trance_png(name, R.img(CACHE_FILE).path)
            result = str(R.img(CACHE_FILE + name).cqcode)
    else:
        if 'gif' not in url:
            url = illust.image_urls.get('large')
        name = url[url.rfind("/") + 1:]
        api.download(url, path=R.img(CACHE_FILE).path, replace=True)
        name = trance_png(name, R.img(CACHE_FILE).path)
        result = str(R.img(CACHE_FILE + name).cqcode)
    try:
        cache._set_cache(illust.get('id'), group, str(result))
    except Exception as e:
        sv_img.logger.error("存储p站缓存失败")
    return result


def gen_gif_response(ill_id):
    result = api.ugoira_metadata(ill_id)
    url = result.get('ugoira_metadata').get('zip_urls').get('medium')
    delay = result.get('ugoira_metadata').get('frames')[0].get('delay')
    fps = 1000 / delay
    zip_name = url[url.rfind("/") + 1:]
    name = zip_name.replace('.zip', '')
    path = R.img(f'ghs/gif/{name}').path
    gif_name = name + '.gif'
    target_name = R.img(f'ghs/gif/{gif_name}').path
    if not os.path.exists(target_name):
        api.download(url, path=R.img(f'ghs/gif').path, replace=True)
        unzip_single(R.img(f'ghs/gif/{zip_name}').path, path)
        filenames = sorted((os.path.join(path, fn) for fn in os.listdir(path)))
        package_2_gif(filenames, target_name, fps=fps)
    return str(R.img(f'ghs/gif/{gif_name}').cqcode)


def gen_webp_response(ill_id):
    result = api.ugoira_metadata(ill_id)
    url = result.get('ugoira_metadata').get('zip_urls').get('medium')
    duration = [i.get('delay') for i in result.get('ugoira_metadata').get('frames')]
    zip_name = url[url.rfind("/") + 1:]
    name = zip_name.replace('.zip', '')
    path = R.img(f'ghs/gif/{name}').path
    gif_name = name + '.webp'
    target_name = R.img(f'ghs/gif/{gif_name}').path
    if not os.path.exists(target_name):
        api.download(url, path=R.img(f'ghs/gif').path, replace=True)
        unzip_single(R.img(f'ghs/gif/{zip_name}').path, path)
        filenames = sorted((os.path.join(path, fn) for fn in os.listdir(path)))
        package_2_webp(filenames, target_name, duration=duration)
    return str(R.img(f'ghs/gif/{gif_name}').cqcode)


def unzip_single(src_file, dest_dir):
    zf = zipfile.ZipFile(src_file)
    try:
        zf.extractall(path=dest_dir)
    except RuntimeError as e:
        print(e)
    zf.close()


def package_2_webp(filenames, target_file, duration):
    filestreams = []
    for i in filenames:
        filestreams += [Image.open(i)]
    filestreams[0].save(target_file, "webp", save_all=True,
                        append_images=filestreams[1:], duration=duration)


def package_2_gif(filenames, target_file, fps=12):
    images = []
    for filename in filenames:
        images.append(imageio.imread(filename))
    imageio.mimsave(target_file, images, fps=fps)
    optimize(target_file, options=["--lossy"], colors=64)
    optimize_gif(target_file)


def optimize_gif(target_file):
    size = os.path.getsize(target_file) / (1024 * 1024)
    if size < 3:
        return
    ratio = math.sqrt((3 / size))
    optimize(target_file, options=["--lossy", f"--scale={ratio}"])


# 修正图片 对图片类型为WEBP进行转换 对JPEG,PNG进行压缩和抖动
def trance_png(name, cq_image_file):
    file_path = os.path.join(cq_image_file, name)
    im = Image.open(file_path)
    if im.format == 'WEBP':
        name = name.replace("jpg", "png")
        file_path = os.path.join(cq_image_file, name)
        try:
            w, h = im.size
            w_s, h_s = float_tenpercent_range(w, h)
            im = im.resize((w_s, h_s))
            im.save(file_path, "PNG")
        except IOError:
            pass
        return name
    elif im.format in ['JPEG', 'PNG']:
        try:
            w, h = im.size
            w_s, h_s = float_tenpercent_range(w, h)
            im = im.resize((w_s, h_s))
            im.save(file_path)
        except IOError:
            pass
        return name
    else:
        return name


# 晃动10%
def float_tenpercent_range(x, y):
    level = round(random.random() * 0.2 + 0.9, 2)
    return int(x * level), int(y * level)


def write_refresh_token(token):
    with open(R.get('img/ghs/token.json').path, 'w') as f:
        json.dump(token, fp=f)


# 获取登录token
def get_token():
    with open(R.get('img/ghs/token.json').path, 'r') as f:
        return json.load(f)


def pixiv_login():
    token = get_token()
    api.set_auth(access_token=token['access_token'], refresh_token=token['refresh_token'])
    api.auth(refresh_token=token['refresh_token'])
    token['refresh_token'] = api.refresh_token
    write_refresh_token(token)


def bulid_context(user_id, user_type):
    context = {}
    context['message_type'] = user_type
    if user_type == 'group':
        context['group_id'] = user_id
        return context
    elif user_type == 'private':
        context['user_id'] = user_id
        return context
    elif user_type == 'discuss':
        context['discuss_id'] = user_id
        return context
    return None


async def build_result(subscribe, illusts):
    mapping = {}
    ill_ids = []
    if not illusts:
        return
    for illust in illusts:
        mapping[illust.get("id")] = illust
        if illust.get("id"):
            ill_ids.append(illust.get("id"))
    if not ill_ids:
        return
    pc = PixivCounter()
    logs = pc.select_sendlog(subscribe.user_id, subscribe.user_type, ill_ids)
    for log in logs:
        if log.message_id in ill_ids:
            ill_ids.remove(log.message_id)
    for i in ill_ids:
        illust = mapping.get(i)
        sv_img.logger.info(f"开始存储ill_id为{i}的作品")
        message = await asyncio.get_event_loop().run_in_executor(
            None, partial(package_pixiv_img, illust, True))
        pc._save_sendlog(subscribe.user_id, subscribe.user_type, 'pixiv', i, str(message))


def send_list():
    result = []
    pc = PixivCounter()
    query = pc.select_no_send_group()
    for e in query:
        content = bulid_context(e.user_id, e.user_type)
        each = {}
        each['content'] = content
        each['message'] = e.message_info
        result.append(each)
        pc.set_sendlog_flag(e.id)
    return result


def trance_2_name(level):
    if level == 0:
        return '普通用户'
    if level == 10:
        return '管理员'
    if level == 50:
        return '超管'
    if level == 100:
        return '你在看谁？'


def add_subscribe(ev, ttype, Auth_User=0):
    msg = ev.detail_type
    if msg == 'group':
        user_id = ev.group_id
    elif msg == 'private':
        user_id = ev.user_id
    elif msg == 'discuss':
        user_id = ev.discuss_id
    else:
        return '不支持群/私聊/讨论组以外的订阅方式'

    if Auth_User != 0:
        results_users = api.user_illusts(Auth_User)
        if len(results_users.illusts) == 0:
            return '此id不存在作品'
        ttype = 'user'
    pc = PixivCounter()
    old = pc._get_subscribe_id(user_id, msg, 'pixiv', ttype, Auth_User)
    if not old:
        pc._save_subscribe(user_id, msg, 'pixiv', ttype, Auth_User)
        return '订阅成功'
    else:
        if ttype != 'user':
            pc._del_by_subscribe_id(old)
            return '取消自动订阅'
        else:
            return '已经订阅 无需重复操作'
