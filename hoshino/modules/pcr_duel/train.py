import asyncio
import re
import time

import nonebot
import pytz

from hoshino.typing import CQEvent
from . import sv
from .ScoreCounter import ScoreCounter2
from .duelconfig import *


@sv.on_fullmatch(['培养帮助'])
async def gift_help(bot, ev: CQEvent):
    msg = '''
╔                                        ╗  
             培养帮助
[技能一览] [性格一览]
[查技能]{技能名}
[查性格]{性格名}
[修炼查询]
[挂机修炼]{女友名}
[结束修炼]
[提升rank]{角色名}
[角色升星] {角色名}
╚                                        ╝
 '''
    await bot.send(ev, msg)


@sv.on_prefix(['查性格'])
async def xiulian_start(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    if len(args) != 1:
        await bot.finish(ev, '请输入 查性格+性格名称 。', at_sender=True)
    name = args[0]
    if not character.get(name):
        await bot.finish(ev, f'未查询到名为"{name}"的性格', at_sender=True)
    msg = f'''
{name}:
{character[name]}
        '''.strip()
    await bot.send(ev, '\n' + msg, at_sender=True)


@sv.on_fullmatch(['性格列表', '性格一览'])
async def skill_li(bot, ev: CQEvent):
    tas_list = []
    data = {
        "type": "node",
        "data": {
            "name": "ご主人様",
            "uin": "1587640710",
            "content": "====== 性格列表 ======"
        }
    }
    tas_list.append(data)
    for i in character.keys():
        msg = f'''
{i}:
{character[i]}
    '''.strip()
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


@sv.on_prefix(['查技能'])
async def xiulian_start(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    if len(args) != 1:
        await bot.finish(ev, '请输入 查技能+性格名称 。', at_sender=True)
    name = args[0]
    if not skill_def_json.get(name):
        await bot.finish(ev, f'未查询到名为"{name}"的技能', at_sender=True)
    cost_msg = ''
    if skill_def_json[name].get('cost'):
        cost_msg = f"\n触发消耗sp:{skill_def_json[name].get('cost')}"
    msg = f'''
{name}:
发动消耗sp:{skill_def_json[name]['sp']}{cost_msg}
{skill_def_json[name]['desc']}
        '''.strip()
    await bot.send(ev, '\n' + msg, at_sender=True)


@sv.on_fullmatch(["技能列表", "技能一览"])
async def skill_li(bot, ev: CQEvent):
    tas_list = []
    data = {
        "type": "node",
        "data": {
            "name": "ご主人様",
            "uin": "1587640710",
            "content": "====== 技能列表 ======"
        }
    }
    tas_list.append(data)
    t = list(skill_def_json.keys())
    step = 5
    b = [t[i:i + step] for i in range(0, len(t), step)]
    for x in b:
        msgli = []
        for i in x:
            cost_msg = ''
            if skill_def_json[i].get('cost'):
                cost_msg = f"\n触发消耗sp:{skill_def_json[i].get('cost')}"
            msg = f'''{i}:
发动消耗sp:{skill_def_json[i]['sp']}{cost_msg}
{skill_def_json[i]['desc']}'''.strip()
            msgli.append(msg)
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content": "\n\n".join(msgli)
            }
        }
        tas_list.append(data)
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)


@sv.on_fullmatch(['修炼查询'])
async def my_fragment_list(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    CE = CECounter()
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过角色，请发送 创建角色 开始你的人生旅途。'
        await bot.send(ev, msg, at_sender=True)
        return
    equip_list = CE._get_fragment_list(gid, uid)
    cids = duel._get_cards(gid, uid)
    if len(equip_list) > 0:
        msg_list = '修炼列表：'
        for i in equip_list:
            if i[0] == 0 or i[0] not in cids:
                continue
            else:
                c = chara.fromid(i[0])
                name = c.name
            msg_list = msg_list + f"\n{name}:{i[1]}"
        await bot.send(ev, msg_list, at_sender=True)
    else:
        await bot.finish(ev, '您还没有挂机修炼过角色', at_sender=True)


@sv.on_prefix(['挂机修炼', '开始挂机'])
async def xiulian_start(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    if len(args) != 1:
        await bot.finish(ev, '请输入 挂机修炼+女友名 中间用空格隔开。', at_sender=True)
    name = args[0]
    cid = chara.name2id(name)
    if cid == 1000:
        await bot.send(ev, '请输入正确的角色名。', at_sender=True)
        return
    duel = DuelCounter()
    CE = CECounter()
    c = chara.fromid(cid)
    nvmes = get_nv_icon(cid)
    up_info = duel._get_fashionup(gid, uid, cid, 0)
    if up_info:
        fashion_info = get_fashion_info(up_info)
        nvmes = fashion_info['icon']
    owner = duel._get_card_owner(gid, cid)

    if uid != owner:
        msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法绑定哦。'
        await bot.send(ev, msg)
        return
    if owner == 0:
        await bot.send(ev, f'{c.name}现在还是单身哦，快去约到她吧。{nvmes}', at_sender=True)
        return
    guajiinfo = CE._get_xiulian(gid, uid)
    if guajiinfo[0] > 0:
        cgj = chara.fromid(guajiinfo[0])
        nvmesgj = get_nv_icon(guajiinfo[0])
        up_info = duel._get_fashionup(gid, uid, guajiinfo[0], 0)
        if up_info:
            fashion_info = get_fashion_info(up_info)
            nvmesgj = fashion_info['icon']
        await bot.finish(ev, f'{cgj.name}已经在修炼中了哦。{nvmesgj}', at_sender=True)
    if uid == owner:
        xltime = time.time()
        xltime = math.ceil(xltime)
        CE._add_xiulian(gid, uid, cid, xltime)
        await bot.send(ev, f'您的女友{c.name}开始修炼了\n注：一次性修炼最长不能超过24小时哦。{nvmes}', at_sender=True)


@sv.on_fullmatch(['结束修炼', '取消修炼'])
async def xiulian_end(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    guajiinfo = CE._get_xiulian(gid, uid)
    if guajiinfo[0] == 0:
        await bot.finish(ev, f'您没有正在修炼中的女友，请输入 挂机修炼+女友名 开始修炼哦。', at_sender=True)
    cid = guajiinfo[0]
    endtime = time.time()
    endtime = math.ceil(endtime)
    jgtime = endtime - guajiinfo[1]
    if jgtime < 3600:
        CE._delete_xiulian(gid, uid)
        await bot.finish(ev, f'修炼结束，修炼时间小于1小时，无法获得修炼度。', at_sender=True)
    sj_msg = ''
    count = check_build_counter(gid, uid, BuildModel.KONGFU)
    if count < 2:
        if jgtime > 86400:
            xlmin1 = math.ceil(jgtime / 60)
            sj_msg = sj_msg + f"总共修炼时间{xlmin1}分钟，由于超过24小时，实际"
            jgtime = 86400
    xlmin = math.ceil(jgtime / 3600)
    sj_msg = sj_msg + f"修炼时间为{xlmin}小时，"
    qinfen_flag = check_have_character(guajiinfo[0], "勤奋")
    if qinfen_flag:
        xlmin = int(xlmin * 1.5)
    CE._add_fragment_num(gid, uid, cid, xlmin)
    ex_msg = ''
    if count > 0:
        addexp = xlmin * GJ_EXP_RATE * count
        add_exp(gid, uid, guajiinfo[0], addexp)
        ex_msg += f"受到道馆的影响额外增加了{addexp}点经验"
    CE._delete_xiulian(gid, uid)
    c = chara.fromid(guajiinfo[0])
    nvmes = get_nv_icon(guajiinfo[0])
    duel = DuelCounter()
    up_info = duel._get_fashionup(gid, uid, guajiinfo[0], 0)
    if up_info:
        fashion_info = get_fashion_info(up_info)
        nvmes = fashion_info['icon']
    bd_msg = f"修炼结束，{sj_msg}\n您的女友{c.name}获得了{xlmin}点修炼度{ex_msg}\n{nvmes}"
    await bot.send(ev, bd_msg, at_sender=True)


@sv.on_prefix(['升级rank', 'rank升级', '提升rank'])
async def up_rank(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    if duel_judger.get_on_off_status(ev.group_id):
        msg = '现在正在决斗中哦，请决斗后再进行提升rank吧。'
        await bot.send(ev, msg, at_sender=True)
        return
    CE = CECounter()
    if len(args) != 1:
        await bot.finish(ev, '请输入 rank升级+女友名 中间用空格隔开。', at_sender=True)
    name = args[0]
    cid = chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的女友名。', at_sender=True)
    cidlist = duel._get_cards(gid, uid)
    if cid not in cidlist:
        await bot.finish(ev, '该女友不在你的身边哦。', at_sender=True)
    rank = CE._get_rank(gid, uid, cid)
    if rank == MAX_RANK:
        await bot.finish(ev, '该女友rank已升至满级，无法继续升级啦。', at_sender=True)
    new_rank = rank + 1
    rank_score = RANK_LIST[int(new_rank)]
    if get_weather(gid) == WeatherModel.YUNTIAN:
        rank_score = int(0.8 * rank_score)
    score_counter = ScoreCounter2()
    myscore = score_counter._get_score(gid, uid)
    if myscore < rank_score:
        await bot.finish(ev, f'升级rank所需金币不足！\n由{rank}级升至{new_rank}级需要：{rank_score}个，您当前剩余：{myscore}个', at_sender=True)
    # 消耗rank证明
    if new_rank < 8:
        item = get_item_by_name("初级进阶许可")
    elif 8 <= new_rank <= 13:
        item = get_item_by_name("中级进阶许可")
    else:
        item = get_item_by_name("高级进阶许可")
    if not check_have_item(gid, uid, item):
        await bot.finish(ev, f'你没有持有{item["name"]},无法提升rank！', at_sender=True)
    use_item(gid, uid, item)
    score_counter._reduce_score(gid, uid, rank_score)
    c = chara.fromid(cid)
    CE._up_rank(gid, uid, cid)
    msg = f'\n您花费了{rank_score}金币和对应级别证明为{c.name}提升了rank，当前rank等级为：{new_rank}级，女友战斗力大大提升！'
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['角色升星', '星级提升'])
async def cardstar_up(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    duel = DuelCounter()
    if len(args) != 1:
        await bot.finish(ev, '请输入 角色升星+女友名 中间用空格隔开。', at_sender=True)
    name = args[0]
    cid = chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的女友名。', at_sender=True)
    cidlist = duel._get_cards(gid, uid)
    if cid not in cidlist:
        await bot.finish(ev, '该女友不在你的身边哦。', at_sender=True)
    star = CE._get_cardstar(gid, uid, cid)
    if star == MAX_STAR:
        await bot.finish(ev, '该女友已升至满星，无法继续升星啦。', at_sender=True)
    new_star = star + 1
    needfragment = STAR_LIST[int(new_star)]

    card_fragment = CE._get_fragment_num(gid, uid, cid)
    mynum = int(card_fragment)
    nvmes = get_nv_icon_with_fashion(gid, uid, cid)
    if mynum < needfragment:
        await bot.finish(ev, f'升级到{new_star}星需要{needfragment}修炼度，您的修炼度为{mynum}，修炼度不够。', at_sender=True)
    CE._add_cardstar(gid, uid, cid)
    await bot.send(ev, f'升星成功！\n成功将您的女友{name}升到了{new_star}星,女友战斗力大大提升！{nvmes}', at_sender=True)
