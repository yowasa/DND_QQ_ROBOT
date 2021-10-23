import asyncio
import copy
from hoshino import priv
from hoshino.typing import CQEvent
from hoshino.typing import CommandSession
from . import duel_chara
from . import sv
from .ScoreCounter import ScoreCounter2
from .duelconfig import *


@sv.on_fullmatch(['物品帮助', '道具帮助'])
async def gift_help(bot, ev: CQEvent):
    msg = '''
╔                                        ╗  
             道具帮助
[我的道具] [道具一览]
[道具效果] {道具名称}
[使用道具] {道具名称}
[批量使用道具] {道具名称}
[决斗储能] [副本储能]
[我的决斗币]
[兑换道具] {道具等级}

道具出现概率：
A:5% B:10% C:20% D:64%
S:1% 
EX道具为成就型道具，无法正常获取。
╚                                        ╝
 '''.strip()
    await bot.send(ev, msg)


@sv.on_fullmatch(['我的道具', '道具列表'])
async def my_item(bot, ev: CQEvent):
    counter = ItemCounter()
    gid = ev.group_id
    uid = ev.user_id
    items = counter._get_item(gid, uid)
    msg = "\n==== 道具列表 ===="
    item_li = []
    for i in items:
        ITEM_INFO[str(i[0])]['num'] = i[1]
        item_li.append(ITEM_INFO[str(i[0])])
    item_li = sorted(item_li, key=lambda x: ['D', 'C', 'B', 'A', 'S', 'EX'].index(x['rank']), reverse=True)
    for i in item_li:
        msg += f"\n{i['rank']}级：{i['name']} *{i['num']}"
    await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch('道具一览')
async def item_all(bot, ev: CQEvent):
    tas_list = []
    data = {
        "type": "node",
        "data": {
            "name": "ご主人様",
            "uin": "1587640710",
            "content": "====== 道具一览 ======"
        }
    }
    tas_list.append(data)
    for i in ['EX', 'S', 'A', 'B', 'C', 'D']:
        for j in ITEM_RANK_MAP[i]:
            msg = f"""{ITEM_INFO[j]['name']}
稀有度：{ITEM_INFO[j]['rank']}
效果：{ITEM_INFO[j]['desc']}
            """.strip()
            data = {
                "type": "node",
                "data": {
                    "name": "ご主人様",
                    "uin": "1587640710",
                    "content": msg
                }
            }
            tas_list.append(data)
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)


@sv.on_prefix(['道具效果', '道具查询', '查询道具'])
async def item_info(bot, ev: CQEvent):
    name = str(ev.message).strip()
    info = ITEM_NAME_MAP.get(name)
    if info:
        await bot.send(ev, f"{name}\n稀有度：{info['rank']}\n效果：{info['desc']}")
    else:
        await bot.send(ev, f"未找到名称为{name}的道具")


@sv.on_prefix(['发放道具', "投放道具"])
async def item_info(bot, ev: CQEvent):
    gid = ev.group_id
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, f"你无权使用投放道具功能", at_sender=True)
    msg = str(ev.message).strip().split()
    try:
        fa_uid = int(msg[0])
    except ValueError:
        fa_uid = int(ev.message[0].data['qq'])
    except:
        await bot.finish(ev, '参数格式错误')
    item_info = ITEM_NAME_MAP.get(msg[1])
    if not item_info:
        await bot.finish(ev, f"未找到名称为{msg[1]}的道具", at_sender=True)
    add_item(gid, fa_uid, item_info)
    await bot.send(ev, f"投放成功", at_sender=True)


@sv.on_prefix(['批量使用道具', '一键使用道具'])
async def consume_item(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg = str(ev.message).strip().split()
    item_info = ITEM_NAME_MAP.get(msg[0])
    if not item_info:
        await bot.finish(ev, f"未找到名称为{msg[0]}的道具", at_sender=True)
    counter = ItemCounter()
    num = counter._get_item_num(gid, uid, int(item_info['id']))
    if num < 1:
        await bot.finish(ev, f"背包中道具{msg[0]}数量不足", at_sender=True)
    batch_result_msg = []
    success_time = 0
    suc_num = 0
    for i in range(num):
        result = await _use_item(msg[0], msg[1:], bot, ev)
        if result[0]:
            suc_num += 1
            success_time += 1
            counter._add_item(gid, uid, int(item_info['id']), num=-1)
        batch_result_msg.append(result[1])
    await bot.send(ev, '\n' + '\n'.join(batch_result_msg), at_sender=True)
    if get_weather(gid) == WeatherModel.LIERI:
        reduce_score = 10000 * suc_num
        sc = ScoreCounter2()
        sc._reduce_score(gid, uid, reduce_score)
        await bot.send(ev, f'由于天气的效果你额外损失了{reduce_score}金币！')


@sv.on_prefix(['使用道具'])
async def consume_item(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg = str(ev.message).strip().split()
    item_info = ITEM_NAME_MAP.get(msg[0])
    if not item_info:
        await bot.finish(ev, f"未找到名称为{msg[0]}的道具", at_sender=True)
    counter = ItemCounter()
    num = counter._get_item_num(gid, uid, int(item_info['id']))
    if num < 1:
        await bot.finish(ev, f"背包中道具{msg[0]}数量不足", at_sender=True)
    result = await _use_item(msg[0], msg[1:], bot, ev)
    suc_num = 0
    if result[0]:
        suc_num += 1
        counter._add_item(gid, uid, int(item_info['id']), num=-1)
    await bot.send(ev, result[1], at_sender=True)
    if get_weather(gid) == WeatherModel.LIERI:
        reduce_score = 10000 * suc_num
        sc = ScoreCounter2()
        sc._reduce_score(gid, uid, reduce_score)
        await bot.send(ev, f'由于天气的效果你额外损失了{reduce_score}金币！')


register = dict()


async def _use_item(name, msg, bot, ev):
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
        return (True, f"{c.name}感受到了命运的指引，前来与你相会。{nvmes}")
    else:
        return (False, f"{c.name}已经心有所属了")


@msg_route("绯想之剑")
async def change_weather(msg, bot, ev: CQEvent):
    gid = ev.group_id
    rd = random.choice([i for i in WeatherModel])
    save_weather(gid, rd)
    return (True, f"你发动了绯想之剑，当前天气变成了{rd.value['name']}")


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
    nvmes = get_nv_icon_with_fashion(gid, uid, cid)
    if owner == 0:
        return (False, f"{c.name}现在还是单身哦,先去约到她吧{nvmes}")
    if uid != owner:
        msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法对其使用道具哦。'
        return (False, msg)
    CE = CECounter()
    max_time = CE._get_zhuansheng(gid, uid, cid)

    if max_time < 5:
        return (False, f"{c.name}等级不足100，请先升级")
    CE._add_zhuansheng(gid, uid, cid)
    max_level = (max_time + 1) * 10 + 50
    return (True, f"角色{c.name}突破了自己的能力界限，等级上限提高10级，目前上限为{max_level}")


@msg_route("后宫之证")
async def add_zhuansheng(msg, bot, ev: CQEvent):
    return (False, f'使用【增加女友上限】指令')


@msg_route("空想之物")
async def add_zhuangbei(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    awardequip_info = add_equip_info(gid, uid, 6, [136, 255, 247, 248, 249, 250, 251, 252, 253, 254])
    return (True,
            f"你使用了空想之物，一道金光闪过，你获得了{awardequip_info['model']}品质的{awardequip_info['type']}:{awardequip_info['name']}")


@msg_route("好事成双")
async def add_item_2(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if not msg:
        return (False, f"请在后面加上空格+道具名称")
    item_info = ITEM_NAME_MAP.get(msg[0])
    if not item_info:
        return (False, f"未找到名称为{msg[0]}的道具")
    counter = ItemCounter()
    num = counter._get_item_num(gid, uid, int(item_info['id']))
    if num < 1:
        return (False, f"背包中不存在道具{msg[0]}")
    counter._add_item(gid, uid, int(item_info['id']))
    return (True, f"你消耗了好事成双，背包中的{msg[0]}增加了一个")


@msg_route("四重存在")
async def add_item_4(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if not msg:
        return (False, f"请在后面加上空格+道具名称")
    item_info = ITEM_NAME_MAP.get(msg[0])
    if not item_info:
        return (False, f"未找到名称为{msg[0]}的道具")
    if item_info['rank'] in ['EX', 'S', 'A']:
        return (False, f"四重存在只能对A级一下（不包括A）的道具使用")
    if item_info['name'] == '投影魔术':
        return (False, f"四重存在无法对[投影魔术]使用")
    counter = ItemCounter()
    num = counter._get_item_num(gid, uid, int(item_info['id']))
    if num < 1:
        return (False, f"背包中不存在道具{msg[0]}")
    counter._add_item(gid, uid, int(item_info['id']), num=3)
    return (True, f"你消耗了四重存在，背包中的一个{msg[0]}分裂成了四个")


@msg_route("帝王法令")
async def open_sou(msg, bot, ev: CQEvent):
    return (False, f"该道具无法使用，只要持有就能增加50点城市面积")


@msg_route("咲夜怀表")
async def open_sou(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    guid = gid, uid
    # 副本 签到 低保 约会 决斗 礼物
    daily_stage_limiter.reset(guid)
    daily_sign_limiter.reset(guid)
    daily_zero_get_limiter.reset(guid)
    daily_date_limiter.reset(guid)
    daily_duel_limiter.reset(guid)
    daily_gift_limiter.reset(guid)
    daily_boss_limiter.reset(guid)
    key_gid = gid + 999
    gkuid = key_gid, uid
    daily_boss_limiter.reset(gkuid)
    # 清除boss限制
    nowyear = datetime.now().year
    nowmonth = datetime.now().month
    nowday = datetime.now().day
    fighttime = str(nowyear) + str(nowmonth) + str(nowday)
    duel = DuelCounter()
    CE = CECounter()
    cidlist = duel._get_cards(gid, uid)
    for cid in cidlist:
        CE._del_cardfightinfo(gid, uid, cid, fighttime, 0)
        CE._del_cardfightinfo(gid, uid, cid, fighttime, 1)
    return (True, f'你拨动了怀表上的一根指针，眼前的一切停滞了下来，指针回转，时间发生了改变。(除领地外所有功能限制已刷新）)')


@msg_route("梦境巡游")
async def xunyou(msg, bot, ev: CQEvent):
    return (False, f'使用"开始巡游"指令开始你的梦境之旅')


@msg_route("初级进阶许可")
async def chuji(msg, bot, ev: CQEvent):
    return (False, f'提升rank自动消耗 无需使用')


@msg_route("中级进阶许可")
async def zhongji(msg, bot, ev: CQEvent):
    return (False, f'提升rank自动消耗 无需使用')


@msg_route("高级进阶许可")
async def gaoji(msg, bot, ev: CQEvent):
    return (False, f'提升rank自动消耗 无需使用')


@msg_route("储能核心")
async def gaoji(msg, bot, ev: CQEvent):
    return (False, f'请使用[决斗储能]或[副本储能]')


@msg_route("超再生力")
async def super_regenerate(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    guid = gid, uid
    if daily_stage_limiter.get_num(guid):
        daily_stage_limiter.increase(guid, num=-1)
        daily_duel_limiter.increase(guid, num=-1)
    num = get_user_counter(gid, uid, UserModel.RECOVER)
    save_user_counter(gid, uid, UserModel.RECOVER, num + 5)
    return (True, f'你使用了超再生力恢复了一次决斗和副本次数，接下来直到持续五次为止，每小时恢复一点决斗次数和关卡次数')


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
    weather = get_weather(gid)
    if weather == WeatherModel.WUYU:
        score = int(1.25 * score)
    CE = ScoreCounter2()
    CE._add_score(gid, uid, score)
    return (True, f'你吃着火锅唱着歌，一低头发现地上有{score}金币。')


@msg_route("乐善好施")
async def fa_money(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    gold = 50000
    num = 5
    each_get_sw = 500
    weather = get_weather(gid)
    if weather == WeatherModel.WUYU:
        gold = int(1.25 * gold)
        each_get_sw = int(1.25 * each_get_sw)
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
        add_p = number * each_get_sw
        r_gold.user = {}
        CE = ScoreCounter2()
        CE._add_prestige(gid, uid, add_p)
        return (True, f"由于你的乐善好施，你的声望提高了{add_p}")
    else:
        return (False, "本群现在已经有红包活动，请稍后再使用")


def wa_all(gid, uid, msg_li, time=1):
    wa_mr(gid, uid, msg_li, time=time)
    wa_ur(gid, uid, msg_li, time=time)
    wa_item(gid, uid, msg_li, time=2 * time)
    wa_gold(gid, uid, msg_li, time=3)
    wa_sw(gid, uid, msg_li, time=3)


def wa_mr(gid, uid, msg_li, time=1):
    for i in range(time):
        rn = random.randint(1, 500)
        if rn == 1:
            awardequip_info = add_equip_info(gid, uid, 6, [136, 255, 247, 248, 249, 250, 251, 252, 253, 254])
            msg_li.append(f"你获得了{awardequip_info['model']}品质的{awardequip_info['type']}:{awardequip_info['name']}")


def wa_ur(gid, uid, msg_li, time=1):
    for i in range(time):
        rn = random.randint(1, 100)
        if rn <= 1:
            awardequip_info = add_equip_info(gid, uid, 5,
                                             [108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122,
                                              123, 124, 125, 126, 127, 128, 195, 196, 197, 198, 199, 200, 201, 202, 204,
                                              205, 206, 207, 208, 209, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237,
                                              238, 239, 240, 241, 242, 243, 244, 245, 246, 260, 265, 266, 267, 278, 279,
                                              280, 282, 283, 284, 285, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297,
                                              298, 299, 300, 301, 302, 303, 304, 305, 306, 312, 313, 314, 315, 316, 317,
                                              318, 319, 320])
            msg_li.append(f"你获得了{awardequip_info['model']}品质的{awardequip_info['type']}:{awardequip_info['name']}")


def wa_item(gid, uid, msg_li, time=2):
    for i in range(time):
        rn = random.randint(1, 100)
        if rn <= 5:
            item = choose_item()
            add_item(gid, uid, item)
            msg_li.append(f"你获得了{item['name']}")


def wa_gold(gid, uid, msg_li, time=3):
    for i in range(time):
        rn = random.randint(1, 100)
        if rn <= 30:
            CE = ScoreCounter2()
            money = random.randint(1, 30000)
            CE._add_score(gid, uid, money)
            msg_li.append(f"你获得了{money}金币")


def wa_sw(gid, uid, msg_li, time=3):
    for i in range(time):
        rn = random.randint(1, 100)
        if rn <= 30:
            CE = ScoreCounter2()
            sw = random.randint(1, 3000)
            CE._add_prestige(gid, uid, sw)
            msg_li.append(f"你获得了{sw}声望")


@msg_route("藏宝图")
async def wabao(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg_li = []
    time = 1
    if check_technolog_counter(gid, uid, TechnologyModel.ARCHAEOLOGIST):
        time = 2
    wa_all(gid, uid, msg_li, time=time)
    if len(msg_li) == 0:
        return (True, f"你进行了一场愉快的探险，但是什么也没有发现")
    return (True, f"你进行了一场惊险的探险:\n" + "\n".join(msg_li))


@msg_route("蓝药水")
async def battle_match(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    guid = gid, uid
    if daily_dun_limiter.check(guid):
        await bot.finish(ev, '请先进入副本再使用药剂', at_sender=True)
    CE = CECounter()
    dun = CE._select_dun_info(gid, uid)
    dun.left_sp += 5
    my = duel_my_buff(gid, uid, dun.cids)
    if dun.left_sp > my.sp:
        dun.left_sp = my.sp
    CE._save_dun_info(dun)
    return (True, f"你使用了蓝药水，副本队伍sp回复至{dun.left_sp}")


@msg_route("战斗记忆")
async def battle_exp(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    get_exp = 50
    weather = get_weather(gid)
    if weather == WeatherModel.WUYU:
        get_exp = int(1.25 * get_exp)
    if len(msg) == 0:
        return (False, "请在道具后+空格+女友名称")
    name = msg[0]
    cid = duel_chara.name2id(name)
    c = duel_chara.fromid(cid)
    if cid == 1000:
        return (False, "请输入正确的角色名")
    test, now_level, msg = add_exp(gid, uid, cid, get_exp)
    CE = CECounter()
    CE._add_exp_chizi(gid, uid, get_exp)
    return (True, f"{c.name}观看了一场精彩的战斗，获得了{get_exp}经验,{msg}")


@msg_route("零时迷子")
async def battle_exp(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    guid = gid, uid
    daily_stage_limiter.reset(guid)
    return (True, f'你使用了零时迷子，今天关闭的副本重新开放了（副本限制已重置）')


@msg_route("红药水")
async def battle_small(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    guid = gid, uid
    if daily_dun_limiter.check(guid):
        await bot.finish(ev, '请先进入副本再使用药剂', at_sender=True)
    CE = CECounter()
    dun = CE._select_dun_info(gid, uid)
    my = duel_my_buff(gid, uid, dun.cids)
    dun.left_hp = my.maxhp
    CE._save_dun_info(dun)
    return (True, f"你使用了红药水，副本队伍hp回复至{my.maxhp}")


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
    counter._save_group_state(gid, GroupModel.OFF_FREE, 1)
    # 刷新当前群组所有贵族的免费招募状态
    user_card_dict = await get_user_card_dict(bot, gid)
    for uid in user_card_dict.keys():
        if uid != ev.self_id:
            guid = gid, uid
            daily_free_limiter.reset(guid)

    return (True, f'在本小时结束前已开启本群免费招募庆典，所有人可以使用免费招募指令招募一次')


@msg_route("公主之心")
async def princess_heart(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    cidlist = duel._get_cards(gid, uid)
    for cid in cidlist:
        duel._add_favor(gid, uid, cid, 30)
    return (True, f'你使用了公主之心，所有的女友好感度提升了30点')


@msg_route("蓬莱之药")
async def favor_cook(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    save_user_counter(gid, uid, UserModel.PENG_LAI_USED, 1)
    return (True, f'你服下此药，从此，你就不再是常人，时间和伤害无法在你的身上留下任何痕迹，你感觉自己失去了什么，却也变得无比充实。')

@msg_route("心意蛋糕")
async def favor_cook(msg, bot, ev: CQEvent):
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
    nvmes = get_nv_icon_with_fashion(gid, uid, cid)
    if owner == 0:
        return (False, f"{c.name}现在还是单身哦,先去约到她吧{nvmes}")
    if uid != owner:
        msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法对其使用道具哦。'
        return (False, msg)
    add_fav = 100
    if check_have_character(cid, "坦率"):
        add_fav = 300
    if check_have_character(cid, "自大"):
        add_fav = 50

    duel._add_favor(gid, uid, cid, add_fav)
    return (True, f'你送了{c.name}一份心意蛋糕,她吃的很开心，好感度提升了{add_fav}点。{nvmes}')


@msg_route("生财有道")
async def money_mall(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    score = random.randint(1000, 30000)
    weather = get_weather(gid)
    if weather == WeatherModel.WUYU:
        score = int(1.25 * score)
    CE = ScoreCounter2()
    CE._add_score(gid, uid, score)
    return (True, f'你开始与相邻城市进行贸易，获得了点小钱，赚取了{score}金币。')


@msg_route("小恩小惠")
async def money_mall(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    sw = random.randint(100, 3000)
    weather = get_weather(gid)
    if weather == WeatherModel.WUYU:
        sw = int(1.25 * sw)
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
    get_exp = 100
    weather = get_weather(gid)
    if weather == WeatherModel.WUYU:
        get_exp = int(1.25 * get_exp)
    if len(msg) == 0:
        return (False, "请在道具后+空格+女友名称")
    name = msg[0]
    cid = duel_chara.name2id(name)
    c = duel_chara.fromid(cid)
    if cid == 1000:
        return (False, "请输入正确的角色名")
    test, now_level, msg = add_exp(gid, uid, cid, get_exp)
    CE = CECounter()
    CE._add_exp_chizi(gid, uid, get_exp)
    return (True, f"{c.name}通读了一本经验之书，获得了{get_exp}经验,{msg}")


@msg_route("许愿神灯")
async def hope(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if not msg:
        return (False, f"请在后面加上道具名称")
    name = msg[0]
    item = get_item_by_name(name)
    if not item:
        return (False, f"未找到名为{name}的道具")
    if item['rank'] == 'EX':
        return (False, f"成就型道具无法正常获取")
    add_item(gid, uid, item)
    return (True, f"你通过向神灯许愿，获得了{item['rank']}级道具{item['name']}！！！")


@msg_route("永恒爱恋")
async def battle_exp(msg, bot, ev: CQEvent):
    return (False, f"该道具无法使用，只要持有就能增加妻子100%战斗力")


@msg_route("光学迷彩")
async def battle_exp(msg, bot, ev: CQEvent):
    return (False, f"该道具无法使用，只要持有就能免受决斗失败的惩罚")


@msg_route("贤者之石")
async def equip_up(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ic = ItemCounter()
    count = ic._get_user_info(gid, uid, UserModel.EQUIP_UP)
    count += 5
    ic._save_user_info(gid, uid, UserModel.EQUIP_UP, count)
    return (True, f"你使用了贤者之石，接下来5次副本的装备将会被转化(如果还留存上一次的buff会叠加次数)")


@msg_route("击鼓传花")
async def battle_exp(msg, bot, ev: CQEvent):
    return (False, f"该道具无法使用，只要持有增加决斗收益")


@msg_route("投影魔术")
async def copy_magic(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if ev.message[1].type == 'at':
        id2 = int(ev.message[1].data['qq'])
    else:
        return (False, '参数格式错误, 请真实的在使用道具后at对方')
    if uid == id2:
        return (False, "无法对自己使用")
    ic = ItemCounter()
    items = ic._get_item(gid, id2)
    if not items:
        return (False, "对方身上没有道具")
    map = {}
    for i in items:
        if ITEM_INFO[str(i[0])]['rank'] == 'EX':
            continue
        if not map.get(ITEM_INFO[str(i[0])]['rank']):
            map[ITEM_INFO[str(i[0])]['rank']] = []
        map[ITEM_INFO[str(i[0])]['rank']].append(i[0])
    if len(map) < 2:
        return (False, "对方身上没有不同稀有度的道具")
    max = 0
    items = []
    for rank in ['S', 'A', 'B', 'C', 'D']:
        if map.get(rank):
            if not max:
                max = rank
            if max == rank:
                continue
            li = map.get(rank)
            items.extend(li)

    i_id = str(random.choice(items))
    add_item(gid, uid, ITEM_INFO[i_id])
    return (True, f"你使用了投影魔术，复制了对方身上的{ITEM_INFO[i_id]['rank']}级道具{ITEM_INFO[i_id]['name']}")


@msg_route("等价交换")
async def change_item(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if not msg:
        return (False, "请选择一个道具")
    item_name = msg[0]
    if item_name == "等价交换":
        return (False, f"不能指定自身")
    item = get_item_by_name(item_name)
    if not item:
        return (False, f"不存在名为{item_name}的道具")
    num = check_have_item(gid, uid, item)
    if not num:
        return (False, f"你身上未持有[{item_name}]")
    if item['rank'] == 'EX':
        return (False, f"成就型道具无法被转换")
    i_c = ItemCounter()
    i_c._add_item(gid, uid, int(item['id']), num=-1)
    li = copy.copy(ITEM_RANK_MAP.get(item['rank']))
    li.remove(item['id'])
    new_id = random.choice(li)
    new_item = ITEM_INFO[new_id]
    add_item(gid, uid, new_item)
    return (True, f"你发动了等价交换，使用[{item_name}]练成了{new_item['rank']}级道具{new_item['name']}")


@msg_route("人海战术")
async def change_item(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    li = ITEM_RANK_MAP['D']
    msg = '当数量达到一定程度，将会发生质变。道具人海战术已发动！获得了：'
    for i in range(10):
        c_ = random.choice(li)
        item = ITEM_INFO[c_]
        add_item(gid, uid, item)
        msg += f'\n{item["name"]}'
    return (True, msg)


@msg_route("公平交易")
async def change_item(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if not msg:
        return (False, "请选择一个道具")
    item_name = msg[0]
    if item_name == "公平交易":
        return (False, f"不能指定自身")
    item = get_item_by_name(item_name)
    if not item:
        return (False, f"不存在名为{item_name}的道具")
    num = check_have_item(gid, uid, item)
    if not num:
        return (False, f"你身上未持有[{item_name}]")
    if item['rank'] == 'EX':
        return (False, f"成就道具无法被转化")
    i_c = ItemCounter()
    i_c._add_item(gid, uid, int(item['id']), num=-1)

    ranks = ['S', 'A', 'B', 'C', 'D']
    index = ranks.index(item['rank'])
    if index != 4:
        index += 1
    rank = ranks[index]
    li = ITEM_RANK_MAP[rank]
    msg = f'你与商人用{item["rank"]}级的{item["name"]}进行了一场公平的交易，获得了以下道具：'
    for i in range(random.randint(1, 2)):
        i_id = random.choice(li)
        new_item = ITEM_INFO[i_id]
        add_item(gid, uid, new_item)
        msg += f'\n{new_item["name"]}'
    return (True, msg)


@msg_route("加速世界")
async def rush_world(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    guid = gid, uid
    daily_manor_limiter.reset(guid)
    return (True, f'您开启了加速世界，城市的时间进行了一次跳跃。（城市结算重置了）')


@msg_route("收获之日")
async def happy_day(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    get_fb = 20
    weather = get_weather(gid)
    if weather == WeatherModel.WUYU:
        get_fb = int(1.25 * get_fb)
    CE = CECounter()
    CE._add_dunscore(gid, uid, get_fb)
    return (True, f'你在副本中发现了隐藏的宝箱，带着副本币满载而归。(副本币增加{get_fb})')


@msg_route("武装镇压")
async def suppress(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    zhian = get_user_counter(gid, uid, UserModel.ZHI_AN)
    zhian += 20
    if zhian > 100:
        zhian = 100
    save_user_counter(gid, uid, UserModel.ZHI_AN, zhian)
    return (True, f'以暴制暴不是最好的做法，但效果确有保障，你派出的大量武装部队去维护了城市内的治安(城市的治安恢复了20)')


@msg_route("太平盛世")
async def peace_and_order(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    fan = get_user_counter(gid, uid, UserModel.PROSPERITY_INDEX)
    fan += 20
    if fan > 1000:
        fan = 1000
    save_user_counter(gid, uid, UserModel.PROSPERITY_INDEX, fan)
    return (True, f'随着你的合理良政，城市逐渐繁荣起来，一个新的盛世即将诞生。已使用道具太平盛世，城市的繁荣度增加了20点')


@msg_route("基建狂魔")
async def capital_construction(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg = ''
    # 计算建筑进度
    cd = get_user_counter(gid, uid, UserModel.BUILD_CD)
    if cd != 0:
        cd -= 1
        if cd == 0:
            buffer_build_id = get_user_counter(gid, uid, UserModel.BUILD_BUFFER)
            build = BuildModel.get_by_id(buffer_build_id)
            build_num = check_build_counter(gid, uid, build)
            build_num += 1
            i_c = ItemCounter()
            i_c._save_user_state(gid, uid, build.value['id'], build_num)
            msg += f"\n施工队报告{build.value['name']}竣工了，已经可以投入使用"
            save_user_counter(gid, uid, UserModel.BUILD_BUFFER, 0)
        save_user_counter(gid, uid, UserModel.BUILD_CD, cd)

    # 计算科研进度
    t_cd = get_user_counter(gid, uid, UserModel.TECHNOLOGY_CD)
    if t_cd != 0:
        t_cd -= 1
        if t_cd == 0:
            buffer_technology_id = get_user_counter(gid, uid, UserModel.TECHNOLOGY_BUFFER)
            technology = TechnologyModel.get_by_id(buffer_technology_id)
            i_c = ItemCounter()
            i_c._save_user_state(gid, uid, technology.value['id'], 1)
            msg += f"\n科研队报告{technology.value['name']}已经研发成功了！"
            save_user_counter(gid, uid, UserModel.TECHNOLOGY_BUFFER, 0)
        save_user_counter(gid, uid, UserModel.TECHNOLOGY_CD, t_cd)
    return (True, f'没有什么是一发基建不能解决的，如果有，那就建到解决！使用道具基建狂魔，建造和科研的速度加快了。' + msg)


@sv.on_fullmatch("我的决斗币", "决斗币查询", "查询决斗币", "查决斗币")
async def search_duel_coin(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    num = get_user_counter(gid, uid, UserModel.DUEL_COIN)
    await bot.send(ev, f"当前拥有决斗币数量为{num}", at_sender=True)


@sv.on_prefix("兑换道具")
async def roll_item(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    rank = str(ev.message).strip()
    price = {
        'A': 50,
        'B': 30,
        'C': 15,
        'D': 5,
    }
    if not rank:
        await bot.finish(ev, f"请输入 兑换物品 + 物品等级 来兑换指定等级的物品", at_sender=True)
    if rank in ['S', 'EX']:
        await bot.finish(ev, f"A级以上物品无法兑换哦", at_sender=True)
    if not price.get(rank):
        await bot.finish(ev, f"未找到级别是'{rank}'的物品", at_sender=True)
    cost = price.get(rank)
    num = get_user_counter(gid, uid, UserModel.DUEL_COIN)
    if cost > num:
        await bot.finish(ev, f"兑换{rank}级物品需要{cost}个决斗币，你的决斗币数量不足", at_sender=True)
    li = ITEM_RANK_MAP[rank]
    i_id = random.choice(li)
    new_item = ITEM_INFO[i_id]
    num -= cost
    save_user_counter(gid, uid, UserModel.DUEL_COIN, num)
    add_item(gid, uid, new_item)
    await bot.send(ev, f"你使用了{cost}枚决斗币兑换了{new_item['rank']}级物品{new_item['name']}!", at_sender=True)


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
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过角色，请发送 创建角色 开始你的人生旅途。'
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


@sv.on_fullmatch(["决斗储能"])
async def duel_contain(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if duel_judger.get_on_off_status(ev.group_id):
        msg = '现在正在决斗中哦，请决斗后再进行储能吧。'
        await bot.send(ev, msg, at_sender=True)
        return
    item = get_item_by_name("储能核心")
    if not check_have_item(gid, uid, item):
        await bot.send(ev, "你没有储能核心，无法进行决斗储能", at_sender=True)
        return
    guid = gid, uid
    daily_duel_limiter.check(guid)
    if daily_duel_limiter.get_num(guid) != 0:
        await bot.finish(ev, f"你已经进行过了决斗，无法进行决斗储能", at_sender=True)
    use_item(gid, uid, item)
    daily_duel_limiter.increase(guid, num=daily_duel_limiter.max)
    item = get_item_by_name("精英对局")
    add_item(gid, uid, item)
    await bot.send(ev, f'今日暂且休息，来日再战（已清空决斗次数，获得了{item["rank"]}级道具{item["name"]}）', at_sender=True)


@sv.on_fullmatch(["副本储能"])
async def duel_contain(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    item = get_item_by_name("储能核心")
    if not check_have_item(gid, uid, item):
        await bot.send(ev, "你没有储能核心，无法进行副本储能", at_sender=True)
        return
    guid = gid, uid
    daily_stage_limiter.check(guid)
    if daily_stage_limiter.get_num(guid) != 0:
        await bot.finish(ev, f"你已经进行过了副本，无法进行副本储能", at_sender=True)
    use_item(gid, uid, item)
    daily_stage_limiter.increase(guid, num=daily_stage_limiter.max)
    item = get_item_by_name("零时迷子")
    add_item(gid, uid, item)
    await bot.send(ev, f'今日暂且休息，来日再战（已清空副本次数，获得了{item["rank"]}级道具{item["name"]}）', at_sender=True)

