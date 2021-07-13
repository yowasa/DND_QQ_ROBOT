import asyncio

from hoshino import priv
from hoshino.typing import CQEvent
from hoshino.typing import CommandSession
from . import duel_chara
from . import sv
from .ItemCounter import ItemCounter
from .ScoreCounter import ScoreCounter2
from .duelconfig import *
from .zhuti import duel_judger, r_gold

ITEM_INFO = {
    "1": {
        "id": "1",
        "name": "天命之子",
        "rank": "S",
        "desc": "无视100的等级上限 为自己的女友增加10级 最高不超过200级(仅100满级以上可以使用)",
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
        "desc": "定向招募卡池中的女友,无视卡池限制与女友上限",
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
        "desc": "为本群开启梭哈庆典 持续到这个小时结束",
    },
    "8": {
        "id": "8",
        "name": "咲夜怀表",
        "rank": "A",
        "desc": "使用后刷新自己的副本 签到 低保 约会 决斗 礼物次数",
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
        "name": "异界馈赠",
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
        "desc": "进行一次愉快的挖宝 随机金币 声望 装备 道具",
    },
    "15": {
        "id": "15",
        "name": "战无不胜",
        "rank": "C",
        "desc": "使用后下一次副本战斗战力计算增加2倍",
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
        "desc": "使用后下一次副本战斗战力计算增加1倍",
    },
    "19": {
        "id": "19",
        "name": "派对狂欢",
        "rank": "D",
        "desc": "为本群开启免费招募庆典 持续到这个小时结束",
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

for k, v in ITEM_INFO.items():
    if ITEM_RANK_MAP.get(v['rank']):
        ITEM_RANK_MAP[v['rank']] = []
    ITEM_RANK_MAP.get(v['rank']).append(v['id'])


@sv.on_fullmatch(['物品帮助', '道具帮助'])
async def gift_help(bot, ev: CQEvent):
    msg = '''
╔                                        ╗  
             道具系统帮助
[我的道具]
[道具效果] {道具名称}
[使用道具] {道具名称} 注意如果需要指定女友或者群友 请在后面加空格加上女友名或@群友
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
    msg = "\n==== 道具列表 ===="
    for i in items:
        msg += f"\n{ITEM_INFO[str(i[0])]['name']} *{i[1]}"
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['道具效果'])
async def item_info(bot, ev: CQEvent):
    name = str(ev.message).strip()
    info = ITEM_NAME_MAP.get(name)
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
    await bot.send(ev, f"投放成功", at_sender=True)


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
        async def warpper(msg, bot, ev: CQEvent):
            return await func(msg, bot, ev)

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
async def add_zhuangbei(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    num = random.randint(1, 100)
    if num <= 10:
        awardequip_info = add_equip_info(gid, uid, 6, [136, 255, 247, 248, 249, 250, 251, 252, 253, 254])
        return (
            True,
            f"你使用了空想之物，一道金光闪过，你获得了{awardequip_info['model']}品质的{awardequip_info['type']}:{awardequip_info['name']}")
    else:
        awardequip_info = add_equip_info(gid, uid, 5,
                                         [108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122,
                                          123, 124, 125, 126, 127, 128, 195, 196, 197, 198, 199, 200, 201, 202, 204,
                                          205, 206, 207, 208, 209, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237,
                                          238, 239, 240, 241, 242, 243, 244, 245, 246, 260, 265, 266, 267, 278, 279,
                                          280, 282, 283, 284, 285, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297,
                                          298, 299, 300, 301, 302, 303, 304, 305, 306, 312, 313, 314, 315, 316, 317,
                                          318, 319, 320])
        return (True,
                f"你使用了空想之物，但你的想象不足以触及幻想，你获得了{awardequip_info['model']}品质的{awardequip_info['type']}:{awardequip_info['name']}")


@msg_route("好事成双")
async def add_item_2(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    item_info = ITEM_NAME_MAP[msg[0]]
    if not item_info:
        return (False, f"未找到名称为{msg[0]}的道具")
    counter = ItemCounter()
    num = counter._get_item_num(gid, uid, int(item_info['id']))
    if num < 1:
        return (False, f"背包中不存在道具{msg[0]}")
    counter._add_item(gid, uid, int(item_info['id']))
    return (True, f"你消耗了好事成双背包中的{msg[0]}增加了一个")


@msg_route("四重存在")
async def add_item_4(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    item_info = ITEM_NAME_MAP[msg[0]]
    if not item_info:
        return (False, f"未找到名称为{msg[0]}的道具")
    if item_info['rank'] in ['S', 'A']:
        return (False, f"四重存在只能对A级一下（不包括A）的道具使用")
    counter = ItemCounter()
    num = counter._get_item_num(gid, uid, int(item_info['id']))
    if num < 1:
        return (False, f"背包中不存在道具{msg[0]}")
    counter._add_item(gid, uid, int(item_info['id']), num=3)
    return (True, f"你消耗了好事成双，背包中的一个{msg[0]}分裂成了四个")


@msg_route("狂赌之渊")
async def open_sou(msg, bot, ev: CQEvent):
    gid = ev.group_id
    duel = DuelCounter()
    if duel._get_SW_CELE(gid) == None:
        duel._initialization_CELE(gid, Gold_Cele, QD_Cele, Suo_Cele, SW_add, FREE_DAILY)
    GC_Data = duel._get_GOLD_CELE(gid)
    QC_Data = duel._get_QC_CELE(gid)
    SW_Data = duel._get_SW_CELE(gid)
    FREE_Data = duel._get_FREE_CELE(gid)
    duel._initialization_CELE(gid, GC_Data, QC_Data, 1, SW_Data, FREE_Data)
    counter = ItemCounter()
    counter._save_group_state(gid, 0, 1)

    return (True, f'在本小时结束前已开启本群梭哈倍率庆典，梭哈时的倍率将额外提升{Suo_Cele_Num}倍')


@msg_route("咲夜怀表")
async def open_sou(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    guid = gid, uid
    # 副本 签到 低保 约会 决斗 礼物
    daily_dun_limiter.reset(guid)
    daily_sign_limiter.reset(guid)
    daily_zero_get_limiter.reset(guid)
    daily_date_limiter.reset(guid)
    daily_duel_limiter.reset(guid)
    daily_gift_limiter.reset(guid)
    return (True, f'时间穿梭，你仿佛来到了第二天，身上的疲劳一扫而空（副本 签到 低保 约会 决斗 礼物次数限制已重置）')


@msg_route("梦境巡游")
async def xunyou(msg, bot, ev: CQEvent):
    return (False, f'使用"开始巡游"指令开始你的梦境之旅')


@msg_route("超再生力")
async def super_regenerate(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    guid = gid, uid
    # 副本 签到 低保 约会 决斗 礼物
    daily_dun_limiter.reset(guid)
    daily_duel_limiter.reset(guid)
    return (True, f'你使用了超再生力，今天所受到的伤害全部恢复了（副本 决斗次数限制已重置）')


@msg_route("有效分裂")
async def super_regenerate(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    item_1 = choose_item()
    item_2 = choose_item()
    counter = ItemCounter()
    counter._add_item(gid, uid, int(item_1['id']))
    counter._add_item(gid, uid, int(item_2['id']))
    return (True, f'你使用了有效分裂 获得了道具{item_1["name"]}和{item_2["name"]}')


@msg_route("异界馈赠")
async def money_mall(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    score = random.randint(10000, 100000)
    CE = ScoreCounter2()
    CE._add_score(gid, uid, score)
    return (True, f'你吃着火锅唱着歌，一低头发现地上有{score}金币。')


@msg_route("乐善好施")
async def fa_money(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    gold = 50000
    num = 5
    if not r_gold.get_on_off_random_gold(ev.group_id):
        await bot.send(ev, f'已发放红包，金币总额为：{gold}\n数量：{num}\n请输入 领取红包')
        r_gold.turn_on_random_gold(gid)
        r_gold.set_gold(gid)
        r_gold.add_gold(gid, gold, num)
        r_gold.random_g(gid, gold, num)
        await asyncio.sleep(60)
        r_gold.turn_off_random_gold(gid)
        await bot.send(ev, '随机金币奖励活动已结束，请期待下次活动开启')
        number = len(r_gold.user[gid])
        add_p = number * 500
        r_gold.user = {}
        CE = ScoreCounter2()
        CE._add_prestige(gid, uid, add_p)
        return (True, f"由于你的乐善好施，你的声望提高了{add_p}")
    else:
        return (False, "本群现在已经有红包活动，请稍后再使用")


@msg_route("藏宝图")
async def wabao(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg_li = []
    sw_1 = random.randint(1, 100)
    sw_2 = random.randint(1, 100)
    sw_3 = random.randint(1, 100)
    sw_4 = random.randint(1, 100)
    sw_5 = random.randint(1, 100)
    sw_6 = random.randint(1, 100)
    sw_7 = random.randint(1, 100)
    sw_8 = random.randint(1, 100)
    sw_9 = random.randint(1, 100)

    CE = ScoreCounter2()
    counter = ItemCounter()
    if sw_1 == 1:
        awardequip_info = add_equip_info(gid, uid, 6, [136, 255, 247, 248, 249, 250, 251, 252, 253, 254])
        msg_li.append(f"你获得了{awardequip_info['model']}品质的{awardequip_info['type']}:{awardequip_info['name']}")
    if sw_2 <= 5:
        awardequip_info = add_equip_info(gid, uid, 5,
                                         [108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122,
                                          123, 124, 125, 126, 127, 128, 195, 196, 197, 198, 199, 200, 201, 202, 204,
                                          205, 206, 207, 208, 209, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237,
                                          238, 239, 240, 241, 242, 243, 244, 245, 246, 260, 265, 266, 267, 278, 279,
                                          280, 282, 283, 284, 285, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297,
                                          298, 299, 300, 301, 302, 303, 304, 305, 306, 312, 313, 314, 315, 316, 317,
                                          318, 319, 320])
        msg_li.append(f"你获得了{awardequip_info['model']}品质的{awardequip_info['type']}:{awardequip_info['name']}")
    if sw_3 <= 5:
        awardequip_info = add_equip_info(gid, uid, 5,
                                         [108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122,
                                          123, 124, 125, 126, 127, 128, 195, 196, 197, 198, 199, 200, 201, 202, 204,
                                          205, 206, 207, 208, 209, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237,
                                          238, 239, 240, 241, 242, 243, 244, 245, 246, 260, 265, 266, 267, 278, 279,
                                          280, 282, 283, 284, 285, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297,
                                          298, 299, 300, 301, 302, 303, 304, 305, 306, 312, 313, 314, 315, 316, 317,
                                          318, 319, 320])
        msg_li.append(f"你获得了{awardequip_info['model']}品质的{awardequip_info['type']}:{awardequip_info['name']}")
    if sw_4 <= 10:
        item = choose_item()
        counter._add_item(gid, uid, int(item['id']))
        msg_li.append(f"你获得了{item['name']}")
    if sw_5 <= 10:
        item = choose_item()
        counter._add_item(gid, uid, int(item['id']))
        msg_li.append(f"你获得了{item['name']}")
    if sw_6 <= 30:
        money = random.randint(1, 30000)
        CE._add_score(gid, uid, money)
        msg_li.append(f"你获得了{money}金币")
    if sw_7 <= 30:
        money = random.randint(1, 30000)
        CE._add_score(gid, uid, money)
        msg_li.append(f"你获得了{money}金币")
    if sw_8 <= 30:
        sw = random.randint(1, 3000)
        CE._add_prestige(gid, uid, sw)
        msg_li.append(f"你获得了{sw}声望")
    if sw_9 <= 30:
        sw = random.randint(1, 3000)
        CE._add_prestige(gid, uid, sw)
        msg_li.append(f"你获得了{sw}声望")
    if len(msg_li) == 0:
        return (True, f"你进行了一场愉快的探险，但是什么也没有发现")
    return (True, f"你进行了一场惊现的探险:\n" + "\n".join(msg_li))


def choose_item():
    number = random.randint(1, 100)
    if number == 1:
        i_ids = ITEM_RANK_MAP['S']
    elif number <= 6:
        i_ids = ITEM_RANK_MAP['A']
    elif number <= 16:
        i_ids = ITEM_RANK_MAP['B']
    elif number <= 36:
        i_ids = ITEM_RANK_MAP['C']
    else:
        i_ids = ITEM_RANK_MAP['D']
    id = random.choice(i_ids)
    return ITEM_INFO.get(id)


@msg_route("战无不胜")
async def battle_match(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    i_c = ItemCounter()
    old = i_c._get_buff_state(gid, uid)
    i_c._save_user_state(gid, uid, 0, old + 200)
    return (True, f"你使用了战无不胜，下一次进入副本战力计算增加200%！！")


@msg_route("战斗记忆")
async def battle_exp(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    CE._add_exp_chizi(gid, uid, 300000)
    return (True, f"你观看了一场异常精彩的战斗，获得了300000经验!！(加入经验池)")


@msg_route("零时迷子")
async def battle_exp(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    guid = gid, uid
    daily_dun_limiter.reset(guid)
    return (True, f'你使用了零时迷子，今天关闭的副本重新开放了（副本限制已重置）')


@msg_route("鬼人药剂")
async def battle_small(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    i_c = ItemCounter()
    old = i_c._get_buff_state(gid, uid)
    i_c._save_user_state(gid, uid, 0, old + 100)
    return (True, f"你使用了鬼人药剂，下一次进入副本战力计算增加100%！！")


@msg_route("派对狂欢")
async def patty_happy(msg, bot, ev: CQEvent):
    gid = ev.group_id
    duel = DuelCounter()
    if duel._get_SW_CELE(gid) == None:
        duel._initialization_CELE(gid, Gold_Cele, QD_Cele, Suo_Cele, SW_add, FREE_DAILY)
    GC_Data = duel._get_GOLD_CELE(gid)
    QC_Data = duel._get_QC_CELE(gid)
    SUO_Data = duel._get_SUO_CELE(gid)
    SW_Data = duel._get_SW_CELE(gid)
    duel._initialization_CELE(gid, GC_Data, QC_Data, SUO_Data, SW_Data, 1)
    counter = ItemCounter()
    counter._save_group_state(gid, 1, 1)
    return (True, f'在本小时结束前已开启本群免费招募庆典，所有人可以使用免费招募指令招募一次')


@msg_route("公主之心")
async def princess_heart(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    cidlist = duel._get_cards(gid, uid)
    for cid in cidlist:
        duel._add_favor(gid, uid, cid, 10)
    return (True, f'你使用了公主之心，所有的女友好感度提升了10点')


@msg_route("生财有道")
async def money_mall(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    score = random.randint(1000, 30000)
    CE = ScoreCounter2()
    CE._add_score(gid, uid, score)
    return (True, f'你开始与相邻领地进行贸易，获得了点小钱，赚取了{score}金币。')


@msg_route("小恩小惠")
async def money_mall(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    sw = random.randint(100, 3000)
    CE = ScoreCounter2()
    CE._add_prestige(gid, uid, sw)
    return (True, f'你走在路边，随手丢给路边乞丐一些金币，被别人看到了，声望增加{sw}。')


@msg_route("再来一瓶")
async def money_mall(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    guid = gid, uid
    daily_sign_limiter.reset(guid)
    return (True, f'你打开了一瓶可乐，瓶盖后面写着再来一瓶（签到次数已重制）')


@msg_route("精英对局")
async def money_mall(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    guid = gid, uid
    daily_duel_limiter.reset(guid)
    return (True, f'精英从不畏惧挑战（决斗次数已重置）')


@msg_route("经验之书")
async def battle_exp(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    CE._add_exp_chizi(gid, uid, 100000)
    return (True, f"你通读了一本经验之书，获得了100000经验(加入经验池)")


@sv.on_command("开始巡游")
async def start_xunyou(session: CommandSession):
    bot = session.bot
    ev = session.event
    gid = ev.group_id
    uid = ev.user_id
    item_info = ITEM_NAME_MAP["梦境巡游"]
    counter = ItemCounter()
    num = counter._get_item_num(gid, uid, int(item_info['id']))
    if num < 1:
        await bot.finish(ev, f"背包中道具梦境巡游数量不足", at_sender=True)

    duel = DuelCounter()
    score_counter = ScoreCounter2()
    if duel_judger.get_on_off_status(ev.group_id):
        msg = '现在正在决斗中哦，请决斗后再开始吧。'
        await bot.send(ev, msg, at_sender=True)
        return
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅。'
        duel_judger.turn_off(ev.group_id)
        await bot.send(ev, msg, at_sender=True)
        return
    else:
        # 防止女友数超过上限
        level = duel._get_level(gid, uid)
        girlnum = get_girlnum_buy(gid, uid)
        cidlist = duel._get_cards(gid, uid)
        cidnum = len(cidlist)
        if cidnum >= girlnum:
            msg = '您的女友已经满了哦，快点发送[升级贵族]进行升级吧。'
            await bot.send(ev, msg, at_sender=True)
            return

        newgirllist = get_newgirl_list(gid)
        # 判断女友是否被抢没和该用户是否已经没有女友
        if len(newgirllist) == 0:
            if cidnum != 0:
                await bot.send(ev, '这个群已经没有可以约到的新女友了哦。', at_sender=True)
                return
            else:
                score_counter._reduce_score(gid, uid, GACHA_COST)
                cid = 9999
                c = duel_chara.fromid(1059)
                duel._add_card(gid, uid, cid)
                msg = f'本群已经没有可以约的女友了哦，一位神秘的可可萝在你孤单时来到了你身边。{c.icon.cqcode}。'
                await bot.send(ev, msg, at_sender=True)
                return

        time = session.state["time"]
        cid = session.state.get("cid")
        jieshou = session.state.get("jieshou")
        if jieshou != "是" or time > 10:
            c = duel_chara.fromid(cid)
            nvmes = get_nv_icon(cid)
            duel._add_card(gid, uid, cid)
            counter._add_item(gid, uid, int(item_info['id']), num=-1)
            await bot.send(ev, f"你的梦醒了，当天招募到了女友{c.name}{nvmes}", at_sender=True)
            return
        if jieshou:
            del session.state['jieshou']
        cid = random.choice(newgirllist)
        session.state['cid'] = cid
        c = duel_chara.fromid(cid)
        nvmes = get_nv_icon(cid)
        jieshou = session.get('jieshou', prompt=f'你梦到的女友为：{c.name}{nvmes}，是否继续寻找（是/否）')
        print(jieshou)


@start_xunyou.args_parser
async def _(session: CommandSession):
    text = session.current_arg_text
    img = session.current_arg_images
    if session.is_first_run:
        session.state['time'] = 1
        session.state["jieshou"] = '是'
        return
    else:
        session.state['time'] += 1
    if img:
        session.state[session.current_key] = img
    else:
        session.state[session.current_key] = text
