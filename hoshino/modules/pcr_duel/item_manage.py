import re
import time
from decimal import Decimal
import asyncio
import nonebot
import pytz
from . import duel_chara
from . import sv
from .duelconfig import *
from hoshino.typing import CQEvent
from .ScoreCounter import ScoreCounter2
from .ItemCounter import ItemCounter
from hoshino import priv

ITEM_INFO = {
    "1": {
        "id": "1",
        "name": "天命之子",
        "rank": "S",
        "desc": "无视100的等级上限 为自己的女友增加10级 最高不超过200级(仅100满级可以使用)",
    },
    "2": {
        "id": "2",
        "name": "前世之忆",
        "rank": "S",
        "desc": "保留女友的等级rank为自己女友增加一次转生次数 不能超过转生次数限制",
    },
    "3": {
        "id": "3",
        "name": "命运牵引",
        "rank": "S",
        "desc": "定向招募卡池中的女友",
    },
    "4": {
        "id": "4",
        "name": "空想之物",
        "rank": "A",
        "desc": "90%概率随机获得一件UR装备 10%概率获得MR装备",
    },
    "5": {
        "id": "5",
        "name": "好事成双",
        "rank": "A",
        "desc": "选择自己已拥有的一件道具 令其数量+1",
    },
    "6": {
        "id": "6",
        "name": "四重存在",
        "rank": "A",
        "desc": "选择自己一个A级以下的道具 令其数量+3",
    },
    "7": {
        "id": "7",
        "name": "狂赌之渊",
        "rank": "B",
        "desc": "为本群开启梭哈庆典 持续一小时",
    },
    "8": {
        "id": "8",
        "name": "咲夜怀表",
        "rank": "B",
        "desc": "使用后刷新自己的副本 签到 低保 约会 决斗次数",
    },
    "9": {
        "id": "9",
        "name": "梦境巡游",
        "rank": "B",
        "desc": "可以发现女友 花钱可以刷新发现结果 选择要或不要 至多10次",
    },

    "10": {
        "id": "10",
        "name": "超再生力",
        "rank": "B",
        "desc": "使用后刷新自己当日副本限制次数及决斗次数",
    },
    "11": {
        "id": "11",
        "name": "有效分裂",
        "rank": "B",
        "desc": "使用后随机获取两个道具",
    },
    "12": {
        "id": "12",
        "name": "财富亨通",
        "rank": "C",
        "desc": "随机增加财富(10000-100000)",
    },
    "13": {
        "id": "13",
        "name": "乐善好施",
        "rank": "C",
        "desc": "发送一次50000金币5个的红包(不消耗自己的金币) 每有一个人领取 增加500声望",
    },
    "14": {
        "id": "14",
        "name": "藏宝图",
        "rank": "C",
        "desc": "进行一次愉快的挖宝 随机金币 经验 装备 道具",
    },
    "15": {
        "id": "15",
        "name": "战无不胜",
        "rank": "C",
        "desc": "使用后下一次副本战斗战力计算增加50%",
    },
    "16": {
        "id": "16",
        "name": "战斗记忆",
        "rank": "C",
        "desc": "增加300000经验到自己经验池",
    },
    "17": {
        "id": "17",
        "name": "零时迷子",
        "rank": "C",
        "desc": "使用后刷新自己当日副本限制次数",
    },
    "18": {
        "id": "18",
        "name": "鬼人药剂",
        "rank": "D",
        "desc": "使用后下一次副本战斗战力计算增加20%",
    },
    "19": {
        "id": "19",
        "name": "派对狂欢",
        "rank": "D",
        "desc": "为本群开启免费招募庆典 持续一小时",
    },
    "20": {
        "id": "20",
        "name": "公主之心",
        "rank": "D",
        "desc": "全部女友增加10好感",
    },
    "21": {
        "id": "21",
        "name": "生财有道",
        "rank": "D",
        "desc": "随机增加财富(1000-30000)",
    },
    "22": {
        "id": "22",
        "name": "小恩小惠",
        "rank": "D",
        "desc": "随机增加声望(100-3000)",
    },
    "23": {
        "id": "23",
        "name": "再来一瓶",
        "rank": "D",
        "desc": "刷新自己签到次数",
    },
    "24": {
        "id": "24",
        "name": "精英对局",
        "rank": "D",
        "desc": "刷新自己的决斗次数",
    },
    "25": {
        "id": "25",
        "name": "经验之书",
        "rank": "D",
        "desc": "增加100000经验到自己经验池",
    },
}

ITEM_NAME_MAP = {ITEM_INFO[i]["name"]: ITEM_INFO[i] for i in ITEM_INFO.keys()}

ITEM_RANK_MAP = {}


@sv.on_fullmatch(['物品帮助', '道具帮助'])
async def gift_help(bot, ev: CQEvent):
    msg = '''
╔                                        ╗  
             道具系统帮助
[我的道具]
[道具效果] {道具名称}
[使用道具] 注意如果需要指定女友或者群友 请在后面加空格加上女友名或@群友
[投放道具] 维护组指令 用来测试道具

注:
道具现只有签到能获取一次
道具出现概率：
S:1%概率
A:5%概率
B:10%概率
C:20%概率
D:64%概率
╚                                        ╝
 '''
    await bot.send(ev, msg)


@sv.on_fullmatch(['道具查询', '我的道具'])
async def my_item(bot, ev: CQEvent):
    counter = ItemCounter()
    gid = ev.group_id
    uid = ev.user_id
    items = counter._get_item(gid, uid)
    msg = "==== 道具列表 ===="
    for i in items:
        msg += f"\n{ITEM_INFO[str(i[0])]['name']} *{i[1]}"
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['道具效果'])
async def item_info(bot, ev: CQEvent):
    name = str(ev.message).strip()
    info = ITEM_NAME_MAP.get("name")
    if info:
        await bot.send(ev, f"道具{name}的效果为：{info['desc']}")
    else:
        await bot.send(ev, f"未找到名称为{name}的道具")


@sv.on_prefix(['发放道具', "投放道具"])
async def item_info(bot, ev: CQEvent):
    gid = ev.group_id
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, f"你无权使用投放道具功能", at_sender=True)
    msg = str(ev.message).strip().split()
    fa_uid = int(msg[0])
    item_info = ITEM_NAME_MAP[msg[1]]
    if not item_info:
        await bot.finish(ev, f"未找到名称为{msg[1]}的道具", at_sender=True)
    item_id = int(item_info['id'])
    counter = ItemCounter()
    counter._add_item(gid, fa_uid, item_id)


@sv.on_prefix(['使用道具'])
async def use_item(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg = str(ev.message).strip().split()
    item_info = ITEM_NAME_MAP[msg[0]]
    if not item_info:
        await bot.finish(ev, f"未找到名称为{msg[0]}的道具", at_sender=True)
    counter = ItemCounter()
    num = counter._get_item_num(gid, uid, int(item_info['id']))
    if num < 1:
        await bot.finish(ev, f"背包中道具{msg[0]}数量不足", at_sender=True)

    result = await use_item(msg[0], msg[1:], bot, ev)
    if result[0]:
        counter._add_item(gid, uid, int(item_info['id']), num=-1)
    await bot.send(ev, result[1])


register = dict()


async def use_item(name, msg, bot, ev):
    func = register.get(name)
    if func:
        return await func(msg, bot, ev)
    return (False, "道具未实装")


# 注解msg 传入正则表达式进行匹配
def msg_route(item_name):
    def show(func):
        def warpper(content):
            func(content)

        register[item_name] = warpper
        return warpper

    return show


@msg_route("命运牵引")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if len(msg) == 0:
        return (False, "请在道具后增加 空格 女友名称")
    name = msg[0]
    cid = duel_chara.name2id(name)
    if cid == 1000:
        return (False, "请输入正确的角色名")
    duel = DuelCounter()
    owner = duel._get_card_owner(gid, cid)
    c = duel_chara.fromid(cid)
    if owner == 0:
        duel._add_card(gid, uid, cid)
        nvmes = get_nv_icon(cid)
        return (True, f"{c.name}感受到了命运的牵引，前来与你相会。{nvmes}")
    else:
        return (False, f"{c.name}已经心有所属了")


@msg_route("天命之子")
async def add_level(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if len(msg) == 0:
        return (False, "请在道具后+空格+女友名称")
    name = msg[0]
    cid = duel_chara.name2id(name)
    if cid == 1000:
        return (False, "请输入正确的角色名")
    duel = DuelCounter()
    owner = duel._get_card_owner(gid, cid)
    c = duel_chara.fromid(cid)
    nvmes = get_nv_icon(cid)
    if owner == 0:
        return (False, f"{c.name}现在还是单身哦,先去约到她吧{nvmes}")
    if uid != owner:
        msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法对其使用道具哦。'
        return (False, msg)
    CE = CECounter()
    dengji = CE._get_card_level(gid, uid, cid)
    if dengji < 100:
        return (False, f"角色等级必须到达100级才能使用,{c.name}现在等级为{dengji}")
    if dengji == 200:
        return (False, f"角色{c.name}已经200级了，无法再突破上限")
    now_level = dengji + 10 if dengji < 190 else 200
    CE._add_card_exp(gid, uid, cid, now_level, 0)
    return (True, f"角色{c.name}突破了自己的才能界限 达到了新的高度，当前等级为{now_level}级{nvmes}")


@msg_route("前世之忆")
async def add_zhuansheng(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if len(msg) == 0:
        return (False, "请在道具后+空格+女友名称")
    name = msg[0]
    cid = duel_chara.name2id(name)
    if cid == 1000:
        return (False, "请输入正确的角色名")
    duel = DuelCounter()
    owner = duel._get_card_owner(gid, cid)
    c = duel_chara.fromid(cid)
    nvmes = get_nv_icon(cid)
    if owner == 0:
        return (False, f"{c.name}现在还是单身哦,先去约到她吧{nvmes}")
    if uid != owner:
        msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法对其使用道具哦。'
        return (False, msg)
    CE = CECounter()
    zllevel = CE._get_zhuansheng(gid, uid, cid)
    MAX_ZS = 5
    if zllevel == MAX_ZS:
        return (False, '该女友已经到最高转生等级，无法继续转生啦。')
    CE._add_zhuansheng(gid, uid, cid)
    await bot.send(ev, f'您的女友{name}想起了前世的记忆，基础战力加成提升了{nvmes}')


@msg_route("空想之物")
async def add_zhuansheng(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    num = random.randint(1, 100)
    if num <=10:
        pass
    else:
        pass
