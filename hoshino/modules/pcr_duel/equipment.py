from hoshino.typing import CQEvent
from . import sv
from .duelconfig import *


@sv.on_fullmatch(['装备帮助'])
async def star_help(bot, ev: CQEvent):
    msg = '''
╔                                        ╗  
             装备帮助
[我的装备]
[查装备] {装备名称}
[穿装备] {女友名} {装备名}
[取消装备] {女友名} {装备名}
[一键卸装] {女友名}
[一键装备] {女友名} 
[装备池][查看保底]
[抽装备(单抽/十连)] {装备池名称} 10副本币一次
[装备分解] {装备名}
[一键分解] {装备品级N/R/SR/SSR/UR/MR}
[星尘兑换] {UP的装备名称}
[兑换戒指] (永恒的守护|世世的相随)
╚                                        ╝
 '''.strip()
    await bot.send(ev, msg)


@sv.on_fullmatch(['装备列表', '我的装备'])
async def my_equip_list(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    CE = CECounter()
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过角色，请发送 创建角色 开始你的人生旅途。'
        await bot.send(ev, msg, at_sender=True)
        return
    equip_list = CE._get_equip_list(gid, uid)
    if len(equip_list) > 0:
        msg_list = '我的装备列表：'
        equipinfo_li = []
        for i in equip_list:
            equipinfo = get_equip_info_id(i[0])
            equipinfo["num"] = i[1]
            equipinfo_li.append(equipinfo)
        equipinfo_li = sorted(equipinfo_li, key=lambda x: ['N', 'R', 'SR', 'SSR', 'UR', 'MR'].index(x['model']),
                              reverse=True)
        for equipinfo in equipinfo_li:
            msg_list = msg_list + f"\n{equipinfo['type']}:({equipinfo['model']}){equipinfo['name']}:{equipinfo['num']}件"
        await bot.send(ev, msg_list, at_sender=True)
    else:
        await bot.finish(ev, '您还没有获得装备哦。', at_sender=True)


@sv.on_prefix(['查装备', '装备信息'])
async def xiulian_start(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    if len(args) != 1:
        await bot.finish(ev, '请输入 查装备+装备名称。', at_sender=True)
    name = args[0]
    info = get_equip_info_name(name)
    await bot.send(ev, '\n' + info['desc'], at_sender=True)


@sv.on_prefix(['穿装备', '穿戴装备'])
async def dress_equip(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    CE = CECounter()
    if len(args) != 2:
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
    if not equipinfo:
        await bot.finish(ev, '请输入正确的装备名。', at_sender=True)
    c = chara.fromid(cid)
    if CE._get_equip_num(gid, uid, equipinfo['eid']) == 0:
        await bot.finish(ev, '你的这件装备的库存不足哦。', at_sender=True)
    now_level = CE._get_card_level(gid, uid, cid)
    need_level = EquipLevelLimit[equipinfo['level']]
    if now_level < need_level:
        await bot.finish(ev, f'你的角色等级不足以装备这件装备。（需要{need_level}级，当前为{now_level}级）', at_sender=True)
    # 获取当前穿戴的装备
    now_dress = CE._get_dress_info(gid, uid, cid, equipinfo['type_id'])
    # 保存数据库
    CE._dress_equip(gid, uid, cid, equipinfo['type_id'], equipinfo['eid'])
    # 可用装备减一
    CE._add_equip(gid, uid, equipinfo['eid'], -1)
    if now_dress > 0:
        now_equipinfo = get_equip_info_id(now_dress)
        # 替换的装备数量增加
        CE._add_equip(gid, uid, now_dress, 1)
        msg_x = f"取消了{equipinfo['type']}部位的装备{now_equipinfo['name']}，穿上了装备{equipinfo['name']}"
    else:
        msg_x = f"穿上了{equipinfo['type']}部位的装备{equipinfo['name']}"
    nvmes = get_nv_icon(cid)
    up_info = duel._get_fashionup(gid, uid, cid, 0)
    if up_info:
        fashion_info = get_fashion_info(up_info)
        nvmes = fashion_info['icon']
    msg = f"您为您的女友{c.name}，{msg_x}\n{nvmes}"
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['取消装备'])
async def dress_equip(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    if len(args) != 2:
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
    if len(equipinfo) > 0:
        c = chara.fromid(cid)
        CE = CECounter()
        now_dress = CE._get_dress_info(gid, uid, cid, equipinfo['type_id'])
        if now_dress > 0:
            now_equipinfo = get_equip_info_id(now_dress)
            if now_dress == equipinfo['eid']:
                # 保存数据库
                CE._dress_equip(gid, uid, cid, equipinfo['type_id'], 0)
                # 可用装备加一
                CE._add_equip(gid, uid, equipinfo['eid'], 1)

                msg_x = f"取消了{equipinfo['type']}部位的装备{equipinfo['name']}"
                nvmes = get_nv_icon(cid)
                up_info = duel._get_fashionup(gid, uid, cid, 0)
                if up_info:
                    fashion_info = get_fashion_info(up_info)
                    nvmes = fashion_info['icon']
                msg = f"您为您的女友{c.name}，{msg_x}\n{nvmes}"
                await bot.send(ev, msg, at_sender=True)
            else:
                msg = f"您的女友{c.name}，当前{equipinfo['type']}部位穿戴的装备是{now_equipinfo['name']}，不是{equipinfo['name']}哦！"
                await bot.finish(ev, msg, at_sender=True)
        else:
            await bot.finish(ev, f"您的女友{c.name}当前{equipinfo['type']}部位未穿戴装备哦。", at_sender=True)
    else:
        await bot.finish(ev, '请输入正确的装备名。', at_sender=True)


@sv.on_prefix(['一键卸装', '一键取消'])
async def quxiao_equip(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    CE = CECounter()
    if len(args) != 1:
        await bot.finish(ev, '请输入 一件穿戴+女友名 中间用空格隔开。', at_sender=True)
    name = args[0]
    cid = chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的女友名。', at_sender=True)
    cidlist = duel._get_cards(gid, uid)
    if cid not in cidlist:
        await bot.finish(ev, '该女友不在你的身边哦。', at_sender=True)
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过角色，请发送 创建角色 开始你的人生旅途。'
        await bot.finish(ev, msg, at_sender=True)
    c = chara.fromid(cid)
    nvmes = get_nv_icon(cid)
    dreeslist = CE._get_dress_list(gid, uid, cid)
    if len(dreeslist) > 0:
        msg = ''
        for eid in dreeslist:
            equipinfo = get_equip_info_id(eid)
            if equipinfo:
                # 保存数据库
                CE._dress_equip(gid, uid, cid, equipinfo['type_id'], 0)
                # 替换的装备数量增加
                CE._add_equip(gid, uid, equipinfo['eid'], 1)
                msg = msg + f"取消了{equipinfo['type']}部位的装备({equipinfo['model']}){equipinfo['name']}\n"
        await bot.send(ev, f"您为您的女友{c.name}\n{msg}{nvmes}", at_sender=True)
    else:
        await bot.finish(ev, f"您的女友{c.name}目前没有穿戴的装备哦\n{nvmes}", at_sender=True)


@sv.on_prefix(['一键装备', '一键穿戴'])
async def dress_equip_list_r(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    CE = CECounter()
    if len(args) != 1:
        await bot.finish(ev, '请输入 一键装备+女友名 中间用空格隔开。', at_sender=True)
    name = args[0]
    cid = chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的女友名。', at_sender=True)
    cidlist = duel._get_cards(gid, uid)
    if cid not in cidlist:
        await bot.finish(ev, '该女友不在你的身边哦。', at_sender=True)
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过角色，请发送 创建角色 开始你的人生旅途。'
        await bot.send(ev, msg, at_sender=True)
        return

    level = CE._get_card_level(gid, uid, cid)
    needlevel = (level / 10) + 1
    equip_list = CE._get_equip_list(gid, uid)
    # 记录不同部位的品质最高装备的品质和eid
    emax = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
    if len(equip_list) > 0:
        for i in equip_list:
            equipinfo = get_equip_info_id(i[0])
            if equipinfo['type_id'] == 1 and equipinfo['level'] <= needlevel and equipinfo['level'] > emax[0][0]:
                emax[0] = [equipinfo['level'], i[0]]
            elif equipinfo['type_id'] == 2 and equipinfo['level'] <= needlevel and equipinfo['level'] > emax[1][0]:
                emax[1] = [equipinfo['level'], i[0]]
            elif equipinfo['type_id'] == 3 and equipinfo['level'] <= needlevel and equipinfo['level'] > emax[2][0]:
                emax[2] = [equipinfo['level'], i[0]]
            elif equipinfo['type_id'] == 4 and equipinfo['level'] <= needlevel and equipinfo['level'] > emax[3][0]:
                emax[3] = [equipinfo['level'], i[0]]
            elif equipinfo['type_id'] == 5 and equipinfo['level'] <= needlevel and equipinfo['level'] > emax[4][0]:
                emax[4] = [equipinfo['level'], i[0]]
    else:
        await bot.finish(ev, '您还没有获得装备哦。', at_sender=True)
    c = chara.fromid(cid)
    nvmes = get_nv_icon_with_fashion(gid, uid, cid)
    msg = ''
    for y in emax:
        if y[1] > 0:
            # 获取当前穿戴的装备
            equipinfo = get_equip_info_id(y[1])
            now_dress = CE._get_dress_info(gid, uid, cid, equipinfo['type_id'])
            if now_dress > 0:
                now_equipinfo = get_equip_info_id(now_dress)
                if now_equipinfo['level'] < y[0]:
                    # 保存数据库
                    CE._dress_equip(gid, uid, cid, equipinfo['type_id'], equipinfo['eid'])
                    # 可用装备减一
                    CE._add_equip(gid, uid, equipinfo['eid'], -1)
                    # 替换的装备数量增加
                    CE._add_equip(gid, uid, now_dress, 1)
                    msg = msg + f"取消了{equipinfo['type']}部位的装备({now_equipinfo['model']}){now_equipinfo['name']}，穿上了装备({equipinfo['model']}){equipinfo['name']}\n"
                else:
                    msg = msg + f"{equipinfo['type']}部位已穿戴同等或更高等级的装备({now_equipinfo['model']}){now_equipinfo['name']}，无替换\n"
            else:
                # 保存数据库
                CE._dress_equip(gid, uid, cid, equipinfo['type_id'], equipinfo['eid'])
                # 可用装备减一
                CE._add_equip(gid, uid, equipinfo['eid'], -1)
                msg = msg + f"穿上了{equipinfo['type']}部位的装备({equipinfo['model']}){equipinfo['name']}\n"
    await bot.send(ev, f"您为您的女友{c.name}\n{msg}{nvmes}", at_sender=True)


@sv.on_fullmatch(['查看武器池', '武器池', '装备池'])
async def get_equipgecha(bot, ev: CQEvent):
    gechalist = Gecha
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
            if level == '2':
                gl_name = 'R'
            if level == '3':
                gl_name = 'SR'
            if level == '4':
                gl_name = 'SSR'
            if level == '5':
                gl_name = 'UR'
            gl_list = gl_list + f"{gl_name}:{gechalist[gecha]['gecha']['quality'][level]}%\n"
        meg = meg + f"概率公示：\n{gl_list}"
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content": meg
            }
        }
        tas_list.append(data)

    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)


@sv.on_fullmatch(['我的保底', '查看保底'])
async def get_my_baodi(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    bdinfo = CE._get_gecha_num(gid, uid)
    xnum = bdinfo[0]  # 10连小保底进度
    last_xnum = 10 - xnum
    dnum = bdinfo[1]  # 大保底进度
    last_dnum = 100 - dnum
    unum = bdinfo[2]  # 大保底进度
    last_unum = 200 - unum
    msg = f"""
品级:SR 抽奖次数:{xnum} 保底次数:{last_xnum}
品级:SSR 抽奖次数:{dnum} 保底次数:{last_dnum}
品级:UR 抽奖次数:{unum} 保底次数:{last_unum}"""
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['抽装备'])
async def add_equip_gecha(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    if len(args) != 2:
        await bot.finish(ev, '请输入 抽装备+(单抽/十连)+装备池名称 中间用空格隔开。', at_sender=True)
    if args[0] == '单抽':
        gechanum = 1
    elif args[0] == '十连':
        gechanum = 10
    else:
        await bot.finish(ev, '请输入正确的抽取数量（单抽/十连）。', at_sender=True)
    if args[1] == '':
        await bot.finish(ev, '请输入装备池名称。', at_sender=True)
    need_dunscore = GECHA_DUNDCORE * gechanum
    myscore = CE._get_dunscore(gid, uid)
    if need_dunscore > myscore:
        await bot.finish(ev, f'您的副本币不足{need_dunscore}，无法抽卡哦。', at_sender=True)
    gechainfo = get_gecha_info(args[1])
    if gechainfo['name']:
        bdinfo = CE._get_gecha_num(gid, uid)
        xnum = bdinfo[0]  # 10连小保底进度
        dnum = bdinfo[1]  # 大保底进度
        unum = bdinfo[2]  # 大保底进度
        getequip = get_gecha_equip(gid, uid, gechanum, xnum, dnum, unum, gechainfo)
        last_score = myscore - need_dunscore
        need_score = 0 - need_dunscore
        CE._add_dunscore(gid, uid, need_score)
        msg = f"消耗{need_dunscore}副本币，剩余副本币{last_score}\n，已加入经验池\n本次{args[0]}获得的装备为：{getequip}"
        counter = get_user_counter(gid, uid, UserModel.CHOU)
        counter += gechanum
        if counter >= 100:
            counter = 0
            rn = random.randint(1, 10)
            if rn == 1:
                item = get_item_by_name('空想之物')
                add_item(gid, uid, item)
                msg += f"\n你在抽取装备的时候抽到了一个神秘的宝箱，获得了{item['rank']}级道具{item['name']}"
        save_user_counter(gid, uid, UserModel.CHOU, counter)
        await bot.send(ev, msg, at_sender=True)
    else:
        await bot.finish(ev, '请输入正确的武器池名称。', at_sender=True)


@sv.on_prefix(['装备分解', '分解装备'])
async def equip_fenjie_one(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    if len(args) != 1:
        await bot.finish(ev, '请输入 装备分解+装备名称 中间用空格隔开。', at_sender=True)
    equipinfo = get_equip_info_name(args[0])
    if len(equipinfo) > 0:
        equipnum = CE._get_equip_num(gid, uid, equipinfo['eid'])
        if equipnum == 0:
            await bot.finish(ev, '你的这件装备的库存不足哦。', at_sender=True)
        fj_one = FenjieGet[equipinfo['level']]
        get_xcz = fj_one * equipnum
        now_num = CE._add_xingchen_num(gid, uid, get_xcz)
        deletenum = 0 - equipnum
        ex_msg = ''
        counter = get_user_counter(gid, uid, UserModel.FENJIE)
        counter += equipnum
        if counter >= 100:
            counter = 0
            rn = random.randint(1, 10)
            if rn == 1:
                item = get_item_by_name('贤者之石')
                add_item(gid, uid, item)
                ex_msg += f"\n你在分解装备的时候熔炉发生了爆炸，在残骸中发现了{item['rank']}级道具{item['name']}"
        save_user_counter(gid, uid, UserModel.FENJIE, counter)
        CE._add_equip(gid, uid, equipinfo['eid'], deletenum)

        msg = f"您成功分解了{equipnum}件{equipinfo['model']}级装备，获得了{get_xcz}星尘，目前星尘数量为{now_num}" + ex_msg
        await bot.send(ev, msg, at_sender=True)
    else:
        await bot.finish(ev, '请输入正确的装备名。', at_sender=True)


@sv.on_prefix(['一键分解'])
async def equip_fenjie_n(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    if len(args) != 1:
        await bot.finish(ev, '请输入 装备分解+装备等级(N/R/SR/SSR/UR/MR) 中间用空格隔开。', at_sender=True)
    modelname = args[0]
    model_li = ["N", "R", "SR", "SSR", "UR", "MR"]
    if modelname not in model_li:
        await bot.finish(ev, '请输入正确的装备等级(N/R/SR/SSR/UR/MR)。', at_sender=True)
    equiplevel = model_li.index(modelname) + 1
    equip_list = CE._get_equip_list(gid, uid)
    if len(equip_list) > 0:
        msg_list = ''
        xingchen = 0
        total_equipnum = 0
        for i in equip_list:
            equipinfo = get_equip_info_id(i[0])
            if equipinfo['level'] == equiplevel:
                equipnum = i[1]
                fj_one = FenjieGet[equipinfo['level']]
                get_xcz = fj_one * equipnum
                total_equipnum += equipnum
                xingchen += get_xcz
                deletenum = 0 - equipnum
                CE._add_equip(gid, uid, equipinfo['eid'], deletenum)
                msg_list = msg_list + f"\n{equipnum}件{equipinfo['model']}级装备,{equipinfo['name']}"
        ex_msg = ''
        counter = get_user_counter(gid, uid, UserModel.FENJIE)
        counter += total_equipnum
        if counter >= 100:
            counter = 0
            rn = random.randint(1, 10)
            if rn == 1:
                item = get_item_by_name('贤者之石')
                add_item(gid, uid, item)
                ex_msg += f"\n你在分解装备的时候熔炉发生了爆炸，在残骸中发现了{item['rank']}级道具{item['name']}"
        save_user_counter(gid, uid, UserModel.FENJIE, counter)
        if xingchen > 0:
            now_num = CE._add_xingchen_num(gid, uid, xingchen)
            msg = f"分解成功，您分解了{msg_list}\n一共获得了{xingchen}星尘，目前星尘数量为{now_num}" + ex_msg
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
    if len(args) != 1:
        await bot.finish(ev, '请输入 星尘兑换+UP的武器名称 中间用空格隔开。', at_sender=True)
    xc_num = CE._get_xingchen_num(gid, uid)
    if xc_num < 100:
        await bot.finish(ev, f'您的星尘剩余{xc_num}，不足100，无法兑换哦。', at_sender=True)
    equipinfo = get_equip_info_name(args[0])
    if len(equipinfo) > 0:
        eid = equipinfo['eid']
        gechalist = Gecha
        find_flag = 0
        for gecha in gechalist:
            if eid in gechalist[gecha]['up_equip']:
                find_flag = 1
                break
        if find_flag == 0:
            await bot.finish(ev, f'{args[0]}目前没有UP哦。', at_sender=True)
        now_num = CE._add_xingchen_num(gid, uid, -100)
        CE._add_equip(gid, uid, equipinfo['eid'], 1)
        msg = f"您消耗了100星尘，成功兑换了装备{args[0]}，剩余星尘{now_num}"
        await bot.send(ev, msg, at_sender=True)
    else:
        await bot.finish(ev, '请输入正确的装备名称。', at_sender=True)


@sv.on_prefix(['兑换戒指'])
async def xingchen_jz(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    if len(args) != 1:
        await bot.finish(ev, '请输入 兑换戒指+戒指名称[永恒的守护/世世的相随] 中间用空格隔开。', at_sender=True)
    xc_num = CE._get_xingchen_num(gid, uid)
    if xc_num < 500:
        await bot.finish(ev, f'您的星尘剩余{xc_num}，不足500，无法兑换哦。', at_sender=True)
    equipinfo = get_equip_info_name(args[0])
    if len(equipinfo) > 0:
        now_num = CE._add_xingchen_num(gid, uid, -500)
        CE._add_equip(gid, uid, equipinfo['eid'], 1)
        msg = f"您消耗了500星尘，成功兑换了戒指 {args[0]}，剩余星尘{now_num}"
        await bot.send(ev, msg, at_sender=True)
    else:
        await bot.finish(ev, '请输入正确的装备名称。', at_sender=True)
