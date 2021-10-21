from hoshino import R, Service, priv, util
import hoshino
from hoshino.typing import CQEvent
from bilibili_api import user
from .BilibiliCounter import *

sv = Service('b站订阅', enable_on_default=False, bundle='b站订阅', help_=
'''[b站订阅] {b站用户id}
[取消b站订阅] {b站用户id}
[检查b站订阅]
[b站订阅列表]
''')


@sv.on_prefix(['b站订阅'])
async def subscribe(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能设置订阅。', at_sender=True)
    msg = str(ev.message).strip()
    if not msg.isdecimal():
        await bot.finish(ev, '请输入订阅用户的id 不能包含数字以外的内容', at_sender=True)
    sub_id = int(msg)
    u = user.User(sub_id)
    try:
        info = await u.get_user_info()
    except:
        await bot.finish(ev, '用户不存在！请检查用户id', at_sender=True)
    bc = BilibiliCounter()
    sub = SubInfo()
    sub.gid = ev.group_id
    sub.subid = sub_id
    sub.last_time = None
    bc._save_sub_info(sub)
    await bot.send(ev, "订阅成功")


@sv.on_prefix(['取消b站订阅'])
async def subscribe(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能设置订阅。', at_sender=True)
    msg = str(ev.message).strip()
    if not msg.isdecimal():
        await bot.finish(ev, '请输入订阅用户的id 不能包含数字以外的内容', at_sender=True)
    sub_id = int(msg)
    bc = BilibiliCounter()
    sub = bc._get_sub(ev.group_id, sub_id)
    if not sub:
        await bot.finish(ev, '未订阅该用户，无需取消', at_sender=True)
    bc._del_sub(ev.group_id, sub_id)
    await bot.send(ev, "取消订阅成功")


@sv.on_prefix(['检查b站订阅'])
async def checksub(bot, ev: CQEvent):
    msg = str(ev.message).strip()
    if not msg.isdecimal():
        await bot.finish(ev, '请输入订阅用户的id 不能包含数字以外的内容', at_sender=True)
    sub_id = int(msg)
    bc = BilibiliCounter()
    sub = bc._get_sub(ev.group_id, sub_id)
    if sub:
        result = '订阅中'
    else:
        result = '未订阅'
    await bot.send(ev, result)


@sv.on_prefix(['b站订阅列表'])
async def sublist(bot, ev: CQEvent):
    gid = ev.group_id
    bc = BilibiliCounter()
    sub_li = bc._get_sub_list(gid)
    msg_li = ['订阅列表：']
    for sub in sub_li:
        sub_id = sub.subid
        u = user.User(sub_id)
        try:
            info = await u.get_user_info()
            name = info['name']
        except:
            name = "未知用户"
        msg_li.append(f'{name}({sub_id})')
    await bot.send(ev, '\n'.join(msg_li))


@sv.on_prefix(['测试b站动态'])
async def unsubscribe(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '测试用 勿扰。', at_sender=True)
    await scan_job()
    print("测试成功")


def resolve_origin_msg(type, origin_dic):
    msg = ""
    if type == 2:
        msg += f"{origin_dic['user']['name']}({origin_dic['user']['uid']}:\n)"
        msg += origin_dic['item']['description']
        pics = origin_dic['item']['pictures']
        for pic in pics:
            pic_img = pic['img_src']
        msg += f"\n[CQ:image,file={pic_img}]"
    elif type == 4:
        name = origin_dic["user"]["uname"]
        uid = origin_dic["user"]["uid"]
        msg += f'{name}({uid}):\n'
        msg += origin_dic['item']['content']
    elif type == 8:
        name = origin_dic["owner"]["name"]
        uid = origin_dic["owner"]["mid"]
        msg += f'{name}({uid}):\n'
        msg += origin_dic["desc"]
        msg += f"\n" + origin_dic['short_link'].replace('\\', '')
        pic = origin_dic['pic'].replace('\\', '')
        msg += f"\n[CQ:image,file={pic}]"
    elif type == 4098:
        msg += origin_dic["apiSeasonInfo"]["type_name"] + ":" + origin_dic["apiSeasonInfo"]["title"]
        cover = origin_dic['cover'].replace('\\', '')
        url = origin_dic['url'].replace('\\', '')
        msg += f"\n[CQ:image,file={cover}]"
        msg += f"\n{url}"
    else:
        msg += "未解析的回复类型，请联系开发人员!"
    return msg


def build_msg(card):
    desc = card.get('desc')
    card = card.get('card')
    msg = ""
    uid = desc['user_profile']['info']['uid']
    name = desc['user_profile']['info']['uname']
    msg += f'{name}({uid}):\n'

    if desc["type"] == 1:
        msg += card['item']['content']
        msg += "\n=======回复=======\n"
        origin_dic = eval(card['origin'].replace('null', 'None'))
        msg += resolve_origin_msg(desc['orig_type'], origin_dic)
    elif desc['type'] == 2:
        msg += card['item']['description']
        pic = card['item']['pictures']
        for i in pic:
            msg += f"\n[CQ:image,file={i['img_src']}]"
    elif desc["type"] == 4:
        msg += card['item']['content']
    elif desc["type"] == 8:
        msg += "=======发布视频======="
        msg += "\n标题:" + card['title']
        msg += "\n简介:" + card['desc']
        msg += "\n地址:" + card['short_link']
        msg += f"\n[CQ:image,file={card['pic']}]"
    else:
        msg += "未解析的动态类型，请联系开发人员!"
    return msg


@sv.scheduled_job('cron', minute='*/5', jitter=20)
async def scan_job():
    sv.logger.info("开始扫描b站订阅信息")

    bc = BilibiliCounter()
    sub_li = bc._get_all_sub()
    dic = {}
    for sub in sub_li:
        if not dic.get(sub.subid):
            dic[sub.subid] = []
        dic[sub.subid].append(sub)

    for sub_id in dic.keys():
        u = user.User(sub_id)
        page = await u.get_dynamics(0)
        g_sub_li = dic[sub_id]
        for sub in g_sub_li:
            if not sub.last_time:
                cards = page['cards']
                if cards:
                    sub.last_time = cards[0]['desc']['timestamp']
                    msg = build_msg(cards[0])
                    for sid in hoshino.get_self_ids():
                        await sv.bot.send_group_msg(self_id=sid, group_id=sub.gid, message=msg)
                bc._save_sub_info(sub)
            else:
                cards = page['cards']
                if cards:
                    old_time = sub.last_time
                    sub.last_time = cards[0]['desc']['timestamp']
                    filter_card = []
                    for card in cards:
                        if card['desc']['timestamp'] > old_time:
                            filter_card.append(card)
                    filter_card.reverse()
                    for i in filter_card:
                        msg = build_msg(i)
                        for sid in hoshino.get_self_ids():
                            await sv.bot.send_group_msg(self_id=sid, group_id=sub.gid, message=msg)
                    bc._save_sub_info(sub)
