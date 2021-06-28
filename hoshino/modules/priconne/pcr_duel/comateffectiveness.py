import asyncio
import base64
import os
import random
import sqlite3
import math
import re
import pytz
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image
from . import sv
from decimal import Decimal
from hoshino import Service, priv
from hoshino.modules.priconne import _pcr_data
from hoshino.modules.priconne.pcr_duel import duel_chara as chara
from hoshino.typing import CQEvent
from hoshino.util import DailyNumberLimiter
import copy
import json
import nonebot
from nonebot import on_command, on_request
from hoshino import sucmd
from nonebot import get_bot
from hoshino.typing import NoticeSession
import time
from .CECounter import *
from .ScoreCounter import *
from .DuelCounter import *
from .duelconfig import *

@sv.on_fullmatch(['战斗系统帮助','战斗帮助'])
async def gift_help(bot, ev: CQEvent):
    msg='''
╔                                        ╗  
             战斗系统帮助
1. 绑定女友 +角色名 (绑定xx女友作为决斗伴侣，会获取经验值升级)
2. 我的女友 +角色名 (查看女友战力等信息)
3. 查看绑定/查看战斗女友
4. rank等级表/rank表 (查看rank等级提升需求)
5. 升级rank/rank升级/提升rank +角色名 (升级女友的rank)
6. 角色转生 +女友名(女友进行转生，等级、rank清零，基础战力加成提升，升级所需经验提升)
7. 创建队伍+女友名(最多5名，用空格隔开)+队名+队伍名称 (保存队伍)
8. 解散队伍+队伍名
9. 我的队伍(查询我的队伍情况)
10. 挂机修炼+女友名
11. 结束修炼
12. 我的经验池
13. 分配经验+女友名+经验值
注:
战力计算器：
    基础战力 = 100 + 等级*(50+转生等级*50)*(1+星级!/10) + 好感度*0.4 + 时装加成战力
    女友战力 = 基础战力*(1+rank/8)
    最大rank等级为12级，达到r12可以增幅2.5倍战力
╚                                        ╝
 '''
    await bot.send(ev, msg)

@sv.on_prefix(['绑定女友'])
async def card_bangdin(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    if not args:
        await bot.send(ev, '请输入绑定女友+pcr角色名。', at_sender=True)
        return
    name = args[0]
    cid = chara.name2id(name)
    if cid == 1000:
        await bot.send(ev, '请输入正确的pcr角色名。', at_sender=True)
        return
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    CE = CECounter()
    c = chara.fromid(cid)
    nvmes = get_nv_icon(cid)
    
    owner = duel._get_card_owner(gid, cid)
    if owner == 0:
        await bot.send(ev, f'{c.name}现在还是单身哦，快去约到她吧。{nvmes}', at_sender=True)
        return
    if uid!=owner:
        msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法绑定哦。'
        await bot.send(ev, msg)
        return
    
    if uid==owner:
        up_info = duel._get_fashionup(gid,uid,cid,0)
        if up_info:  
            fashion_info = get_fashion_info(up_info)
            nvmes = fashion_info['icon']
        CE._add_guaji(gid,uid,cid)
        msg = f"女友{c.name}绑定成功\n之后决斗胜利后{c.name}可以获得经验值哦\n{nvmes}"
    await bot.send(ev, msg, at_sender=True)

@sv.on_fullmatch(['查看绑定','查看战斗女友'])
async def get_bangdin(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    duel = DuelCounter()
    cid = CE._get_guaji(gid,uid)
    if cid==0:
        msg = '您尚未绑定任何角色参与战斗。'
        await bot.finish(ev, msg)
    owner = duel._get_card_owner(gid, cid)
    c = chara.fromid(cid)
    if uid!=owner:
        msg = f'您绑定了：{c.name}，但她已不在您身边，请重新绑定您的女友。'
        await bot.finish(ev, msg)
    nvmes = get_nv_icon(cid)
    msg = f"您当前绑定的女友是：{c.name}，每位贵族只能绑定一位女友参与战斗哦~\n{nvmes}"
    await bot.send(ev, msg, at_sender=True)

@sv.on_fullmatch(['女友rank等级表','rank表','rank等级表'])
async def rank_list(bot, ev: CQEvent):
    msg = '女友rank等级需求表：\n'
    rank = 1
    while (rank <= 12):
        rankInfo = RANK_LIST[rank]
        if rank>10:
            levelrank = 10
        else:
            levelrank = rank
        noblename = get_noblename(levelrank)
        ce_up = 1+rank/8
        
        if rank<=4:
            needmodel = 'N'
            needlevel = 1
        elif rank>4 and rank<=8:
            needmodel = 'R'
            needlevel = 2
        elif rank>8 and rank<=11:
            needmodel = 'SR'
            needlevel = 3
        else:
            needmodel = 'SSR'
            needlevel = 4
        msg += f'"R{rank}": 需求贵族等级≥{noblename}，消耗{rankInfo}金币，身上穿戴的4件{needmodel}品质及以上装备，女友战力提升为{ce_up}倍\n'
        rank = rank + 1
    await bot.send(ev, msg)

@sv.on_prefix(['升级rank','rank升级','提升rank'])
async def up_rank(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    CE = CECounter()
    if len(args)!=1:
        await bot.finish(ev, '请输入 rank升级+女友名 中间用空格隔开。', at_sender=True)
    name = args[0]
    cid = chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的女友名。', at_sender=True)
    cidlist = duel._get_cards(gid, uid)
    if cid not in cidlist:
        await bot.finish(ev, '该女友不在你的身边哦。', at_sender=True)
    rank = CE._get_rank(gid,uid,cid)
    if rank==MAX_RANK:
        await bot.finish(ev, '该女友rank已升至满级，无法继续升级啦。', at_sender=True)
    new_rank = rank + 1
    level = duel._get_level(gid,uid)
    if new_rank>10:
        levelrank = 10
    else:
        levelrank = new_rank
    if levelrank>level:
        await bot.finish(ev, '您的贵族等级不足，请发送[升级贵族]提升您的等级吧。', at_sender=True)
    rank_score = RANK_LIST[int(new_rank)]
    score_counter = ScoreCounter2()
    myscore = score_counter._get_score(gid,uid)
    if myscore < rank_score:
        await bot.finish(ev, f'升级rank所需金币不足！\n由{rank}级升至{new_rank}级需要：{rank_score}个，您当前剩余：{myscore}个',at_sender=True)
    
    #获取角色穿戴装备列表
    dreeslist = CE._get_dress_list(gid, uid, cid)
    if dreeslist:
        dreesnum = len(dreeslist)
    else:
        dreesnum = 0
    
    if dreesnum<4:
        await bot.finish(ev, f'升级rank所需需要穿戴4件装备哦！您当前穿戴的装备数量为：{dreesnum}件',at_sender=True)
    islevelok = 1
    lastrank = rank+1
    if lastrank<=4:
        needmodel = 'N'
        needlevel = 1
    elif lastrank>4 and lastrank<=8:
        needmodel = 'R'
        needlevel = 2
    elif lastrank>8 and lastrank<=11:
        needmodel = 'SR'
        needlevel = 3
    else:
        needmodel = 'SSR'
        needlevel = 4
    for eid in dreeslist:
        equipinfo = get_equip_info_id(eid)
        if equipinfo:
            if equipinfo['level']<needlevel:
                islevelok = 0
                break
    if islevelok==0:
        await bot.finish(ev, f'升级rank所需需要穿戴4件{needmodel}品质的装备哦！您未达到要求哦',at_sender=True)
    
    for eid in dreeslist:
        equipinfo = get_equip_info_id(eid)
        if equipinfo and equipinfo['type_id']!=99:
            CE._dress_equip(gid, uid, cid, equipinfo['type_id'], 0)
            CE._add_equip(gid, uid, equipinfo['eid'], 1)
    equip_list = CE._get_equip_list(gid, uid)
    lowest = [99, 99, 99, 99]
    removelist = [[0,''],[0,''],[0,''],[0,'']]
    for i in equip_list:
        equipinfo = get_equip_info_id(i[0])
        if equipinfo['type_id'] == 1 and equipinfo['level'] >= needlevel and equipinfo['level'] < lowest[0]:
            removelist[0][0] = equipinfo['eid']
            removelist[0][1] = equipinfo['model']
            removelist[0][1] += equipinfo['name']
            lowest[0] = equipinfo['level']
            #print(f'准备移除1号{removelist[0][0]}{removelist[0][1]}')
            continue
        if equipinfo['type_id'] == 2 and equipinfo['level'] >= needlevel and equipinfo['level'] < lowest[1]:
            removelist[1][0] = equipinfo['eid']
            removelist[1][1] = equipinfo['model']
            removelist[1][1] += equipinfo['name']
            lowest[1] = equipinfo['level']
            #print(f'准备移除2号{removelist[1][0]}{removelist[1][1]}')
            continue
        if equipinfo['type_id'] == 3 and equipinfo['level'] >= needlevel and equipinfo['level'] < lowest[2]:
            removelist[2][0] = equipinfo['eid']
            removelist[2][1] = equipinfo['model']
            removelist[2][1] += equipinfo['name']
            lowest[2] = equipinfo['level']
            #print(f'准备移除3号{removelist[2][0]}{removelist[2][1]}')
            continue
        if equipinfo['type_id'] == 4 and equipinfo['level'] >= needlevel and equipinfo['level'] < lowest[3]:
            removelist[3][0] = equipinfo['eid']
            removelist[3][1] = equipinfo['model']
            removelist[3][1] += equipinfo['name']
            lowest[3] = equipinfo['level']
            #print(f'准备移除4号{removelist[3][0]}{removelist[3][1]}')
            continue
    part_msg = '\n自动为您消耗了女友身上或装备仓库中，满足升rank条件的较差装备：\n'
    for i in removelist:
        part_msg += f'{i[1]} '
        CE._add_equip(gid, uid, i[0], -1)
    
    for eid in dreeslist:
        equipinfo = get_equip_info_id(eid)
        if equipinfo:
            if CE._get_equip_num(gid,uid,equipinfo['eid'])>0 and equipinfo['type_id']!=99:
                CE._dress_equip(gid, uid, cid, equipinfo['type_id'], eid)
                CE._add_equip(gid, uid, equipinfo['eid'], -1)
    
    
    score_counter._reduce_score(gid, uid, rank_score)
    CE._up_rank(gid,uid,cid)
    c = chara.fromid(cid)
    msg = f'{part_msg}\n您花费了{rank_score}金币为{c.name}提升了rank，当前rank等级为：{new_rank}级，女友战斗力大大提升！'
    await bot.send(ev, msg, at_sender=True)

@sv.on_fullmatch(['战力榜','女友战力榜','战力排行榜'])
async def girl_power_rank(bot, ev: CQEvent):
    ranking_list = get_power_rank(ev.group_id)
    gid = ev.group_id
    CE = CECounter()
    msg = '本群女友战力排行榜(仅展示rank>0的)：\n'
    if len(ranking_list)>0:
        rank = 1
        for girl in ranking_list:
            if rank<=15:
                user_card_dict = await get_user_card_dict(bot, ev.group_id)
                rank1,power,uid,cid = girl
                user_card = uid2card(uid, user_card_dict)
                c = chara.fromid(cid)
                dengji = CE._get_card_level(gid, uid, cid)
                zhuansheng = CE._get_zhuansheng(gid, uid, cid)
                msg += f'第{rank}名: {user_card}的 {c.name}({dengji}级，{zhuansheng}转，rank{rank1})，战斗力{power}点\n'
            rank = rank+1
    else:
        msg += '暂无女友上榜'
    await bot.send(ev, msg)
    
@sv.on_fullmatch(['副本系统帮助','副本帮助','装备帮助'])
async def dun_help(bot, ev: CQEvent):
    msg='''
╔                                        ╗  
             副本系统帮助
1. 编队+女友名(最多5名，用空格隔开)进入副本+副本名称
2. 装备列表（查询我未穿戴的装备列表）
3. 穿装备+女友名+装备名
4. 取消装备+女友名+装备名
5. 副本列表
注:
通过副本战斗可以活动角色经验，好感度，礼物与装备产出
升级角色等级，装备装备可以提升角色战力
╚                                        ╝
 '''  
    await bot.send(ev, msg)  

@sv.on_fullmatch(['副本列表','查看副本'])
async def dungeon_list(bot, ev: CQEvent):
    dungeonlist={}
    with open(os.path.join(FILE_PATH,'dungeon.json'),'r',encoding='UTF-8') as fa:
        dungeonlist = json.load(fa, strict=False)  
    tas_list = []
    for dungeon in dungeonlist:
        msg = ''
        msg = msg + f"\n副本名  ：{dungeonlist[dungeon]['name']}"
        msg = msg + f"\n推荐战力：\n[简单]{dungeonlist[dungeon]['recommend_ce']}\n[困难]{dungeonlist[dungeon]['recommend_ce']*10}\n[地狱]{dungeonlist[dungeon]['recommend_ce']*20}"
        msg = msg + f"\n战胜获得经验：\n[简单]{dungeonlist[dungeon]['add_exp']}\n[困难]{dungeonlist[dungeon]['add_exp']*3} \n[地狱]{dungeonlist[dungeon]['add_exp']*5}"
        msg = msg + f"\n战胜获得碎片：\n[简单]{dungeonlist[dungeon]['fragment_w']}万能碎片，{dungeonlist[dungeon]['fragment_c']}随机碎片\n[困难]{dungeonlist[dungeon]['fragment_w']*3}万能碎片，{dungeonlist[dungeon]['fragment_c']*3}随机碎片\n[地狱]{dungeonlist[dungeon]['fragment_w']*5}万能碎片，{dungeonlist[dungeon]['fragment_c']*5}随机碎片"
        msg = msg + f"\n战胜获得好感：{dungeonlist[dungeon]['add_favor']}"
        msg = msg + f"\n副本描述：{dungeonlist[dungeon]['content']}，不同难度掉率不同"
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content": msg
                    }
                }
        tas_list.append(data)
    #await bot.send(ev, msg)
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)

@sv.on_rex(f'^编队(.*)进入(.*)副本(.*)$')
async def add_duiwu_t(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    CE = CECounter()
    # 处理输入数据
    match = ev['match']
    if match.group(2):
        dun_nd = str(match.group(2)).strip()
    else:
        dun_nd='简单'

    if dun_nd=='简单':
        dun_model=1
        sp_d=1
        e_d=1
        nd_t=1
    elif dun_nd=='困难':
        dun_model=2
        sp_d=3
        e_d=1.3
        nd_t=10
    elif dun_nd=='地狱':
        dun_model=3
        sp_d=5
        e_d=1.7
        nd_t=20
    else:
        await bot.finish(ev, '请输入正确的副本难度(简单/困难/地狱)', at_sender=True)
    dunname = str(match.group(3)).strip()
    dunname = re.sub(r'[?？，,_ ]', '', dunname)
    defen = str(match.group(1)).strip()
    defen = re.sub(r'[?？，,_]', '', defen)
    #await bot.finish(ev, f'进入{dun_nd}副本', at_sender=True)
    if not defen:
        await bot.finish(ev, '请发送"编队+女友名/队伍名+进入(简单/困难/地狱)副本+副本名"，无需+号', at_sender=True)
    #查询是否是队伍
    teamlist = CE._get_teamlist(gid, uid, defen)
    if teamlist!=0:
        defen = []
        for i in teamlist:
            cid = i[0]
            defen.append(cid)
    else:
        defen, unknown = chara.roster.parse_team(defen)
        cidlist = duel._get_cards(gid, uid)
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
    z_ce=0
    bianzu=''
    dungeoninfo=get_dun_info(dunname)
    print(dungeoninfo)
    if dungeoninfo:
        #获取编队战力与信息
        charalist = []
        for cid in defen:
            c = chara.fromid(cid)
            nvmes = get_nv_icon(cid)
            owner = duel._get_card_owner(gid, cid)
            if owner == 0:
                await bot.send(ev, f'{c.name}现在还是单身哦，快去约到她吧。{nvmes}', at_sender=True)
                return
            if uid!=owner:
                msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法编队哦。'
                await bot.send(ev, msg)
                return
            card_ce=get_card_ce(gid,uid,cid)
            z_ce=z_ce+card_ce
            if cid == 9999:
                cid = 1059
            star = CE._get_cardstar(gid,uid,cid)
            charalist.append(chara.Chara(cid, star, 0))
            bianzu=bianzu+f"{c.name} "
        #获取进入副本信息
        #判定每日上限
        guid = gid ,uid
        if not daily_dun_limiter.check(guid):
            await bot.send(ev, '今天的副本次数已经超过上限了哦，明天再来吧。', at_sender=True)
            return
        daily_dun_limiter.increase(guid)
        recommend_ce = dungeoninfo['recommend_ce']*nd_t
        is_win = Decimal(z_ce/recommend_ce).quantize(Decimal('0.00'))*100
        if is_win>100:
            is_win=100
        res = chara.gen_team_pic(charalist, star_slot_verbose=False)
        bio = BytesIO()
        res.save(bio, format='PNG')
        base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
        mes = f"[CQ:image,file={base64_str}]"
        msg1=f"编组成功{bianzu}\n开始进入{dun_nd}副本{dunname}\n当前副本推荐战力{recommend_ce}，您的编组战力为{z_ce}，您的胜率为{is_win}%，开始战斗{mes}"
        tas_list = []
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content":msg1
                    }
                }
        tas_list.append(data)
        #await bot.send(ev, msg1, at_sender=True)
        #await asyncio.sleep(3)
        if_win = int(math.floor( random.uniform(1,100) ))
        #战斗胜利
        if if_win<=is_win:
            msg = "战斗胜利了！\n"
            for cid in defen:
                get_exp = dungeoninfo['add_exp'] * sp_d
                duel._add_favor(gid,uid,cid,dungeoninfo['add_favor'])
                card_level=add_exp(gid,uid,cid,get_exp)
            msg = msg + f"您的女友{bianzu}获得了{get_exp}点经验，{dungeoninfo['add_favor']}点好感\n"
            #增加副本币
            get_dun_score = dungeoninfo['dun_score']*sp_d
            CE._add_dunscore(gid, uid, get_dun_score)
            msg = msg + f"您获得了{get_dun_score}副本币\n"
            
            #增加角色碎片
            #万能碎片
            get_fragment_w = dungeoninfo['fragment_w'] * sp_d
            CE._add_fragment_num(gid, uid, 0, get_fragment_w)
            msg = msg + f"您获得了{get_fragment_w}万能碎片\n"
            fragment_s = dungeoninfo['fragment_c'] * sp_d
            cidlist = defen
            while fragment_s>0:
                if len(cidlist)>1:
                    fragment_run = int(math.floor( random.uniform(1,fragment_s) ))
                else:
                    fragment_run = fragment_s
                addcid = random.sample(cidlist,1)
                c = chara.fromid(addcid[0])
                msg = msg + f"您获得了{fragment_run}{c.name}碎片\n"
                cidlist.remove(addcid[0])
                CE._add_fragment_num(gid, uid, addcid[0], fragment_run)
                fragment_s = fragment_s - fragment_run
            
            msg = msg + "您获得的战利品为：\n"
            favor_ran = int(math.floor( random.uniform(1,100)*e_d ))
            if favor_ran>100:
                favor_ran=100
            z_favor = 0
            dun_get_favor = 0
            for favor_num in dungeoninfo['drop']['favor']:
                z_favor = z_favor + dungeoninfo['drop']['favor'][favor_num]
                if z_favor>=favor_ran:
                    dun_get_favor = int(favor_num)
                    break
            gift_list = ''
            for x in range(dun_get_favor):
                select_gift = random.choice(list(GIFT_DICT.keys()))
                gfid = GIFT_DICT[select_gift]
                duel._add_gift(gid,uid,gfid)
                gift_list = gift_list + f"[{select_gift}] "
            msg = msg + f'获得了礼物:{gift_list}\n'
            
            equip_ran = int(math.floor( random.uniform(1,100)*e_d ))
            if equip_ran>100:
                equip_ran=100
            z_equip = 0
            dun_get_equip = 0
            for equip_num in dungeoninfo['drop']['equipment']['num']:
                z_equip = z_equip + dungeoninfo['drop']['equipment']['num'][equip_num]
                if z_equip>=equip_ran:
                    dun_get_equip = int(equip_num)
                    break
            equip_list = ''
            if dun_model>1:
                max_equip_quality = 0
                for equip_num_quality in dungeoninfo['drop']['equipment']['quality']:
                    if int(equip_num_quality)>max_equip_quality:
                        max_equip_quality = int(equip_num_quality)            
            if dun_get_equip>0:
                for y in range(dun_get_equip):
                    equip_type_run = int(math.floor( random.uniform(1,100)*e_d ))
                    if equip_type_run>100:
                        equip_type_run=100
                    get_equip_quality = 1
                    z_equip_quality = 0
                    for equip_num_quality in dungeoninfo['drop']['equipment']['quality']:
                        z_equip_quality = z_equip_quality + dungeoninfo['drop']['equipment']['quality'][equip_num_quality]
                        if z_equip_quality>=equip_type_run:
                            get_equip_quality = int(equip_num_quality)
                            break
                    if dun_model>1:
                        down_num_run = 40*(dun_model-1)
                        down_up_run = int(math.floor( random.uniform(1,100) ))
                        if down_num_run>=down_up_run:
                            down_up_flag = 1
                        else:
                            down_up_flag = 0
                        if down_up_flag==1:
                            get_equip_quality = get_equip_quality+1
                            if get_equip_quality>max_equip_quality:
                                get_equip_quality = max_equip_quality
                    down_list=[]
                    for equip_down in dungeoninfo['drop']['equipment']['equip']:
                        
                        if int(get_equip_quality) == int(equip_down):
                            down_list = dungeoninfo['drop']['equipment']['equip'][equip_down]
                    #随机获得一个品质的装备
                    equip_info = add_equip_info(gid,uid,get_equip_quality,down_list)
                    #print(equip_info)
                    equip_list = equip_list + f"{equip_info['model']}品质{equip_info['type']}:{equip_info['name']}\n"
            if equip_list:
                msg = msg + f"获得了装备:\n{equip_list}"
            data = {
                "type": "node",
                "data": {
                    "name": "ご主人様",
                    "uin": "1587640710",
                    "content":msg
                        }
                    }
            tas_list.append(data)
            await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)
            #await bot.send(ev, msg, at_sender=True)
        else:
            msg = ''
            msg = msg + "您战斗失败了，副本次数-1"
            for cid in defen:
                #duel._add_favor(gid,uid,cid,dungeoninfo['add_favor'])
                card_level=add_exp(gid,uid,cid,dungeoninfo['add_exp'])
            msg = msg + f"您的女友{bianzu}获得了{dungeoninfo['add_exp']}点经验\n"
            data = {
                "type": "node",
                "data": {
                    "name": "ご主人様",
                    "uin": "1587640710",
                    "content":msg
                        }
                    }
            tas_list.append(data)
            await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)
            #await bot.send(ev, "您战斗失败了，副本次数-1", at_sender=True)
            #return
    else:
        await bot.finish(ev, '请输入正确的副本名称', at_sender=True)
        return

@sv.on_prefix(['取消装备'])
async def dress_equip(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()  
    if len(args)!=2:
        await bot.finish(ev, '请输入 取消装备+女友名+装备名 中间用空格隔开。', at_sender=True)
    name = args[0]
    cid = chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的女友名。', at_sender=True)
    cidlist = duel._get_cards(gid, uid) 
    if cid not in cidlist:
        await bot.finish(ev, '该女友不在你的身边哦。', at_sender=True)    
    equipname = args[1]
    equipinfo = get_equip_info_name(equipname)
    if len(equipinfo)>0:
        c = chara.fromid(cid)
        CE = CECounter()
        now_dress = CE._get_dress_info(gid, uid, cid, equipinfo['type_id'])
        if now_dress>0:
            if now_dress == equipinfo['eid']:
                now_equipinfo = get_equip_info_id(now_dress)
                #保存数据库
                CE._dress_equip(gid, uid, cid, equipinfo['type_id'], 0)
                #可用装备加一
                CE._add_equip(gid, uid, equipinfo['eid'], 1)

                msg_x = f"取消了{equipinfo['type']}部位的装备{equipinfo['name']}"
                nvmes = get_nv_icon(cid)
                msg = f"您为您的女友{c.name}，{msg_x}\n{nvmes}"
                await bot.send(ev, msg, at_sender=True)   
            else:
                msg = f"您的女友{c.name}，当前{equipinfo['type']}部位穿戴的装备是{now_equipinfo['name']}，不是{equipinfo['name']}哦！"
                await bot.finish(ev, msg, at_sender=True)
        else:
            await bot.finish(ev, f"您的女友{c.name}当前{equipinfo['type']}部位未穿戴装备哦。", at_sender=True)
    else:
        await bot.finish(ev, '请输入正确的装备名。', at_sender=True)

@sv.on_prefix(['穿装备','穿戴装备'])
async def dress_equip(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()  
    CE = CECounter()
    if len(args)!=2:
        await bot.finish(ev, '请输入 穿装备+女友名+装备名 中间用空格隔开。', at_sender=True)
    name = args[0]
    cid = chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的女友名。', at_sender=True)
    cidlist = duel._get_cards(gid, uid) 
    if cid not in cidlist:
        await bot.finish(ev, '该女友不在你的身边哦。', at_sender=True)    
    equipname = args[1]
    equipinfo = get_equip_info_name(equipname)
    if len(equipinfo)>0:
        if equipinfo['type_id']==99:
            zllevel = CE._get_zhuansheng(gid,uid,cid)
            if zllevel==0:
                await bot.finish(ev, '戒指需要角色转生后才能装备哦。', at_sender=True)    
        c = chara.fromid(cid)
        if CE._get_equip_num(gid,uid,equipinfo['eid'])==0:
            await bot.finish(ev, '你的这件装备的库存不足哦。', at_sender=True)
        #获取当前穿戴的装备
        now_dress = CE._get_dress_info(gid, uid, cid, equipinfo['type_id'])
        #保存数据库
        CE._dress_equip(gid, uid, cid, equipinfo['type_id'], equipinfo['eid'])
        #可用装备减一
        CE._add_equip(gid, uid, equipinfo['eid'], -1)
        if now_dress>0:
            now_equipinfo = get_equip_info_id(now_dress)
            #替换的装备数量增加
            CE._add_equip(gid, uid, now_dress, 1)
            msg_x = f"取消了{equipinfo['type']}部位的装备{now_equipinfo['name']}，穿上了装备{equipinfo['name']}"
        else:
            msg_x = f"穿上了{equipinfo['type']}部位的装备{equipinfo['name']}"
        nvmes = get_nv_icon(cid)
        msg = f"您为您的女友{c.name}，{msg_x}\n{nvmes}"
        await bot.send(ev, msg, at_sender=True)    
    else:
        await bot.finish(ev, '请输入正确的装备名。', at_sender=True)

@sv.on_fullmatch(['装备列表','我的装备'])
async def my_equip_list(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter() 
    CE = CECounter()
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅。'
        await bot.send(ev, msg, at_sender=True)
        return
    equip_list = CE._get_equip_list(gid, uid)
    if len(equip_list)>0:
        msg_list = '我的装备列表：'
        for i in equip_list:
            equipinfo=get_equip_info_id(i[0])
            msg_list = msg_list + f"\n{equipinfo['icon']}{equipinfo['type']}:({equipinfo['model']}){equipinfo['name']}:{i[1]}件"
        await bot.send(ev, msg_list, at_sender=True)
    else:
        await bot.finish(ev, '您还没有获得装备哦。', at_sender=True)

@sv.on_prefix(['一键卸装','一键取消'])
async def quxiao_equip(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    CE = CECounter()
    if len(args)!=1:
        await bot.finish(ev, '请输入 一件穿戴+女友名 中间用空格隔开。', at_sender=True)
    name = args[0]
    cid = chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的女友名。', at_sender=True)
    cidlist = duel._get_cards(gid, uid)
    if cid not in cidlist:
        await bot.finish(ev, '该女友不在你的身边哦。', at_sender=True)
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅。'
        await bot.finish(ev, msg, at_sender=True)
    c = chara.fromid(cid)
    nvmes = get_nv_icon(cid)
    dreeslist = CE._get_dress_list(gid, uid, cid)
    if len(dreeslist)>0:
        msg = ''
        for eid in dreeslist:
            equipinfo = get_equip_info_id(eid)
            if equipinfo:
                #保存数据库
                CE._dress_equip(gid, uid, cid, equipinfo['type_id'], 0)
                #替换的装备数量增加
                CE._add_equip(gid, uid, equipinfo['eid'], 1)
                msg = msg + f"取消了{equipinfo['type']}部位的装备({equipinfo['model']}){equipinfo['name']}\n"
        await bot.send(ev, f"您为您的女友{c.name}\n{msg}{nvmes}", at_sender=True)
    else:
        await bot.finish(ev, f"您的女友{c.name}目前没有穿戴的装备哦\n{nvmes}", at_sender=True)

@sv.on_prefix(['一键穿戴'])
async def dress_equip_list(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    CE = CECounter()
    if len(args)!=1:
        await bot.finish(ev, '请输入 一件穿戴+女友名 中间用空格隔开。', at_sender=True)
    name = args[0]
    cid = chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的女友名。', at_sender=True)
    cidlist = duel._get_cards(gid, uid)
    if cid not in cidlist:
        await bot.finish(ev, '该女友不在你的身边哦。', at_sender=True)
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅。'
        await bot.send(ev, msg, at_sender=True)
        return
    zllevel = CE._get_zhuansheng(gid,uid,cid)
    equip_list = CE._get_equip_list(gid, uid)
    #记录不同部位的品质最高装备的品质和eid
    emax = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
    tsequipflag = 0
    if len(equip_list)>0:
        msg_list = '我的装备列表：'
        for i in equip_list:
            equipinfo=get_equip_info_id(i[0])
            if equipinfo['type_id'] == 1 and equipinfo['level'] > emax[0][0] and equipinfo['add_ce'] > emax[0][2]:
                emax[0] = [equipinfo['level'],i[0],equipinfo['add_ce']]
            if equipinfo['type_id'] == 2 and equipinfo['level'] > emax[1][0] and equipinfo['add_ce'] > emax[1][2]:
                emax[1] = [equipinfo['level'],i[0],equipinfo['add_ce']]
            if equipinfo['type_id'] == 3 and equipinfo['level'] > emax[2][0] and equipinfo['add_ce'] > emax[2][2]:
                emax[2] = [equipinfo['level'],i[0],equipinfo['add_ce']]
            if equipinfo['type_id'] == 4 and equipinfo['level'] > emax[3][0] and equipinfo['add_ce'] > emax[3][2]:
                emax[3] = [equipinfo['level'],i[0],equipinfo['add_ce']]
            if zllevel>0 and equipinfo['type_id'] == 99 and equipinfo['level'] > emax[3][0] and equipinfo['add_ce'] > emax[3][2]:
                emax[4] = [equipinfo['level'],i[0],equipinfo['add_ce']]
                
    else:
        await bot.finish(ev, '您还没有获得装备哦。', at_sender=True)
    c = chara.fromid(cid)
    nvmes = get_nv_icon(cid)
    msg = ''
    for y in emax:
        if y[1] > 0:
            #获取当前穿戴的装备
            equipinfo = get_equip_info_id(y[1])
            now_dress = CE._get_dress_info(gid, uid, cid, equipinfo['type_id'])
            if now_dress>0:
                now_equipinfo = get_equip_info_id(now_dress)
                if now_equipinfo['level'] < y[0] or now_equipinfo['add_ce'] < y[2]:
                    #保存数据库
                    CE._dress_equip(gid, uid, cid, equipinfo['type_id'], equipinfo['eid'])
                    #可用装备减一
                    CE._add_equip(gid, uid, equipinfo['eid'], -1)
                    #替换的装备数量增加
                    CE._add_equip(gid, uid, now_dress, 1)
                    msg = msg + f"取消了{equipinfo['type']}部位的装备({now_equipinfo['model']}){now_equipinfo['name']}，穿上了装备({equipinfo['model']}){equipinfo['name']}\n"
                else:
                    msg = msg + f"{equipinfo['type']}部位已穿戴同等或更高等级的装备({now_equipinfo['model']}){now_equipinfo['name']}，无替换\n"
            else:
                #保存数据库
                CE._dress_equip(gid, uid, cid, equipinfo['type_id'], equipinfo['eid'])
                #可用装备减一
                CE._add_equip(gid, uid, equipinfo['eid'], -1)
                msg = msg + f"穿上了{equipinfo['type']}部位的装备({equipinfo['model']}){equipinfo['name']}\n"
    await bot.send(ev, f"您为您的女友{c.name}\n{msg}{nvmes}", at_sender=True)


@sv.on_prefix(['一键装备'])
async def dress_equip_list_r(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    CE = CECounter()
    if len(args)!=1:
        await bot.finish(ev, '请输入 一件穿戴+女友名 中间用空格隔开。', at_sender=True)
    name = args[0]
    cid = chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的女友名。', at_sender=True)
    cidlist = duel._get_cards(gid, uid)
    if cid not in cidlist:
        await bot.finish(ev, '该女友不在你的身边哦。', at_sender=True)
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅。'
        await bot.send(ev, msg, at_sender=True)
        return
    rank = CE._get_rank(gid, uid, cid)
    lastrank = rank+1
    if lastrank<=4:
        needmodel = 'N'
        needlevel = 1
    elif lastrank>4 and lastrank<8:
        needmodel = 'R'
        needlevel = 2
    else:
        needmodel = 'SR'
        needlevel = 3
    equip_list = CE._get_equip_list(gid, uid)
    #记录不同部位的品质最高装备的品质和eid
    emax = [[0,0],[0,0],[0,0],[0,0]]
    if len(equip_list)>0:
        msg_list = '我的装备列表：'
        for i in equip_list:
            equipinfo=get_equip_info_id(i[0])
            if equipinfo['type_id'] == 1 and equipinfo['level'] <= needlevel and equipinfo['level'] > emax[0][0]:
                emax[0] = [equipinfo['level'],i[0]]
            if equipinfo['type_id'] == 2 and equipinfo['level'] <= needlevel and equipinfo['level'] > emax[1][0]:
                emax[1] = [equipinfo['level'],i[0]]
            if equipinfo['type_id'] == 3 and equipinfo['level'] <= needlevel and equipinfo['level'] > emax[2][0]:
                emax[2] = [equipinfo['level'],i[0]]
            if equipinfo['type_id'] == 4 and equipinfo['level'] <= needlevel and equipinfo['level'] > emax[3][0]:
                emax[3] = [equipinfo['level'],i[0]]
    else:
        await bot.finish(ev, '您还没有获得装备哦。', at_sender=True)
    c = chara.fromid(cid)
    nvmes = get_nv_icon(cid)
    msg = ''
    for y in emax:
        if y[1] > 0:
            #获取当前穿戴的装备
            equipinfo = get_equip_info_id(y[1])
            now_dress = CE._get_dress_info(gid, uid, cid, equipinfo['type_id'])
            if now_dress>0:
                now_equipinfo = get_equip_info_id(now_dress)
                if now_equipinfo['level'] < y[0]:
                    #保存数据库
                    CE._dress_equip(gid, uid, cid, equipinfo['type_id'], equipinfo['eid'])
                    #可用装备减一
                    CE._add_equip(gid, uid, equipinfo['eid'], -1)
                    #替换的装备数量增加
                    CE._add_equip(gid, uid, now_dress, 1)
                    msg = msg + f"取消了{equipinfo['type']}部位的装备({now_equipinfo['model']}){now_equipinfo['name']}，穿上了装备({equipinfo['model']}){equipinfo['name']}\n"
                else:
                    msg = msg + f"{equipinfo['type']}部位已穿戴同等或更高等级的装备({now_equipinfo['model']}){now_equipinfo['name']}，无替换\n"
            else:
                #保存数据库
                CE._dress_equip(gid, uid, cid, equipinfo['type_id'], equipinfo['eid'])
                #可用装备减一
                CE._add_equip(gid, uid, equipinfo['eid'], -1)
                msg = msg + f"穿上了{equipinfo['type']}部位的装备({equipinfo['model']}){equipinfo['name']}\n"
    await bot.send(ev, f"您为您的女友{c.name}\n{msg}{nvmes}", at_sender=True)

@sv.on_fullmatch(['副本商城'])
async def equip_shop(bot, ev: CQEvent):
    equiplist={}
    with open(os.path.join(FILE_PATH,'equipment.json'),'r',encoding='UTF-8') as fa:
        equiplist = json.load(fa, strict=False)  
    tas_list = []
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    myscore = CE._get_dunscore(gid, uid)
    msg_t = f"您的副本币为{myscore}，每日可以兑换装备5次"
    #合并转发： 
    data = {
        "type": "node",
        "data": {
            "name": "ご主人様",
            "uin": "1587640710",
            "content": msg_t
                }
            }
    tas_list.append(data)
    #await bot.send(ev, msg_t)
    for equip in equiplist:
        shul = 0
        msg = ''
        for eid in equiplist[equip]['e_list']:
            if equiplist[equip]['e_list'][eid]['dun_score'] > 0:
                shul += 1
                msg = msg + f"装备信息：[{equiplist[equip]['e_list'][eid]['type']}]{equiplist[equip]['e_list'][eid]['name']}\n装备品质：{equiplist[equip]['model']}\n售价(副本币)：{equiplist[equip]['e_list'][eid]['dun_score']}\n"
        if shul>0:
            #合并转发： 
            data = {
                "type": "node",
                "data": {
                    "name": "ご主人様",
                    "uin": "1587640710",
                    "content":msg
                        }
                    }
            tas_list.append(data)
            #await bot.send(ev, msg)
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)

@sv.on_prefix(['兑换装备'])
async def buy_equip(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    #判定每日上限
    guid = gid ,uid
    if not daily_equip_limiter.check(guid):
        await bot.send(ev, '今天的兑换次数已经超过上限了哦，明天再来吧。', at_sender=True)
        return
    if not args:
        await bot.send(ev, '请输入兑换装备+装备名称。', at_sender=True)
        return
    equipinfo = get_equip_info_name(args[0])
    if len(equipinfo)>0:
        if equipinfo['dun_score']>0:
            myscore = CE._get_dunscore(gid, uid)
            if myscore < equipinfo['dun_score']:
                await bot.finish(ev, f"您的副本币不足，兑换{equipinfo['name']}需要{equipinfo['dun_score']}哦。", at_sender=True)
            daily_equip_limiter.increase(guid)
            need_score = 0 - equipinfo['dun_score']
            last_score = myscore - equipinfo['dun_score']
            CE._add_dunscore(gid, uid, need_score)
            CE._add_equip(gid, uid, equipinfo['eid'], 1)
            msg = f"兑换装备({equipinfo['model']}){equipinfo['type']}:{equipinfo['name']}成功，消耗副本币{equipinfo['dun_score']}，您剩余副本币为{last_score}"
            await bot.send(ev, msg, at_sender=True) 
        else:
            await bot.finish(ev, '限购商品无法兑换哦。', at_sender=True)
    else:
        await bot.finish(ev, '请输入正确的装备名。', at_sender=True)
        
@sv.on_prefix(['购买物品'])
async def buy_gift(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter() 
    score_counter = ScoreCounter2()
    if not args:
        await bot.send(ev, '请输入购买物品+物品名称。', at_sender=True)
        return
    gift = args[0]
    if gift not in GIFT_DICT.keys():
        await bot.finish(ev, '请输入正确的礼物名。', at_sender=True)
    gfid = GIFT_DICT[gift]
    duel._add_gift(gid,uid,gfid)
    msg = f'\n您花费了30000金币，\n买到了[{gift}]哦，\n欢迎下次惠顾。'
    score_counter._reduce_score(gid,uid,30000)
    await bot.send(ev, msg, at_sender=True)
   
@sv.on_rex(f'^编队(.*)模拟(.*)$')
async def moni_huizhan(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    CE = CECounter()
    
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    if now.day == 1 and now.hour == 0: #每月1号结算
        await bot.finish(ev, '会战奖励结算中，禁止出刀', at_sender=True)
        return
    
    # 处理输入数据
    match = ev['match']
    gotype = str(match.group(2))
    gotype = re.sub(r'[?？，,_ ]', '', gotype)
    if gotype == "世界boss":
        sendgid = 999
        shijieflag = 1
    elif gotype == "boss战":
        sendgid = gid
        shijieflag = 0
    else:
        await bot.finish(ev, '请选择正确的boss战类型（世界boss/boss战）', at_sender=True)
    defen = str(match.group(1))
    defen = re.sub(r'[?？，,_]', '', defen)
    if not defen:
        await bot.finish(ev, '请发送"编队+女友名/队伍名+模拟+(boss战/世界boss)"，无需+号', at_sender=True)
    #查询是否是队伍
    teamlist = CE._get_teamlist(gid, uid, defen)
    if teamlist!=0:
        defen = []
        for i in teamlist:
            cid = i[0]
            defen.append(cid)
    else:
        defen, unknown = chara.roster.parse_team(defen)
        cidlist = duel._get_cards(gid, uid)
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
            return
        if uid!=owner:
            msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法编队哦。'
            await bot.finish(ev, msg)
            return
    z_ce=0
    bianzu=''
    #获取本群boss状态和血量
    bossinfo = get_boss_info(sendgid)
    if len(bossinfo)>0:
        #获取编队战力与信息
        charalist = []
        for cid in defen:
            c = chara.fromid(cid)
            card_ce=get_card_ce(gid,uid,cid)
            z_ce=z_ce+card_ce
            if cid == 9999:
                cid = 1059
            star = CE._get_cardstar(gid,uid,cid)
            charalist.append(chara.Chara(cid, star, 0))
            bianzu=bianzu+f"{c.name} "
        #
        res = chara.gen_team_pic(charalist, star_slot_verbose=False)
        bio = BytesIO()
        res.save(bio, format='PNG')
        base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
        mes = f"[CQ:image,file={base64_str}]"
        boss_ce = bossinfo['ce']
        msg1=f"[CQ:at,qq={uid}]编组成功{bianzu}\n{mes}\n开始模拟会战\n当前boss为：第{bossinfo['zhoumu']}周目{bossinfo['bossid']}号boss({bossinfo['name']})\nboss战力为{bossinfo['ce']}，当前血量为{bossinfo['hp']}\n您的编组战力为{z_ce}，开始模拟战斗\n{bossinfo['icon']}"
        tas_list = []
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content":msg1
                    }
                }
        tas_list.append(data)
        
        #计算造成的伤害
        #2者相加的总战力
        zhanlz = boss_ce + z_ce
        #计算总战力扩值
        kuo = zhanlz * zhanlz
        #计算总战力差值
        cha = (zhanlz/z_ce)
        #计算无战力压制因素的输出伤害
        shuchu = (kuo/boss_ce)/cha
        #计算战力压制因素印象可以造成的伤害比
        zhanbi = z_ce/zhanlz+1
        #计算输出浮动数+-10%
        fudong = int(math.floor( random.uniform(1,20) ))
        if fudong>10:
            fudong = fudong/200+1
        else:
            fudong = 1-fudong/100
        #计算最终输出伤害
        shanghai = math.ceil((shuchu * fudong)/zhanbi)
        msg = ''
        if shanghai>bossinfo['hp']:
            #计算健康状态
            card_jk = 100-math.ceil(bossinfo['hp']/shanghai*100)
            #计算下一个boss
            nextboss = bossinfo['bossid'] + 1
            nextzhoumu = bossinfo['zhoumu']
            if nextboss == 6:
                nextboss = 1
                nextzhoumu = bossinfo['zhoumu'] + 1
            nextbossinfo = get_nextbossinfo(nextzhoumu,nextboss,shijieflag)
            boss_msg = f"模拟击杀了boss\n下一个boss为：第{nextzhoumu}周目{nextboss}号boss({nextbossinfo['name']})"
            msg = msg + f"您模拟战对boss造成了{shanghai}点伤害，{boss_msg}\n由于伤害超出boss剩余血量，实际模拟造成伤害为{bossinfo['hp']}点\n您的队伍可以剩余血量{card_jk}%\n{nextbossinfo['icon']}"
        else:
            #每日次数-1
            #daily_boss_limiter.increase(guid)
            #计算下一个boss
            nextboss = bossinfo['bossid']
            nextzhoumu = bossinfo['zhoumu']
            if shanghai==bossinfo['hp']:
                nextboss = bossinfo['bossid'] + 1
                if nextboss == 6:
                    nextboss = 1
                    nextzhoumu = bossinfo['zhoumu'] + 1
                nextbossinfo = get_nextbossinfo(nextzhoumu,nextboss,shijieflag)
                boss_msg = f"击杀了boss\n下一个boss为：第{nextzhoumu}周目{nextboss}号boss({nextbossinfo['name']})\n{nextbossinfo['icon']}"
            else:
                now_hp = bossinfo['hp'] - shanghai
                boss_msg = f"boss剩余血量{now_hp}点"
            msg = msg + f"您模拟战对boss造成了{shanghai}点伤害，{boss_msg}"
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content":msg
                    }
                }
        tas_list.append(data)
        await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)
    else:
        await bot.finish(ev, '无法获取boss信息', at_sender=True)
        return

@sv.on_rex(f'^(.*)补时刀模拟$')
async def bushi_moni(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    if now.day == 1 and now.hour == 0: #每月1号结算
        await bot.finish(ev, '会战奖励结算中，禁止出刀', at_sender=True)
        return
    
    match = ev['match']
    gotype = str(match.group(1))
    gotype = re.sub(r'[?？，,_ ]', '', gotype)
    if gotype == "世界boss":
        sendgid = 999
        shijieflag = 1
    elif gotype == "boss战":
        sendgid = gid
        shijieflag = 0
    else:
        await bot.finish(ev, '请选择正确的boss战类型（世界boss/boss战）', at_sender=True)
    duel = DuelCounter()
    CE = CECounter()
    cidlist = duel._get_cards(gid, uid)
    nowyear = datetime.now().year
    nowmonth = datetime.now().month
    nowday = datetime.now().day
    fighttime = str(nowyear) + str(nowmonth) + str(nowday)
    bushilist = CE._get_cardbushi(gid,uid,fighttime,shijieflag)
    if bushilist==0:
        await bot.finish(ev, '您没有处于补时刀状态，请正常模拟出刀哦', at_sender=True)
    #print(fighttime)
    z_ce=0
    bianzu=''
    #获取本群boss状态和血量
    bossinfo = get_boss_info(sendgid)
    if len(bossinfo)>0:
        #获取编队战力与信息
        card_jk = 0
        charalist = []
        for i in bushilist:
            cid = i[0]
            card_jk = i[1]/100
            c = chara.fromid(cid)
            card_ce=get_card_ce(gid,uid,cid)
            z_ce=z_ce+card_ce
            if cid == 9999:
                cid = 1059
            star = CE._get_cardstar(gid,uid,cid)
            charalist.append(chara.Chara(cid, star, 0))
            bianzu=bianzu+f"{c.name} "
        #
        res = chara.gen_team_pic(charalist, star_slot_verbose=False)
        bio = BytesIO()
        res.save(bio, format='PNG')
        base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
        mes = f"[CQ:image,file={base64_str}]"
        boss_ce = bossinfo['ce']
        msg1=f"[CQ:at,qq={uid}]编组成功{bianzu}\n{mes}\n开始进入模拟补时刀\n当前boss为：第{bossinfo['zhoumu']}周目{bossinfo['bossid']}号boss({bossinfo['name']})\nboss战力为{bossinfo['ce']}，当前血量为{bossinfo['hp']}\n您的编组战力为{z_ce}，开始模拟补时刀\n{bossinfo['icon']}"
        tas_list = []
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content":msg1
                    }
                }
        tas_list.append(data)
        
        #计算造成的伤害
        #2者相加的总战力
        zhanlz = boss_ce + z_ce
        #计算总战力扩值
        kuo = zhanlz * zhanlz
        #计算总战力差值
        cha = (zhanlz/z_ce)
        #计算无战力压制因素的输出伤害
        shuchu = (kuo/boss_ce)/cha
        #计算战力压制因素印象可以造成的伤害比
        zhanbi = z_ce/zhanlz+1
        #计算输出浮动数+-10%
        fudong = int(math.floor( random.uniform(1,20) ))
        if fudong>10:
            fudong = fudong/200+1
        else:
            fudong = 1-fudong/100
        #计算最终输出伤害
        shanghai_zc = math.ceil((shuchu * fudong)/zhanbi)
        shanghai = math.ceil((shuchu * fudong)/zhanbi * card_jk)
        msg = ''
        #判断造成的伤害是否大于boss血量
        if shanghai>bossinfo['hp']:
            #计算健康状态
            #card_jk = 100-math.ceil(bossinfo['hp']/shanghai*100)
            #计算下一个boss
            nextboss = bossinfo['bossid'] + 1
            nextzhoumu = bossinfo['zhoumu']
            if nextboss == 6:
                nextboss = 1
                nextzhoumu = bossinfo['zhoumu'] + 1
            nextbossinfo = get_nextbossinfo(nextzhoumu,nextboss,shijieflag)
            boss_msg = f"模拟击杀了boss\n下一个boss为：第{nextzhoumu}周目{nextboss}号boss({nextbossinfo['name']})"
            msg = msg + f"您模拟战对boss造成了{shanghai}点伤害，{boss_msg}\n由于伤害超出boss剩余血量，实际模拟造成伤害为{bossinfo['hp']}点\n{nextbossinfo['icon']}"
        else:
            
            #计算下一个boss
            nextboss = bossinfo['bossid']
            nextzhoumu = bossinfo['zhoumu']
            if shanghai==bossinfo['hp']:
                nextboss = bossinfo['bossid'] + 1
                if nextboss == 6:
                    nextboss = 1
                    nextzhoumu = bossinfo['zhoumu'] + 1
                nextbossinfo = get_nextbossinfo(nextzhoumu,nextboss,shijieflag)
                boss_msg = f"击杀了boss\n下一个boss为：第{nextzhoumu}周目{nextboss}号boss({nextbossinfo['name']})\n{nextbossinfo['icon']}"
            else:
                now_hp = bossinfo['hp'] - shanghai
                boss_msg = f"boss剩余血量{now_hp}点"
            msg = msg + f"您对boss造成了{shanghai}点伤害，{boss_msg}"
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content":msg
                    }
                }
        tas_list.append(data)
        await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)
    else:
        await bot.finish(ev, '无法获取boss信息', at_sender=True)
        return
@sv.on_rex(f'^(.*)补时刀$')
async def start_bushi(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    match = ev['match']
    
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    if now.day == 1 and now.hour == 0: #每月1号结算
        await bot.finish(ev, '会战奖励结算中，禁止出刀', at_sender=True)
        return
    
    gotype = str(match.group(1))
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
    
    guid = keygid ,uid
    if not daily_boss_limiter.check(guid):
        await bot.send(ev, f'今天的{gotype}次数已经超过上限了哦，明天再来吧。', at_sender=True)
        return
    duel = DuelCounter()
    CE = CECounter()
    cidlist = duel._get_cards(gid, uid)
    nowyear = datetime.now().year
    nowmonth = datetime.now().month
    nowday = datetime.now().day
    fighttime = str(nowyear) + str(nowmonth) + str(nowday)
    bushilist = CE._get_cardbushi(gid,uid,fighttime,shijieflag)
    if bushilist==0:
        await bot.finish(ev, '您没有处于补时刀状态，请正常出刀哦', at_sender=True)
    #print(fighttime)
    z_ce=0
    bianzu=''
    #获取本群boss状态和血量
    bossinfo = get_boss_info(sendgid)
    if len(bossinfo)>0:
        #获取编队战力与信息
        card_jk = 0
        charalist = []
        for i in bushilist:
            cid = i[0]
            card_jk = i[1]/100
            c = chara.fromid(cid)
            card_ce=get_card_ce(gid,uid,cid)
            z_ce=z_ce+card_ce
            if cid == 9999:
                cid = 1059
            star = CE._get_cardstar(gid,uid,cid)
            charalist.append(chara.Chara(cid, star, 0))
            bianzu=bianzu+f"{c.name} "
        #
        res = chara.gen_team_pic(charalist, star_slot_verbose=False)
        bio = BytesIO()
        res.save(bio, format='PNG')
        base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
        mes = f"[CQ:image,file={base64_str}]"
        boss_ce = bossinfo['ce']
        msg1=f"[CQ:at,qq={uid}]编组成功{bianzu}\n{mes}\n开始进入补时刀\n当前boss为：第{bossinfo['zhoumu']}周目{bossinfo['bossid']}号boss({bossinfo['name']})\nboss战力为{bossinfo['ce']}，当前血量为{bossinfo['hp']}\n您的编组战力为{z_ce}，开始战斗\n{bossinfo['icon']}"
        tas_list = []
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content":msg1
                    }
                }
        tas_list.append(data)
        
        #计算造成的伤害
        #2者相加的总战力
        zhanlz = boss_ce + z_ce
        #计算总战力扩值
        kuo = zhanlz * zhanlz
        #计算总战力差值
        cha = (zhanlz/z_ce)
        #计算无战力压制因素的输出伤害
        shuchu = (kuo/boss_ce)/cha
        #计算战力压制因素印象可以造成的伤害比
        zhanbi = z_ce/zhanlz+1
        #计算输出浮动数+-10%
        fudong = int(math.floor( random.uniform(1,20) ))
        if fudong>10:
            fudong = fudong/200+1
        else:
            fudong = 1-fudong/100
        #计算最终输出伤害
        shanghai_zc = math.ceil((shuchu * fudong)/zhanbi)
        shanghai = math.ceil((shuchu * fudong)/zhanbi * card_jk)
        msg = ''
        #for i in bushilist:
            #cid = i[0]
            #duel._add_favor(gid,uid,cid,dungeoninfo['add_favor'])
            #card_level=add_exp(gid,uid,cid,bossinfo['add_exp'])
        #每日次数-1
        daily_boss_limiter.increase(guid)
        #判断造成的伤害是否大于boss血量
        if shanghai>bossinfo['hp']:
            #计算健康状态
            #card_jk = 100-math.ceil(bossinfo['hp']/shanghai*100)
            #计算下一个boss
            nextboss = bossinfo['bossid'] + 1
            nextzhoumu = bossinfo['zhoumu']
            nexthp = 0
            if nextboss == 6:
                nextboss = 1
                nextzhoumu = bossinfo['zhoumu'] + 1
            nextbossinfo = get_nextbossinfo(nextzhoumu,nextboss,shijieflag)
            boss_msg = f"击杀了boss\n下一个boss为：第{nextzhoumu}周目{nextboss}号boss({nextbossinfo['name']})"
            msg = msg + f"您对boss造成了{shanghai}点伤害，{boss_msg}\n由于伤害超出boss剩余血量，实际造成伤害为{bossinfo['hp']}点\n{nextbossinfo['icon']}"
            shanghai = bossinfo['hp']
        else:
            
            #计算下一个boss
            nextboss = bossinfo['bossid']
            nextzhoumu = bossinfo['zhoumu']
            nexthp = 0
            if shanghai==bossinfo['hp']:
                nextboss = bossinfo['bossid'] + 1
                if nextboss == 6:
                    nextboss = 1
                    nextzhoumu = bossinfo['zhoumu'] + 1
                nextbossinfo = get_nextbossinfo(nextzhoumu,nextboss,shijieflag)
                boss_msg = f"击杀了boss\n下一个boss为：第{nextzhoumu}周目{nextboss}号boss({nextbossinfop['name']})\n{nextbossinfo['icon']}"
            else:
                now_hp = bossinfo['hp'] - shanghai
                nexthp = now_hp
                boss_msg = f"boss剩余血量{now_hp}点"
            msg = msg + f"您对boss造成了{shanghai}点伤害，{boss_msg}"
        #保存boss状态
        CE._up_bossinfo(sendgid, nextzhoumu, nextboss, nexthp)
        CE._add_bossfight(gid, uid, bossinfo['zhoumu'], bossinfo['bossid'], shanghai, shijieflag)
        for i in bushilist:
            cid = i[0]
            CE._add_cardfight(gid, uid, cid, fighttime, 0, shijieflag)
            card_level=add_exp(gid,uid,cid,bossinfo['add_exp'])
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content":msg
                    }
                }
        tas_list.append(data)
        await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)
        await asyncio.sleep(3)
        
        #判断是否击杀boss，分配boss掉落
        if shanghai>=bossinfo['hp']:
            #获取boss伤害输出表
            group_list=[]
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
                        "content":f"{gotype}战况：\n第{bossinfo['zhoumu']}周目{bossinfo['bossid']}号boss({bossinfo['name']})\n已被打死，开始分配boss掉落"
                            }
                        }
                tas_list.append(data)
                for shuchu in shuchulist:
                    if groupid == shuchu[0]:
                        get_equip = ''
                        get_awardequip = ''
                        for y in range(bossinfo['dropnum']):
                            equip_info = add_equip_info(shuchu[0],shuchu[1],bossinfo['dropequip'],bossinfo['equip'])
                            get_equip = get_equip + f"{equip_info['model']}品质{equip_info['type']}:{equip_info['name']}\n"
                        if shuchu[2] in awardlist:
                            awardequip_info = add_equip_info(shuchu[0],shuchu[1],bossinfo['awardequip'],bossinfo['awardlist'])
                            get_awardequip = get_awardequip + f"由于您的本次输出为前三名，额外获得装备：{awardequip_info['model']}品质{awardequip_info['type']}:{awardequip_info['name']}\n"
                        data = {
                            "type": "node",
                            "data": {
                                "name": "ご主人様",
                                "uin": "1587640710",
                                "content":f"[CQ:at,qq={shuchu[1]}]您对boss造成了{shuchu[2]}点伤害，获得了装备\n{get_equip}{get_awardequip}"
                                    }
                                }
                        tas_list.append(data)
                await bot.send_group_forward_msg(group_id=groupid, messages=tas_list)
    else:
        await bot.finish(ev, '无法获取boss信息', at_sender=True)
        return

   
@sv.on_rex(f'^编队(.*)开始(.*)$')
async def start_huizhan(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    CE = CECounter()
    # 处理输入数据
    
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    if now.day == 1 and now.hour == 0: #每月1号结算
        await bot.finish(ev, '会战奖励结算中，禁止出刀', at_sender=True)
        return
    
    
    match = ev['match']
    gotype = str(match.group(2))
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
    guid = keygid ,uid
    if not daily_boss_limiter.check(guid):
        await bot.send(ev, f'今天的{gotype}次数已经超过上限了哦，明天再来吧。', at_sender=True)
        return
    defen = str(match.group(1))
    defen = re.sub(r'[?？，,_]', '', defen)
    if not defen:
        await bot.finish(ev, '请发送"编队+女友名/队伍名+开始+(boss战/世界boss)"，无需+号', at_sender=True)
    #查询是否是队伍
    teamlist = CE._get_teamlist(gid, uid, defen)
    if teamlist!=0:
        defen = []
        for i in teamlist:
            cid = i[0]
            defen.append(cid)
    else:
        defen, unknown = chara.roster.parse_team(defen)
        cidlist = duel._get_cards(gid, uid)
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
        if uid!=owner:
            msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法编队哦。'
            await bot.finish(ev, msg)
        fightinfo = CE._get_cardfightinfo(gid, uid, cid, fighttime, shijieflag)
        if fightinfo[0]>0:
            if fightinfo[1]>0:
                msg = f'您现在正处于补时刀状态，无法正常出刀，请输入指令‘{gotype}补时刀’进入下一轮boss战斗。'
                await bot.finish(ev, msg)
            else:
                msg = f'{c.name}今日已战斗过了，无法继续战斗了哦，请替换其他的女友出战哦。'
                await bot.finish(ev, msg)
    #print("开始会战")
    z_ce=0
    bianzu=''
    #获取本群boss状态和血量
    bossinfo = get_boss_info(sendgid)
    #print(bossinfo)
    if len(bossinfo)>0:
        #获取编队战力与信息
        charalist = []
        for cid in defen:
            c = chara.fromid(cid)
            card_ce=get_card_ce(gid,uid,cid)
            z_ce=z_ce+card_ce
            if cid == 9999:
                cid = 1059
            star = CE._get_cardstar(gid,uid,cid)
            charalist.append(chara.Chara(cid, star, 0))
            bianzu=bianzu+f"{c.name} "
        #
        res = chara.gen_team_pic(charalist, star_slot_verbose=False)
        bio = BytesIO()
        res.save(bio, format='PNG')
        base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
        mes = f"[CQ:image,file={base64_str}]"
        boss_ce = bossinfo['ce']
        msg1=f"[CQ:at,qq={uid}]编组成功{bianzu}\n{mes}\n开始进入会战\n当前boss为：第{bossinfo['zhoumu']}周目{bossinfo['bossid']}号boss({bossinfo['name']})\nboss战力为{bossinfo['ce']}，当前血量为{bossinfo['hp']}\n您的编组战力为{z_ce}，开始战斗\n{bossinfo['icon']}"
        tas_list = []
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content":msg1
                    }
                }
        tas_list.append(data)
        
        #计算造成的伤害
        #2者相加的总战力
        zhanlz = boss_ce + z_ce
        #计算总战力扩值
        kuo = zhanlz * zhanlz
        #计算总战力差值
        cha = (zhanlz/z_ce)
        #计算无战力压制因素的输出伤害
        shuchu = (kuo/boss_ce)/cha
        #计算战力压制因素印象可以造成的伤害比
        zhanbi = z_ce/zhanlz+1
        #计算输出浮动数+-10%
        fudong = int(math.floor( random.uniform(1,20) ))
        if fudong>10:
            fudong = fudong/200+1
        else:
            fudong = 1-fudong/100
        #计算最终输出伤害
        shanghai = math.ceil((shuchu * fudong)/zhanbi)
        msg = ''
        #for cid in defen:
            #duel._add_favor(gid,uid,cid,dungeoninfo['add_favor'])
            #card_level=add_exp(gid,uid,cid,bossinfo['add_exp'])
        #判断造成的伤害是否大于boss血量
        card_jk = 0
        if shanghai>bossinfo['hp']:
            #计算健康状态
            card_jk = 100-math.ceil(bossinfo['hp']/shanghai*100)
            #计算下一个boss
            nextboss = bossinfo['bossid'] + 1
            nextzhoumu = bossinfo['zhoumu']
            nexthp = 0
            if nextboss == 6:
                nextboss = 1
                nextzhoumu = bossinfo['zhoumu'] + 1
            nextbossinfo = get_nextbossinfo(nextzhoumu,nextboss,shijieflag)
            boss_msg = f"击杀了boss\n下一个boss为：第{nextzhoumu}周目{nextboss}号boss({nextbossinfo['name']})"
            msg = msg + f"您对boss造成了{shanghai}点伤害，{boss_msg}\n由于伤害超出boss剩余血量，实际造成伤害为{bossinfo['hp']}点\n您的队伍剩余血量{card_jk}%，请输入指令‘{gotype}补时刀’进入下一轮boss战斗\n{nextbossinfo['icon']}"
            shanghai = bossinfo['hp']
        else:
            #每日次数-1
            daily_boss_limiter.increase(guid)
            #计算下一个boss
            nextboss = bossinfo['bossid']
            nextzhoumu = bossinfo['zhoumu']
            nexthp = 0
            if shanghai==bossinfo['hp']:
                nextboss = bossinfo['bossid'] + 1
                if nextboss == 6:
                    nextboss = 1
                    nextzhoumu = bossinfo['zhoumu'] + 1
                nextbossinfo = get_nextbossinfo(nextzhoumu,nextboss,shijieflag)
                boss_msg = f"击杀了boss\n下一个boss为：第{nextzhoumu}周目{nextboss}号boss({nextbossinfo['name']}){nextbossinfo['icon']}"
            else:
                now_hp = bossinfo['hp'] - shanghai
                nexthp = now_hp
                boss_msg = f"boss剩余血量{now_hp}点"
            msg = msg + f"您对boss造成了{shanghai}点伤害，{boss_msg}"
        CE._up_bossinfo(sendgid, nextzhoumu, nextboss, nexthp)
        CE._add_bossfight(gid, uid, bossinfo['zhoumu'], bossinfo['bossid'], shanghai, shijieflag)
        for cid in defen:
            CE._add_cardfight(gid, uid, cid, fighttime, card_jk, shijieflag)
            card_level=add_exp(gid,uid,cid,bossinfo['add_exp'])
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content":msg
                    }
                }
        tas_list.append(data)
        await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)
        await asyncio.sleep(3)
        #await bot.send(ev, '计算boss掉落')
        #判断是否击杀boss，分配boss掉落
        if shanghai>=bossinfo['hp']:
            #获取boss伤害输出表
            group_list=[]
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
                        "content":f"{gotype}战况：\n第{bossinfo['zhoumu']}周目{bossinfo['bossid']}号boss({bossinfo['name']})\n已被打死，开始分配boss掉落"
                            }
                        }
                tas_list.append(data)
                for shuchu in shuchulist:
                    if groupid == shuchu[0]:
                        get_equip = ''
                        get_awardequip = ''
                        for y in range(bossinfo['dropnum']):
                            equip_info = add_equip_info(shuchu[0],shuchu[1],bossinfo['dropequip'],bossinfo['equip'])
                            get_equip = get_equip + f"{equip_info['model']}品质{equip_info['type']}:{equip_info['name']}\n"
                        if shuchu[2] in awardlist:
                            awardequip_info = add_equip_info(shuchu[0],shuchu[1],bossinfo['awardequip'],bossinfo['awardlist'])
                            get_awardequip = get_awardequip + f"由于您的本次输出为前三名，额外获得装备：{awardequip_info['model']}品质{awardequip_info['type']}:{awardequip_info['name']}\n"
                        data = {
                            "type": "node",
                            "data": {
                                "name": "ご主人様",
                                "uin": "1587640710",
                                "content":f"[CQ:at,qq={shuchu[1]}]您对boss造成了{shuchu[2]}点伤害，获得了装备\n{get_equip}{get_awardequip}"
                                    }
                                }
                        tas_list.append(data)
                await bot.send_group_forward_msg(group_id=groupid, messages=tas_list)
    else:
        await bot.finish(ev, '无法获取boss信息', at_sender=True)
        return


@sv.on_fullmatch(['会战系统帮助','会战帮助'])
async def boss_help(bot, ev: CQEvent):
    msg='''
╔                                        ╗  
             会战系统帮助
1. (boss/世界boss)状态
2. 编队+女友名(最多5名，用空格隔开)开始(boss战/世界boss)
3. 编队+女友名(最多5名，用空格隔开)模拟(boss战/世界boss)
4. (boss战/世界boss)补时刀模拟
5. (boss战/世界boss)补时刀
6. (boss战/世界boss)伤害排行
注:
世界boss为所有加的群一起打，打死一个boss有装备掉落，不同类型的boss每日各有3次次数
╚                                        ╝
 '''  
    await bot.send(ev, msg)

@sv.on_rex(f'^(.*)伤害排行$')
async def shuchu_list(bot, ev: CQEvent):
    gid = ev.group_id
    CE = CECounter()
    match = ev['match']
    gotype = str(match.group(1))
    gotype = re.sub(r'[?？，,_ ]', '', gotype)
    if gotype == "世界boss":
        sendgid = 999
        shijieflag = 1
    elif gotype == "boss战":
        sendgid = gid
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
                "content":f"为保护个人隐私，世界boss只显示本群数据"
                    }
                }
        tas_list.append(data)
    for shuchu in shuchu_list:
        #print(shuchu)
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content":f"[CQ:at,qq={shuchu[0]}]总共造成了{shuchu[1]}点伤害"
                    }
                }
        tas_list.append(data)
    await bot.send_group_forward_msg(group_id=gid, messages=tas_list)

@sv.on_rex(f'^(.*)状态$')
async def boss_info(bot, ev: CQEvent):
    gid = ev.group_id
    match = ev['match']
    gotype = str(match.group(1))
    gotype = re.sub(r'[?？，,_ ]', '', gotype)
    if gotype == "世界boss":
        sendgid = 999
        shijieflag = 1
    elif gotype == "boss战":
        sendgid = gid
        shijieflag = 0
    else:
        await bot.finish(ev, '请选择正确的boss战类型（世界boss/boss战）', at_sender=True)
    bossinfo = get_boss_info(sendgid)
    msg = f"当前boss状态为：\n第{bossinfo['zhoumu']}周目{bossinfo['bossid']}号boss({bossinfo['name']})\nboss战力为{bossinfo['ce']}，当前血量为{bossinfo['hp']}\n{bossinfo['icon']}"
    await bot.send(ev, msg)

@sv.on_rex(f'^创建队伍(.*)队名(.*)$')
async def add_team(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id

    # 处理输入数据
    match = ev['match']
    
    teamname = str(match.group(2))
    teamname = re.sub(r'[?？，,_ ]', '', teamname)
    if not teamname:
        await bot.finish(ev, '请发送"创建队伍+女友名+队名+队伍名称"，无需+号', at_sender=True)
    defen = str(match.group(1))
    defen = re.sub(r'[?？，,_]', '', defen)
    defen, unknown = chara.roster.parse_team(defen)
    duel = DuelCounter()
    cidlist = duel._get_cards(gid, uid)
    if unknown:
        _, name, score = chara.guess_id(unknown)
        if score < 70 and not defen:
            return  # 忽略无关对话
        msg = f'无法识别"{unknown}"' if score < 70 else f'无法识别"{unknown}" 您说的有{score}%可能是{name}'
        await bot.finish(ev, msg)
    if not defen:
        await bot.finish(ev, '请发送"创建队伍+女友名+队名+队伍名称"，无需+号', at_sender=True)
    if len(defen) > 5:
        await bot.finish(ev, '编队不能多于5名角色', at_sender=True)
    if len(defen) != len(set(defen)):
        await bot.finish(ev, '编队中含重复角色', at_sender=True)
    if 1004 in defen:
        await bot.finish(ev, '\n⚠️您正在查询普通版炸弹人\n※万圣版可用万圣炸弹人/瓜炸等别称', at_sender=True)
    for cid in defen:
        c = chara.fromid(cid)
        nvmes = get_nv_icon(cid)
        owner = duel._get_card_owner(gid, cid)
        if owner == 0:
            await bot.finish(ev, f'{c.name}现在还是单身哦，快去约到她吧。{nvmes}', at_sender=True)
        if uid!=owner:
            msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法编队哦。'
            await bot.finish(ev, msg)
    CE = CECounter()
    teaminfo = CE._get_teamlist(gid, uid, teamname)
    
    if teaminfo!=0:
        z_ce=0
        bianzu=''
        charalist = []
        for i in teaminfo:
            cid = i[0]
            c = chara.fromid(cid)
            card_ce=get_card_ce(gid,uid,cid)
            z_ce=z_ce+card_ce
            if cid == 9999:
                cid = 1059
            star = CE._get_cardstar(gid,uid,cid)
            charalist.append(chara.Chara(cid, star, 0))
            bianzu=bianzu+f"{c.name} "
        res = chara.gen_team_pic(charalist, star_slot_verbose=False)
        bio = BytesIO()
        res.save(bio, format='PNG')
        base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
        mes = f"[CQ:image,file={base64_str}]"
        msg1=f"创建队伍失败！\n已有重复的队伍：{teamname}\n队伍成员为：{bianzu}\队伍战力为：{z_ce}\n{mes}"
        await bot.finish(ev, msg1, at_sender=True)
    
    teamnum = CE._get_teamnum(gid, uid)
    print(teamnum)
    if teamnum>=5:
        await bot.finish(ev, '保存的队伍不能超过5支，请删除其他队伍再来创建吧', at_sender=True)
    
    z_ce=0
    bianzu=''
    charalist = []
    for cid in defen:
        c = chara.fromid(cid)
        card_ce=get_card_ce(gid,uid,cid)
        z_ce=z_ce+card_ce
        bianzu=bianzu+f"{c.name} "
        if cid == 9999:
            cid = 1059
        star = CE._get_cardstar(gid,uid,cid)
        charalist.append(chara.Chara(cid, star, 0))
        CE._add_team(gid, uid, cid, teamname)
    res = chara.gen_team_pic(charalist, star_slot_verbose=False)
    bio = BytesIO()
    res.save(bio, format='PNG')
    base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
    mes = f"[CQ:image,file={base64_str}]"
    msg=f"创建队伍成功！\n队伍名称：{teamname}\n队伍成员为：{bianzu}\n队伍战力为：{z_ce}\n{mes}"
    await bot.send(ev, msg, at_sender=True)
  
@sv.on_prefix(['解散队伍','删除队伍'])
async def delete_team(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    duel = DuelCounter()
    if len(args)!=1:
        await bot.finish(ev, '请输入 解散队伍+队伍名 中间用空格隔开。', at_sender=True)
    teamname = args[0]  
    teaminfo = CE._get_teamlist(gid, uid, teamname)
    
    if teaminfo!=0:
        CE._delete_team(gid, uid, teamname)
        await bot.send(ev, f'解散队伍{teamname}成功', at_sender=True)
    else:
        await bot.finish(ev, '队伍名称出错，无法查询到此队伍', at_sender=True)
        
@sv.on_fullmatch(['我的队伍','查询队伍'])
async def my_teamlst(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    teamlist = CE._get_teamname(gid, uid)
    if teamlist==0:
        await bot.finish(ev, '您还没有创建队伍，请发送"创建队伍+女友名+队名+队伍名称"创建您的队伍', at_sender=True)
    msg = ''
    for name in teamlist:
        teamname = name[0]
        cidlist = CE._get_teamlist(gid, uid, teamname)
        z_ce=0
        bianzu=''
        charalist = []
        for i in cidlist:
            cid = i[0]
            c = chara.fromid(cid)
            card_ce=get_card_ce(gid,uid,cid)
            z_ce=z_ce+card_ce
            if cid == 9999:
                cid = 1059
            star = CE._get_cardstar(gid,uid,cid)
            charalist.append(chara.Chara(cid, star, 0))
            bianzu=bianzu+f"{c.name} "
        res = chara.gen_team_pic(charalist, star_slot_verbose=False)
        bio = BytesIO()
        res.save(bio, format='PNG')
        base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
        mes = f"[CQ:image,file={base64_str}]\n"
        msg = msg + f"队伍名称：{teamname}\n队伍成员：{bianzu}\n队伍战力：{z_ce}\n{mes}"
    await bot.send(ev, msg, at_sender=True)
        
@sv.on_prefix(['挂机修炼','开始挂机'])
async def xiulian_start(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    if len(args)!=1:
        await bot.finish(ev, '请输入 挂机修炼+女友名 中间用空格隔开。', at_sender=True)
    name = args[0]
    cid = chara.name2id(name)
    if cid == 1000:
        await bot.send(ev, '请输入正确的pcr角色名。', at_sender=True)
        return
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    CE = CECounter()
    c = chara.fromid(cid)
    nvmes = get_nv_icon(cid)
    owner = duel._get_card_owner(gid, cid)
    
    if uid!=owner:
        msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法绑定哦。'
        await bot.send(ev, msg)
        return
    if owner == 0:
        await bot.send(ev, f'{c.name}现在还是单身哦，快去约到她吧。{nvmes}', at_sender=True)
        return
    guajiinfo = CE._get_xiulian(gid,uid)
    if guajiinfo[0] > 0:
        cgj = chara.fromid(guajiinfo[0])
        nvmesgj = get_nv_icon(guajiinfo[0])
        await bot.finish(ev, f'{cgj.name}已经在修炼中了哦。{nvmesgj}', at_sender=True)
    if uid==owner:
        xltime = time.time()
        xltime = math.ceil(xltime)
        CE._add_xiulian(gid,uid,cid,xltime)
        await bot.send(ev, f'您的女友{c.name}开始修炼了\n注：一次性修炼最长不能超过24小时哦。{nvmes}', at_sender=True)
    
@sv.on_fullmatch(['结束修炼','取消修炼'])
async def xiulian_end(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    guajiinfo = CE._get_xiulian(gid,uid)
    if guajiinfo[0] == 0:
        await bot.finish(ev, f'您没有正在修炼中的女友，请输入 挂机修炼+女友名 开始修炼哦。', at_sender=True)
    endtime = time.time()
    endtime = math.ceil(endtime)
    jgtime = endtime-guajiinfo[1]
    if jgtime<60:
        CE._delete_xiulian(gid,uid)
        await bot.finish(ev, f'修炼结束，修炼时间小于1分钟，无法获得经验。', at_sender=True)
    sj_msg = ''
    if jgtime>86400:
        xlmin1 = math.ceil(jgtime/60)
        sj_msg = sj_msg + f"总共修炼时间{xlmin1}分钟，由于超过24小时，实际"
        jgtime = 86400
    xlmin = math.ceil(jgtime/60)
    sj_msg = sj_msg + f"修炼时间为{xlmin}分钟，"
    addexp = xlmin*50
    card_level=add_exp(gid,uid,guajiinfo[0],addexp)
    CE._delete_xiulian(gid,uid)
    c = chara.fromid(guajiinfo[0])
    nvmes = get_nv_icon(guajiinfo[0])
    bd_msg = f"修炼结束，{sj_msg}\n您的女友{c.name}获得了{addexp}点经验，{card_level[2]}\n{nvmes}"
    await bot.send(ev, bd_msg, at_sender=True)

@sv.on_fullmatch(['我的经验池','经验池'])
async def get_exp_chizi_num(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    myexp = CE._get_exp_chizi(gid, uid)
    await bot.send(ev, f'您的经验池目前剩余经验为{myexp}点。', at_sender=True)
    
@sv.on_prefix(['分配经验'])
async def add_exp_chizi(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    if len(args)!=2:
        await bot.finish(ev, '请输入 分配经验+女友名+经验值 中间用空格隔开。', at_sender=True)
    name = args[0]
    cid = chara.name2id(name)
    addexp = int(args[1])
    if addexp<1:
        await bot.finish(ev, '请输入正确的经验数。', at_sender=True)
    if cid == 1000:
        await bot.send(ev, '请输入正确的pcr角色名。', at_sender=True)
        return
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    CE = CECounter()
    c = chara.fromid(cid)
    nvmes = get_nv_icon(cid)
    owner = duel._get_card_owner(gid, cid)
    if uid!=owner:
        msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法绑定哦。'
        await bot.send(ev, msg)
        return
    if owner == 0:
        await bot.send(ev, f'{c.name}现在还是单身哦，快去约到她吧。{nvmes}', at_sender=True)
        return
    if uid==owner:
        myexp = CE._get_exp_chizi(gid, uid)
        if addexp>myexp:
            await bot.finish(ev, f'您的经验池经验只有{myexp}点，不足{addexp}，无法分配哦。', at_sender=True)
        card_level=add_exp(gid,uid,cid,addexp)
        last_exp = 0-addexp
        CE._add_exp_chizi(gid, uid, last_exp)
        bd_msg = f"经验分配成功\n您的女友{c.name}获得了{addexp}点经验，{card_level[2]}\n{nvmes}"
        await bot.send(ev, bd_msg, at_sender=True)

@sv.on_fullmatch(['抽卡系统帮助','抽卡帮助'])
async def gecha_help(bot, ev: CQEvent):
    msg='''
╔                                        ╗  
             抽卡系统帮助
1. 查看武器池 (查看当前武器池)
2. 抽装备+(单抽/十连)+装备池名称 (抽取武器)
3. 我的保底 (查看我的保底情况)
4. 我的副本币 (查看我剩余的副本币)
5. 装备分解+装备名 (分解装备)
6. 一键分解+装备等级(N/R/SR/SSR/UR/MR) (一键分解指定等级的装备)
7. 星尘兑换+UP的武器名称 (用300星尘兑换UP的武器)
注:
副本币获取其他路径：通关每日副本
╚                                        ╝
 '''
    await bot.send(ev, msg)

@sv.on_fullmatch(['查看武器池','武器池'])
async def get_equipgecha(bot, ev: CQEvent):
    gechalist={}
    with open(os.path.join(FILE_PATH,'equipgecha.json'),'r',encoding='UTF-8') as fa:
        gechalist = json.load(fa, strict=False)  
    tas_list = []
    for gecha in gechalist:
        meg = ''
        meg = meg + f"武器池名称：{gechalist[gecha]['name']}\n"
        equiplist = ''
        for eid in gechalist[gecha]['up_equip']:
            equipinfo = get_equip_info_id(eid)
            equiplist = equiplist + f"[{equipinfo['name']}] "
        meg = meg + f"up武器：{equiplist}\n"
        meg = meg + f"保底：第{gechalist[gecha]['up_num']}抽之前没有抽到SSR/SSR以上装备时，必定抽到SSR/SSR以上装备\n"
        gl_list = ''
        for level in gechalist[gecha]['gecha']['quality']:
            if level=='2':
                gl_name = 'R'
            if level=='3':
                gl_name = 'SR'
            if level=='4':
                gl_name = 'SSR'
            if level=='5':
                gl_name = 'UR'    
            gl_list = gl_list + f"{gl_name}:{gechalist[gecha]['gecha']['quality'][level]}%\n"
        meg = meg + f"概率公示：\n{gl_list}"
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content":meg
                    }
                }
        tas_list.append(data)
        
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)

@sv.on_fullmatch(['我的保底','查看保底'])
async def get_my_baodi(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    bdinfo = CE._get_gecha_num(gid, uid)
    xnum = bdinfo[0]#10连小保底进度
    last_xnum = 10-xnum
    dnum = bdinfo[1]#大保底进度
    last_dnum = 100-dnum
    unum = bdinfo[2]#大保底进度
    last_unum = 200-unum
    msg = f"您已经{xnum}次没有抽到SR/SR以上装备了，再抽{last_xnum}次必定获得SR/SR以上装备\n您已经{dnum}次没有抽到SSR/SSR以上装备了，再抽{last_dnum}次必定获得SSR/SSR以上装备\n您已经{unum}次没有抽到ur装备了，再抽{last_unum}次必定获得ur装备"
    await bot.send(ev, msg, at_sender=True)

@sv.on_fullmatch(['我的副本币','查看副本币'])
async def get_my_dunscore(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    myscore = CE._get_dunscore(gid, uid)
    await bot.send(ev, f"您的副本币为{myscore}", at_sender=True)

@sv.on_prefix(['抽装备'])
async def add_equip_gecha(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    if len(args)!=2:
        await bot.finish(ev, '请输入 抽装备+(单抽/十连)+装备池名称 中间用空格隔开。', at_sender=True)
    if args[0] == '单抽':
        gechanum = 1
    elif args[0] == '十连':
        gechanum = 10
    else:
        await bot.finish(ev, '请输入正确的抽取数量（单抽/十连）。', at_sender=True)
    if args[1] == '':
        await bot.finish(ev, '请输入装备池名称。', at_sender=True)
    need_dunscore = GECHA_DUNDCORE*gechanum
    myscore = CE._get_dunscore(gid, uid)
    if need_dunscore>myscore:
        await bot.finish(ev, f'您的副本币不足{need_dunscore}，无法抽卡哦。', at_sender=True)
    gechainfo = get_gecha_info(args[1])
    if gechainfo['name']:
        #print(gechainfo['name'])
        bdinfo = CE._get_gecha_num(gid, uid)
        xnum = bdinfo[0]#10连小保底进度
        dnum = bdinfo[1]#大保底进度
        unum = bdinfo[2]#大保底进度
        getequip = get_gecha_equip(gid, uid, gechanum, xnum, dnum, unum, gechainfo)
        last_score = myscore - need_dunscore
        need_score = 0-need_dunscore
        CE._add_dunscore(gid, uid, need_score)
        add_exp = gechanum*500
        CE._add_exp_chizi(gid, uid, add_exp)
        msg = f"消耗{need_dunscore}副本币，剩余副本币{last_score}\n获得经验{add_exp}，已加入经验池\n本次{args[0]}获得的装备为：{getequip}"
        await bot.send(ev, msg, at_sender=True)
    else:
        await bot.finish(ev, '请输入正确的武器池名称。', at_sender=True)
    
@sv.on_prefix(['装备分解','分解装备'])
async def equip_fenjie_one(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    if len(args)!=1:
        await bot.finish(ev, '请输入 装备分解+装备名称 中间用空格隔开。', at_sender=True)
    equipinfo = get_equip_info_name(args[0])
    if len(equipinfo)>0:
        equipnum = CE._get_equip_num(gid,uid,equipinfo['eid'])
        if equipnum==0:
            await bot.finish(ev, '你的这件装备的库存不足哦。', at_sender=True)
        if equipinfo['level']<=3:
            chenji = 1
        else:
            chenji = 3
        fj_one = equipinfo['level']*chenji*10
        get_dunscore = fj_one * equipnum
        CE._add_dunscore(gid, uid, get_dunscore)
        deletenum = 0-equipnum
        CE._add_equip(gid, uid, equipinfo['eid'], deletenum)
        msg = f"您成功分解了{equipnum}件{equipinfo['model']}级装备，获得了{get_dunscore}副本币"
        await bot.send(ev, msg, at_sender=True)
    else:
        await bot.finish(ev, '请输入正确的装备名。', at_sender=True)
    
@sv.on_prefix(['一键分解'])
async def equip_fenjie_n(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    if len(args)!=1:
        await bot.finish(ev, '请输入 装备分解+装备等级(N/R/SR/SSR/UR/MR) 中间用空格隔开。', at_sender=True)
    modelname = args[0]
    equiplist={}
    with open(os.path.join(FILE_PATH,'equipment.json'),'r',encoding='UTF-8') as fa:
        equiplist = json.load(fa, strict=False)  
    equiplevel = 0
    for i in equiplist:
        if str(modelname) == str(equiplist[i]['model']):
            equiplevel = equiplist[i]['level']
            break
    if equiplevel == 0:
        await bot.finish(ev, '请输入正确的装备等级(N/R/SR/SSR/UR/MR)。', at_sender=True)
    
    equip_list = CE._get_equip_list(gid, uid)
    if len(equip_list)>0:
        msg_list = ''
        dunscore = 0
        for i in equip_list:
            equipinfo=get_equip_info_id(i[0])
            if equipinfo['level'] == equiplevel:
                if equipinfo['level']<=3:
                    chenji = 1
                else:
                    chenji = equipinfo['level']
                fj_one = equipinfo['level']*chenji*10
                equipnum = i[1]
                get_dunscore = fj_one * equipnum
                dunscore = dunscore + get_dunscore
                deletenum = 0-equipnum
                CE._add_equip(gid, uid, equipinfo['eid'], deletenum)
                msg_list = msg_list + f"\n{equipnum}件{equipinfo['model']}级装备,{equipinfo['name']}"
        if dunscore>0:
            CE._add_dunscore(gid, uid, dunscore)
            msg = f"分解成功，您分解了{msg_list}\n一共获得了{dunscore}副本币"
            await bot.send(ev, msg, at_sender=True)
        else:
            await bot.finish(ev, f'您没有{modelname}级及以下的装备哦。', at_sender=True)
    else:
        await bot.finish(ev, '您还没有获得装备哦。', at_sender=True)
        
@sv.on_prefix(['星尘兑换'])
async def xingchen_change(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    if len(args)!=1:
        await bot.finish(ev, '请输入 星尘兑换+UP的武器名称 中间用空格隔开。', at_sender=True)
    xc_num = CE._get_xingchen_num(gid, uid)
    if xc_num<300:
        await bot.finish(ev, f'您的星尘剩余{xc_num}，不足300，无法兑换哦。', at_sender=True)
    equipinfo = get_equip_info_name(args[0])
    if len(equipinfo)>0:
        eid = equipinfo['eid']
        gechalist={}
        with open(os.path.join(FILE_PATH,'equipgecha.json'),'r',encoding='UTF-8') as fa:
            gechalist = json.load(fa, strict=False)  
        tas_list = []
        find_flag = 0
        for gecha in gechalist:
            if eid in gechalist[gecha]['up_equip']:
                find_flag = 1
                break
        if find_flag==0:
            await bot.finish(ev, f'{args[0]}目前没有UP哦。', at_sender=True)
        now_num = CE._add_xingchen_num(gid, uid, -300)
        CE._add_equip(gid, uid, equipinfo['eid'], 1)
        msg = f"您消耗了300星尘，成功兑换了装备{args[0]}，剩余星尘{now_num}"
        await bot.send(ev, msg, at_sender=True)
    else:
        await bot.finish(ev, '请输入正确的装备名称。', at_sender=True)

@sv.on_prefix(['兑换戒指'])
async def xingchen_jz(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    if len(args)!=1:
        await bot.finish(ev, '请输入 兑换戒指+戒指名称[永恒的守护/世世的相随] 中间用空格隔开。', at_sender=True)
    xc_num = CE._get_xingchen_num(gid, uid)
    if xc_num<500:
        await bot.finish(ev, f'您的星尘剩余{xc_num}，不足500，无法兑换哦。', at_sender=True)
    equipinfo = get_equip_info_name(args[0])
    if len(equipinfo)>0:
        now_num = CE._add_xingchen_num(gid, uid, -500)
        CE._add_equip(gid, uid, equipinfo['eid'], 1)
        msg = f"您消耗了500星尘，成功兑换了戒指 {args[0]}，剩余星尘{now_num}"
        await bot.send(ev, msg, at_sender=True)
    else:
        await bot.finish(ev, '请输入正确的装备名称。', at_sender=True)

@sv.on_prefix(['群排名','会战群排名'])
async def paiming_list(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    if len(args)!=1:
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
    bosslist={}
    with open(os.path.join(FILE_PATH,'bossinfo.json'),'r',encoding='UTF-8') as fa:
        bosslist = json.load(fa, strict=False)
    bl_list = []
    for boss in bosslist:
        bv=[]
        for j in bosslist[boss]['bosslist']:
            bv_boss = bosslist[boss]['bosslist'][j]['fenshu']
            bv.append(bv_boss)
        for i in bosslist[boss]['zhoumu']:
            bl_list.append(bv)
    #print(bl_list)
    group_list = []
    for shuchu in shuchu_list:
        if shuchu[0] not in group_list:
            group_list.append(shuchu[0])
    msg = ''
    grouplist_s=[]
    grouplist_b=[]
    for groupid in group_list:
        defen_s = 0
        defen_b = 0
        for shuchuinfo in shuchu_list:
            if shuchuinfo[0] == groupid:
                zhoumu = shuchuinfo[2] - 1
                bossid = shuchuinfo[3] - 1
                beilv = bl_list[zhoumu][bossid]
                defen = math.ceil(shuchuinfo[4] * beilv)
                #sc_text = f"{groupid},周目{shuchuinfo[2]},boss{shuchuinfo[3]},倍率{beilv},类型{shuchuinfo[5]},伤害{shuchuinfo[4]}"
                #print(sc_text)
                if shuchuinfo[5] == 1:
                    defen_s = defen_s + defen
                else:
                    defen_b = defen_b + defen
        dfgroup_s = [groupid,defen_s]
        dfgroup_b = [groupid,defen_b]
        grouplist_s.append(dfgroup_s)
        grouplist_b.append(dfgroup_b)
    
    grouplist_s = sorted(grouplist_s,key=lambda cus:cus[1],reverse=True)
    grouplist_b = sorted(grouplist_b,key=lambda cus:cus[1],reverse=True)
    
    
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
            "content":f"{msg_s_b}{leibie}boss战群排行榜\n{msg_b}"
                }
            }
    tas_list.append(data)
    
    data = {
        "type": "node",
        "data": {
            "name": "ご主人様",
            "uin": "1587640710",
            "content":f"{msg_s_q}{leibie}世界boss群排行榜\n{msg_s}"
                }
            }
    tas_list.append(data)
    await bot.send_group_forward_msg(group_id=gid, messages=tas_list)
    
 
@sv.scheduled_job('cron', hour ='*',)
async def clock():
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    nowyear = now.year
    nowmonth = now.month
    nowday = now.day
    if not now.day == 1: #每月1号结算
        return
    if not now.hour == 1: #每天1点结算
        return 
    
    jianglilist={
        1:4000,
        2:3500,
        3:3000,
        4:2500,
        5:2500,
        6:2500,
        7:2000,
        8:2000,
        9:2000,
        10:2000,
        11:1500,
        12:1500,
        13:1500,
        14:1500,
        15:1500,
        16:1000,
        17:1000,
        18:1000,
        19:1000,
        20:1000,
    }
    
    bot = nonebot.get_bot()
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
    bosslist={}
    with open(os.path.join(FILE_PATH,'bossinfo.json'),'r',encoding='UTF-8') as fa:
        bosslist = json.load(fa, strict=False)
    bl_list = []
    for boss in bosslist:
        bv=[]
        for j in bosslist[boss]['bosslist']:
            bv_boss = bosslist[boss]['bosslist'][j]['fenshu']
            bv.append(bv_boss)
        for i in bosslist[boss]['zhoumu']:
            bl_list.append(bv)
    #print(bl_list)
    group_list = []
    for shuchu in shuchu_list:
        if shuchu[0] not in group_list:
            group_list.append(shuchu[0])
    msg = ''
    grouplist_s=[]
    grouplist_b=[]
    for groupid in group_list:
        defen_s = 0
        defen_b = 0
        for shuchuinfo in shuchu_list:
            if shuchuinfo[0] == groupid:
                zhoumu = shuchuinfo[2] - 1
                bossid = shuchuinfo[3] - 1
                beilv = bl_list[zhoumu][bossid]
                defen = math.ceil(shuchuinfo[4] * beilv)
                #sc_text = f"{groupid},周目{shuchuinfo[2]},boss{shuchuinfo[3]},倍率{beilv},类型{shuchuinfo[5]},伤害{shuchuinfo[4]}"
                #print(sc_text)
                if shuchuinfo[5] == 1:
                    defen_s = defen_s + defen
                else:
                    defen_b = defen_b + defen
        dfgroup_s = [groupid,defen_s]
        dfgroup_b = [groupid,defen_b]
        grouplist_s.append(dfgroup_s)
        grouplist_b.append(dfgroup_b)
    
    grouplist_s = sorted(grouplist_s,key=lambda cus:cus[1],reverse=True)
    grouplist_b = sorted(grouplist_b,key=lambda cus:cus[1],reverse=True)
    
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
                "content":f"本群boss战群排名第{gidmc_b}名，获得奖励"
                    }
                }
        tas_list_b.append(data)
        
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content":msg_b
                    }
                }
        tas_list_b.append(data)
        
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content":f"本群世界boss群排名第{gidmc_s}名，获得奖励"
                    }
                }
        tas_list_s.append(data)
        
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content":msg_s
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
                                "content":f"[CQ:at,qq={shuchuinfo[1]}]您获得了{gidjl_s}副本币"
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
                                "content":f"[CQ:at,qq={shuchuinfo[1]}]您获得了{gidjl_b}副本币"
                                    }
                                }
                        tas_list_b.append(data)
        await bot.send_group_forward_msg(group_id=groupid, messages=tas_list_s)
        await bot.send_group_forward_msg(group_id=groupid, messages=tas_list_b)
    
@sv.on_fullmatch(['碎片列表','我的碎片'])
async def my_fragment_list(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter() 
    CE = CECounter()
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅。'
        await bot.send(ev, msg, at_sender=True)
        return
    equip_list = CE._get_fragment_list(gid, uid)
    if len(equip_list)>0:
        msg_list = '我的碎片列表：'
        for i in equip_list:
            if i[0]==0:
                name = '万能'
            else:
                c = chara.fromid(i[0])
                name = c.name
            msg_list = msg_list + f"\n{name}碎片:{i[1]}"
        await bot.send(ev, msg_list, at_sender=True)
    else:
        await bot.finish(ev, '您还没有获得角色碎片哦。', at_sender=True)



@sv.on_prefix(['角色升星','星级提升'])
async def cardstar_up(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    duel = DuelCounter()
    if len(args)!=1:
        await bot.finish(ev, '请输入 角色升星+女友名 中间用空格隔开。', at_sender=True)
    name = args[0]
    cid = chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的女友名。', at_sender=True)
    cidlist = duel._get_cards(gid, uid)
    if cid not in cidlist:
        await bot.finish(ev, '该女友不在你的身边哦。', at_sender=True)
    star = CE._get_cardstar(gid,uid,cid)
    if star==MAX_STAR:
        await bot.finish(ev, '该女友已升至满星，无法继续升星啦。', at_sender=True)
    new_star = star + 1
    needfragment = STAR_LIST[int(new_star)]
    card_fragment = CE._get_fragment_num(gid,uid,cid)
    wn_fragment = CE._get_fragment_num(gid,uid,0)
    mynum = int(card_fragment) + int(wn_fragment)
    nvmes = get_nv_icon(cid)
    up_info = duel._get_fashionup(gid,uid,cid,0)
    fashion_ce=0
    up_icon=''
    if up_info:
        #获取穿戴时装所加的战斗力   
        fashion_info = get_fashion_info(up_info)
        up_icon = fashion_info['icon']
    if up_icon:
        nvmes=up_icon
    if mynum<needfragment:
        await bot.finish(ev, f'升级到{new_star}星需要{needfragment}碎片，您的碎片不够哦。', at_sender=True)
    if card_fragment>=needfragment:
        cardnum = 0-needfragment
        CE._add_fragment_num(gid, uid, cid, cardnum)
        msg = f"您消耗了{needfragment}{name}碎片"
    else:
        cardnum = 0-card_fragment
        CE._add_fragment_num(gid, uid, cid, cardnum)
        need_wn = needfragment - card_fragment
        wnnum = 0-need_wn
        CE._add_fragment_num(gid, uid, 0, wnnum)
        msg = f"您消耗了{card_fragment}{name}碎片,{need_wn}万能碎片"
    CE._add_cardstar(gid, uid, cid)
    await bot.send(ev, f'升星成功！\n{msg}\n成功将您的女友{name}升到了{new_star}星,女友战斗力大大提升！{nvmes}', at_sender=True)

@sv.on_fullmatch(['碎片一键兑换经验'])
async def fragment_exp_all(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter() 
    CE = CECounter()
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅。'
        await bot.send(ev, msg, at_sender=True)
        return
    equip_list = CE._get_fragment_list(gid, uid)
    if len(equip_list)>0:
        add_exp = 0
        msg_list = '兑换成功！消耗了'
        for i in equip_list:
            if i[0]==0:
                name = '万能'
                add_exp = add_exp + i[1] * 2000
                wnnum = 0-i[1]
                CE._add_fragment_num(gid, uid, 0, wnnum)
            else:
                c = chara.fromid(i[0])
                name = c.name
                add_exp = add_exp + i[1] * 1000
                delete_num = 0-i[1]
                CE._add_fragment_num(gid, uid, i[0], delete_num)
            msg_list = msg_list + f"\n{name}碎片:{i[1]}"
        CE._add_exp_chizi(gid, uid, add_exp)
        msg_list = msg_list + f"\n累计获得{add_exp}经验"
        await bot.send(ev, msg_list, at_sender=True)
    else:
        await bot.finish(ev, '您还没有获得角色碎片哦。', at_sender=True)

@sv.on_rex(f'^用(.*)片(.*)碎片兑换经验$')
async def fragment_exp(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    CE = CECounter()
    # 处理输入数据
    match = ev['match']

    name = str(match.group(2))
    if name == '万能':
        cid = 0
    else:
        cid = chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的pcr角色名1。', at_sender=True)


    if match.group(1):
        num = int(match.group(1))
        if num > 1:
            num = num
        else:
            num = 1
    else:
        num = 1
        
    card_fragment = CE._get_fragment_num(gid,uid,cid)
    if card_fragment<num:
        await bot.finish(ev, f'{name}碎片不足{num}无法兑换', at_sender=True)
    
    if cid==0:
        add_exp = num * 2000
    else:
        add_exp = num * 1000
    
    fragment_num = 0-num
    CE._add_exp_chizi(gid, uid, add_exp)
    CE._add_fragment_num(gid, uid, cid, fragment_num)
    await bot.send(ev, f'兑换成功！消耗了{num}{name}碎片，获得{add_exp}经验', at_sender=True)

@sv.on_rex(f'^用(.*)碎片兑换(.*)碎片(.*)$')
async def fragment_duihuan(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    CE = CECounter()
    # 处理输入数据
    match = ev['match']

    name1 = str(match.group(1))
    cid1 = chara.name2id(name1)
    if cid1 == 1000:
        await bot.finish(ev, '请输入正确的pcr角色名1。', at_sender=True)
        
    name2 = str(match.group(2))
    cid2 = chara.name2id(name2)
    if cid2 == 1000:
        await bot.finish(ev, '请输入正确的pcr角色名2。', at_sender=True)

    if match.group(3):
        num = int(match.group(3))
        if num > 1:
            num = num
        else:
            num = 1
    else:
        num = 1
        
    need_fragment = num*2
    card_fragment2 = CE._get_fragment_num(gid,uid,cid1)
    if card_fragment2<need_fragment:
        await bot.finish(ev, f'兑换{num}{name2}碎片，需要{need_fragment}其他角色碎片，您的{name1}碎片只有{card_fragment2}，无法兑换。', at_sender=True)
    
    fragment_num = 0-need_fragment
    CE._add_fragment_num(gid, uid, cid1, fragment_num)
    CE._add_fragment_num(gid, uid, cid2, num)
    await bot.send(ev, f'兑换成功！消耗了{need_fragment}{name1}碎片，兑换了{num}{name2}碎片', at_sender=True)
    
@sv.on_fullmatch(['升星系统帮助','升星帮助'])
async def star_help(bot, ev: CQEvent):
    msg='''
╔                                        ╗  
             升星系统帮助
1. 碎片列表(查看我的角色碎片信息)
2. 角色升星 +角色名 (给角色升星)
3. 用(.*)碎片兑换(.*)碎片+数量(碎片兑换，兑换比例2:1，数量可以不填，默认是1)
注:
角色碎片可以通过每日副本掉落
碎片掉落详解：
    1.必定掉落固定数量的万能碎片
    2.碎片掉落本次进入战斗的角色的碎片，角色碎片数量上限固定
升星提升战力：
    星级只加成角色等级增加的基础战力，目前最高5星
    1星增加战力的1.1倍
    2星增加战力的1.3倍
    3星增加战力的1.7倍
    4星增加战力的2倍
    5星增加战力的2.5倍
╚                                        ╝
 '''
    await bot.send(ev, msg)
    
    
@sv.on_prefix(['角色转生'])
async def card_zhuansheng(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    duel = DuelCounter()
    if len(args)!=1:
        await bot.finish(ev, '请输入 角色转生+女友名 中间用空格隔开。', at_sender=True)
    name = args[0]
    cid = chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的女友名。', at_sender=True)
    cidlist = duel._get_cards(gid, uid)
    if cid not in cidlist:
        await bot.finish(ev, '该女友不在你的身边哦。', at_sender=True)
    zllevel = CE._get_zhuansheng(gid,uid,cid)
    MAX_ZS = 5
    if zllevel==MAX_ZS:
        await bot.finish(ev, '该女友已经到最高转生等级，无法继续转生啦。', at_sender=True)
    new_zl = zllevel + 1

    nvmes = get_nv_icon(cid)
    up_info = duel._get_fashionup(gid,uid,cid,0)
    fashion_ce=0
    up_icon=''
    if up_info:
        #获取穿戴时装所加的战斗力   
        fashion_info = get_fashion_info(up_info)
        up_icon = fashion_info['icon']
    if up_icon:
        nvmes=up_icon
    level_info = CE._get_card_level(gid, uid, cid)
    rank = CE._get_rank(gid, uid, cid)
    if level_info>=100 and rank>=10:
        CE._set_card_exp(gid,uid,cid)
        CE._add_rank(gid,uid,cid)
        CE._add_zhuansheng(gid,uid,cid)
        await bot.send(ev, f'转生成功！\n您的女友{name}成功进行了{new_zl}转，等级变成了0级，rank变成了0级，基础战力加成提升了{nvmes}', at_sender=True)
    else:
        await bot.finish(ev, f'转生需要角色等级>=100，RANK>=10哦。您没有达到转生条件', at_sender=True)
    






