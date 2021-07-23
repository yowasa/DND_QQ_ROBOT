import asyncio
import copy
import re

import pytz

from hoshino import priv
from hoshino.typing import CQEvent
from . import duel_chara
from . import sv
from .ScoreCounter import *
from .duelconfig import *


@sv.on_prefix(['贵族决斗帮助', '贵族帮助', '贵族指令'])
async def duel_help(bot, ev: CQEvent):
    msg = '''
╔                                       ╗    
        贵族决斗相关指令
[创建贵族]
[查询贵族]
[贵族签到]
[升级贵族]
[贵族决斗] @群友
[设置决斗偏好] 设置决斗风格
[贵族舞会] 招募新角色
[声望招募] 等级到神才可以操作
[免费招募] 庆典开启才能使用 每日限一次
[领金币] 金币过低的时候才能使用
[查金币]
[查声望]
[查女友]{角色名}
[我的女友] {角色名} 查看女友详细信息
[分手]{角色名}
[一键分手]{用空格分隔的角色名}
[兑换{数量}声望]
[用{数量}声望兑换金币]
[为@群友转账{数量}金币]
[用{数量}金币与@群友交易女友]{角色名}
[绑定女友]{角色名}
[查看绑定]{角色名}
[解除绑定]
[增加女友上限]
[贵族等级表]
[本群贵族]
[金币排行]
[声望排行]
[女友排行]
[当前庆典]
==== 其他帮助 ====
[dlc帮助]
[管理帮助]
[好感帮助]
[时装帮助]
[培养帮助]
[会战帮助]
[装备帮助]
[副本帮助]
[道具帮助]
[领地帮助]

    *一个女友只属于一位群友
    
╚                                        ╝
'''
    await bot.send(ev, msg)


@sv.on_prefix(['管理帮助'])
async def manage_help(bot, ev: CQEvent):
    msg = '''
╔                                       ╗    
        管理帮助相关指令
[重置决斗]群管理限定 决斗卡住时使用
[重置礼物交换]群管理限定 交换卡住时使用
[重置金币]{qq号}重置某一用户的金币 群主限定 
[重置角色]{qq号}重置某一用户的角色 群主限定
[重置交易]群管理限定 交易卡住时使用
============== 维护组 ==============
[发送红包]{金额} {个数} 
[初始化本群庆典]
[开启本群(金币|签到|梭哈倍率|免费招募|声望招募)庆典]
[关闭本群(金币|签到|梭哈倍率|免费招募|声望招募)庆典]
[为@群友充值{数量}金币]
[设定群{群号}为{数量}号死]
[为{qq号}充值{数量}声望]
[扣除{qq号}的{数量}声望]
[投放道具] @群友 {道具名}
[刷新结算] @群友
    
╚                                        ╝
'''
    await bot.send(ev, msg)


@sv.on_prefix(['加载dlc', '加载DLC', '开启dlc', '开启DLC'])
async def add_dlc(bot, ev: CQEvent):
    gid = ev.group_id
    if not priv.check_priv(ev, priv.OWNER):
        await bot.finish(ev, '只有群主才能加载dlc哦。', at_sender=True)
    args = ev.message.extract_plain_text().split()
    if len(args) >= 2:
        await bot.finish(ev, '指令格式错误。', at_sender=True)
    if len(args) == 0:
        await bot.finish(ev, '请输入加载dlc+dlc名。', at_sender=True)
    dlcname = args[0]
    if dlcname not in cfg.dlcdict.keys():
        await bot.finish(ev, 'DLC名填写错误。', at_sender=True)
    check_dlc()
    if gid in dlc_switch[dlcname]:
        await bot.finish(ev, '本群已开启此dlc哦。', at_sender=True)
    dlc_switch[dlcname].append(gid)
    save_dlc_switch()
    await bot.finish(ev, f'加载dlc {cfg.dlcintro[dlcname]}  成功!', at_sender=True)


@sv.on_prefix(['卸载dlc', '卸载DLC', '关闭dlc', '关闭DLC'])
async def delete_dlc(bot, ev: CQEvent):
    gid = ev.group_id
    if not priv.check_priv(ev, priv.OWNER):
        await bot.finish(ev, '只有群主才能卸载dlc哦。', at_sender=True)
    args = ev.message.extract_plain_text().split()
    if len(args) >= 2:
        await bot.finish(ev, '指令格式错误', at_sender=True)
    if len(args) == 0:
        await bot.finish(ev, '请输入卸载dlc+dlc名。', at_sender=True)
    dlcname = args[0]
    if dlcname not in cfg.dlcdict.keys():
        await bot.finish(ev, 'DLC名填写错误', at_sender=True)

    if gid not in dlc_switch[dlcname]:
        await bot.finish(ev, '本群没有开启此dlc哦。', at_sender=True)
    dlc_switch[dlcname].remove(gid)
    save_dlc_switch()
    await bot.finish(ev, f'卸载dlc {dlcname}  成功!', at_sender=True)


@sv.on_fullmatch(['dlc列表', 'DLC列表', 'dlc介绍', 'DLC介绍'])
async def intro_dlc(bot, ev: CQEvent):
    msg = '可用DLC列表：\n\n'
    i = 1
    for dlc in cfg.dlcdict.keys():
        msg += f'{i}.{dlc}:\n'
        intro = cfg.dlcintro[dlc]
        msg += f'介绍:{intro}\n'
        num = len(cfg.dlcdict[dlc])
        msg += f'共有{num}名角色\n\n'
        i += 1
    msg += '发送 加载\卸载dlc+dlc名\n可加载\卸载dlc\n卸载的dlc不会被抽到，但是角色仍留在玩家仓库，可以被抢走。'

    await bot.finish(ev, msg)


@sv.on_fullmatch(['dlc帮助', 'DLC帮助', 'dlc指令', 'DLC指令'])
async def help_dlc(bot, ev: CQEvent):
    msg = '''
╔                                 ╗
         DLC帮助
      
[加载dlc]{dlc名称} 群主可用
[卸载dlc]{dlc名称} 群主可用
[dlc列表]
  
  卸载的dlc不会被抽到
  但是角色仍留在仓库
  可以被他人抢走
  
╚                                 ╝    
'''
    await bot.finish(ev, msg)


@sv.on_fullmatch(['贵族表', '贵族等级表'])
async def duel_biao(bot, ev: CQEvent):
    msg = f'''"1": "平民",  最多可持有{LEVEL_GIRL_NEED[str(1)]}名女友，每日签到额外获得100金币，初始等级。
"2": "骑士",  升级需要{LEVEL_SW_NEED[str(2)]}声望和{LEVEL_COST_DICT[str(2)]}金币，最多可持有{LEVEL_GIRL_NEED[str(2)]}名女友，保持等级最少持有{LEVEL_GIRL_NEED[str(1)]}名女友。
"3": "准男爵", 升级需要{LEVEL_SW_NEED[str(3)]}声望和{LEVEL_COST_DICT[str(3)]}金币，最多可持有{LEVEL_GIRL_NEED[str(3)]}名女友，保持等级最少持有{LEVEL_GIRL_NEED[str(2)]}名女友。
"4": "男爵",升级需要{LEVEL_SW_NEED[str(4)]}声望和{LEVEL_COST_DICT[str(4)]}金币，最多可持有{LEVEL_GIRL_NEED[str(4)]}名女友，保持等级最少持有{LEVEL_GIRL_NEED[str(3)]}名女友。
"5": "子爵",升级需要{LEVEL_SW_NEED[str(5)]}声望和{LEVEL_COST_DICT[str(5)]}金币，最多可持有{LEVEL_GIRL_NEED[str(5)]}名女友，保持等级最少持有{LEVEL_GIRL_NEED[str(4)]}名女友。
"6": "伯爵",升级需要{LEVEL_SW_NEED[str(6)]}声望和{LEVEL_COST_DICT[str(6)]}金币，最多可持有{LEVEL_GIRL_NEED[str(6)]}名女友，保持等级最少持有{LEVEL_GIRL_NEED[str(5)]}名女友。
"7": "侯爵",升级需要{LEVEL_SW_NEED[str(7)]}声望和{LEVEL_COST_DICT[str(7)]}金币，最多可持有{LEVEL_GIRL_NEED[str(7)]}名女友，保持等级最少持有{LEVEL_GIRL_NEED[str(6)]}名女友。
"8": "公爵",升级需要{LEVEL_SW_NEED[str(8)]}声望和{LEVEL_COST_DICT[str(8)]}金币，最多可持有{LEVEL_GIRL_NEED[str(8)]}名女友，不再会掉级，可拥有一名妻子。
"9": "国王",升级需要{LEVEL_SW_NEED[str(9)]}声望和{LEVEL_COST_DICT[str(9)]}金币，最多可持有{LEVEL_GIRL_NEED[str(9)]}名女友，不再会掉级，可拥有一名妻子。
"10": "皇帝"升级需要{DJ_NEED_SW}声望和{DJ_NEED_GOLD}金币，最多可持有{LEVEL_GIRL_NEED[str(10)]}名女友，不再会掉级，可拥有一名妻子。
"11": "神"升级需要{FS_NEED_SW}声望和{FS_NEED_GOLD}金币，最多可持有{LEVEL_GIRL_NEED[str(20)]}名女友，当输光女友时贬为平民，可拥有一名妻子。
'''
    await bot.send(ev, msg)


class NvYouJiaoYi:
    def __init__(self):
        self.jiaoyion = {}
        self.jiaoyiflag = {}
        self.jiaoyiid = {}
        self.jiaoyiname = {}
        self.jiaoyi_on = {}

    def get_jiaoyi_on_off_status(self, gid):
        return self.jiaoyion[gid] if self.jiaoyion.get(gid) is not None else False

    # 记录群交易开关
    def turn_jiaoyion(self, gid):
        self.jiaoyion[gid] = True

    def turn_jiaoyioff(self, gid):
        self.jiaoyion[gid] = False

    # 记录群交易是否接受开关
    def turn_on_jiaoyi(self, gid):
        self.jiaoyi_on[gid] = True

    def turn_off_jiaoyi(self, gid):
        self.jiaoyi_on[gid] = False

    # 记录交易者id
    def init_jiaoyiid(self, gid):
        self.jiaoyiid[gid] = []

    def set_jiaoyiid(self, gid, id1, id2, cid):
        self.jiaoyiid[gid] = [id1, id2, cid]

    def get_jiaoyiid(self, gid):
        return self.jiaoyiid[gid] if self.jiaoyi_on.get(gid) is not None else [0, 0, 0]

    # 记录是否接受交易
    def init_jiaoyiflag(self, gid):
        self.jiaoyiflag[gid] = False

    def on_jiaoyiflag(self, gid):
        self.jiaoyiflag[gid] = True

    def off_jiaoyiflag(self, gid):
        self.jiaoyiflag[gid] = False

    def get_jiaoyiflag(self, gid):
        return self.jiaoyiflag[gid] if self.jiaoyiflag[gid] is not None else False


duel_jiaoyier = NvYouJiaoYi()


@sv.on_rex(f'^用(\d+)金币与(.*)交易女友(.*)$')
async def nobleduel(bot, ev: CQEvent):
    if duel_jiaoyier.get_jiaoyi_on_off_status(ev.group_id):
        await bot.send(ev, "此轮交易还没结束，请勿重复使用指令。")
        return
    if duel_judger.get_on_off_status(ev.group_id):
        msg = '现在正在决斗中哦，请决斗后再进行交易吧。'
        await bot.send(ev, msg, at_sender=True)
        return
    gid = ev.group_id
    match = ev['match']
    try:
        id2 = int(match.group(2))
    except ValueError:
        id2 = int(ev.message[1].data['qq'])
    except:
        await bot.finish(ev, '参数格式错误')
    name = str(match.group(3)).strip()
    num = int(match.group(1))
    duel_jiaoyier.turn_jiaoyion(gid)
    id1 = ev.user_id
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    level2 = duel._get_level(gid, id2)
    noblename = get_noblename(level2)
    score = score_counter._get_score(gid, id1)
    if score < num:
        msg = f'您的金币不足{num}，无法交易哦。'
        duel_jiaoyier.turn_jiaoyioff(ev.group_id)
        await bot.send(ev, msg, at_sender=True)
        return
    if id2 == id1:
        await bot.send(ev, "不能和自己交易！", at_sender=True)
        duel_jiaoyier.turn_jiaoyioff(ev.group_id)
        return
    if girl_outlimit(gid, id1):
        await bot.send(ev, "您的女友超过了爵位上限，无法进行交易哦！", at_sender=True)
        duel_jiaoyier.turn_jiaoyioff(ev.group_id)
        return

    if duel._get_level(gid, id1) == 0:
        msg = f'[CQ:at,qq={id1}]交易发起者还未在创建过贵族\n请发送 创建贵族 开始您的贵族之旅。'
        duel_jiaoyier.turn_jiaoyioff(ev.group_id)
        await bot.send(ev, msg)
        return
    if duel._get_cards(gid, id1) == {}:
        msg = f'[CQ:at,qq={id1}]您没有女友，不能参与交易哦。'
        duel_jiaoyier.turn_jiaoyioff(ev.group_id)
        await bot.send(ev, msg)
        return

    if duel._get_level(gid, id2) == 0:
        msg = f'[CQ:at,qq={id2}]被交易者还未在本群创建过贵族\n请发送 创建贵族 开始您的贵族之旅。'
        duel_jiaoyier.turn_jiaoyioff(ev.group_id)
        await bot.send(ev, msg)
        return
    if duel._get_cards(gid, id2) == {}:
        msg = f'[CQ:at,qq={id2}]您没有女友，不能参与交易哦。'
        duel_jiaoyier.turn_jiaoyioff(ev.group_id)
        await bot.send(ev, msg)
        return

    if not name:
        await bot.send(ev, '请输入查女友+角色名。', at_sender=True)
        duel_jiaoyier.turn_jiaoyioff(ev.group_id)
        return
    cid = duel_chara.name2id(name)
    if cid == 1000:
        await bot.send(ev, '请输入正确的角色名。', at_sender=True)
        duel_jiaoyier.turn_jiaoyioff(ev.group_id)
        return
    owner = duel._get_card_owner(gid, cid)
    c = duel_chara.fromid(cid)
    # 判断是否是妻子。
    if duel._get_queen_owner(gid, cid) != 0:
        owner = duel._get_queen_owner(gid, cid)
        duel_jiaoyier.turn_jiaoyioff(ev.group_id)
        await bot.finish(ev, f'\n{c.name}现在是\n[CQ:at,qq={owner}]的妻子，无法交易哦。', at_sender=True)

    if owner == 0:
        await bot.send(ev, f'{c.name}现在还是单身哦，快去约到她吧。', at_sender=True)
        duel_jiaoyier.turn_jiaoyioff(ev.group_id)
        return
    if id2 != owner:
        msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您需要与此人进行交易哦。'
        duel_jiaoyier.turn_jiaoyioff(ev.group_id)
        await bot.send(ev, msg)
        return
    duel_jiaoyier.init_jiaoyiflag(gid)
    duel_jiaoyier.set_jiaoyiid(gid, id1, id2, cid)
    duel_jiaoyier.turn_on_jiaoyi(gid)
    cost = Jiao_Need
    if duel._get_SUO_CELE(gid) == 1:
        cost = Suo_Ex_NEED
    msg = f'[CQ:at,qq={id2}]尊敬的{noblename}您好\n[CQ:at,qq={id1}]试图以{num}金币的价格购买您的女友{c.name}，请在{WAIT_TIME_jy}秒内[接受交易/拒绝交易]，女友交易需要收{cost * 100}%手续费哦。'
    await bot.send(ev, msg)

    await asyncio.sleep(WAIT_TIME_jy)
    duel_jiaoyier.turn_off_jiaoyi(gid)
    if duel_jiaoyier.get_jiaoyiflag(gid) is False:
        msg = '交易被拒绝。'
        duel_jiaoyier.turn_jiaoyioff(gid)
        await bot.send(ev, msg, at_sender=True)
        return

    duel = DuelCounter()
    get_num = num * (1 - cost)
    score_counter._add_score(gid, id2, get_num)
    score = score_counter._get_score(gid, id2)

    score_counter._reduce_score(gid, id1, num)
    scoreyou = score_counter._get_score(gid, id1)
    duel._delete_card(gid, id2, cid)
    duel._add_card(gid, id1, cid)
    duel_jiaoyier.turn_jiaoyioff(gid)
    nvmes = get_nv_icon(cid)
    CE = CECounter()
    guaji = CE._get_guaji(gid, id2)
    if cid == guaji:
        CE._add_guaji(gid, id2, 0)
    msg = f'[CQ:at,qq={id1}]以{num}金币的价格购买了[CQ:at,qq={id2}]的女友{c.name}，交易成功\n[CQ:at,qq={id1}]您失去了{num}金币，剩余{scoreyou}金币\n[CQ:at,qq={id2}]扣除{cost * 100}%手续费，您能得到了{get_num}金币，剩余{score}金币。{nvmes}'
    await bot.send(ev, msg)


@sv.on_fullmatch('接受交易')
async def duelaccept(bot, ev: CQEvent):
    gid = ev.group_id
    if duel_jiaoyier.get_jiaoyi_on_off_status(gid):
        if ev.user_id == duel_jiaoyier.get_jiaoyiid(gid)[1]:
            gid = ev.group_id
            msg = '交易接受成功，请耐心等待交易开始。'
            await bot.send(ev, msg, at_sender=True)
            duel_jiaoyier.turn_off_jiaoyi(gid)
            duel_jiaoyier.on_jiaoyiflag(gid)
        else:
            print('不是被交易者')
    else:
        print('现在不在交易期间')


@sv.on_fullmatch('重置交易')
async def init_duel(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能使用重置交易哦。', at_sender=True)
    duel_jiaoyier.turn_jiaoyioff(ev.group_id)
    msg = '已重置本群交易状态！'
    await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch('拒绝交易')
async def duelrefuse(bot, ev: CQEvent):
    gid = ev.group_id
    if duel_jiaoyier.get_jiaoyi_on_off_status(gid):
        if ev.user_id == duel_jiaoyier.get_jiaoyiid(gid)[1]:
            gid = ev.group_id
            msg = '您已拒绝女友交易。'
            await bot.send(ev, msg, at_sender=True)
            duel_jiaoyier.turn_off_jiaoyi(gid)
            duel_jiaoyier.off_jiaoyiflag(gid)


@sv.on_fullmatch('贵族签到')
async def noblelogin(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    guid = gid, uid
    if not daily_sign_limiter.check(guid):
        await bot.send(ev, '今天已经签到过了哦，明天再来吧。', at_sender=True)
        return
    duel = DuelCounter()

    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅。'
        await bot.send(ev, msg, at_sender=True)
        return
    # 根据概率随机获得收益。
    score_counter = ScoreCounter2()
    prestige = score_counter._get_prestige(gid, uid)
    if prestige == None:
        score_counter._set_prestige(gid, uid, 0)
    daily_sign_limiter.increase(guid)
    loginnum_ = ['1', '2', '3', '4']
    r_ = [0.3, 0.4, 0.2, 0.1]
    sum_ = 0
    ran = random.random()
    for num, r in zip(loginnum_, r_):
        sum_ += r
        if ran < sum_: break
    Bonus = {'1': [200, Login100],
             '2': [500, Login200],
             '3': [700, Login300],
             '4': [1000, Login600]
             }
    score1 = Bonus[num][0]
    score1 = 3 * score1
    text1 = random.choice(Bonus[num][1])

    # 根据爵位的每日固定收入
    level = duel._get_level(gid, uid)
    score2 = 300 * level
    SW2 = 100 * level
    scoresum = score1 + score2
    noblename = get_noblename(level)
    if duel._get_QC_CELE(gid) == 1:
        scoresum = scoresum * QD_Gold_Cele_Num
        SW2 = SW2 * QD_SW_Cele_Num
        msg = f'\n{text1}\n签到成功！\n[庆典举办中]\n您领取了：\n\n{score1}金币(随机)和\n{score2}金币以及{SW2}声望({noblename}爵位)'
    else:
        msg = f'\n{text1}\n签到成功！\n您领取了：\n\n{score1}金币(随机)和\n{score2}金币以及{SW2}声望({noblename}爵位)'
    score_counter._add_prestige(gid, uid, SW2)
    score_counter._add_score(gid, uid, scoresum)
    cidlist = duel._get_cards(gid, uid)
    cidnum = len(cidlist)

    if cidnum > 0:
        cid = random.choice(cidlist)
        c = duel_chara.fromid(cid)
        nvmes = get_nv_icon(cid)
        up_info = duel._get_fashionup(gid, uid, cid, 0)
        if up_info:
            fashion_info = get_fashion_info(up_info)
            nvmes = fashion_info['icon']
        msg += f'\n\n今天向您请安的是\n{c.name}{nvmes}'
        # 随机获得一件礼物
    select_gift = random.choice(list(GIFT_DICT.keys()))
    gfid = GIFT_DICT[select_gift]
    duel._add_gift(gid, uid, gfid)
    msg += f'\n随机获得了礼物[{select_gift}]'
    item = choose_item()
    add_item(gid, uid, item)
    msg += f'\n随机获得了{item["rank"]}级道具[{item["name"]}]'
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    hour = now.hour
    minu = now.minute
    if hour == 0 and minu == 0:
        r_num = random.randint(1, 20)
        if r_num == 1:
            i_2 = get_item_by_name("零时迷子")
            add_item(gid, uid, i_2)
            msg += f'\n你隐约听到了午夜的钟声 获得了{i_2["rank"]}级道具[{i_2["name"]}]'
    await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch('免费招募')
async def noblelogin(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    if duel._get_FREE_CELE(gid) != 1:
        await bot.send(ev, '当前未开放免费招募庆典！', at_sender=True)
        return
    else:
        guid = gid, uid
        if not daily_free_limiter.check(guid):
            await bot.send(ev, '今天已经免费招募过了喔，明天再来吧。(免费招募次数每天0点刷新)', at_sender=True)
            return
        if duel._get_level(gid, uid) == 0:
            msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅。'
            await bot.send(ev, msg, at_sender=True)
            return
        score_counter = ScoreCounter2()
        if duel_judger.get_on_off_status(ev.group_id):
            msg = '现在正在决斗中哦，请决斗后再参加舞会吧。'
            await bot.send(ev, msg, at_sender=True)
            return
        else:
            # 防止女友数超过上限
            level = duel._get_level(gid, uid)
            girlnum = get_girlnum_buy(gid, uid)
            cidlist = duel._get_cards(gid, uid)
            cidnum = len(cidlist)
            if cidnum >= girlnum:
                msg = '您的女友已经满了哦，您转为获得500声望。'
                score_counter._add_prestige(gid, uid, 500)
                daily_free_limiter.increase(guid)
                await bot.send(ev, msg, at_sender=True)
                return
            prestige = score_counter._get_prestige(gid, uid)
            if prestige == None:
                score_counter._set_prestige(gid, uid, 0)
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

            # 招募女友成功
            daily_free_limiter.increase(guid)
            cid = random.choice(newgirllist)
            c = duel_chara.fromid(cid)
            nvmes = get_nv_icon(cid)
            duel._add_card(gid, uid, cid)
            wintext = random.choice(Addgirlsuccess)
            msg = f'\n{wintext}\n招募女友成功！\n新招募的女友为：{c.name}{nvmes}'
            await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch(['本群贵族状态', '查询本群贵族', '本群贵族'])
async def group_noble_status(bot, ev: CQEvent):
    gid = ev.group_id
    duel = DuelCounter()
    newgirllist = get_newgirl_list(gid)
    newgirlnum = len(newgirllist)
    l1_num = duel._get_level_num(gid, 1)
    l2_num = duel._get_level_num(gid, 2)
    l3_num = duel._get_level_num(gid, 3)
    l4_num = duel._get_level_num(gid, 4)
    l5_num = duel._get_level_num(gid, 5)
    l6_num = duel._get_level_num(gid, 6)
    l7_num = duel._get_level_num(gid, 7)
    l8_num = duel._get_level_num(gid, 8)
    l9_num = duel._get_level_num(gid, 9)
    lA_num = duel._get_level_num(gid, 10)
    lB_num = duel._get_level_num(gid, 20)
    dlctext = ''
    for dlc in cfg.dlcdict.keys():
        if gid in dlc_switch[dlc]:
            dlctext += f'  {cfg.dlcintro[dlc]}\n'
    msg = f'''
╔                          ╗
         本群贵族
    神：{lB_num}名  
  皇帝：{lA_num}名  
  国王：{l9_num}名  
  公爵：{l8_num}名  
  侯爵：{l7_num}名
  伯爵：{l6_num}名
  子爵：{l5_num}名
  男爵：{l4_num}名
  准男爵：{l3_num}名
  骑士：{l2_num}名
  平民：{l1_num}名
  已开启DLC:
{dlctext}
  *还有{newgirlnum}名单身女友 
╚                          ╝
'''
    await bot.send(ev, msg)


@sv.on_fullmatch('创建贵族')
async def add_noble(bot, ev: CQEvent):
    try:
        gid = ev.group_id
        uid = ev.user_id
        duel = DuelCounter()
        if duel._get_level(gid, uid) != 0:
            msg = '您已经在本群创建过贵族了，请发送 查询贵族 查询。'
            await bot.send(ev, msg, at_sender=True)
            return

        # 判定本群女友是否已空，如果空则分配一个复制人可可萝。
        newgirllist = get_newgirl_list(gid)
        if len(newgirllist) == 0:
            cid = 9999
            c = duel_chara.fromid(1059)
            girlmsg = f'本群已经没有可以约的女友了哦，一位神秘的可可萝在你孤单时来到了你身边。{c.icon.cqcode}。'
            duel._add_card(gid, uid, cid)
        else:
            item = get_item_by_name("梦境巡游")
            add_item(gid, uid, item)
            girlmsg = f'为您发放了道具[梦境巡游],使用[开始巡游]指令去寻找你的初始女友吧'
        duel._set_level(gid, uid, 1)
        msg = f'\n创建贵族成功！\n您的初始爵位是平民\n可以拥有1名女友。\n初始金币为1000，初始声望为0\n{girlmsg}'
        score_counter = ScoreCounter2()
        score_counter._set_prestige(gid, uid, 0)
        score_counter._add_score(gid, uid, 1000)
        await bot.send(ev, msg, at_sender=True)
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))


@sv.on_fullmatch(['增加容量', '增加女友上限'])
async def add_warehouse(bot, ev: CQEvent):
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    gid = ev.group_id
    uid = ev.user_id
    current_score = score_counter._get_score(gid, uid)
    prestige = score_counter._get_prestige(gid, uid)
    if duel._get_level(gid, uid) <= 9:
        msg = '只有成为皇帝后，才能扩充女友上限喔'
        await bot.send(ev, msg, at_sender=True)
        return
    if prestige < SHANGXIAN_SW:
        msg = f'扩充女友上限，需要{SHANGXIAN_SW}声望，您的声望不足喔'
        await bot.send(ev, msg, at_sender=True)
        return
    if current_score < SHANGXIAN_NUM:
        msg = f'增加女友上限需要消耗{SHANGXIAN_NUM}金币，您的金币不足哦'
        await bot.send(ev, msg, at_sender=True)
        return
    else:
        housenum = duel._get_warehouse(gid, uid)
        if housenum >= WAREHOUSE_NUM:
            msg = f'您已增加{WAREHOUSE_NUM}次上限，无法继续增加了哦'
            await bot.send(ev, msg, at_sender=True)
            return
        duel._add_warehouse(gid, uid, 1)
        score_counter._reduce_score(gid, uid, SHANGXIAN_NUM)
        score_counter._reduce_prestige(gid, uid, SHANGXIAN_SW)
        myhouse = get_girlnum_buy(gid, uid)
        msg = f'您消耗了{SHANGXIAN_NUM}金币，{SHANGXIAN_SW}声望，增加了1个女友上限，目前的女友上限为{myhouse}名'
        await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch(['查询贵族', '贵族查询', '我的贵族'])
async def inquire_noble(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    CE = CECounter()
    score_counter = ScoreCounter2()
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅。'
        await bot.send(ev, msg, at_sender=True)
        return
    level = duel._get_level(gid, uid)
    noblename = get_noblename(level)
    girlnum = get_girlnum_buy(gid, uid)
    score = score_counter._get_score(gid, uid)
    charalist = []

    cidlist = duel._get_cards(gid, uid)
    cidnum = len(cidlist)
    prestige = score_counter._get_prestige(gid, uid)
    if prestige == None:
        prestige = 0
        partmsg = f'您的声望为{prestige}点'
    else:
        partmsg = f'您的声望为{prestige}点'
    myscore = CE._get_dunscore(gid, uid)
    duel_coin = get_user_counter(gid, uid, UserModel.DUEL_COIN)
    nv_names = ''
    if cidnum == 0:
        msg = f'''
╔                          ╗
  您的爵位为{noblename}
  您的金币为{score}
  {partmsg}
  您的副本币为{myscore}
  您的决斗币为{duel_coin}
  您共可拥有{girlnum}名女友
  您目前没有女友。
  发送[贵族舞会]
  可以招募女友哦。
  
╚                          ╝
'''
        await bot.send(ev, msg, at_sender=True)

    else:
        shuzi_flag = 0
        for cid in cidlist:
            # 替换复制人可可萝
            if cid == 9999:
                cid = 1059
            star = CE._get_cardstar(gid, uid, cid)
            charalist.append(duel_chara.Chara(cid, star, 0))
            c = duel_chara.fromid(cid)
            shuzi_flag = shuzi_flag + 1
            nv_names = nv_names + c.name + ' '
            if shuzi_flag == 6:
                nv_names = nv_names + '\n'
                shuzi_flag = 0

        # 制图部分，六个一行
        num = copy.deepcopy(cidnum)
        position = 6
        if num <= 6:
            res = duel_chara.gen_team_pic(charalist, star_slot_verbose=False)
        else:
            num -= 6
            res = duel_chara.gen_team_pic(charalist[0:position], star_slot_verbose=False)
            while (num > 0):
                if num >= 6:
                    res1 = duel_chara.gen_team_pic(charalist[position:position + 6], star_slot_verbose=False)
                else:
                    res1 = duel_chara.gen_team_pic(charalist[position:], star_slot_verbose=False)
                res = concat_pic([res, res1])
                position += 6
                num -= 6

        bio = BytesIO()
        res.save(bio, format='PNG')
        base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
        mes = f"[CQ:image,file={base64_str}]"

        # 判断是否开启声望

        msg = f'''
╔                          ╗
  您的爵位为{noblename}
  您的金币为{score}
  {partmsg}
  您的副本币为{myscore}
  您的决斗币为{duel_coin}
  您共可拥有{girlnum}名女友
  您已拥有{cidnum}名女友
  她们是：
  {nv_names}
    {mes}   
╚                          ╝
'''
        # 判断有无妻子
        queen = duel._search_queen(gid, uid)
        if queen != 0:
            c = duel_chara.fromid(queen)

            msg = f'''
╔                          ╗
  您的爵位为{noblename}
  您的金币为{score}
  {partmsg}
  您的副本币为{myscore}
  您的决斗币为{duel_coin}
  您的妻子是{c.name}
  您共可拥有{girlnum}名女友
  您已拥有{cidnum}名女友
  她们是：
  {nv_names}
    {mes}  
    
╚                          ╝
'''

        await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch(['招募女友', '贵族舞会'])
async def add_girl(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    if duel_judger.get_on_off_status(ev.group_id):
        msg = '现在正在决斗中哦，请决斗后再参加舞会吧。'
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
        score = score_counter._get_score(gid, uid)
        if score < GACHA_COST:
            msg = f'您的金币不足{GACHA_COST}哦。'
            await bot.send(ev, msg, at_sender=True)
            return
        prestige = score_counter._get_prestige(gid, uid)
        if prestige == None:
            score_counter._set_prestige(gid, uid, 0)
        if prestige < 0 and level > 7:
            msg = f'您现在身败名裂（声望为负），无法招募女友！。'
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

        score_counter._reduce_score(gid, uid, GACHA_COST)
        # 招募女友失败
        rrn = random.random()
        if rrn < 0.4:
            ex_msg = ''
            count = get_user_counter(gid, uid, UserModel.YUE_FAILE)
            count += 1
            if count >= 10:
                item = get_item_by_name('命运牵引')
                add_item(gid, uid, item)
                count = 0
                ex_msg += f'\n今天的舞会很漫长，直到现在还没有约到一个人。但是命运不会缺席，你和她命中注定会在一起！获取到了{item["rank"]}级道具{item["name"]}'
            save_user_counter(gid, uid, UserModel.YUE_FAILE, count)
            losetext = random.choice(Addgirlfail)
            msg = f'\n{losetext}\n您花费了{GACHA_COST}金币，但是没有约到新的女友。获得了{GACHA_COST_Fail}金币补偿。' + ex_msg
            score_counter._add_score(gid, uid, GACHA_COST_Fail)
            await bot.send(ev, msg, at_sender=True)
            return

        # 招募女友成功
        save_user_counter(gid, uid, UserModel.YUE_FAILE, 0)
        cid = random.choice(newgirllist)
        c = duel_chara.fromid(cid)
        nvmes = get_nv_icon(cid)
        duel._add_card(gid, uid, cid)
        wintext = random.choice(Addgirlsuccess)

        msg = f'\n{wintext}\n招募女友成功！\n您花费了{GACHA_COST}金币\n新招募的女友为：{c.name}{nvmes}'
        await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch('声望招募')
async def add_girl(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    if duel._get_SW_CELE(gid) != 1 and duel._get_level(gid, uid) != 20:
        msg = '目前不在限时开放声望招募期间，只有神能参与！'
        duel_judger.turn_off(ev.group_id)
        await bot.send(ev, msg, at_sender=True)
        return
    if duel_judger.get_on_off_status(ev.group_id):
        msg = '现在正在决斗中哦，请决斗后再参加舞会吧。'
        await bot.send(ev, msg, at_sender=True)
        return
    else:
        # 防止女友数超过上限
        girlnum = get_girlnum_buy(gid, uid) + 10
        cidlist = duel._get_cards(gid, uid)
        cidnum = len(cidlist)
        if cidnum >= girlnum:
            msg = '您的女友已经满了哦，快点发送[升级贵族]进行升级吧。'
            await bot.send(ev, msg, at_sender=True)
            return
        needSW2 = SW_COST
        prestige = score_counter._get_prestige(gid, uid)
        if prestige == None:
            score_counter._set_prestige(gid, uid, 0)
        if prestige < needSW2:
            msg = f'您的声望不足{needSW2}哦。'
            await bot.send(ev, msg, at_sender=True)
            return

        newgirllist = get_newgirl_list(gid)
        # 判断女友是否被抢没和该用户是否已经没有女友
        if len(newgirllist) == 0:
            if cidnum != 0:
                await bot.send(ev, '这个群已经没有可以约到的新女友了哦。', at_sender=True)
                return
            else:
                score_counter._reduce_prestige(gid, uid, needSW2)
                cid = 9999
                c = duel_chara.fromid(1059)
                duel._add_card(gid, uid, cid)
                msg = f'本群已经没有可以约的女友了哦，一位神秘的可可萝在你孤单时来到了你身边。{c.icon.cqcode}。'
                await bot.send(ev, msg, at_sender=True)
                return

        score_counter._reduce_prestige(gid, uid, needSW2)
        # 招募女友成功
        cid = random.choice(newgirllist)
        c = duel_chara.fromid(cid)
        nvmes = get_nv_icon(cid)
        duel._add_card(gid, uid, cid)
        wintext = random.choice(Addgirlsuccess)

        msg = f'\n{wintext}\n招募女友成功！\n您花费了{needSW2}声望\n新招募的女友为：{c.name}{nvmes}'
        await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch(['升级爵位', '升级贵族', '贵族升级'])
async def add_girl(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    score = score_counter._get_score(gid, uid)
    level = duel._get_level(gid, uid)
    noblename = get_noblename(level)
    girlnum = get_girlnum(level)
    cidlist = duel._get_cards(gid, uid)
    cidnum = len(cidlist)

    if duel_judger.get_on_off_status(ev.group_id):
        msg = '现在正在决斗中哦，请决斗后再升级爵位吧。'
        await bot.send(ev, msg, at_sender=True)
        return
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅。'
        await bot.send(ev, msg, at_sender=True)
        return
    if level == 9:
        msg = f'您已经是国王了， 需要通过声望加冕称帝哦。'
        await bot.send(ev, msg, at_sender=True)
        return

    if level == 10:
        msg = f'您是本群的皇帝， 再往前一步就能成神了，请飞升成神。'
        await bot.send(ev, msg, at_sender=True)
        return

    if level == 20:
        msg = f'您已经到达了世界的巅峰， 无法再继续提升了。'
        await bot.send(ev, msg, at_sender=True)
        return

    if cidnum < girlnum:
        msg = f'您的女友没满哦。\n需要达到{girlnum}名女友\n您现在有{cidnum}名。'
        await bot.send(ev, msg, at_sender=True)
        return
    prestige = score_counter._get_prestige(gid, uid)
    needscore = get_noblescore(level + 1)
    futurename = get_noblename(level + 1)
    needSW = get_noblesw(level + 1)
    if score < needscore:
        msg = f'您的金币不足哦。\n升级到{futurename}需要{needscore}金币'
        await bot.send(ev, msg, at_sender=True)
        return

    if prestige < needSW:
        await bot.finish(ev, f'您的声望不足哦。升级到{futurename}需要{needSW}声望。', at_sender=True)

    score_counter._reduce_prestige(gid, uid, needSW)
    score_counter._reduce_score(gid, uid, needscore)
    duel._add_level(gid, uid)
    newlevel = duel._get_level(gid, uid)
    newnoblename = get_noblename(newlevel)
    newgirlnum = get_girlnum_buy(gid, uid)
    msg = f'花费了{needscore}金币和{needSW}声望\n您成功由{noblename}升到了{newnoblename}\n可以拥有{newgirlnum}名女友了哦。'
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['设置决斗偏好', '决斗偏好设置', '决斗方式设置', '设置决斗方式'])
async def duel_set(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg = str(ev.message)
    duel_setting = {
        "俄罗斯轮盘": [0, "弹夹为6 轮流对自己扣动扳机"],
        "野蛮厮杀": [1, "弹夹为6 朝对方射击"],
        "西部牛仔": [2, "弹夹为2 朝对方射击"]
    }
    if not msg:
        await bot.finish(ev, "请选择俄罗斯轮盘(轮流对自己开枪)，野蛮厮杀(轮流向对方开枪)，西部牛仔(一枪定胜负)三种方式之一")

    if not duel_setting.get(msg):
        await bot.finish(ev, "请选择俄罗斯轮盘(轮流对自己开枪)，野蛮厮杀(轮流向对方开枪)，西部牛仔(一枪定胜负)三种方式之一")

    save_user_counter(gid, uid, UserModel.DUEL_SETTING, duel_setting.get(msg)[0])
    await bot.finish(ev, f"已经成功设置决斗偏好为{msg}({duel_setting.get(msg)[1]})")


@sv.on_prefix('贵族决斗')
async def nobleduel(bot, ev: CQEvent):
    if ev.message[0].type == 'at':
        id2 = int(ev.message[0].data['qq'])
    else:
        await bot.finish(ev, '参数格式错误, 请重试')
    if duel_judger.get_on_off_status(ev.group_id):
        await bot.send(ev, "此轮决斗还没结束，请勿重复使用指令。")
        return

    gid = ev.group_id
    duel_judger.turn_on(gid)
    id1 = ev.user_id
    duel = DuelCounter()
    is_overtime = 0
    if id2 == id1:
        await bot.send(ev, "不能和自己决斗！", at_sender=True)
        duel_judger.turn_off(ev.group_id)
        return

    if duel._get_level(gid, id1) == 0:
        msg = f'[CQ:at,qq={id1}]决斗发起者还未在创建过贵族\n请发送 创建贵族 开始您的贵族之旅。'
        duel_judger.turn_off(ev.group_id)
        await bot.send(ev, msg)
        return
    if duel._get_cards(gid, id1) == {}:
        msg = f'[CQ:at,qq={id1}]您没有女友，不能参与决斗哦。'
        duel_judger.turn_off(ev.group_id)
        await bot.send(ev, msg)
        return

    if duel._get_level(gid, id2) == 0:
        msg = f'[CQ:at,qq={id2}]被决斗者还未在本群创建过贵族\n请发送 创建贵族 开始您的贵族之旅。'
        duel_judger.turn_off(ev.group_id)
        await bot.send(ev, msg)
        return
    if duel._get_cards(gid, id2) == {}:
        msg = f'[CQ:at,qq={id2}]您没有女友，不能参与决斗哦。'
        duel_judger.turn_off(ev.group_id)
        await bot.send(ev, msg)
        return
    # 判定每日上限
    guid = gid, id1
    if not daily_duel_limiter.check(guid):
        await bot.send(ev, '今天的决斗次数已经超过上限了哦，明天再来吧。', at_sender=True)
        duel_judger.turn_off(ev.group_id)
        return

    # 判定双方的女友是否已经超过上限
    # 这里设定大于才会提醒，就是可以超上限1名，可以自己改成大于等于。
    if girl_outlimit(gid, id1):
        msg = f'[CQ:at,qq={id1}]您的女友超过了爵位上限，本次决斗获胜只能获得金币哦。'
        await bot.send(ev, msg)
    if girl_outlimit(gid, id2):
        msg = f'[CQ:at,qq={id2}]您的女友超过了爵位上限，本次决斗获胜只能获得金币哦。'
        await bot.send(ev, msg)
    duel_judger.init_isaccept(gid)
    duel_judger.set_duelid(gid, id1, id2)
    duel_judger.turn_on_accept(gid)
    way = get_user_counter(gid, id1, UserModel.DUEL_SETTING)
    duel_setting = {
        "0": ["俄罗斯轮盘", "弹夹为6 轮流对自己扣动扳机"],
        "1": ["野蛮厮杀", "弹夹为6 朝对方射击"],
        "2": ["西部牛仔", "弹夹为2 朝对方射击"]
    }
    msg = f'[CQ:at,qq={id2}]对方向您发起了{duel_setting[str(way)][0]}决斗({duel_setting[str(way)][1]})，请在{WAIT_TIME}秒内[接受/拒绝]。'

    await bot.send(ev, msg)
    await asyncio.sleep(WAIT_TIME)
    duel_judger.turn_off_accept(gid)
    if duel_judger.get_isaccept(gid) is False:
        msg = '决斗被拒绝。'
        duel_judger.turn_off(gid)
        await bot.send(ev, msg, at_sender=True)
        return
    # 接受决斗后再增加每日判定次数
    daily_duel_limiter.increase(guid)
    duel = DuelCounter()
    level1 = duel._get_level(gid, id1)
    noblename1 = get_noblename(level1)
    level2 = duel._get_level(gid, id2)
    noblename2 = get_noblename(level2)
    if duel._get_GOLD_CELE(gid) == 1:
        msg = f'''对方接受了决斗！    
1号：[CQ:at,qq={id1}]
爵位为：{noblename1}
2号：[CQ:at,qq={id2}]
爵位为：{noblename2}
其他人请在{DUEL_SUPPORT_TIME}秒选择支持的对象
[庆典举办中]支持成功时，金币的获取量将会变为{Gold_Cele_Num * WIN_NUM}倍！
[支持1/2号xxx金币]'''
    else:
        msg = f'''对方接受了决斗！    
1号：[CQ:at,qq={id1}]
爵位为：{noblename1}
2号：[CQ:at,qq={id2}]
爵位为：{noblename2}
其他人请在{DUEL_SUPPORT_TIME}秒选择支持的对象
支持成功时，金币的获取量将会变为{WIN_NUM}倍！
[支持1/2号xxx金币]'''

    await bot.send(ev, msg)
    duel_judger.turn_on_support(gid)
    dan = 6
    if way == 2:
        dan = 2
    deadnum = random.randint(1, dan)
    print(f"{duel_setting[str(way)][0]}死的枪数是", deadnum)
    duel_judger.set_deadnum(gid, deadnum)
    await asyncio.sleep(DUEL_SUPPORT_TIME)
    duel_judger.turn_off_support(gid)
    duel_judger.init_turn(gid)
    duel_judger.turn_on_fire(gid)
    duel_judger.turn_off_hasfired(gid)
    msg = f'支持环节结束，下面请决斗双方轮流[开枪]。\n[CQ:at,qq={id1}]先开枪，30秒未开枪自动认输'

    await bot.send(ev, msg)
    n = 1
    while n <= dan:
        wait_n = 0
        while (wait_n < 30):
            if duel_judger.get_on_off_hasfired_status(gid):
                break

            wait_n += 1
            await asyncio.sleep(1)
        if wait_n >= 30:
            # 超时未开枪的胜负判定
            loser = duel_judger.get_duelid(gid)[duel_judger.get_turn(gid) - 1]
            winner = duel_judger.get_duelid(gid)[2 - duel_judger.get_turn(gid)]
            msg = f'[CQ:at,qq={loser}]\n你明智的选择了认输。'
            await bot.send(ev, msg)

            # 记录本局为超时局。
            is_overtime = 1

            break
        else:
            if n == duel_judger.get_deadnum(gid):
                if way == 0:
                    # 被子弹打到的胜负判定
                    loser = duel_judger.get_duelid(gid)[duel_judger.get_turn(gid) - 1]
                    winner = duel_judger.get_duelid(gid)[2 - duel_judger.get_turn(gid)]
                    msg = f'[CQ:at,qq={loser}]\n砰！你死了。'
                    await bot.send(ev, msg)
                    break
                else:
                    # 被子弹打到的胜负判定
                    winner = duel_judger.get_duelid(gid)[duel_judger.get_turn(gid) - 1]
                    loser = duel_judger.get_duelid(gid)[2 - duel_judger.get_turn(gid)]
                    msg = f'[CQ:at,qq={loser}]\n砰！你死了。'
                    await bot.send(ev, msg)
                    break
            else:
                id = duel_judger.get_duelid(gid)[duel_judger.get_turn(gid) - 1]
                id2 = duel_judger.get_duelid(gid)[2 - duel_judger.get_turn(gid)]
                if way == 0:
                    msg = f'[CQ:at,qq={id}]\n砰！松了一口气，你并没有死。\n[CQ:at,qq={id2}]\n轮到你开枪了哦。'
                else:
                    msg = f'[CQ:at,qq={id}]\n砰！你没有打到对方。\n[CQ:at,qq={id2}]\n轮到你开枪了哦。'
                await bot.send(ev, msg)
                if (n == 1 and way == 2) or (way == 1 and n == 5):
                    winner = id2
                    loser = id
                    msg = f'[CQ:at,qq={id2}]\n你看到对方没有打到你，你迅速朝对面开了一枪\n[CQ:at,qq={id}]\n砰！你死了。'
                    await bot.send(ev, msg)
                    break
                n += 1
                duel_judger.change_turn(gid)
                duel_judger.turn_off_hasfired(gid)
                duel_judger.turn_on_fire(gid)
    score_counter = ScoreCounter2()
    cidlist = duel._get_cards(gid, loser)
    queen = duel._search_queen(gid, loser)
    CE = CECounter()
    bangdinwin = CE._get_guaji(gid, winner)
    bangdinlose = CE._get_guaji(gid, loser)
    # 判断决斗胜利者是否有绑定角色,有则增加经验值
    bd_msg = ''
    if bangdinwin:
        bd_info = duel_chara.fromid(bangdinwin)
        card_level = add_exp(gid, winner, bangdinwin, WIN_EXP)
        nvmes = get_nv_icon(bangdinwin)
        up_info = duel._get_fashionup(gid, winner, bangdinwin, 0)
        if up_info:
            fashion_info = get_fashion_info(up_info)
            nvmes = fashion_info['icon']
        bd_msg = f"\n您绑定的女友{bd_info.name}获得了{WIN_EXP}点经验，{card_level[2]}\n{nvmes}"
    item = get_item_by_name("光学迷彩")
    have_item = check_have_item(gid, loser, item)
    if have_item:
        rn = random.randint(1, 50)
        if rn == 1:
            use_item(gid, loser, item)
            msg = f'[CQ:at,qq={loser}] 你在失败逃窜时不小心划破了光学迷彩，你的光学迷彩不能继续使用了。'
            await bot.send(ev, msg)
    item_jigu = get_item_by_name("击鼓传花")
    win_have_jigu = check_have_item(gid, winner, item_jigu)
    lose_have_jigu = check_have_item(gid, loser, item_jigu)
    if lose_have_jigu:
        use_item(gid, loser, item_jigu)
        add_item(gid, winner, item_jigu)
        msg = f'[CQ:at,qq={loser}] 由于你决斗失败，失去了道具[击鼓传花]'
        msg += f'\n[CQ:at,qq={winner}] 由于你战胜了对手，获得了对手的道具[击鼓传花]。'
        await bot.send(ev, msg)

    selected_girl = random.choice(cidlist)
    # 判定被输掉的是否是复制人可可萝，是则换成金币。
    if have_item:
        msg = f'[CQ:at,qq={loser}]\n你使用光学迷彩逃脱了，本次决斗不会对你造成损失'
        await bot.send(ev, msg)
    elif selected_girl == 9999:
        score_counter._add_score(gid, winner, 300)
        c = duel_chara.fromid(1059)
        nvmes = get_nv_icon(1059)
        duel._delete_card(gid, loser, selected_girl)
        msg = f'[CQ:at,qq={winner}]\n您赢得了神秘的可可萝，但是她微笑着消失了。\n本次决斗获得了300金币。'
        msg += f'\n[CQ:at,qq={loser}]\n您输掉了贵族决斗，被抢走了女友\n{c.name}，\n只要招募，她就还会来到你的身边哦。{nvmes}'
        await bot.send(ev, msg)

    # 判断被输掉的是否为妻子。
    elif selected_girl == queen:
        score_counter._add_score(gid, winner, NTR_QUEEN_REWARD)
        msg = f'[CQ:at,qq={winner}]您赢得的角色为对方的妻子，\n您改为获得{NTR_QUEEN_REWARD}金币。'
        score_counter._reduce_prestige(gid, loser, LOSS_QUEEN_PUNISH_SW)
        msg += f'\n[CQ:at,qq={loser}]您差点输掉了妻子，额外失去了{LOSS_QUEEN_PUNISH_SW}声望。'
        await bot.send(ev, msg)

    # 判断被输掉的是否为绑定经验获取角色。
    elif selected_girl == bangdinlose:
        score_counter._add_score(gid, winner, NTR_BIND_REWARD)
        msg = f'[CQ:at,qq={winner}]您赢得的角色为对方的绑定女友，\n您改为获得{NTR_BIND_REWARD}金币。'
        score_counter._reduce_prestige(gid, loser, LOSS_BIND_PUNISH_SW)
        msg += f'\n[CQ:at,qq={loser}]您差点输掉了绑定女友，额外失去了{LOSS_BIND_PUNISH_SW}声望。'
        await bot.send(ev, msg)


    elif girl_outlimit(gid, winner):
        score_counter._add_score(gid, winner, FULL_GIRL_COMPENSATE)
        msg = f'[CQ:at,qq={winner}]您的女友超过了爵位上限，\n本次决斗额外获得了{FULL_GIRL_COMPENSATE}金币。'
        c = duel_chara.fromid(selected_girl)
        # 判断好感是否足够，足够则扣掉好感
        favor = duel._get_favor(gid, loser, selected_girl)
        if favor >= favor_reduce:
            duel._reduce_favor(gid, loser, selected_girl, favor_reduce)
            msg += f'\n[CQ:at,qq={loser}]您输掉了贵族决斗，您与{c.name}的好感下降了{favor_reduce}点。\n{c.icon.cqcode}'
            await bot.send(ev, msg)
        else:
            duel._delete_card(gid, loser, selected_girl)
            msg += f'\n[CQ:at,qq={loser}]您输掉了贵族决斗且对方超过了爵位上限，您的女友恢复了单身。\n{c.name}{c.icon.cqcode}'
            await bot.send(ev, msg)

    else:
        # 判断好感是否足够，足够则扣掉好感
        favor = duel._get_favor(gid, loser, selected_girl)
        c = duel_chara.fromid(selected_girl)
        if favor >= favor_reduce:
            duel._reduce_favor(gid, loser, selected_girl, favor_reduce)
            msg = f'[CQ:at,qq={loser}]您输掉了贵族决斗，您与{c.name}的好感下降了{favor_reduce}点。\n{c.icon.cqcode}'
            score_counter._add_score(gid, winner, FAVOR_GIRL_COMPENSATE)
            msg += f'\n[CQ:at,qq={winner}]您赢得了决斗，对方女友仍有一定好感。\n本次决斗额外获得了{FAVOR_GIRL_COMPENSATE}金币。'
            await bot.send(ev, msg)
        else:
            duel._delete_card(gid, loser, selected_girl)
            duel._add_card(gid, winner, selected_girl)
            msg = f'[CQ:at,qq={loser}]您输掉了贵族决斗，您被抢走了女友\n{c.name}{c.icon.cqcode}'
            await bot.send(ev, msg)
            # 判断赢家的角色列表里是否有复制人可可萝。
            wincidlist = duel._get_cards(gid, winner)
            if 9999 in wincidlist:
                duel._delete_card(gid, winner, 9999)
                score_counter._add_score(gid, winner, 300)
                msg = f'[CQ:at,qq={winner}]\n“主人有了女友已经不再孤单了，我暂时离开了哦。”\n您赢得了{c.name},可可萝微笑着消失了。\n您获得了300金币。'
                await bot.send(ev, msg)

    # 判断胜者败者是否需要增减声望
    level_loser = duel._get_level(gid, loser)
    level_winner = duel._get_level(gid, winner)
    wingold = 1500 + (level_loser * 400)
    if win_have_jigu:
        wingold = int(wingold * 1.2)
        bd_msg = '（击鼓传花）' + bd_msg
    if is_overtime == 1:
        if not (n == 6 and way == 0):
            wingold = 100

    score_counter._add_score(gid, winner, wingold)
    msg = f'[CQ:at,qq={winner}]本次决斗胜利获得了{wingold}金币。{bd_msg}'
    await bot.send(ev, msg)
    winprestige = score_counter._get_prestige(gid, winner)
    if winprestige == None:
        winprestige == 0
    if winprestige != None:
        level_cha = level_loser - level_winner
        level_zcha = max(level_cha, 0)
        winSW = WinSWBasics + (level_zcha * 20)
        if is_overtime == 1:
            if not (n == 6 and way == 0):
                if level_loser < 6:
                    winSW = 0
                else:
                    winSW = 150
        if win_have_jigu:
            winSW = int(winSW * 1.2)
        score_counter._add_prestige(gid, winner, winSW)
        msg = f'[CQ:at,qq={winner}]决斗胜利使您的声望上升了{winSW}点。'
        if win_have_jigu:
            msg += "（击鼓传花）"
        await bot.send(ev, msg)
    if not have_item:
        loseprestige = score_counter._get_prestige(gid, loser)
        if loseprestige == -1:
            loseprestige == 0
        if loseprestige != -1:
            level_cha = level_loser - level_winner
            level_zcha = max(level_cha, 0)
            LOSESW = LoseSWBasics + (level_zcha * 10)
            score_counter._reduce_prestige(gid, loser, LOSESW)
            msg = f'[CQ:at,qq={loser}]决斗失败使您的声望下降了{LOSESW}点。'
            await bot.send(ev, msg)

        # 判定败者是否掉爵位，皇帝不会因为决斗掉爵位。
        level_loser = duel._get_level(gid, loser)
        if level_loser > 1 and level_loser < 8:
            girlnum_loser = get_girlnum(level_loser - 1)
            cidlist_loser = duel._get_cards(gid, loser)
            cidnum_loser = len(cidlist_loser)
            if cidnum_loser < girlnum_loser:
                duel._reduce_level(gid, loser)
                new_noblename = get_noblename(level_loser - 1)
                msg = f'[CQ:at,qq={loser}]\n您的女友数为{cidnum_loser}名\n小于爵位需要的女友数{girlnum_loser}名\n您的爵位下降到了{new_noblename}'
                await bot.send(ev, msg)

    # 结算下注金币，判定是否为超时局。
    if is_overtime == 1:
        if not (n == 6 and way == 0):
            if level_loser < 6:
                msg = '认输警告！本局为超时局/认输局，不进行金币结算，支持的金币全部返还。胜者获得的声望为0，金币大幅减少。'
            else:
                msg = '认输警告！本局为超时局/认输局，不进行金币结算，支持的金币全部返还。胜者获得的声望减半，金币大幅减少，不计等级差。'
            await bot.send(ev, msg)
            duel_judger.set_support(ev.group_id)
            duel_judger.turn_off(ev.group_id)
            return
    else:
        w_c = get_user_counter(gid, winner, UserModel.WIN)
        w_c += 1
        save_user_counter(gid, winner, UserModel.WIN, w_c)
        save_user_counter(gid, winner, UserModel.LOSE, 0)
        coin_num = 1
        ex_msg = ''
        if w_c >= 3:
            coin_num += 1
        if w_c >= 5:
            coin_num += 1
        if w_c >= 8:
            coin_num += 1
        if coin_num > 1:
            ex_msg += f"由于你连续取得胜利，额外获取了{coin_num - 1}个决斗币!!!"
        num = get_user_counter(gid, winner, UserModel.DUEL_COIN)
        num += coin_num
        save_user_counter(gid, winner, UserModel.DUEL_COIN, num)
        msg = f'[CQ:at,qq={winner}]你获取了决斗胜利，获得了1个决斗币!!!' + ex_msg
        await bot.send(ev, msg)
        if w_c >= 10:
            item = get_item_by_name('精英对局')
            add_item(gid, winner, item)
            msg = f'[CQ:at,qq={winner}]你越战越勇，无人可挡！获得了{item["rank"]}级道具{item["name"]}!!!'
            await bot.send(ev, msg)
        l_c = get_user_counter(gid, loser, UserModel.LOSE)
        l_c += 1
        if l_c >= 10:
            item = get_item_by_name('光学迷彩')
            add_item(gid, loser, item)
            msg = f'[CQ:at,qq={loser}]你认真反思了近期的对局，认为逃避可耻但有用，获得了{item["rank"]}级道具{item["name"]}!!!'
            l_c = 0
            await bot.send(ev, msg)
        save_user_counter(gid, loser, UserModel.WIN, 0)
        save_user_counter(gid, loser, UserModel.LOSE, l_c)

    support = duel_judger.get_support(gid)
    winuid = []
    supportmsg = '金币结算:\n'
    winnum = duel_judger.get_duelnum(gid, winner)

    if support != 0:
        for uid in support:
            support_id = support[uid][0]
            support_score = support[uid][1]
            if support_id == winnum:
                winuid.append(uid)
                # 这里是赢家获得的金币结算，可以自己修改倍率。
                if duel._get_GOLD_CELE(gid) == 1:
                    winscore = support_score * WIN_NUM * Gold_Cele_Num
                else:
                    winscore = support_score * WIN_NUM
                score_counter._add_score(gid, uid, winscore)
                supportmsg += f'[CQ:at,qq={uid}]+{winscore}金币\n'
            else:
                score_counter._reduce_score(gid, uid, support_score)
                supportmsg += f'[CQ:at,qq={uid}]-{support_score}金币\n'
                if support_score >= 1000000:
                    rn = random.randint(1, 100)
                    if rn == 1:
                        item = get_item_by_name("狂赌之渊")
                        add_item(gid, uid, item)
                        supportmsg += f'[CQ:at,qq={uid}] 这一次赌博的结果让你出离愤怒，获得了{item["rank"]}级道具{item["name"]}\n'

    await bot.send(ev, supportmsg)
    duel_judger.set_support(ev.group_id)
    duel_judger.turn_off(ev.group_id)
    return


@sv.on_fullmatch('接受')
async def duelaccept(bot, ev: CQEvent):
    gid = ev.group_id
    if duel_judger.get_on_off_accept_status(gid):
        if ev.user_id == duel_judger.get_duelid(gid)[1]:
            gid = ev.group_id
            msg = '贵族决斗接受成功，请耐心等待决斗开始。'
            await bot.send(ev, msg, at_sender=True)
            duel_judger.turn_off_accept(gid)
            duel_judger.on_isaccept(gid)
        else:
            print('不是被决斗者')
    else:
        print('现在不在决斗期间')


@sv.on_fullmatch('拒绝')
async def duelrefuse(bot, ev: CQEvent):
    gid = ev.group_id
    if duel_judger.get_on_off_accept_status(gid):
        if ev.user_id == duel_judger.get_duelid(gid)[1]:
            gid = ev.group_id
            msg = '您已拒绝贵族决斗。'
            await bot.send(ev, msg, at_sender=True)
            duel_judger.turn_off_accept(gid)
            duel_judger.off_isaccept(gid)


@sv.on_fullmatch(['开枪'])
async def duelfire(bot, ev: CQEvent):
    gid = ev.group_id
    if duel_judger.get_on_off_fire_status(gid):
        if ev.user_id == duel_judger.get_duelid(gid)[duel_judger.get_turn(gid) - 1]:
            duel_judger.turn_on_hasfired(gid)
            duel_judger.turn_off_fire(gid)


@sv.on_rex(r'^支持(1|2)号(\d+)(金币|币)$')
async def on_input_duel_score(bot, ev: CQEvent):
    try:
        if duel_judger.get_on_off_support_status(ev.group_id):
            gid = ev.group_id
            uid = ev.user_id

            match = ev['match']
            select_id = int(match.group(1))
            input_score = int(match.group(2))
            print(select_id, input_score)
            score_counter = ScoreCounter2()
            # 若下注该群下注字典不存在则创建
            if duel_judger.get_support(gid) == 0:
                duel_judger.set_support(gid)
            support = duel_judger.get_support(gid)
            # 检查是否重复下注
            if uid in support:
                msg = '您已经支持过了。'
                await bot.send(ev, msg, at_sender=True)
                return
            # 检查是否是决斗人员
            duellist = duel_judger.get_duelid(gid)
            if uid in duellist:
                msg = '决斗参与者不能支持。'
                await bot.send(ev, msg, at_sender=True)
                return

                # 检查金币是否足够下注
            if score_counter._judge_score(gid, uid, input_score) == 0:
                msg = '您的金币不足。'
                await bot.send(ev, msg, at_sender=True)
                return
            else:
                duel_judger.add_support(gid, uid, select_id, input_score)
                msg = f'支持{select_id}号成功。'
                await bot.send(ev, msg, at_sender=True)
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))


@sv.on_rex(r'^梭哈支持(1|2)号$')
async def on_input_duel_score2(bot, ev: CQEvent):
    try:
        if duel_judger.get_on_off_support_status(ev.group_id):
            gid = ev.group_id
            duel = DuelCounter()
            uid = ev.user_id
            if Suo_allow != True:
                msg = '管理员禁止梭哈。'
                await bot.send(ev, msg, at_sender=True)
                return
            score_counter = ScoreCounter2()
            match = ev['match']
            select_id = int(match.group(1))
            current_score = score_counter._get_score(gid, uid)
            input_score = current_score
            print(select_id, input_score)
            score_counter = ScoreCounter2()
            # 若下注该群下注字典不存在则创建
            if duel_judger.get_support(gid) == 0:
                duel_judger.set_support(gid)
            support = duel_judger.get_support(gid)
            # 检查是否重复下注
            if uid in support:
                msg = '您已经支持过了。'
                await bot.send(ev, msg, at_sender=True)
                return
            # 检查是否是决斗人员
            duellist = duel_judger.get_duelid(gid)
            if uid in duellist:
                msg = '决斗参与者不能支持。'
                await bot.send(ev, msg, at_sender=True)
                return
                # 检查金币是否足够下注
            if score_counter._judge_score(gid, uid, input_score) == 0:
                msg = '您的金币不足。'
                await bot.send(ev, msg, at_sender=True)
                return
            else:
                if duel._get_SUO_CELE(gid) == 1:
                    input_score = Suo * current_score * Suo_Cele_Num
                    duel_judger.add_support(gid, uid, select_id, input_score)
                    msg = f'梭哈支持{select_id}号{current_score}金币成功，[庆典举办中]胜利时，将获得相对于平常值{Suo * Suo_Cele_Num}倍的金币！'
                    await bot.send(ev, msg, at_sender=True)
                else:
                    input_score = Suo * current_score
                    duel_judger.add_support(gid, uid, select_id, input_score)
                    msg = f'梭哈支持{select_id}号{current_score}金币成功，胜利时，将获得相对于平常值{Suo}倍的金币！'
                    await bot.send(ev, msg, at_sender=True)
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))


# 以下部分与赛跑的重合，有一个即可，两个插件都装建议注释掉。
@sv.on_prefix(['领金币', '领取金币'])
async def add_score(bot, ev: CQEvent):
    try:
        score_counter = ScoreCounter2()
        gid = ev.group_id
        uid = ev.user_id
        guid = gid, uid
        if not daily_zero_get_limiter.check(guid):
            await bot.send(ev, f'今天已经领取过了{ZERO_GET_LIMIT}次了哦，明天再来吧。', at_sender=True)
            return

        current_score = score_counter._get_score(gid, uid)
        if current_score <= ZERO_GET_REQUIREMENT:
            score_counter._add_score(gid, uid, ZERO_GET_AMOUNT)
            msg = f'您已领取{ZERO_GET_AMOUNT}金币'
            daily_zero_get_limiter.increase(guid)
            r_n = random.randint(1, 100)
            if r_n == 1:
                i_2 = get_item_by_name("生财有道")
                add_item(gid, uid, i_2)
                msg += f'\n发低保的人看你太可怜了，偷偷的告诉了你几个赚钱的办法，你获得了{i_2["rank"]}级道具[{i_2["name"]}]'
            await bot.send(ev, msg, at_sender=True)
            return
        else:
            msg = f'金币为低于{ZERO_GET_REQUIREMENT}才能领取哦。'
            await bot.send(ev, msg, at_sender=True)
            return
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))


@sv.on_prefix(['查金币', '查询金币', '查看金币', '金币查询'])
async def get_score(bot, ev: CQEvent):
    try:
        score_counter = ScoreCounter2()
        gid = ev.group_id
        uid = ev.user_id

        current_score = score_counter._get_score(gid, uid)
        msg = f'您的金币为{current_score}'
        await bot.send(ev, msg, at_sender=True)
        return
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))


@sv.on_rex(f'^为(.*)充值(\d+)金币$')
async def cheat_score(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '不要想着走捷径哦。', at_sender=True)
    gid = ev.group_id
    match = ev['match']
    try:
        id = int(match.group(1))
    except ValueError:
        id = int(ev.message[1].data['qq'])
    except:
        await bot.finish(ev, '参数格式错误')
    num = int(match.group(2))
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    if duel._get_level(gid, id) == 0:
        await bot.finish(ev, '该用户还未在本群创建贵族哦。', at_sender=True)
    score_counter._add_score(gid, id, num)
    score = score_counter._get_score(gid, id)
    msg = f'已为[CQ:at,qq={id}]充值{num}金币。\n现在共有{score}金币。'
    await bot.send(ev, msg)


@sv.on_rex(f'^设定群(.*)为(\d+)号死$')
async def cheat_num(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '不要想着走捷径哦。', at_sender=True)
    match = ev['match']
    try:
        gid = int(match.group(1))
    except ValueError:
        gid = int(ev.message[1].data['qq'])
    except:
        await bot.finish(ev, '参数格式错误')
    deadnum = int(match.group(2))
    duel_judger.set_deadnum(gid, deadnum)
    msg = f'已将群{gid}本次决斗死亡位置修改为{deadnum}号。\n'
    print("死的位置是", duel_judger.get_deadnum(gid))
    await bot.send(ev, msg)


@sv.on_rex(f'^为(.*)转账(\d+)金币$')
async def cheat_score(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    match = ev['match']
    try:
        id = int(match.group(1))
    except ValueError:
        id = int(ev.message[1].data['qq'])
    except:
        await bot.finish(ev, '参数格式错误')
    num = int(match.group(2))
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    if duel_judger.get_on_off_status(ev.group_id):
        msg = '现在正在决斗中哦，请决斗后再进行转账吧。'
        await bot.send(ev, msg, at_sender=True)
        return
    if duel._get_level(gid, id) == 0:
        await bot.finish(ev, '该用户还未在本群创建贵族哦。', at_sender=True)
    score = score_counter._get_score(gid, uid)
    if score < num:
        msg = f'您的金币不足{num}哦。'
        await bot.send(ev, msg, at_sender=True)
        return
    else:
        score_counter._reduce_score(gid, uid, num)
        scoreyou = score_counter._get_score(gid, uid)
        cost = Zhuan_Need
        if duel._get_SUO_CELE(gid) == 1:
            cost = Suo_Ex_NEED
        num2 = num * (1 - cost)
        score_counter._add_score(gid, id, num2)
        score = score_counter._get_score(gid, id)
        msg = f'已为[CQ:at,qq={id}]转账{num}金币。\n扣除{cost * 100}%手续费，您的金币剩余{scoreyou}金币，对方金币剩余{score}金币。'
        if num >= 100000:
            if random.randint(1, 10) == 1:
                item = get_item_by_name("小恩小惠")
                add_item(gid, uid, item)
                msg += f"你的慷慨行为被别人看在眼里记在心里，获得了{item['rank']}级道具{item['name']}"

        await bot.send(ev, msg)


@sv.on_fullmatch('重置决斗')
async def init_duel(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能使用重置决斗哦。', at_sender=True)
    duel_judger.turn_off(ev.group_id)
    msg = '已重置本群决斗状态！'
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['查女友', '查询女友', '查看女友'])
async def search_girl(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    if not args:
        await bot.send(ev, '请输入查女友+角色名。', at_sender=True)
        return
    name = args[0]
    cid = duel_chara.name2id(name)
    if cid == 1000:
        await bot.send(ev, '请输入正确的角色名。', at_sender=True)
        return
    duel = DuelCounter()
    owner = duel._get_card_owner(gid, cid)
    c = duel_chara.fromid(cid)
    # 判断是否是妻子。
    print(duel._get_queen_owner(gid, cid))
    nvmes = get_nv_icon(cid)
    lh_msg = ''
    fashioninfo = get_fashion(cid)
    jishu = 0
    if fashioninfo:
        lh_msg = lh_msg + '\n角色目前拥有时装(只显示前3个)：'
        for fashion in fashioninfo:
            jishu = jishu + 1
            if jishu < 4:
                lh_msg = lh_msg + f"\n{fashion['icon']}\n{fashion['name']}\n获取途径{fashion['content']}"
    if duel._get_queen_owner(gid, cid) != 0:
        owner = duel._get_queen_owner(gid, cid)
        up_info = duel._get_fashionup(gid, owner, cid, 0)
        if up_info:
            fashion_info = get_fashion_info(up_info)
            nvmes = fashion_info['icon']
        await bot.finish(ev, f'\n{c.name}现在是\n[CQ:at,qq={owner}]的妻子哦。{nvmes}', at_sender=True)

    if owner == 0:
        try:
            await bot.send(ev, f'{c.name}现在还是单身哦，快去约到她吧。{nvmes}{lh_msg}', at_sender=True)
        except Exception as e:
            print(e)
        return
    else:
        up_info = duel._get_fashionup(gid, owner, cid, 0)
        if up_info:
            fashion_info = get_fashion_info(up_info)
            nvmes = fashion_info['icon']
        msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦。{nvmes}'
        await bot.send(ev, msg)


# 重置某一用户的金币，只用做必要时删库用。
@sv.on_prefix('重置金币')
async def reset_score(bot, ev: CQEvent):
    gid = ev.group_id
    if not priv.check_priv(ev, priv.OWNER):
        await bot.finish(ev, '只有群主才能使用重置金币功能哦。', at_sender=True)
    args = ev.message.extract_plain_text().split()
    if len(args) >= 2:
        await bot.finish(ev, '指令格式错误', at_sender=True)
    if len(args) == 0:
        await bot.finish(ev, '请输入重置金币+被重置者QQ', at_sender=True)
    else:
        id = args[0]
        duel = DuelCounter()
        if duel._get_level(gid, id) == 0:
            await bot.finish(ev, '该用户还未在本群创建贵族哦。', at_sender=True)
        score_counter = ScoreCounter2()
        current_score = score_counter._get_score(gid, id)
        score_counter._reduce_score(gid, id, current_score)
        await bot.finish(ev, f'已清空用户{id}的金币。', at_sender=True)


# 注意会清空此人的角色以及贵族等级，只用做必要时删库用。
@sv.on_prefix('重置角色')
async def reset_chara(bot, ev: CQEvent):
    gid = ev.group_id
    if not priv.check_priv(ev, priv.OWNER):
        await bot.finish(ev, '只有群主才能使用重置角色功能哦。', at_sender=True)
    args = ev.message.extract_plain_text().split()
    if len(args) >= 2:
        await bot.finish(ev, '指令格式错误', at_sender=True)
    if len(args) == 0:
        await bot.finish(ev, '请输入重置角色+被重置者QQ', at_sender=True)
    else:
        id = args[0]
        duel = DuelCounter()
        if duel._get_level(gid, id) == 0:
            await bot.finish(ev, '该用户还未在本群创建贵族哦。', at_sender=True)
        cidlist = duel._get_cards(gid, id)
        for cid in cidlist:
            duel._delete_card(gid, id, cid)
        score_counter = ScoreCounter2()
        current_score = score_counter._get_score(gid, id)
        score_counter._reduce_score(gid, id, current_score)
        queen = duel._search_queen(gid, id)
        duel._delete_queen_owner(gid, queen)
        duel._set_level(gid, id, 0)
        await bot.finish(ev, f'已清空用户{id}的女友和贵族等级。', at_sender=True)


@sv.on_prefix('确认重开')
async def reset_CK(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if Remake_allow == False:
        await bot.finish(ev, '管理员不允许自行重开。', at_sender=True)
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    prestige = score_counter._get_prestige(gid, uid)
    if prestige < 0:
        await bot.finish(ev, '您现在身败名裂（声望为负），无法重开！请联系管理员重开！', at_sender=True)
    if duel._get_level(gid, uid) == 0:
        await bot.finish(ev, '该用户还未在本群创建贵族哦。', at_sender=True)
    cidlist = duel._get_cards(gid, uid)
    for cid in cidlist:
        duel._delete_card(gid, uid, cid)
    score_counter = ScoreCounter2()
    current_score = score_counter._get_score(gid, uid)
    score_counter._reduce_score(gid, uid, current_score)
    queen = duel._search_queen(gid, uid)
    duel._delete_queen_owner(gid, queen)
    duel._set_level(gid, uid, 0)
    await bot.finish(ev, f'已清空您的女友和贵族等级，金币等。', at_sender=True)


@sv.on_prefix('分手')
async def breakup(bot, ev: CQEvent):
    if BREAK_UP_SWITCH == True:
        args = ev.message.extract_plain_text().split()
        gid = ev.group_id
        uid = ev.user_id
        duel = DuelCounter()
        level = duel._get_level(gid, uid)
        if duel_judger.get_on_off_status(ev.group_id):
            msg = '现在正在决斗中哦，请决斗后再来谈分手事宜吧。'
            await bot.finish(ev, msg, at_sender=True)
        if level == 0:
            await bot.finish(ev, '该用户还未在本群创建贵族哦。', at_sender=True)
        if not args:
            await bot.finish(ev, '请输入分手+角色名。', at_sender=True)
        name = args[0]
        cid = duel_chara.name2id(name)
        if cid == 1000:
            await bot.finish(ev, '请输入正确的角色名。', at_sender=True)
        score_counter = ScoreCounter2()
        needscore = level * 100
        needSW = level * 15
        if level == 20:
            needSW = 600
        score = score_counter._get_score(gid, uid)
        prestige = score_counter._get_prestige(gid, uid)
        cidlist = duel._get_cards(gid, uid)
        if cid not in cidlist:
            await bot.finish(ev, '该角色不在你的身边哦。', at_sender=True)
        # 检测是否是妻子
        queen = duel._search_queen(gid, uid)
        if cid == queen:
            await bot.finish(ev, '不可以和您的妻子分手哦。', at_sender=True)
        if score < needscore:
            msg = f'您的爵位分手一位女友需要{needscore}金币和{needSW}声望哦。\n分手不易，做好准备再来吧。'
            await bot.finish(ev, msg, at_sender=True)
        if prestige < needSW:
            msg = f'您的爵位分手一位女友需要{needscore}金币和{needSW}声望哦。\n分手不易，做好准备再来吧。'
            await bot.finish(ev, msg, at_sender=True)
        score_counter._reduce_score(gid, uid, needscore)
        score_counter._reduce_prestige(gid, uid, needSW)
        duel._delete_card(gid, uid, cid)
        count = get_user_counter(gid, uid, UserModel.FENSHOU)
        count += 1
        c = duel_chara.fromid(cid)
        CE = CECounter()
        guaji = CE._get_guaji(gid, uid)
        if cid == guaji:
            CE._add_guaji(gid, uid, 0)
        msg = f'\n“真正离开的那次，关门声最小。”\n你和{c.name}分手了。失去了{needscore}金币分手费,声望减少了{needSW}。\n{c.icon.cqcode}'
        if count >= 100:
            count = 0
            item = get_item_by_name("梦境巡游")
            add_item(gid, uid, item)
            msg += f"\n最近的分手让你感到十分疲惫了，很想睡一觉来回复心情。获取了{item['rank']}级道具{item['name']}"
        save_user_counter(gid, uid, UserModel.FENSHOU, count)
        await bot.send(ev, msg, at_sender=True)


@sv.on_rex(f'^一键分手(.*)$')
async def breakup_yj(bot, ev: CQEvent):
    if BREAK_UP_SWITCH == True:
        gid = ev.group_id
        uid = ev.user_id
        duel = DuelCounter()
        score_counter = ScoreCounter2()
        level = duel._get_level(gid, uid)
        # 处理输入数据
        match = ev['match']
        defen = str(match.group(1))
        defen = re.sub(r'[?？，,_]', '', defen)
        defen, unknown = duel_chara.roster.parse_team(defen)
        duel = DuelCounter()
        if unknown:
            _, name, score = duel_chara.guess_id(unknown)
            if score < 70 and not defen:
                return  # 忽略无关对话
            msg = f'无法识别"{unknown}"' if score < 70 else f'无法识别"{unknown}" 您说的有{score}%可能是{name}'
            await bot.finish(ev, msg)
            return
        if not defen:
            await bot.finish(ev, '请发送"进入副本+编组队伍"，无需+号', at_sender=True)
            return
        if len(defen) > 10:
            await bot.finish(ev, '不能多于10名角色', at_sender=True)
            return
        if len(defen) != len(set(defen)):
            await bot.finish(ev, '编队中含重复角色', at_sender=True)
            return
        if duel_judger.get_on_off_status(ev.group_id):
            msg = '现在正在决斗中哦，请决斗后再来谈分手事宜吧。'
            await bot.finish(ev, msg, at_sender=True)
        tas_list = []
        cidlist = duel._get_cards(gid, uid)
        for cid in defen:
            c = duel_chara.fromid(cid)

            needscore = level * 100
            needSW = level * 15
            if level == 20:
                needSW = 600
            score = score_counter._get_score(gid, uid)
            prestige = score_counter._get_prestige(gid, uid)
            if cid not in cidlist:
                await bot.finish(ev, f'{c.name}不在你的身边哦。', at_sender=True)
            # 检测是否是妻子
            queen = duel._search_queen(gid, uid)
            if cid == queen:
                await bot.finish(ev, '不可以和您的妻子分手哦。', at_sender=True)
            if score < needscore:
                msg = f'您的爵位分手一位女友需要{needscore}金币和{needSW}声望哦。\n分手不易，做好准备再来吧。'
                await bot.finish(ev, msg, at_sender=True)
            if prestige < needSW:
                msg = f'您的爵位分手一位女友需要{needscore}金币和{needSW}声望哦。\n分手不易，做好准备再来吧。'
                await bot.finish(ev, msg, at_sender=True)
            duel._delete_card(gid, uid, cid)
            score_counter._reduce_score(gid, uid, needscore)
            score_counter._reduce_prestige(gid, uid, needSW)
            msg = f"真正离开的那次，关门声最小。\n你和{c.name}分手了\n{c.icon.cqcode}"
            data = {
                "type": "node",
                "data": {
                    "name": "ご主人様",
                    "uin": "1587640710",
                    "content": msg
                }
            }
            tas_list.append(data)
        await bot.send_group_forward_msg(group_id=gid, messages=tas_list)


@sv.on_fullmatch(['查询声望', '查声望', '声望查询'])
async def inquire_prestige(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    prestige = score_counter._get_prestige(gid, uid)
    if prestige == None:
        await bot.finish(ev, '您还未开启声望系统哦。', at_sender=True)
    msg = f'您的声望为{prestige}点。'
    await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch(['加冕称帝', '加冕仪式'])
async def be_emperor(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    level = duel._get_level(gid, uid)
    score_counter = ScoreCounter2()
    prestige = score_counter._get_prestige(gid, uid)

    if prestige == None:
        await bot.finish(ev, '您还未开启声望系统哦。', at_sender=True)
    if level != 9:
        await bot.finish(ev, '只有国王才能进行加冕仪式哦。', at_sender=True)
    if prestige < DJ_NEED_SW:
        await bot.finish(ev, f'加冕仪式需要{DJ_NEED_SW}声望，您的声望不足哦。', at_sender=True)
    score = score_counter._get_score(gid, uid)
    if score < DJ_NEED_GOLD:
        await bot.finish(ev, f'加冕仪式需要{DJ_NEED_GOLD}金币，您的金币不足哦。', at_sender=True)
    score_counter._reduce_score(gid, uid, DJ_NEED_GOLD)
    score_counter._reduce_prestige(gid, uid, DJ_NEED_SW)
    duel._set_level(gid, uid, 10)
    msg = f'\n礼炮鸣响，教皇领唱“感恩赞美歌”。“皇帝万岁！”\n在民众的欢呼声中，你加冕为了皇帝。\n花费了{DJ_NEED_SW}点声望，{DJ_NEED_GOLD}金币。'
    await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch(['飞升成神', '成神飞升'])
async def be_feisheng(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    level = duel._get_level(gid, uid)
    score_counter = ScoreCounter2()
    prestige = score_counter._get_prestige(gid, uid)

    if level != 10:
        await bot.finish(ev, '只有皇帝才能飞升哦。', at_sender=True)
    if prestige < FS_NEED_SW:
        await bot.finish(ev, f'飞升成神需要{FS_NEED_SW}声望，您的声望不足哦。', at_sender=True)
    score = score_counter._get_score(gid, uid)
    if score < FS_NEED_GOLD:
        await bot.finish(ev, f'飞升成神需要{FS_NEED_GOLD}金币，您的金币不足哦。', at_sender=True)
    score_counter._reduce_score(gid, uid, FS_NEED_GOLD)
    score_counter._reduce_prestige(gid, uid, FS_NEED_SW)
    duel._set_level(gid, uid, 20)
    msg = f'\n光柱冲天，你感觉无尽的力量涌入了自己的体内。\n在民众的惊讶的目光中，你飞升成神了。\n花费了{FS_NEED_SW}点声望，{FS_NEED_GOLD}金币。'
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix('皇室婚礼')
async def marry_queen(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    level = duel._get_level(gid, uid)
    score_counter = ScoreCounter2()
    prestige = score_counter._get_prestige(gid, uid)
    if prestige == None:
        await bot.finish(ev, '您还未开启声望系统哦。', at_sender=True)
    if level <= 7:
        await bot.finish(ev, '只有8级(公爵)及以上才可以举办皇室婚礼哦。', at_sender=True)
    if duel._search_queen(gid, uid) != 0:
        await bot.finish(ev, '皇帝只可以举办一次皇室婚礼哦。', at_sender=True)
    if not args:
        await bot.finish(ev, '请输入皇室婚礼+角色名。', at_sender=True)
    name = args[0]
    cid = duel_chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的角色名。', at_sender=True)
    cidlist = duel._get_cards(gid, uid)
    if cid not in cidlist:
        await bot.finish(ev, '该角色不在你的身边哦。', at_sender=True)
    if prestige < 1000:
        await bot.finish(ev, '您现在名声不好，不能结婚哦（结婚需要声望大于1000）。', at_sender=True)
    if prestige < 0:
        await bot.finish(ev, '您现在身败名裂，不能结婚哦（结婚需要声望大于1000）。', at_sender=True)
    score = score_counter._get_score(gid, uid)
    if score < 3000:
        await bot.finish(ev, '皇室婚礼需要3000金币，您的金币不足哦。', at_sender=True)
    favor = duel._get_favor(gid, uid, cid)
    if favor < NEED_favor:
        await bot.finish(ev, f'举办婚礼的女友需要达到{NEED_favor}好感，您的好感不足哦。', at_sender=True)
    score_counter._reduce_score(gid, uid, 3000)
    duel._set_queen_owner(gid, cid, uid)
    nvmes = get_nv_icon(cid)
    c = duel_chara.fromid(cid)
    msg = f'繁杂的皇室礼仪过后\n\n{c.name}与[CQ:at,qq={uid}]\n\n正式踏上了婚礼的殿堂\n成为了他的妻子。\n让我们为他们表示祝贺！\n妻子不会因决斗被抢走了哦。\n{nvmes}'
    await bot.send(ev, msg)


@sv.on_prefix(['查好感', '查询好感'])
async def girl_story(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    if not args:
        await bot.finish(ev, '请输入查好感+女友名。', at_sender=True)
    name = args[0]
    cid = duel_chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的女友名。', at_sender=True)
    cidlist = duel._get_cards(gid, uid)
    if cid not in cidlist:
        await bot.finish(ev, '该女友不在你的身边哦。', at_sender=True)

    if duel._get_favor(gid, uid, cid) == None:
        duel._set_favor(gid, uid, cid, 0)
    favor = duel._get_favor(gid, uid, cid)
    relationship, text = get_relationship(favor)
    c = duel_chara.fromid(cid)
    nvmes = get_nv_icon_with_fashion(gid, uid, cid)
    msg = f'\n{c.name}对你的好感是{favor}\n你们的关系是{relationship}\n“{text}”\n{nvmes}'
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['每日约会', '女友约会', '贵族约会'])
async def daily_date(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    if not args:
        await bot.finish(ev, '请输入贵族约会+女友名。', at_sender=True)
    name = args[0]
    cid = duel_chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的女友名。', at_sender=True)
    cidlist = duel._get_cards(gid, uid)
    if cid not in cidlist:
        await bot.finish(ev, '该女友不在你的身边哦。', at_sender=True)
    guid = gid, uid
    if not daily_date_limiter.check(guid):
        await bot.finish(ev, '今天已经和女友约会过了哦，明天再来吧。', at_sender=True)

    loginnum_ = ['1', '2', '3', '4']
    r_ = [0.2, 0.4, 0.35, 0.05]
    sum_ = 0
    ran = random.random()
    for num, r in zip(loginnum_, r_):
        sum_ += r
        if ran < sum_: break
    Bonus = {'1': [5, Date5],
             '2': [10, Date10],
             '3': [15, Date15],
             '4': [20, Date20]
             }
    favor = Bonus[num][0]
    text = random.choice(Bonus[num][1])
    duel._add_favor(gid, uid, cid, favor)
    c = duel_chara.fromid(cid)
    nvmes = get_nv_icon(cid)
    up_info = duel._get_fashionup(gid, uid, cid, 0)
    if up_info:
        fashion_info = get_fashion_info(up_info)
        nvmes = fashion_info['icon']
    current_favor = duel._get_favor(gid, uid, cid)
    relationship = get_relationship(current_favor)[0]
    msg = f'\n\n{text}\n\n你和{c.name}的好感上升了{favor}点\n她现在对你的好感是{current_favor}点\n你们现在的关系是{relationship}\n{nvmes}'
    daily_date_limiter.increase(guid)
    if num == '4':
        item = choose_item()
        add_item(gid, uid, item)
        msg += f'\n{c.name}对你这次的表现十分满意，赠送给了你{item["rank"]}级道具[{item["name"]}]'
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['送礼物', '送礼', '赠送礼物'])
async def give_gift(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    if gift_change.get_on_off_giftchange_status(ev.group_id):
        await bot.finish(ev, "有正在进行的礼物交换，礼物交换结束再来送礼物吧。")
    if len(args) != 2:
        await bot.finish(ev, '请输入 送礼物+女友名+礼物名 中间用空格隔开。', at_sender=True)
    name = args[0]
    cid = duel_chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的女友名。', at_sender=True)
    cidlist = duel._get_cards(gid, uid)
    if cid not in cidlist:
        await bot.finish(ev, '该女友不在你的身边哦。', at_sender=True)
    gift = args[1]
    if gift not in GIFT_DICT.keys():
        await bot.finish(ev, '请输入正确的礼物名。', at_sender=True)
    gfid = GIFT_DICT[gift]
    if duel._get_gift_num(gid, uid, gfid) == 0:
        await bot.finish(ev, '你的这件礼物的库存不足哦。', at_sender=True)
    duel._reduce_gift(gid, uid, gfid)
    favor, text = check_gift(cid, gfid)
    duel._add_favor(gid, uid, cid, favor)
    current_favor = duel._get_favor(gid, uid, cid)
    relationship = get_relationship(current_favor)[0]

    c = duel_chara.fromid(cid)
    nvmes = get_nv_icon_with_fashion(gid, uid, cid)
    msg = f'\n{c.name}:“{text}”\n\n你和{c.name}的好感上升了{favor}点\n她现在对你的好感是{current_favor}点\n你们现在的关系是{relationship}\n{nvmes}'
    if current_favor >= PRINCESS_HEART_FAVOR:
        rn = random.randint(1, 100)
        if rn == 1:
            item = get_item_by_name("公主之心")
            add_item(gid, uid, item)
            msg += f"爱情是相对的，不能只是单方面付出，今天她也为你准备了一份礼物，获得了{item['rank']}级道具{item['name']}"
    if current_favor >= ETERNAL_LOVE_FAVOR:
        count = get_user_counter(gid, uid, UserModel.YONGHENG)
        if count == 0:
            item = get_item_by_name("永恒爱恋")
            add_item(gid, uid, item)
            save_user_counter(gid, uid, UserModel.YONGHENG, 1)
            msg += f"死生契阔，与子成说。执子之手，与子偕老。你获得了{item['rank']}级道具{item['name']}"
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['批量送礼', '一键送礼'])
async def give_gift_all(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    if gift_change.get_on_off_giftchange_status(ev.group_id):
        await bot.finish(ev, "有正在进行的礼物交换，礼物交换结束再来送礼物吧。")
    if len(args) != 2:
        await bot.finish(ev, '请输入 送礼物+女友名+礼物名 中间用空格隔开。', at_sender=True)
    name = args[0]
    cid = duel_chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的女友名。', at_sender=True)
    cidlist = duel._get_cards(gid, uid)
    if cid not in cidlist:
        await bot.finish(ev, '该女友不在你的身边哦。', at_sender=True)
    gift = args[1]
    if gift not in GIFT_DICT.keys():
        await bot.finish(ev, '请输入正确的礼物名。', at_sender=True)
    gfid = GIFT_DICT[gift]
    gift_num = duel._get_gift_num(gid, uid, gfid)
    if gift_num == 0:
        await bot.finish(ev, '你的这件礼物的库存不足哦。', at_sender=True)
    duel._reduce_gift(gid, uid, gfid, gift_num)
    favor, text = check_gift(cid, gfid)
    favor = gift_num * favor
    duel._add_favor(gid, uid, cid, favor)
    current_favor = duel._get_favor(gid, uid, cid)
    relationship = get_relationship(current_favor)[0]
    c = duel_chara.fromid(cid)
    nvmes = get_nv_icon_with_fashion(gid, uid, cid)
    msg = f'\n{c.name}:“{text}”\n您送给了{c.name}{gift}x{gift_num}\n你和{c.name}的好感上升了{favor}点\n她现在对你的好感是{current_favor}点\n你们现在的关系是{relationship}\n{nvmes}'
    if current_favor >= PRINCESS_HEART_FAVOR:
        rn = random.randint(1, 100)
        if rn <= gift_num:
            item = get_item_by_name("公主之心")
            add_item(gid, uid, item)
            msg += f"爱情是相对的，不能只是单方面付出，今天她也为你准备了一份礼物，获得了{item['rank']}级道具{item['name']}"
    if current_favor >= ETERNAL_LOVE_FAVOR:
        count = get_user_counter(gid, uid, UserModel.YONGHENG)
        if count == 0:
            item = get_item_by_name("永恒爱恋")
            add_item(gid, uid, item)
            save_user_counter(gid, uid, UserModel.YONGHENG, 1)
            msg += f"死生契阔，与子成说。执子之手，与子偕老。你获得了{item['rank']}级道具{item['name']}"
    await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch(['抽礼物', '买礼物', '购买礼物'])
async def buy_gift(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    guid = gid, uid
    if duel_judger.get_on_off_status(ev.group_id):
        msg = '现在正在决斗中哦，请决斗后再来买礼物吧。'
        await bot.finish(ev, msg, at_sender=True)
    score = score_counter._get_score(gid, uid)
    if score < 300:
        await bot.finish(ev, '购买礼物需要300金币，您的金币不足哦。', at_sender=True)
    if not daily_gift_limiter.check(guid):
        await bot.finish(ev, f'今天购买礼物已经超过{GIFT_DAILY_LIMIT}次了哦，明天再来吧。', at_sender=True)
    select_gift = random.choice(list(GIFT_DICT.keys()))
    gfid = GIFT_DICT[select_gift]
    duel._add_gift(gid, uid, gfid)
    msg = f'\n您花费了300金币，\n买到了[{select_gift}]哦，\n欢迎下次惠顾。'
    score_counter._reduce_score(gid, uid, 300)
    daily_gift_limiter.increase(guid)
    r_n = random.randint(1, 100)
    if r_n == 1:
        item = choose_item()
        add_item(gid, uid, item)
        msg += f'\n礼物店老板回馈消费者抽奖抽到了你，你获得了{item["rank"]}级道具[{item["name"]}]'
    await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch(['我的礼物', '礼物仓库', '查询礼物', '礼物列表', '礼物查询'])
async def my_gift(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    msg = f'\n您的礼物仓库如下:'
    giftmsg = ''
    for gift in GIFT_DICT.keys():
        gfid = GIFT_DICT[gift]
        num = duel._get_gift_num(gid, uid, gfid)
        if num != 0:
            # 补空格方便对齐
            length = len(gift)
            msg_part = '    ' * (4 - length)
            giftmsg += f'\n{gift}{msg_part}: {num}件'
    if giftmsg == '':
        await bot.finish(ev, '您现在没有礼物哦，快去发送 买礼物 购买吧。', at_sender=True)
    msg += giftmsg
    await bot.send(ev, msg, at_sender=True)


@sv.on_rex(f'^用([1-9][0-9]*个)?(.*)与(.*)交换(.*)$')
async def change_gift(bot, ev: CQEvent):
    gid = ev.group_id
    duel = DuelCounter()
    if gift_change.get_on_off_giftchange_status(ev.group_id):
        await bot.finish(ev, "有正在进行的礼物交换，请勿重复使用指令。")
    gift_change.turn_on_giftchange(gid)
    id1 = ev.user_id
    match = ev['match']
    try:
        id2 = int(ev.message[1].data['qq'])
    except:
        gift_change.turn_off_giftchange(ev.group_id)
        await bot.finish(ev, '参数格式错误')
    if id2 == id1:
        await bot.send(ev, "不能和自己交换礼物！", at_sender=True)
        gift_change.turn_off_giftchange(ev.group_id)
        return
    number = match.group(1)
    if not number:
        number = 1
    else:
        number = int(str(number).replace('个', ''))
    gift1 = match.group(2)
    gift2 = match.group(4)
    if gift1 not in GIFT_DICT.keys():
        gift_change.turn_off_giftchange(ev.group_id)
        await bot.finish(ev, f'礼物1不存在。')
    if gift2 not in GIFT_DICT.keys():
        gift_change.turn_off_giftchange(ev.group_id)
        await bot.finish(ev, f'礼物2不存在。')
    gfid1 = GIFT_DICT[gift1]
    gfid2 = GIFT_DICT[gift2]
    if gfid2 == gfid1:
        await bot.send(ev, "不能交换相同的礼物！", at_sender=True)
        gift_change.turn_off_giftchange(ev.group_id)
        return

    if duel._get_gift_num(gid, id1, gfid1) < number:
        gift_change.turn_off_giftchange(ev.group_id)
        await bot.finish(ev, f'[CQ:at,qq={id1}]\n您的{gift1}的库存不足哦。')
    if duel._get_gift_num(gid, id2, gfid2) < number:
        gift_change.turn_off_giftchange(ev.group_id)
        await bot.finish(ev, f'[CQ:at,qq={id2}]\n您的{gift2}的库存不足哦。')
    level2 = duel._get_level(gid, id2)
    noblename = get_noblename(level2)
    gift_change.turn_on_waitchange(gid)
    gift_change.set_changeid(gid, id2)
    gift_change.turn_off_accept_giftchange(gid)
    msg = f'[CQ:at,qq={id2}]\n尊敬的{noblename}您好：\n\n[CQ:at,qq={id1}]试图用[{gift1}]交换您的礼物[{gift2}],数量为{number}个。\n\n请在{WAIT_TIME_CHANGE}秒内[接受交换/拒绝交换]。'
    await bot.send(ev, msg)
    await asyncio.sleep(WAIT_TIME_CHANGE)
    gift_change.turn_off_waitchange(gid)
    if gift_change.get_isaccept_giftchange(gid) is False:
        msg = '\n礼物交换被拒绝。'
        gift_change.init_changeid(gid)
        gift_change.turn_off_giftchange(gid)
        await bot.finish(ev, msg, at_sender=True)
    duel._reduce_gift(gid, id1, gfid1, num=number)
    duel._add_gift(gid, id1, gfid2, num=number)
    duel._reduce_gift(gid, id2, gfid2, num=number)
    duel._add_gift(gid, id2, gfid1, num=number)
    msg = f'\n礼物交换成功！\n您使用[{gift1}]交换了\n[CQ:at,qq={id2}]的[{gift2}],共计{number}个。'
    gift_change.init_changeid(gid)
    gift_change.turn_off_giftchange(gid)
    await bot.finish(ev, msg, at_sender=True)


@sv.on_fullmatch('接受交换')
async def giftchangeaccept(bot, ev: CQEvent):
    gid = ev.group_id
    if gift_change.get_on_off_waitchange_status(gid):
        if ev.user_id == gift_change.get_changeid(gid):
            msg = '\n礼物交换接受成功，请耐心等待礼物交换结束。'
            await bot.send(ev, msg, at_sender=True)
            gift_change.turn_off_waitchange(gid)
            gift_change.turn_on_accept_giftchange(gid)


@sv.on_fullmatch('拒绝交换')
async def giftchangerefuse(bot, ev: CQEvent):
    gid = ev.group_id
    if gift_change.get_on_off_waitchange_status(gid):
        if ev.user_id == gift_change.get_changeid(gid):
            msg = '\n礼物交换拒绝成功，请耐心等待礼物交换结束。'
            await bot.send(ev, msg, at_sender=True)
            gift_change.turn_off_waitchange(gid)
            gift_change.turn_off_accept_giftchange(gid)


@sv.on_prefix(['购买情报', '买情报'])
async def buy_information(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    if duel_judger.get_on_off_status(ev.group_id):
        msg = '现在正在决斗中哦，请决斗后再来买情报吧。'
        await bot.finish(ev, msg, at_sender=True)
    if not args:
        await bot.finish(ev, '请输入买情报+女友名。', at_sender=True)
    name = args[0]
    cid = duel_chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的女友名。', at_sender=True)
    score = score_counter._get_score(gid, uid)
    if score < 500:
        await bot.finish(ev, '购买女友情报需要500金币，您的金币不足哦。', at_sender=True)
    score_counter._reduce_score(gid, uid, 500)
    last_num = cid % 10
    like = ''
    normal = ''
    dislike = ''
    for gift in GIFT_DICT.keys():
        if GIFT_DICT[gift] == last_num:
            favorite = gift
            continue
        num1 = last_num % 3
        num2 = GIFT_DICT[gift] % 3
        choicelist = GIFTCHOICE_DICT[num1]

        if num2 == choicelist[0]:
            like += f'{gift}\n'
            continue
        if num2 == choicelist[1]:
            normal += f'{gift}\n'
            continue
        if num2 == choicelist[2]:
            dislike += f'{gift}\n'
            continue
    c = duel_chara.fromid(cid)
    nvmes = get_nv_icon(cid)
    msg = f'\n花费了500金币，您买到了以下情报：\n{c.name}最喜欢的礼物是:\n{favorite}\n喜欢的礼物是:\n{like}一般喜欢的礼物是:\n{normal}不喜欢的礼物是:\n{dislike}{nvmes}'
    await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch('重置礼物交换')
async def init_change(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能使用重置礼物交换哦。', at_sender=True)
    gift_change.turn_off_giftchange(ev.group_id)
    msg = '已重置本群礼物交换状态！'
    await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch(['好感系统帮助', '礼物系统帮助', '好感帮助', '礼物帮助'])
async def gift_help(bot, ev: CQEvent):
    msg = '''
╔                                        ╗  
             好感系统帮助
[购买情报]{角色名}
[皇室婚礼]
[查好感]{角色名}
[贵族约会]{角色名}
[送礼物]{角色名} {礼物名}
[一键送礼]{角色名} {礼物名} 将库存的礼物全部送出
[买礼物]
[礼物列表]
[用{数量}个{礼物名}与@群友交换{礼物名}] 不输入"{数量}个"时数量为1
[好感列表]
[确认离婚]
注:
通过约会或者送礼可以提升好感
决斗输掉某女友会扣除30好感，不够则被抢走
女友喜好与原角色无关，只是随机生成，仅供娱乐
╚                                        ╝
 '''
    await bot.send(ev, msg)


@sv.on_fullmatch(['好感列表', '女友好感列表'])
async def get_favorlist(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅。'
        await bot.send(ev, msg, at_sender=True)
        return
    cidlist = duel._get_cards(gid, uid)
    if len(cidlist) == 0:
        await bot.finish(ev, '您现在还没有女友哦。', at_sender=True)
    favorlist = []
    for cid in cidlist:
        favor = duel._get_favor(gid, uid, cid)
        if favor != 0 and favor != None:
            favorlist.append({"cid": cid, "favor": favor})
    if len(favorlist) == 0:
        await bot.finish(ev, '您的女友好感全部为0哦。', at_sender=True)
    rows_by_favor = sorted(favorlist, key=lambda r: r['favor'], reverse=True)
    msg = '\n您好感0以上的女友的前15名如下所示:\n'
    num = min(len(rows_by_favor), 15)
    for i in range(0, num):
        cid = rows_by_favor[i]["cid"]
        favor = rows_by_favor[i]["favor"]
        c = duel_chara.fromid(cid)
        msg += f'{c.name}:{favor}点\n'
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix('确认离婚')
async def lihun_queen(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    level = duel._get_level(gid, uid)
    score_counter = ScoreCounter2()
    prestige = score_counter._get_prestige(gid, uid)
    if duel._search_queen(gid, uid) == 0:
        await bot.finish(ev, '您没有妻子！。', at_sender=True)
    score = score_counter._get_score(gid, uid)
    if prestige < 3000:
        await bot.finish(ev, '离婚需要3000声望，您的声望现在离婚可能身败名裂哦。', at_sender=True)
    if score < 20000:
        await bot.finish(ev, '离婚需要20000金币，您的金币不足哦。', at_sender=True)
    score_counter._reduce_score(gid, uid, 20000)
    score_counter._reduce_prestige(gid, uid, 3000)
    queen = duel._search_queen(gid, uid)
    duel._delete_card(gid, uid, queen)
    c = duel_chara.fromid(queen)
    nvmes = get_nv_icon_with_fashion(gid,uid,queen)
    msg = f'花费了20000金币，[CQ:at,qq={uid}]总算将他的妻子{c.name}赶出家门\n，引起了众人的不满，损失3000声望。{nvmes}'
    duel._delete_queen_owner(gid, queen)
    await bot.send(ev, msg)


@sv.on_rex(f'^为(.*)充值(\d+)声望$')
async def cheat_SW(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '不要想着走捷径哦。', at_sender=True)
    gid = ev.group_id
    match = ev['match']
    try:
        id = int(match.group(1))
    except ValueError:
        id = int(ev.message[1].data['qq'])
    except:
        await bot.finish(ev, '参数格式错误')
    num = int(match.group(2))
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    prestige = score_counter._get_prestige(gid, id)
    if duel._get_level(gid, id) == 0:
        await bot.finish(ev, '该用户还未在本群创建贵族哦。', at_sender=True)
    if prestige == None:
        await bot.finish(ev, '该用户尚未开启声望系统哦！。', at_sender=True)
    score_counter._add_prestige(gid, id, num)
    msg = f'已为[CQ:at,qq={id}]充值{num}声望。'
    await bot.send(ev, msg)


@sv.on_rex(f'^扣除(.*)的(\d+)声望$')
async def cheat_SW2(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '不要想着走捷径哦。', at_sender=True)
    gid = ev.group_id
    match = ev['match']
    try:
        id = int(match.group(1))
    except ValueError:
        id = int(ev.message[1].data['qq'])
    except:
        await bot.finish(ev, '参数格式错误')
    num = int(match.group(2))
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    prestige = score_counter._get_prestige(gid, id)
    if duel._get_level(gid, id) == 0:
        await bot.finish(ev, '该用户还未在本群创建贵族哦。', at_sender=True)
    if prestige == None:
        await bot.finish(ev, '该用户尚未开启声望系统哦！。', at_sender=True)
    score_counter._reduce_prestige(gid, id, num)
    msg = f'已扣除[CQ:at,qq={id}]的{num}声望。'
    await bot.send(ev, msg)


async def get_user_card_dict(bot, group_id):
    mlist = await bot.get_group_member_list(group_id=group_id)
    d = {}
    for m in mlist:
        d[m['user_id']] = m['card'] if m['card'] != '' else m['nickname']
    return d


@sv.on_fullmatch(('金币排行榜', '金币排行'))
async def Race_ranking(bot, ev: CQEvent):
    try:
        user_card_dict = await get_user_card_dict(bot, ev.group_id)
        score_dict = {}
        score_counter = ScoreCounter2()
        gid = ev.group_id
        for uid in user_card_dict.keys():
            if uid != ev.self_id:
                score_dict[user_card_dict[uid]] = score_counter._get_score(gid, uid)
        group_ranking = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)
        msg = '此群贵族决斗金币排行为:\n'
        for i in range(min(len(group_ranking), 10)):
            if group_ranking[i][1] != 0:
                msg += f'第{i + 1}名: {group_ranking[i][0]}, 金币: {group_ranking[i][1]}\n'
        await bot.send(ev, msg.strip())
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))


@sv.on_fullmatch(('声望排行榜', '声望排行'))
async def SW_ranking(bot, ev: CQEvent):
    try:
        user_card_dict = await get_user_card_dict(bot, ev.group_id)
        score_dict = {}
        score_counter = ScoreCounter2()
        gid = ev.group_id
        for uid in user_card_dict.keys():
            if uid != ev.self_id:
                score_dict[user_card_dict[uid]] = score_counter._get_prestige(gid, uid)
                if score_dict[user_card_dict[uid]] == None:
                    score_dict[user_card_dict[uid]] = 0
        group_ranking = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)
        msg = '此群贵族对决声望排行为:\n'
        for i in range(min(len(group_ranking), 10)):
            if group_ranking[i][1] != 0:
                msg += f'第{i + 1}名: {group_ranking[i][0]}, 声望: {group_ranking[i][1]}\n'
        await bot.send(ev, msg.strip())
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))


@sv.on_fullmatch(('女友排行榜', '女友排行'))
async def SW_ranking(bot, ev: CQEvent):
    try:
        user_card_dict = await get_user_card_dict(bot, ev.group_id)
        score_dict = {}
        score_counter = ScoreCounter2()
        duel = DuelCounter()
        gid = ev.group_id
        for uid in user_card_dict.keys():
            if uid != ev.self_id:
                cidlist = duel._get_cards(gid, uid)
                score_dict[user_card_dict[uid]] = cidnum = len(cidlist)
        group_ranking = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)
        msg = '此群贵族对决女友数排行为:\n'
        for i in range(min(len(group_ranking), 10)):
            if group_ranking[i][1] != 0:
                msg += f'第{i + 1}名: {group_ranking[i][0]}, 女友数: {group_ranking[i][1]}\n'
        await bot.send(ev, msg.strip())
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))


@sv.on_rex(f'^用(\d+)声望兑换金币$')
async def cheat_score(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    match = ev['match']
    num = int(match.group(1))
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    prestige = score_counter._get_prestige(gid, uid)
    if duel._get_level(gid, uid) == 0:
        await bot.finish(ev, '您还没有在本群创建贵族哦。', at_sender=True)
    if prestige == None:
        await bot.finish(ev, '您未开启声望系统哦！。', at_sender=True)
    if num < 200:
        await bot.finish(ev, '200声望起兑换哦！。', at_sender=True)
    score = score_counter._get_score(gid, uid)
    pay_score = num
    num2 = num * 10
    if prestige < pay_score:
        msg = f'您的声望只有{prestige}，无法兑换哦。'
        await bot.send(ev, msg, at_sender=True)
        return
    else:
        score_counter._reduce_prestige(gid, uid, pay_score)
        score_counter._add_score(gid, uid, num2)
        scoreyou = score_counter._get_score(gid, uid)
        prestige = score_counter._get_prestige(gid, uid)
        msg = f'使用{num}声望兑换{num2}金币成功\n您的声望剩余{prestige}，金币为{scoreyou}。'
        await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch(('查询庆典', '庆典状况', '当前庆典'))
async def GET_Cele(bot, ev: CQEvent):
    duel = DuelCounter()
    gid = ev.group_id
    if Show_Cele_Not == True:
        if duel._get_GOLD_CELE(gid) == 1:
            msg = f'\n当前正举办押注金币庆典，当支持成功时，获得的金币将变为原来的{Gold_Cele_Num}倍\n'
        else:
            msg = f'\n当前未举办金币庆典\n'
        if duel._get_QC_CELE(gid) == 1:
            msg += f'当前正举办贵族签到庆典，签到时获取的声望将变为{QD_SW_Cele_Num}倍，金币将变为{QD_Gold_Cele_Num}倍\n'
        else:
            msg += f'当前未举办签到庆典\n'
        if duel._get_SUO_CELE(gid) == 1:
            msg += f'当前正举办梭哈倍率庆典，梭哈时的倍率将额外提升{Suo_Cele_Num}倍\n'
        else:
            msg += f'当前未举办梭哈倍率庆典\n'
        if duel._get_FREE_CELE(gid) == 1:
            msg += f'当前正举办免费招募庆典，每日可免费招募{FREE_DAILY_LIMIT}次\n'
        else:
            msg += f'当前未举办免费招募庆典\n'
        if duel._get_SW_CELE(gid) == 1:
            msg += f'当前正举办限时开启声望招募庆典'
        else:
            msg += f'当前未举办限时开启声望招募庆典'
        await bot.send(ev, msg, at_sender=True)
    else:
        if duel._get_GOLD_CELE(gid) == 1:
            msg = f'\n当前正举办押注金币庆典，当支持成功时，获得的金币将变为原来的{Gold_Cele_Num}倍\n'
        else:
            msg = f'\n'
        if duel._get_QC_CELE(gid) == 1:
            msg += f'当前正举办贵族签到庆典，签到时获取的声望将变为{QD_SW_Cele_Num}倍，金币将变为{QD_Gold_Cele_Num}倍\n'
        if duel._get_SUO_CELE(gid) == 1:
            msg += f'当前正举办梭哈倍率庆典，梭哈时的倍率将额外提升{Suo_Cele_Num}倍\n'
        if duel._get_FREE_CELE(gid) == 1:
            msg += f'当前正举办免费招募庆典，每日可免费招募{FREE_DAILY_LIMIT}次\n'
        if duel._get_SW_CELE(gid) == 1:
            msg += f'当前正举办限时开启声望招募庆典'
        await bot.send(ev, msg, at_sender=True)


@sv.on_rex(r'^开启本群(金币|签到|梭哈倍率|免费招募|声望招募)庆典$')
async def ON_Cele_SWITCH(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '您无权开放庆典！', at_sender=True)
    duel = DuelCounter()
    if duel._get_SW_CELE(gid) == None:
        await bot.finish(ev, '本群庆典未初始化，请先发"初始化本群庆典"初始化数据！', at_sender=True)
    match = (ev['match'])
    cele = (match.group(1))
    if cele == '金币':
        QC_Data = duel._get_QC_CELE(gid)
        SUO_Data = duel._get_SUO_CELE(gid)
        SW_Data = duel._get_SW_CELE(gid)
        FREE_Data = duel._get_FREE_CELE(gid)
        duel._initialization_CELE(gid, 1, QC_Data, SUO_Data, SW_Data, FREE_Data)
        msg = f'已开启本群金币庆典，当支持成功时，获得的金币将变为原来的{Gold_Cele_Num}倍\n'
        await bot.send(ev, msg, at_sender=True)
        return
    elif cele == '签到':
        GC_Data = duel._get_GOLD_CELE(gid)
        SUO_Data = duel._get_SUO_CELE(gid)
        SW_Data = duel._get_SW_CELE(gid)
        FREE_Data = duel._get_FREE_CELE(gid)
        duel._initialization_CELE(gid, GC_Data, 1, SUO_Data, SW_Data, FREE_Data)
        msg = f'已开启本群贵族签到庆典，签到时获取的声望将变为{QD_SW_Cele_Num}倍，金币将变为{QD_Gold_Cele_Num}倍\n'
        await bot.send(ev, msg, at_sender=True)
        return
    elif cele == '梭哈倍率':
        GC_Data = duel._get_GOLD_CELE(gid)
        QC_Data = duel._get_QC_CELE(gid)
        SW_Data = duel._get_SW_CELE(gid)
        FREE_Data = duel._get_FREE_CELE(gid)
        duel._initialization_CELE(gid, GC_Data, QC_Data, 1, SW_Data, FREE_Data)
        msg = f'已开启本群梭哈倍率庆典，梭哈时的倍率将额外提升{Suo_Cele_Num}倍\n'
        await bot.send(ev, msg, at_sender=True)
        return
    elif cele == '免费招募':
        GC_Data = duel._get_GOLD_CELE(gid)
        QC_Data = duel._get_QC_CELE(gid)
        SUO_Data = duel._get_SUO_CELE(gid)
        SW_Data = duel._get_SW_CELE(gid)
        duel._initialization_CELE(gid, GC_Data, QC_Data, SUO_Data, SW_Data, 1)
        msg = f'已开启本群免费招募庆典，每日可免费招募{FREE_DAILY_LIMIT}次\n'
        await bot.send(ev, msg, at_sender=True)
        return
    elif cele == '声望招募':
        GC_Data = duel._get_GOLD_CELE(gid)
        QC_Data = duel._get_QC_CELE(gid)
        SUO_Data = duel._get_SUO_CELE(gid)
        FREE_Data = duel._get_FREE_CELE(gid)
        duel._initialization_CELE(gid, GC_Data, QC_Data, SUO_Data, 1, FREE_Data)
        msg = f'已开启本群限时开启声望招募庆典\n'
        await bot.send(ev, msg, at_sender=True)
        return
    msg = f'庆典名匹配出错！请输入金币/签到/梭哈/免费招募/声望招募庆典中的一个！'
    await bot.send(ev, msg, at_sender=True)


@sv.on_rex(r'^关闭本群(金币|签到|梭哈倍率|免费招募|声望招募)庆典$')
async def OFF_Cele_SWITCH(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '您无权开放庆典！', at_sender=True)
    match = (ev['match'])
    cele = (match.group(1))
    duel = DuelCounter()
    if duel._get_SW_CELE(gid) == None:
        await bot.finish(ev, '本群庆典未初始化，请先发"初始化本群庆典"初始化数据！', at_sender=True)
    if cele == '金币':
        QC_Data = duel._get_QC_CELE(gid)
        SUO_Data = duel._get_SUO_CELE(gid)
        SW_Data = duel._get_SW_CELE(gid)
        FREE_Data = duel._get_FREE_CELE(gid)
        duel._initialization_CELE(gid, 0, QC_Data, SUO_Data, SW_Data, FREE_Data)
        msg = f'\n已关闭本群金币庆典'
        await bot.send(ev, msg, at_sender=True)
        return
    elif cele == '签到':
        GC_Data = duel._get_GOLD_CELE(gid)
        SUO_Data = duel._get_SUO_CELE(gid)
        SW_Data = duel._get_SW_CELE(gid)
        FREE_Data = duel._get_FREE_CELE(gid)
        duel._initialization_CELE(gid, GC_Data, 0, SUO_Data, SW_Data, FREE_Data)
        msg = f'\n已关闭本群贵族签到庆典'
        await bot.send(ev, msg, at_sender=True)
        return
    elif cele == '梭哈倍率':
        GC_Data = duel._get_GOLD_CELE(gid)
        QC_Data = duel._get_QC_CELE(gid)
        SW_Data = duel._get_SW_CELE(gid)
        FREE_Data = duel._get_FREE_CELE(gid)
        duel._initialization_CELE(gid, GC_Data, QC_Data, 0, SW_Data, FREE_Data)
        msg = f'\n已关闭本群梭哈倍率庆典'
        await bot.send(ev, msg, at_sender=True)
        return
    elif cele == '免费招募':
        GC_Data = duel._get_GOLD_CELE(gid)
        QC_Data = duel._get_QC_CELE(gid)
        SUO_Data = duel._get_SUO_CELE(gid)
        SW_Data = duel._get_SW_CELE(gid)
        duel._initialization_CELE(gid, GC_Data, QC_Data, SUO_Data, SW_Data, 0)
        msg = f'\n已关闭本群免费招募庆典'
        await bot.send(ev, msg, at_sender=True)
        return
    elif cele == '声望招募':
        GC_Data = duel._get_GOLD_CELE(gid)
        QC_Data = duel._get_QC_CELE(gid)
        SUO_Data = duel._get_SUO_CELE(gid)
        FREE_Data = duel._get_FREE_CELE(gid)
        duel._initialization_CELE(gid, GC_Data, QC_Data, SUO_Data, 0, FREE_Data)
        msg = f'\n已关闭本群限时声望招募庆典'
        await bot.send(ev, msg, at_sender=True)
        return
    msg = f'庆典名匹配出错！请输入金币/签到/梭哈/免费招募/声望招募庆典中的一个！'
    await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch('初始化本群庆典')
async def initialization(bot, ev: CQEvent):
    uid = ev.user_id
    gid = ev.group_id
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '您无权初始化庆典！', at_sender=True)
    duel = DuelCounter()
    duel._initialization_CELE(gid, Gold_Cele, QD_Cele, Suo_Cele, SW_add, FREE_DAILY)
    msg = f'已成功初始化本群庆典！\n您可发送查询庆典来查看本群庆典情况！\n'
    await bot.send(ev, msg, at_sender=True)


@sv.on_rex(f'^兑换(\d+)声望$')
async def cheat_score(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    match = ev['match']
    num = int(match.group(1))
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    prestige = score_counter._get_prestige(gid, uid)
    if duel._get_level(gid, uid) == 0:
        await bot.finish(ev, '您还没有在本群创建贵族哦。', at_sender=True)
    if prestige == None:
        await bot.finish(ev, '您未开启声望系统哦！。', at_sender=True)
    score = score_counter._get_score(gid, uid)
    pay_score = num * 100
    if score < pay_score:
        msg = f'兑换{num}声望需要{pay_score}金币，您的金币只有{score}，无法兑换哦。'
        await bot.send(ev, msg, at_sender=True)
        return
    else:
        score_counter._reduce_score(gid, uid, pay_score)
        score_counter._add_prestige(gid, uid, num)
        scoreyou = score_counter._get_score(gid, uid)
        prestige = score_counter._get_prestige(gid, uid)
        msg = f'兑换{num}声望成功，扣除{pay_score}金币\n您的声望为{prestige}，金币剩余{scoreyou}。'
        await bot.send(ev, msg, at_sender=True)


# 时装系统模块
@sv.on_fullmatch(['时装系统帮助', '时装帮助'])
async def fashion_help(bot, ev: CQEvent):
    msg = '''
╔                                        ╗  
               时装系统帮助
[时装商城]
[购买时装] {角色名} {时装名}
[穿戴时装] {角色名} {时装名}
[还原穿戴]{角色名}
注:
通过购买时装可以提升好感
╚                                        ╝
 '''
    await bot.send(ev, msg)


@sv.on_fullmatch('时装商城')
async def fashion_list(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅。'
        await bot.send(ev, msg, at_sender=True)
        return

    cidlist = duel._get_cards(gid, uid)
    cidnum = len(cidlist)

    if cidnum == 0:
        msg = '您还没有女友，无法购买时装哦。'
        await bot.send(ev, msg, at_sender=True)
        return
    else:
        jishu = 0
        tas_list = []
        tat_list = (ev, f'[CQ:at,qq={uid}]您可以购买的时装为：\r\n')
        for tat in tat_list:
            data = {
                "type": "node",
                "data": {
                    "name": "ご主人様",
                    "uin": "1587640710",
                    "content": tat
                }
            }
            tas_list.append(data)
        for fashion in cfg.fashionlist:
            if cfg.fashionlist[fashion]['cid'] in cidlist:
                if cfg.fashionlist[fashion]['xd_flag'] == 0:
                    buy_info = duel._get_fashionbuy(gid, uid, cfg.fashionlist[fashion]['cid'],
                                                    cfg.fashionlist[fashion]['fid'])
                    if buy_info == 0:
                        jishu = jishu + 1
                        # if jishu<7:
                        lh_msg = ''
                        icon = get_fashion_icon(cfg.fashionlist[fashion]['fid'])
                        lh_msg = lh_msg + f"\n{icon}\n{cfg.fashionlist[fashion]['name']}"
                        if cfg.fashionlist[fashion]['pay_score'] > 0:
                            lh_msg = lh_msg + f"\n需要金币:{cfg.fashionlist[fashion]['pay_score']}"
                        if cfg.fashionlist[fashion]['pay_sw'] > 0:
                            lh_msg = lh_msg + f"\n需要声望:{cfg.fashionlist[fashion]['pay_sw']}"
                        data = {
                            "type": "node",
                            "data": {
                                "name": "ご主人様",
                                "uin": "1587640710",
                                "content": lh_msg
                            }
                        }
                        tas_list.append(data)
                        # else:
                        #    break
        if jishu > 0:
            await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)
            # await bot.send(ev, lh_msg, at_sender=True)
        else:
            msg = '您的女友中目前没有出售中的时装哦。'
            await bot.send(ev, msg, at_sender=True)


UNKNOWN = 1000


@sv.on_prefix(['购买时装', '买时装'])
async def buy_fashion(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    score_counter = ScoreCounter2()

    if duel_judger.get_on_off_status(ev.group_id):
        msg = '现在正在决斗中哦，请决斗后再来买时装吧。'
        await bot.finish(ev, msg, at_sender=True)
    if not args:
        await bot.finish(ev, '请输入购买时装+角色名+时装名。', at_sender=True)
    if len(args) < 2:
        await bot.finish(ev, '请输入购买时装+角色名+时装名。', at_sender=True)
    c_name = args[0]
    f_name = args[1]
    chara_id = duel_chara.name2id(c_name)
    if chara_id == UNKNOWN:
        await bot.finish(ev, f'未查询到名称为{c_name}的女友信息')
    fashioninfo_li = get_fashion(chara_id)
    fashioninfo = None
    for i in fashioninfo_li:
        if i['name'] == f_name:
            fashioninfo = i
            break
    if fashioninfo:
        cid = fashioninfo['cid']
        buy_info = duel._get_fashionbuy(gid, uid, cid, fashioninfo['fid'])
        if buy_info:
            await bot.finish(ev, f"您已购买过时装{fashioninfo['name']}请勿重复够吗哦。", at_sender=True)
            return
        owner = duel._get_card_owner(gid, fashioninfo['cid'])
        c = duel_chara.fromid(fashioninfo['cid'])
        if uid != owner:
            msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您没有购买时装的权限哦。'
            await bot.send(ev, msg)
            return
        if fashioninfo['xd_flag'] == 1:
            await bot.finish(ev, f"{fashioninfo['name']}为限定时装无法购买哦。", at_sender=True)
            return
        msg_score = ""
        if fashioninfo['pay_score'] > 0:
            score = score_counter._get_score(gid, uid)
            if score < fashioninfo['pay_score']:
                await bot.finish(ev, f"购买{fashioninfo['name']}需要{fashioninfo['pay_score']}金币，您的金币不足哦。", at_sender=True)
                return
            score_counter._reduce_score(gid, uid, fashioninfo['pay_score'])
            msg_score = msg_score + f"{fashioninfo['pay_score']}金币，"
        msg_prestige = ""
        if fashioninfo['pay_sw'] > 0:
            prestige = score_counter._get_prestige(gid, uid)
            if prestige == None:
                await bot.finish(ev, '您未开启声望系统哦！。', at_sender=True)
                return
            if prestige < fashioninfo['pay_sw']:
                await bot.finish(ev, f"购买{fashioninfo['name']}需要{fashioninfo['pay_sw']}声望，您的声望不足哦。", at_sender=True)
                return
            score_counter._reduce_prestige(gid, uid, fashioninfo['pay_sw'])
            msg_prestige = msg_prestige + f"{fashioninfo['pay_sw']}声望，"
        duel._add_favor(gid, uid, cid, fashioninfo['favor'])
        duel._add_fashionbuy(gid, uid, cid, fashioninfo['fid'])
        current_favor = duel._get_favor(gid, uid, cid)
        relationship = get_relationship(current_favor)[0]
        msg = f"您花费了{msg_score}{msg_prestige}为您的女友{c.name}购买了时装{fashioninfo['name']}\n您与{c.name}的好感上升了{fashioninfo['favor']}点\n她现在对你的好感是{current_favor}点\n你们现在的关系是{relationship}\n{fashioninfo['icon']}"
        await bot.send(ev, msg, at_sender=True)
    else:
        await bot.finish(ev, '请输入正确的时装名。', at_sender=True)


@sv.on_prefix(['穿戴时装', '穿时装'])
async def up_fashion(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()

    if not args:
        await bot.finish(ev, '请输入穿戴时装+角色名+时装名。', at_sender=True)
    if len(args) < 2:
        await bot.finish(ev, '请输入穿戴时装+角色名+时装名。', at_sender=True)
    c_name = args[0]
    f_name = args[1]
    chara_id = duel_chara.name2id(c_name)
    if chara_id == UNKNOWN:
        await bot.finish(ev, f'未查询到名称为{c_name}的女友信息')
    fashioninfo_li = get_fashion(chara_id)
    fashioninfo = None
    for i in fashioninfo_li:
        if i['name'] == f_name:
            fashioninfo = i
            break
    if fashioninfo:
        cid = fashioninfo['cid']
        c = duel_chara.fromid(cid)
        buy_info = duel._get_fashionbuy(gid, uid, cid, fashioninfo['fid'])
        if buy_info:
            duel._add_fashionup(gid, uid, cid, fashioninfo['fid'])
            msg = f"您为女友{c.name}穿上了时装{fashioninfo['name']}\n{fashioninfo['icon']}"
            await bot.send(ev, msg, at_sender=True)
        else:
            await bot.finish(ev, f"您还没有该时装哦，请输入购买时装+时装名进行购买哦。", at_sender=True)
            return
    else:
        await bot.finish(ev, '请输入正确的时装名。', at_sender=True)


@sv.on_prefix(['我的女友', '女友信息'])
async def my_fashion(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    if not args:
        await bot.send(ev, '请输入我的女友+角色名。', at_sender=True)
        return
    name = args[0]
    cid = duel_chara.name2id(name)
    if cid == 1000:
        await bot.send(ev, '请输入正确的角色名。', at_sender=True)
        return
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    CE = CECounter()
    c = duel_chara.fromid(cid)
    nvmes = get_nv_icon(cid)
    lh_msg = ''
    fashioninfo = get_fashion(cid)
    up_icon = ''
    up_info = duel._get_fashionup(gid, uid, cid, 0)
    jishu = 0
    up_name = ''
    if fashioninfo:
        for fashion in fashioninfo:
            buy_info = duel._get_fashionbuy(gid, uid, cid, fashion['fid'])
            if up_info == fashion['fid']:
                up_icon = fashion['icon']
                up_name = fashion['name']
            if buy_info:
                if up_info != fashion['fid']:
                    jishu = jishu + 1
                    if jishu < 3:
                        lh_msg = lh_msg + f"\n{fashion['icon']}\n{fashion['name']}"
    owner = duel._get_card_owner(gid, cid)
    if uid != owner:
        msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法查询哦。'
        await bot.send(ev, msg)
        return
    if owner == 0:
        await bot.send(ev, f'{c.name}现在还是单身哦，快去约到她吧。{nvmes}', at_sender=True)
        return
    if uid == owner:
        queen_msg = ''
        if duel._get_queen_owner(gid, cid) != 0:
            queen_msg = f'现在是您的妻子\n'
        if duel._get_favor(gid, uid, cid) == None:
            duel._set_favor(gid, uid, cid, 0)
        # 获取角色星级
        cardstar = CE._get_cardstar(gid, uid, cid)
        zllevel = CE._get_zhuansheng(gid, uid, cid)
        equip_list = ''
        equip_msg = ''
        dreeslist = CE._get_dress_list(gid, uid, cid)
        for eid in dreeslist:
            equipinfo = get_equip_info_id(eid)
            if equipinfo:
                equip_list = equip_list + f"\n{equipinfo['icon']}{equipinfo['type']}:{equipinfo['name']}({equipinfo['model']})"
        if equip_list:
            equip_msg = f"\n目前穿戴的装备为:{equip_list}"
        favor = duel._get_favor(gid, uid, cid)
        relationship, text = get_relationship(favor)
        card_ce = get_card_ce(gid, uid, cid)
        level_info = CE._get_card_level(gid, uid, cid)
        rank = CE._get_rank(gid, uid, cid)
        if up_icon:
            nvmes = up_icon
        up_msg = ''
        if up_name:
            up_msg = f"\n目前穿戴的时装是{up_name}\n"
        if lh_msg:
            lh_msg = f"\n您为{c.name}购买的时装有(只显示未穿的2件)：" + lh_msg
        msg = f'\n{c.name}目前的等级是{level_info}级，{zllevel}转，星级为{cardstar}星，rank等级为：{rank}级，战斗力为{card_ce}点\n{queen_msg}对你的好感是{favor}\n你们的关系是{relationship}\n“{text}”{equip_msg}{up_msg}{nvmes}{lh_msg}'
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['还原穿戴', '取消穿戴'])
async def up_fashion(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    if not args:
        await bot.send(ev, '请输入取消穿戴+角色名。', at_sender=True)
        return
    name = args[0]
    cid = duel_chara.name2id(name)
    if cid == 1000:
        await bot.send(ev, '请输入正确的角色名。', at_sender=True)
        return
    duel = DuelCounter()
    c = duel_chara.fromid(cid)
    nvmes = get_nv_icon(cid)
    owner = duel._get_card_owner(gid, cid)
    if uid != owner:
        msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法处理哦。'
        await bot.send(ev, msg)
        return
    if owner == 0:
        await bot.send(ev, f'{c.name}现在还是单身哦，快去约到她吧。{nvmes}', at_sender=True)
        return
    if uid == owner:
        up_info = duel._get_fashionup(gid, uid, cid, 0)
        if up_info:
            duel._delete_fashionup(gid, uid, cid)
            msg = f"您为您的女友{c.name}取消了时装的穿戴\n{nvmes}"
        else:
            msg = f"您的女友{c.name}没有穿戴时装，无法取消哦\n{nvmes}"
        await bot.send(ev, msg, at_sender=True)


@sv.on_prefix('发送红包')
async def ramdom_gold(bot, ev: CQEvent):
    if not r_gold.get_on_off_random_gold(ev.group_id):
        if not priv.check_priv(ev, priv.SUPERUSER):
            await bot.finish(ev, '该功能仅限超级管理员使用')
        gid = ev.group_id
        msg = ev.message.extract_plain_text().split()
        if not msg[0].isdecimal():
            await bot.finish(ev, '请输入正确的奖励金额')
        if not msg[1].isdecimal():
            await bot.finish(ev, '请输入正确的奖励个数')
        gold = int(msg[0])
        num = int(msg[1])
        await bot.send(ev, f'已发放红包，金币总额为：{gold}\n数量：{num}\n请输入 领取红包')
        r_gold.turn_on_random_gold(gid)
        r_gold.set_gold(gid)
        r_gold.add_gold(gid, gold, num)
        r_gold.random_g(gid, gold, num)
        await asyncio.sleep(60)
        r_gold.turn_off_random_gold(gid)
        await bot.send(ev, '随机金币奖励活动已结束，请期待下次活动开启')
        r_gold.user = {}


@sv.on_fullmatch('领取红包')
async def get_random_gold(bot, ev: CQEvent):
    if r_gold.get_on_off_random_gold(ev.group_id):
        uid = int(ev.user_id)
        gid = ev.group_id
        if uid in r_gold.user[gid]:
            await bot.finish(ev, '您已领取过红包', at_sender=True)
        score_counter = ScoreCounter2()
        # 获取金币
        gold = r_gold.get_gold(gid)
        # 获取个数
        num = r_gold.get_num(gid)
        # 获取金额
        rd = r_gold.get_user_random_gold(gid, num)
        r_gold.add_gold(gid, gold - rd, num - 1)
        newnum = r_gold.get_num(gid)
        newgold = r_gold.get_gold(gid)
        score_counter._add_score(gid, uid, rd)
        r_gold.add_user(gid, uid)
        await bot.send(ev, f'已领取红包：{rd}\n剩余{newnum}个总额：{newgold}', at_sender=True)
        if newnum == 0:
            await bot.send(ev, f'红包已全部领取完毕')
            r_gold.turn_off_random_gold(gid)
