import asyncio
import re
import time
from hoshino import priv
import nonebot
import pytz
from .battle import *

from hoshino.typing import CQEvent
from . import sv
from .ScoreCounter import ScoreCounter2
from .duelconfig import *


@sv.on_fullmatch(['会战系统帮助', '会战帮助'])
async def boss_help(bot, ev: CQEvent):
    msg = '''
╔                                        ╗  
             会战帮助
[编队{队伍名/角色名}开始boss战]
[编队{队伍名/角色名}开始世界boss]
[boss战状态][世界boss状态]
[boss战伤害排行][世界boss伤害排行]
[会战群排名]
╚                                        ╝
 '''
    await bot.send(ev, msg)


@sv.on_rex(f'^编队(.*)开始(.*)$')
async def start_huizhan(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    CE = CECounter()
    # 处理输入数据
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    if now.day == 1 and now.hour == 0:  # 每月1号结算
        await bot.finish(ev, '会战奖励结算中，禁止出刀', at_sender=True)
        return

    match = ev['match']
    gotype = str(match.group(2)).strip()
    gotype = re.sub(r'[?？，,_ ]', '', gotype)
    if gotype == "世界boss":
        sendgid = 999
        shijieflag = 1
        keygid = gid + sendgid
    elif gotype == "boss战":
        sendgid = gid
        shijieflag = 0
        keygid = gid
    else:
        await bot.finish(ev, '请选择正确的boss战类型（世界boss/boss战）', at_sender=True)
    nowyear = datetime.now().year
    nowmonth = datetime.now().month
    nowday = datetime.now().day
    fighttime = str(nowyear) + str(nowmonth) + str(nowday)
    guid = keygid, uid
    if not daily_boss_limiter.check(guid):
        await bot.send(ev, f'今天的{gotype}次数已经超过上限了哦，明天再来吧。', at_sender=True)
        return
    defen = str(match.group(1)).strip()
    defen = re.sub(r'[?？，,_]', '', defen)
    if not defen:
        await bot.finish(ev, '请发送"编队+女友名/队伍名+开始+(boss战/世界boss)"，无需+号', at_sender=True)
    # 查询是否是队伍
    teamlist = CE._get_teamlist(gid, uid, defen)
    if teamlist != 0:
        defen = []
        for i in teamlist:
            cid = i[0]
            defen.append(cid)
    else:
        defen, unknown = chara.roster.parse_team(defen)
        if unknown:
            _, name, score = chara.guess_id(unknown)
            if score < 70 and not defen:
                return  # 忽略无关对话
            msg = f'无法识别"{unknown}"' if score < 70 else f'无法识别"{unknown}" 您说的有{score}%可能是{name}'
            await bot.finish(ev, msg)
        if len(defen) > 5:
            await bot.finish(ev, '编队不能多于5名角色', at_sender=True)
        if len(defen) != len(set(defen)):
            await bot.finish(ev, '编队中含重复角色', at_sender=True)
    for cid in defen:
        c = chara.fromid(cid)
        nvmes = get_nv_icon(cid)
        owner = duel._get_card_owner(gid, cid)
        if owner == 0:
            await bot.finish(ev, f'{c.name}现在还是单身哦，快去约到她吧。{nvmes}', at_sender=True)
        if uid != owner:
            msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法编队哦。'
            await bot.finish(ev, msg)
        fightinfo = CE._get_cardfightinfo(gid, uid, cid, fighttime, shijieflag)
        if fightinfo[0] > 0:
            msg = f'{c.name}今日已战斗过了，无法继续战斗了哦，请替换其他的女友出战哦。'
            await bot.finish(ev, msg)

    # print("开始会战")
    bianzu = ''
    # 获取本群boss状态和血量
    bossinfo = get_boss_info(sendgid)
    if len(bossinfo) > 0:
        # 获取编队战力与信息
        charalist = []
        for cid in defen:
            c = chara.fromid(cid)
            star = CE._get_cardstar(gid, uid, cid)
            charalist.append(chara.Chara(cid, star, 0))
            bianzu = bianzu + f"{c.name} "
        res = chara.gen_team_pic(charalist, star_slot_verbose=False)
        bio = BytesIO()
        res.save(bio, format='PNG')
        base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
        mes = f"[CQ:image,file={base64_str}]"
        msg1 = f"[CQ:at,qq={uid}]编组成功{bianzu}\n{mes}\n开始进入会战\n当前boss为：第{bossinfo['zhoumu']}周目{bossinfo['bossid']}号boss({bossinfo['name']})\nboss的atk为{bossinfo['ce']}，当前血量为{bossinfo['hp']}\n，开始战斗\n{bossinfo['icon']}"
        tas_list = []
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content": msg1
            }
        }
        tas_list.append(data)
        my = duel_my_buff(gid, uid, defen)
        enemy = duel_enemy_buff([], bossinfo['hp'], bossinfo['sp'], bossinfo['ce'], bossinfo['buff'], bossinfo['skill'])
        success, log = battle(my, enemy)
        tas_list.extend(build_battle_tag_list(log))
        msg = ''
        # 判断造成的伤害是否大于boss血量
        shanghai = bossinfo['hp'] - enemy.hp
        if success:
            # 计算下一个boss
            nextboss = bossinfo['bossid'] + 1
            nextzhoumu = bossinfo['zhoumu']
            nexthp = 0
            if nextboss == 6:
                nextboss = 1
                nextzhoumu = bossinfo['zhoumu'] + 1
            if nextzhoumu > 20:
                nextzhoumu = 1
            nextbossinfo = get_nextbossinfo(nextzhoumu, nextboss, shijieflag)
            boss_msg = f"击杀了boss\n下一个boss为：第{nextzhoumu}周目{nextboss}号boss({nextbossinfo['name']})"
            msg = msg + f"您对boss造成了{shanghai}点伤害，{boss_msg}"
            shanghai = bossinfo['hp']
        else:
            # 每日次数-1
            daily_boss_limiter.increase(guid)
            # 计算下一个boss
            nextboss = bossinfo['bossid']
            nextzhoumu = bossinfo['zhoumu']
            now_hp = enemy.hp
            nexthp = now_hp
            boss_msg = f"boss剩余血量{now_hp}点"
            msg = msg + f"您对boss造成了{shanghai}点伤害，{boss_msg}"
        CE._up_bossinfo(sendgid, nextzhoumu, nextboss, nexthp)
        CE._add_bossfight(gid, uid, bossinfo['zhoumu'], bossinfo['bossid'], shanghai, shijieflag)
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content": msg
            }
        }
        tas_list.append(data)
        # 增加经验值
        record_msg = '出刀奖励结算：'
        exp = bossinfo['add_exp']
        if success:
            exp = exp * 2
        for cid in defen:
            c = chara.fromid(cid)
            card_level = add_exp(gid, uid, cid, exp)
            CE._add_cardfight(gid, uid, cid, fighttime, 0, shijieflag)
            record_msg += f"\n你的女友 {c.name} 获取了{bossinfo['add_exp']}点经验，{card_level[2]}"
        # 奖励声望
        score_counter = ScoreCounter2()
        sw_add = len(defen) * 100
        score_counter._add_prestige(gid, uid, sw_add)
        record_msg += f'\n由于你的英勇出战你获得了{sw_add}声望'
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content": record_msg
            }
        }
        tas_list.append(data)
        await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)
        await asyncio.sleep(3)
        # 判断是否击杀boss，分配boss掉落
        if shanghai >= bossinfo['hp']:
            # 获取boss伤害输出表
            group_list = []
            awardlist = []
            awardnum = 0
            shuchulist = CE._get_shuchulist(sendgid, bossinfo['zhoumu'], bossinfo['bossid'], shijieflag)
            for shuchu in shuchulist:
                if awardnum < 3:
                    awardlist.append(shuchu[2])
                awardnum += 1
                if shuchu[0] not in group_list:
                    group_list.append(shuchu[0])
            for groupid in group_list:
                tas_list = []
                data = {
                    "type": "node",
                    "data": {
                        "name": "ご主人様",
                        "uin": "1587640710",
                        "content": f"{gotype}战况：\n第{bossinfo['zhoumu']}周目{bossinfo['bossid']}号boss({bossinfo['name']})\n已被打死，开始分配boss掉落"
                    }
                }
                tas_list.append(data)
                user_card_dict = await get_user_card_dict(bot, groupid)
                for shuchu in shuchulist:
                    if groupid == shuchu[0]:
                        get_equip = ''
                        get_awardequip = ''
                        for y in range(bossinfo['dropnum']):
                            equip_info = add_equip_info(shuchu[0], shuchu[1], bossinfo['dropequip'], bossinfo['equip'])
                            get_equip = get_equip + f"{equip_info['model']}品质{equip_info['type']}:{equip_info['name']}\n"
                        if shuchu[2] in awardlist:
                            awardequip_info = add_equip_info(shuchu[0], shuchu[1], bossinfo['awardequip'],
                                                             bossinfo['awardlist'])
                            get_awardequip = get_awardequip + f"由于您的本次输出为前三名，额外获得装备：{awardequip_info['model']}品质{awardequip_info['type']}:{awardequip_info['name']}\n"
                        u_n = user_card_dict.get(shuchu[1])
                        if not u_n:
                            u_n = "未知角色"
                        data = {
                            "type": "node",
                            "data": {
                                "name": "ご主人様",
                                "uin": "1587640710",
                                "content": f"{u_n}，您对boss造成了{shuchu[2]}点伤害，获得了装备\n{get_equip}{get_awardequip}"
                            }
                        }
                        tas_list.append(data)
                await bot.send_group_forward_msg(group_id=groupid, messages=tas_list)
    else:
        await bot.finish(ev, '无法获取boss信息', at_sender=True)
        return


@sv.on_rex(f'^(.*)状态$')
async def boss_info(bot, ev: CQEvent):
    gid = ev.group_id
    match = ev['match']
    gotype = str(match.group(1))
    gotype = re.sub(r'[?？，,_ ]', '', gotype)
    if gotype == "世界boss":
        sendgid = 999
    elif gotype == "boss战":
        sendgid = gid
    else:
        await bot.finish(ev, '请选择正确的boss战类型（世界boss/boss战）', at_sender=True)
    bossinfo = get_boss_info(sendgid)
    msg = f"当前boss状态为：\n第{bossinfo['zhoumu']}周目{bossinfo['bossid']}号boss({bossinfo['name']})\nboss的atk为{bossinfo['ce']}，当前血量为{bossinfo['hp']}\n{bossinfo['icon']}"
    await bot.send(ev, msg)


@sv.on_rex(f'^((世界boss)|(boss战))伤害排行$')
async def shuchu_list(bot, ev: CQEvent):
    gid = ev.group_id
    CE = CECounter()
    match = ev['match']
    gotype = str(match.group(1))
    gotype = re.sub(r'[?？，,_ ]', '', gotype)
    if gotype == "世界boss":
        shijieflag = 1
    elif gotype == "boss战":
        shijieflag = 0
    else:
        await bot.finish(ev, '请选择正确的boss战类型（世界boss/boss战）', at_sender=True)
    shuchu_list = CE._get_shuchu_pm(gid, shijieflag)

    if shuchu_list == 0:
        await bot.finish(ev, f'本群没有{gotype}的出刀记录哦', at_sender=True)
    tas_list = []
    if shijieflag == 1:
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content": f"为保护个人隐私，世界boss只显示本群数据"
            }
        }
        tas_list.append(data)
    user_card_dict = await get_user_card_dict(bot, ev.group_id)
    for shuchu in shuchu_list:
        print(shuchu)
        u_n = user_card_dict.get(shuchu[0])
        if not u_n:
            u_n = '未知角色'
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content": f"{u_n}总共造成了{shuchu[1]}点伤害"
            }
        }
        tas_list.append(data)
    await bot.send_group_forward_msg(group_id=gid, messages=tas_list)


@sv.on_prefix(['群排名', '会战群排名'])
async def paiming_list(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    CE = CECounter()
    if len(args) != 1:
        leibie = '本月'
    else:
        leibie = args[0]
    if leibie == "本月":
        nowyear = datetime.now().year
        nowmonth = datetime.now().month
        period = str(nowyear) + str(nowmonth)
    elif leibie == "上月":
        nowyear = datetime.now().year
        nowmonth = datetime.now().month
        if nowmonth == 1:
            nowyear = nowyear - 1
            nowmonth = 12
        else:
            nowyear = nowyear
            nowmonth = nowmonth - 1
        period = str(nowyear) + str(nowmonth)
    else:
        await bot.finish(ev, '请选择正确的时间(本月/上月)', at_sender=True)

    shuchu_list = CE._get_shuchu_pmq(period)
    if not shuchu_list[0][0]:
        await bot.finish(ev, f'无法获取到{leibie}的数据', at_sender=True)
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

    tas_list = []
    msg_s = ''
    mingc_s = 1
    for info in grouplist_s:
        if info[0] == gid:
            groupid = info[0]
            msg_s_q = f"本群{leibie}总积分{info[1]},排名第{mingc_s}名\n"
        else:
            groupid = str(info[0])
            groupid = str(groupid[:3]) + '****' + str(groupid[-3:])
        msg_s = msg_s + f"群号：{groupid}，总积分：{info[1]},名次：{mingc_s}\n"
        mingc_s = mingc_s + 1

    msg_b = ''
    mingc_b = 1
    for info in grouplist_b:
        if info[0] == gid:
            groupid = info[0]
            msg_s_b = f"本群{leibie}总积分{info[1]},排名第{mingc_b}名\n"
        else:
            groupid = str(info[0])
            groupid = str(groupid[:3]) + '****' + str(groupid[-3:])
        msg_b = msg_b + f"群号：{groupid}，总积分：{info[1]},名次：{mingc_b}\n"
        mingc_b = mingc_b + 1

    data = {
        "type": "node",
        "data": {
            "name": "ご主人様",
            "uin": "1587640710",
            "content": f"{msg_s_b}{leibie}boss战群排行榜\n{msg_b}"
        }
    }
    tas_list.append(data)

    data = {
        "type": "node",
        "data": {
            "name": "ご主人様",
            "uin": "1587640710",
            "content": f"{msg_s_q}{leibie}世界boss群排行榜\n{msg_s}"
        }
    }
    tas_list.append(data)
    await bot.send_group_forward_msg(group_id=gid, messages=tas_list)
