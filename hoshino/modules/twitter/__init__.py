import asyncio
import re
from datetime import datetime
from functools import partial, wraps

import pytz
import requests
from TwitterAPI import TwitterAPI, OAuthType

from hoshino import R, util, Service, priv
from hoshino.config import twitter as cfg
from hoshino.typing import CQEvent
from hoshino.util.utils import get_message_text
from .TwitterCounter import *

sv = Service('推特功能', enable_on_default=True, bundle='推特功能', help_='''推特搜索功能
[看推特]{推主的screen_name,即用户下面@后面的字符} {推文条数 不超过15,且会自动过滤转推内容}
[推特查询]{推文id}
[推特订阅] {推特用户screen_name}
[推特图片订阅] {推特用户screen_name} 仅发送含图片的推特
[取消推特订阅] {推特用户screen_name}
[检查推特订阅]
[推特订阅列表]
''')

api = TwitterAPI(cfg.consumer_key, cfg.consumer_secret, cfg.access_token_key, cfg.access_token_secret,
                 auth_type=OAuthType.OAUTH2)
URL_USER_LOOKUP = 'users/lookup'
URL_TIMELINE = 'statuses/user_timeline'


@wraps(api.request)
async def twt_request(*args, **kwargs):
    return await asyncio.get_event_loop().run_in_executor(
        None, partial(api.request, *args, **kwargs))


def time_formatter(time_str):
    dt = datetime.strptime(time_str, r"%a %b %d %H:%M:%S %z %Y")
    dt = dt.astimezone(pytz.timezone('Asia/Shanghai'))
    return f"{util.month_name(dt.month)}{util.date_name(dt.day)}・{util.time_name(dt.hour, dt.minute)}"


def time_stamp(time_str):
    dt = datetime.strptime(time_str, r"%a %b %d %H:%M:%S %z %Y")
    dt = dt.astimezone(pytz.timezone('Asia/Shanghai'))
    return int(dt.timestamp())


def requests_download_url(url, path):
    name = url[url.rfind("/") + 1:]
    if os.path.exists(os.path.join(path, name)):
        return name
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        open(os.path.join(path, name), 'wb').write(r.content)
    return name


# 封装id查询结果
def tweet_id_formatter(item):
    name = item['user']['name']
    screen_name = item['user']['screen_name']
    time = time_formatter(item['created_at'])
    text = item['text']
    imgs = []
    for media in item.get('extended_entities', item['entities']).get('media', []):
        try:
            img = media['media_url']
            if re.search(r'\.(jpg|jpeg|png|gif|jfif|webp)$', img, re.I):
                name = requests_download_url(img, R.img('twitter').path)
                imgs.append(str(R.img(f'twitter/{name}').cqcode))
        except Exception as e:
            sv.logger.exception(e)
    imgs = ' '.join(imgs)
    return f"@{name}({screen_name})\n{time}\n\n{text}\n{imgs}"


def has_media(item):
    try:
        return bool(item['extended_entities']['media'][0]['media_url'])
    except:
        return False


@sv.on_prefix('推特查询')
async def one_tweet(bot, ev: CQEvent):
    args = str(ev.message).strip()
    if not args or not args.isdecimal():
        await bot.finish(ev, "请在指令后输入推文id")
    rsp = api.request('statuses/show/:%d' % int(args))
    items = rsp.get_iterator()
    twts = list(map(tweet_id_formatter, items))
    for t in twts:
        try:
            await bot.send(ev, t)
        except Exception as e:
            sv.logger.exception(e)
        await asyncio.sleep(0.5)


def check_screen_name(screen_name):
    params = {
        'screen_name': screen_name,
        'count': 10,
        'exclude_replies': 'true',
        'include_rts': 'true',
    }
    rsp = api.request('statuses/user_timeline', params)
    if not rsp.status_code == 200:
        return False
    item_li = rsp.json()
    if len(item_li) == 0:
        return False
    return True


@sv.on_prefix(['推特订阅'])
async def subscribe(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能设置订阅。', at_sender=True)
    sub_id = get_message_text(ev)
    # 检查推主是否存在
    if not check_screen_name(sub_id):
        await bot.finish(ev, '查询用户失败。', at_sender=True)
    # params = {'screen_name': sub_id}
    # r = await twt_request(URL_USER_LOOKUP, params)
    # if not r.status_code == 200:
    #     await bot.finish(ev, '查询用户失败。', at_sender=True)
    # screen_name = r.json()[0].get('screen_name')
    # if screen_name != sub_id:
    #     await bot.finish(ev, f'用户名查询不符，是否为"{screen_name}"?', at_sender=True)
    bc = TwitterCounter()
    sub = SubInfo()
    sub.gid = ev.group_id
    sub.subid = sub_id
    sub.mode = 1
    sub.last_time = None
    bc._save_sub_info(sub)
    await bot.send(ev, "订阅成功")


@sv.on_prefix(['推特图片订阅'])
async def subscribe(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能设置订阅。', at_sender=True)
    msg = str(ev.message).strip()
    sub_id = msg
    # 检查推主是否存在
    # 检查推主是否存在
    if not check_screen_name(sub_id):
        await bot.finish(ev, '查询用户失败。', at_sender=True)
    # params = {'screen_name': sub_id}
    # r = await twt_request(URL_USER_LOOKUP, params)
    # if not r.status_code == 200:
    #     await bot.finish(ev, '查询用户失败。', at_sender=True)
    # screen_name = r.json()[0].get('screen_name')
    # if screen_name != sub_id:
    #     await bot.finish(ev, f'用户名查询不符，是否为"{screen_name}"?', at_sender=True)
    bc = TwitterCounter()
    sub = SubInfo()
    sub.gid = ev.group_id
    sub.subid = sub_id
    sub.mode = 0
    sub.last_time = None
    bc._save_sub_info(sub)
    await bot.send(ev, "订阅成功")


@sv.on_prefix(['取消推特订阅'])
async def subscribe(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能设置订阅。', at_sender=True)
    msg = str(ev.message).strip()
    sub_id = msg
    bc = TwitterCounter()
    sub = bc._get_sub(ev.group_id, sub_id)
    if not sub:
        await bot.finish(ev, '未订阅该用户，无需取消', at_sender=True)
    bc._del_sub(ev.group_id, sub_id)
    await bot.send(ev, "取消订阅成功")


@sv.on_prefix(['检查推特订阅'])
async def checksub(bot, ev: CQEvent):
    msg = str(ev.message).strip()
    sub_id = msg
    bc = TwitterCounter()
    sub = bc._get_sub(ev.group_id, sub_id)
    if sub:
        result = '订阅中'
    else:
        result = '未订阅'
    await bot.send(ev, result)


@sv.on_prefix(['推特订阅列表'])
async def sublist(bot, ev: CQEvent):
    gid = ev.group_id
    bc = TwitterCounter()
    sub_li = bc._get_sub_list(gid)
    msg_li = ['订阅列表：']
    for sub in sub_li:
        sub_id = sub.subid
        mode_desc = "全部推特" if sub.mode else "仅图片"
        msg_li.append(f'{sub_id}({mode_desc})')
    await bot.send(ev, '\n'.join(msg_li))


@sv.on_prefix(['测试推特订阅'])
async def test_scan(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '测试用 勿扰。', at_sender=True)
    await scan_job()
    print("测试成功")


def build_msg(item):
    user_name = item['user']['name']
    screen_name = item['user']['screen_name']
    text = item['text']
    time = time_formatter(item['created_at'])
    imgs = []
    if has_media(item):
        for u_item in item['extended_entities']['media']:
            img = u_item['media_url']
            if re.search(r'\.(jpg|jpeg|png|gif|jfif|webp)$', img, re.I):
                name = requests_download_url(img, R.img('twitter').path)
            imgs.append(str(R.img(f'twitter/{name}').cqcode))
    img_msg = ""
    if imgs:
        img_msg += '\n' + "\n".join(imgs)
    msg = f"""
{time}
{user_name}({screen_name}):
{text}{img_msg}
""".strip()
    return msg


@sv.scheduled_job('cron', minute='*/20', jitter=20)
async def scan_job():
    sv.logger.info("开始扫描推特订阅信息")
    bot = sv.bot
    bc = TwitterCounter()
    sub_li = bc._get_all_sub()
    dic = {}
    for sub in sub_li:
        if not dic.get(sub.subid):
            dic[sub.subid] = []
        dic[sub.subid].append(sub)

    for sub_id in dic.keys():
        params = {
            'screen_name': sub_id,
            'count': 10,
            'exclude_replies': 'true',
            'include_rts': 'true',
        }
        rsp = api.request('statuses/user_timeline', params)
        if not rsp.status_code == 200:
            continue
        item_li = rsp.json()
        if len(item_li) == 0:
            continue
        g_sub_li = dic[sub_id]
        self_dic = {}
        self_ids = bot._wsr_api_clients.keys()
        for sid in self_ids:
            gl = await bot.get_group_list(self_id=sid)
            g_ids = [g['group_id'] for g in gl]
            self_dic[sid] = g_ids

        last_time = time_stamp(item_li[0]['created_at'])
        for sub in g_sub_li:
            old_time = sub.last_time
            sub.last_time = last_time
            bc._save_sub_info(sub)
            if not old_time:
                if sub.mode:
                    item = item_li[0]
                    msg = build_msg(item)
                else:
                    filter_li = [i for i in item_li if has_media(i)]
                    if filter_li:
                        msg = build_msg(filter_li[0])
                    else:
                        continue
                # self_ids = bot._wsr_api_clients.keys()
                for sid in self_ids:
                    if sub.gid in self_dic[sid]:
                        try:
                            await sv.bot.send_group_msg(self_id=sid, group_id=sub.gid, message=msg)
                        except:
                            sv.logger.error("发送群消息失败！")
            else:
                if sub.mode:
                    filter_li = [i for i in item_li if time_stamp(i['created_at']) > old_time]
                else:
                    last_time = sub.last_time
                    sub.last_time = time_stamp(item_li[0]['created_at'])
                    filter_li = [i for i in item_li if time_stamp(i['created_at']) > old_time]
                    filter_li = [i for i in filter_li if has_media(i)]
                filter_li.reverse()

                for item in filter_li:
                    msg = build_msg(item)
                    for sid in self_ids:
                        if sub.gid in self_dic[sid]:
                            try:
                                await sv.bot.send_group_msg(self_id=sid, group_id=sub.gid, message=msg)
                            except:
                                sv.logger.error("发送群消息失败！")


@sv.on_prefix(['看推特'])
async def sublist(bot, ev: CQEvent):
    screen_name = get_message_text(ev)
    params = {
        'screen_name': screen_name,
        'count': 10,
        'exclude_replies': 'true',
        'include_rts': 'true',
    }
    rsp = api.request('statuses/user_timeline', params)
    if not rsp.status_code == 200:
        await bot.finish(ev, "查询失败")
    item_li = rsp.json()
    if len(item_li) == 0:
        await bot.finish(ev, "没有查询到推特内容")
    for i in item_li:
        msg = build_msg(i)
        await bot.send(ev, msg)
        await asyncio.sleep(1)
