import asyncio
import re
import time
from hoshino import priv
import nonebot
import pytz

from hoshino.typing import CQEvent
from . import sv
from .ScoreCounter import ScoreCounter2
from .duelconfig import *


@sv.on_fullmatch(['解除绑定'])
async def card_unbangdin(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    duel = DuelCounter()
    cid = CE._get_guaji(gid, uid)
    if cid == 0:
        msg = '您尚未绑定任何角色参与战斗。'
        await bot.finish(ev, msg)
    CE._add_guaji(gid, uid, 0)
    c = chara.fromid(cid)
    nvmes = get_nv_icon(cid)
    up_info = duel._get_fashionup(gid, uid, cid, 0)
    if up_info:
        fashion_info = get_fashion_info(up_info)
        nvmes = fashion_info['icon']
    msg = f"你解除了绑定的女友：{c.name}，该女友不会再参与战斗。\n{nvmes}"
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['绑定女友'])
async def card_bangdin(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    if not args:
        await bot.send(ev, '请输入绑定女友+角色名。', at_sender=True)
        return
    name = args[0]
    cid = chara.name2id(name)
    if cid == 1000:
        await bot.send(ev, '请输入正确的角色名。', at_sender=True)
        return
    duel = DuelCounter()
    CE = CECounter()
    c = chara.fromid(cid)
    nvmes = get_nv_icon(cid)

    owner = duel._get_card_owner(gid, cid)
    if owner == 0:
        await bot.send(ev, f'{c.name}现在还是单身哦，快去约到她吧。{nvmes}', at_sender=True)
        return
    if uid != owner:
        msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法绑定哦。'
        await bot.send(ev, msg)
        return

    if uid == owner:
        up_info = duel._get_fashionup(gid, uid, cid, 0)
        if up_info:
            fashion_info = get_fashion_info(up_info)
            nvmes = fashion_info['icon']
        CE._add_guaji(gid, uid, cid)
        msg = f"女友{c.name}绑定成功\n之后决斗胜利后{c.name}可以获得经验值哦\n{nvmes}"
    await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch(['查看绑定', '查看战斗女友'])
async def get_bangdin(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    duel = DuelCounter()
    cid = CE._get_guaji(gid, uid)
    if cid == 0:
        msg = '您尚未绑定任何角色参与战斗。'
        await bot.finish(ev, msg)
    owner = duel._get_card_owner(gid, cid)
    c = chara.fromid(cid)
    if uid != owner:
        msg = f'您绑定了：{c.name}，但她已不在您身边，请重新绑定您的女友。'
        await bot.finish(ev, msg)
    nvmes = get_nv_icon(cid)
    up_info = duel._get_fashionup(gid, uid, cid, 0)
    if up_info:
        fashion_info = get_fashion_info(up_info)
        nvmes = fashion_info['icon']
    msg = f"您当前绑定的女友是：{c.name}，每位角色只能绑定一位女友参与战斗哦~\n{nvmes}"
    await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch(['测试cron'])
async def paiming_list(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '测试用 勿扰。', at_sender=True)
    await clock()
    print("测试成功")


@sv.scheduled_job('cron', hour='*', minute='55', second='30')
async def clock():
    bot = nonebot.get_bot()
    i_c = ItemCounter()
    recover_info = i_c._get_all_user_recover()
    for i in recover_info:
        gid = i[0]
        uid = i[1]
        num = i[2]
        guid = gid, uid
        if daily_stage_limiter.get_num(guid):
            daily_stage_limiter.increase(guid, num=-1)
        if daily_duel_limiter.get_num(guid):
            daily_duel_limiter.increase(guid, num=-1)
        num -= 1
        save_user_counter(gid, uid, UserModel.RECOVER, num)
        await bot.send_group_msg(group_id=gid, message=f"[CQ:at,qq={uid}]由于超再生力的效果你恢复了一次决斗次数和副本次数")
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    if now.hour % 2 == 1:
        penglai_info = i_c._get_all_user_penglai()
        for i in penglai_info:
            gid = i[0]
            uid = i[1]
            guid = gid, uid
            if daily_stage_limiter.get_num(guid):
                daily_stage_limiter.increase(guid, num=-1)
            if daily_duel_limiter.get_num(guid):
                daily_duel_limiter.increase(guid, num=-1)

    free_li = i_c._get_free_state()
    duel = DuelCounter()
    for i in free_li:
        gid = i[0]
        GC_Data = duel._get_GOLD_CELE(gid)
        QC_Data = duel._get_QC_CELE(gid)
        SUO_Data = duel._get_SUO_CELE(gid)
        SW_Data = duel._get_SW_CELE(gid)
        duel._initialization_CELE(gid, GC_Data, QC_Data, SUO_Data, SW_Data, 0)
        i_c._save_group_state(gid, GroupModel.OFF_FREE, 0)
        await bot.send_group_msg(group_id=gid, message="本群免费招募庆典已关闭")

    # 每天早上4:55变更天气
    if now.hour == 4:
        group_list = []
        self_ids = bot._wsr_api_clients.keys()
        for sid in self_ids:
            gl = await bot.get_group_list(self_id=sid)
            each = [g["group_id"] for g in gl]
            group_list.extend(each)
        for gid in group_list:
            rd = random.choice([i for i in WeatherModel])
            save_weather(gid, rd)

    if not now.day == 1:  # 每月1号结算
        return
    if not now.hour == 1:  # 每天1点结算
        return

    jianglilist = {
        1: 4000,
        2: 3500,
        3: 3000,
        4: 2500,
        5: 2500,
        6: 2500,
        7: 2000,
        8: 2000,
        9: 2000,
        10: 2000,
        11: 1500,
        12: 1500,
        13: 1500,
        14: 1500,
        15: 1500,
        16: 1000,
        17: 1000,
        18: 1000,
        19: 1000,
        20: 1000,
    }

    CE = CECounter()

    nowyear = datetime.now().year
    nowmonth = datetime.now().month
    if nowmonth == 1:
        nowyear = nowyear - 1
        nowmonth = 12
    else:
        nowyear = nowyear
        nowmonth = nowmonth - 1
    period = str(nowyear) + str(nowmonth)

    shuchu_list = CE._get_shuchu_pmq(period)
    if not shuchu_list[0][0]:
        print('无法获取到数据')
    with open(os.path.join(FILE_PATH, 'bossinfo.json'), 'r', encoding='UTF-8') as fa:
        bosslist = json.load(fa, strict=False)
    bl_list = []
    for boss in bosslist:
        bv = []
        for j in bosslist[boss]['bosslist']:
            bv_boss = bosslist[boss]['bosslist'][j]['fenshu']
            bv.append(bv_boss)
        for i in bosslist[boss]['zhoumu']:
            bl_list.append(bv)
    group_list = []
    for shuchu in shuchu_list:
        if shuchu[0] not in group_list:
            group_list.append(shuchu[0])
    grouplist_s = []
    grouplist_b = []
    for groupid in group_list:
        defen_s = 0
        defen_b = 0
        for shuchuinfo in shuchu_list:
            if shuchuinfo[0] == groupid:
                zhoumu = shuchuinfo[2] - 1
                bossid = shuchuinfo[3] - 1
                beilv = bl_list[zhoumu][bossid]
                defen = math.ceil(shuchuinfo[4] * beilv)
                if shuchuinfo[5] == 1:
                    defen_s = defen_s + defen
                else:
                    defen_b = defen_b + defen
        dfgroup_s = [groupid, defen_s]
        dfgroup_b = [groupid, defen_b]
        grouplist_s.append(dfgroup_s)
        grouplist_b.append(dfgroup_b)

    grouplist_s = sorted(grouplist_s, key=lambda cus: cus[1], reverse=True)
    grouplist_b = sorted(grouplist_b, key=lambda cus: cus[1], reverse=True)

    msg_s = ''
    mingc_s = 1
    for info in grouplist_s:
        groupid = str(info[0])
        groupid = str(groupid[:3]) + '****' + str(groupid[-3:])
        msg_s = msg_s + f"群号：{groupid}，总积分：{info[1]},名次：{mingc_s}\n"
        mingc_s = mingc_s + 1

    msg_b = ''
    mingc_b = 1
    for info in grouplist_b:
        groupid = str(info[0])
        groupid = str(groupid[:3]) + '****' + str(groupid[-3:])
        msg_b = msg_b + f"群号：{groupid}，总积分：{info[1]},名次：{mingc_b}\n"
        mingc_b = mingc_b + 1

    mingcilist_s = {}
    mingc_s = 1
    for info in grouplist_s:
        mingcilist_s[info[0]] = mingc_s
        mingc_s = mingc_s + 1

    mingcilist_b = {}
    mingc_b = 1
    for info in grouplist_b:
        mingcilist_b[info[0]] = mingc_b
        mingc_b = mingc_b + 1

    for groupid in group_list:

        tas_list_s = []
        tas_list_b = []
        uidlist_s = []
        uidlist_b = []
        gidmc_s = mingcilist_s[groupid]
        gidmc_b = mingcilist_b[groupid]
        gidjl_s = jianglilist[gidmc_s]
        gidjl_b = jianglilist[gidmc_b]

        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content": f"本群boss战群排名第{gidmc_b}名，获得奖励"
            }
        }
        tas_list_b.append(data)

        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content": msg_b
            }
        }
        tas_list_b.append(data)

        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content": f"本群世界boss群排名第{gidmc_s}名，获得奖励"
            }
        }
        tas_list_s.append(data)

        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content": msg_s
            }
        }
        tas_list_s.append(data)

        for shuchuinfo in shuchu_list:
            if shuchuinfo[0] == groupid:
                if shuchuinfo[5] == 1:
                    if shuchuinfo[1] not in uidlist_s:
                        uidlist_s.append(shuchuinfo[1])
                        CE._add_dunscore(groupid, shuchuinfo[1], gidjl_s)
                        data = {
                            "type": "node",
                            "data": {
                                "name": "ご主人様",
                                "uin": "1587640710",
                                "content": f"[CQ:at,qq={shuchuinfo[1]}]您获得了{gidjl_s}副本币"
                            }
                        }
                        tas_list_s.append(data)
                else:
                    if shuchuinfo[1] not in uidlist_b:
                        uidlist_b.append(shuchuinfo[1])
                        CE._add_dunscore(groupid, shuchuinfo[1], gidjl_b)
                        data = {
                            "type": "node",
                            "data": {
                                "name": "ご主人様",
                                "uin": "1587640710",
                                "content": f"[CQ:at,qq={shuchuinfo[1]}]您获得了{gidjl_b}副本币"
                            }
                        }
                        tas_list_b.append(data)
        await bot.send_group_forward_msg(group_id=groupid, messages=tas_list_s)
        await bot.send_group_forward_msg(group_id=groupid, messages=tas_list_b)
