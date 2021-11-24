from hoshino.config import telegram as cfg
from hoshino import R, Service, priv
from hoshino.typing import CQEvent
from .TelegramCounter import *
from nonebot import MessageSegment
import time
from telethon import TelegramClient
import socks
proxy = dict(hostname=cfg.proxy_ip, port=int(cfg.proxy_port))

def getClient():
    return TelegramClient('anon',cfg.api_id, cfg.api_hash, proxy=("socks5", cfg.proxy_ip, cfg.proxy_port))
    # return Client("my_account", cfg.api_id, cfg.api_hash, proxy=proxy)


async def getChannel():
    able_dia_map = {}
    async with getClient() as client:
        dialogs = await client.get_dialogs()
    for dialog in dialogs:
        if dialog.is_channel:
            able_dia_map[dialog.id] = dialog.name
    return able_dia_map


# 缓存数据
async def get_10_chat_msg(sub_id):
    data = []
    async with getClient() as client:
        async for message in client.iter_messages(sub_id, limit=20):
            content = {}
            timestamp = int(time.mktime(message.date.timetuple()))
            content['timestamp'] = message.id
            content['msg'] = f"{message.chat.title}:\n{message.text}"
            if message.photo:
                path = await message.download_media(file=R.img("ghs/channel").path)
                image = str(MessageSegment.image(f'file:///{os.path.abspath(path)}'))
                content['msg'] = content['msg'] + image
            data.append(content)
    return data


sv = Service('电报订阅', enable_on_default=False, bundle='电报订阅', help_=
'''[电报订阅] {电报频道id}
[取消电报订阅] {电报频道id}
[检查电报订阅] {电报频道id}
[电报订阅列表]
[可订阅电报列表]
''')


@sv.on_prefix(['电报订阅'])
async def subscribe(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能设置订阅。', at_sender=True)
    msg = str(ev.message).strip()
    if not msg.isdecimal():
        await bot.finish(ev, '请输入订阅用户的id 不能包含数字以外的内容', at_sender=True)
    sub_id = -int(msg)
    able_dia_map = await getChannel()
    if sub_id not in able_dia_map.keys():
        await bot.finish(ev, '频道不存在！请联系维护人员添加！', at_sender=True)
    bc = TelegramCounter()
    sub = SubInfo()
    sub.gid = ev.group_id
    sub.subid = sub_id
    sub.last_time = None
    bc._save_sub_info(sub)
    await bot.send(ev, "订阅成功")


@sv.on_prefix(['取消电报订阅'])
async def subscribe(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能设置订阅。', at_sender=True)
    msg = str(ev.message).strip()
    if not msg.isdecimal():
        await bot.finish(ev, '请输入订阅用户的id 不能包含数字以外的内容', at_sender=True)
    sub_id = -int(msg)
    bc = TelegramCounter()
    sub = bc._get_sub(ev.group_id, sub_id)
    if not sub:
        await bot.finish(ev, '未订阅该用户，无需取消', at_sender=True)
    bc._del_sub(ev.group_id, sub_id)
    await bot.send(ev, "取消订阅成功")


@sv.on_prefix(['检查电报订阅'])
async def checksub(bot, ev: CQEvent):
    msg = str(ev.message).strip()
    if not msg.isdecimal():
        await bot.finish(ev, '请输入订阅用户的id 不能包含数字以外的内容', at_sender=True)
    sub_id = -int(msg)
    bc = TelegramCounter()
    sub = bc._get_sub(ev.group_id, sub_id)
    if sub:
        result = '订阅中'
    else:
        result = '未订阅'
    await bot.send(ev, result)


@sv.on_prefix(['可订阅电报列表'])
async def able_sublist(bot, ev: CQEvent):
    able_dia_map = await getChannel()
    msg_li = ["可订阅列表："]
    for i in able_dia_map.keys():
        name = able_dia_map[i]
        msg_li.append(f"{name}({-i})")
    await bot.send(ev, '\n'.join(msg_li))


@sv.on_prefix(['电报订阅列表'])
async def sublist(bot, ev: CQEvent):
    gid = ev.group_id
    bc = TelegramCounter()
    sub_li = bc._get_sub_list(gid)
    msg_li = ['订阅列表：']
    able_dia_map = await getChannel()
    for sub in sub_li:
        sub_id = sub.subid
        name = able_dia_map.get(sub_id)
        if not name:
            name = "未知频道"
        msg_li.append(f'{name}({sub_id})')
    await bot.send(ev, '\n'.join(msg_li))


@sv.on_prefix(['测试电报订阅'])
async def unsubscribe(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '测试用 勿扰。', at_sender=True)
    await scan_job()
    print("测试成功")


@sv.scheduled_job('cron', minute='*/7', jitter=20)
async def scan_job():
    sv.logger.info("开始扫描电报频道信息")
    bot = sv.bot
    bc = TelegramCounter()
    sub_li = bc._get_all_sub()
    dic = {}
    for sub in sub_li:
        if not dic.get(sub.subid):
            dic[sub.subid] = []
        dic[sub.subid].append(sub)

    for sub_id in dic.keys():
        page = await get_10_chat_msg(sub_id)
        if not page:
            continue
        g_sub_li = dic[sub_id]
        self_dic = {}
        self_ids = bot._wsr_api_clients.keys()
        for sid in self_ids:
            gl = await bot.get_group_list(self_id=sid)
            g_ids = [g['group_id'] for g in gl]
            self_dic[sid] = g_ids
        for sub in g_sub_li:
            last_time = sub.last_time
            sub.last_time = page[0]['timestamp']
            # 没发过时 发最后一条
            if not last_time:
                msg = page[0]['msg']
                self_ids = bot._wsr_api_clients.keys()
                for sid in self_ids:
                    if sub.gid in self_dic[sid]:
                        try:
                            await sv.bot.send_group_msg(self_id=sid, group_id=sub.gid, message=msg)
                        except:
                            sv.logger.error("发送群消息失败！")
            # 发过时 发没发过的所有
            else:
                cards = page
                filter_card = []
                for card in cards:
                    if card['timestamp'] > last_time:
                        filter_card.append(card)
                filter_card.reverse()
                for i in filter_card:
                    msg = i['msg']
                    for sid in self_ids:
                        if sub.gid in self_dic[sid]:
                            try:
                                await sv.bot.send_group_msg(self_id=sid, group_id=sub.gid, message=msg)
                            except:
                                sv.logger.error("发送群消息失败！")
            bc._save_sub_info(sub)
