from hoshino.typing import CQEvent
from . import sv
from .battle import *


@sv.on_fullmatch(['pvp帮助'])
async def pvp_help(bot, ev: CQEvent):
    msg = '''
╔                                        ╗  
             pvp帮助
[设置pvp队伍] {角色列表/队伍名}
[发动pvp技能] {技能列表}
[查看pvp队伍]
[取消pvp队伍]
[pvp]@群友

仅双方均设pvp队伍时可以进行pvp战斗
pvp时双方sp+10(默认氪蓝药)
获胜失败暂无奖惩
╚                                        ╝
 '''.strip()
    await bot.send(ev, msg)


@sv.on_prefix(['设置pvp队伍'])
async def set_pvp_group(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    defen = str(ev.message).strip().strip()
    if not defen:
        await bot.finish(ev, "请在后面追加队伍名或者用空格隔开的角色名列表")
    # 查询是否是队伍
    CE = CECounter()
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
    # 获取编队战力与信息
    duel = DuelCounter()
    for cid in defen:
        c = chara.fromid(cid)
        nvmes = get_nv_icon(cid)
        owner = duel._get_card_owner(gid, cid)
        if owner == 0:
            await bot.send(ev, f'{c.name}现在还是单身哦，快去约到她吧。{nvmes}', at_sender=True)
            return
        if uid != owner:
            msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法编队哦。'
            await bot.send(ev, msg)
            return
    bianzu = ''
    charalist = []
    for cid in defen:
        c = chara.fromid(cid)
        bianzu = bianzu + f"{c.name} "
        star = CE._get_cardstar(gid, uid, cid)
        charalist.append(chara.Chara(cid, star, 0))
    my = duel_my_buff(gid, uid, defen)
    duel._save_pvp_info(gid, uid, defen,my.all_skill)
    res = chara.gen_team_pic(charalist, star_slot_verbose=False)
    bio = BytesIO()
    res.save(bio, format='PNG')
    base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
    mes = f"[CQ:image,file={base64_str}]"
    buff_msg = f"boost:{my.boost}% 暴击:{my.crit}% 连击:{my.double}% 回复:{my.recover}% 闪避:{my.dodge}%"
    msg = f"设置pvp队伍成功！\n队伍成员为：{bianzu}\nhp:{my.hp} atk:{my.atk} sp:{my.sp} \nskill:{' '.join(my.all_skill)}\n{buff_msg}\n{mes}"
    await bot.send(ev, msg, at_sender=True)

@sv.on_prefix(['发动pvp技能'])
async def set_pvp_group(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg = str(ev.message).strip()
    # 校验人员完整
    duel = DuelCounter()
    defen = duel._select_pvp_info(gid, uid)
    if not defen:
        await bot.finish(ev, "你尚未设置pvp队伍，请使用[设置pvp队伍]进行设置")
    CE = CECounter()
    for cid in defen:
        c = chara.fromid(cid)
        nvmes = get_nv_icon(cid)
        owner = duel._get_card_owner(gid, cid)
        if owner == 0:
            await bot.send(ev, f'{c.name}现在还是单身哦，快去约到她吧。{nvmes}', at_sender=True)
            return
        if uid != owner:
            msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法进入关卡'
            await bot.send(ev, msg)
            return
    if not msg:
        duel._save_pvp_info(gid, uid, defen, [])
        await bot.send(ev, "已取消发动的所有技能")
        return
    my = duel_my_buff(gid, uid, defen)
    msg_li = str(msg).split(" ")
    for i in msg_li:
        if not skill_def_json.get(i):
            await bot.send(ev, f"未找到名为{i}的技能")
            return
        if i not in my.all_skill:
            await bot.send(ev, f"发动技能失败，你队伍中没有会{i}技能的角色,请使用 '发动技能 空格隔开的技能名' 重新设定")
            return
    duel._save_pvp_info(gid, uid, defen, msg_li)
    await bot.send(ev, "发动技能成功", at_sender=True)

@sv.on_prefix(['查看pvp队伍'])
async def set_pvp_group(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    CE = CECounter()
    defen = duel._select_pvp_info(gid, uid)
    if not defen:
        await bot.finish(ev, "你尚未设置pvp队伍，请使用[设置pvp队伍]进行设置")
    bianzu = ''
    charalist = []
    for cid in defen:
        c = chara.fromid(cid)
        bianzu = bianzu + f"{c.name} "
        star = CE._get_cardstar(gid, uid, cid)
        charalist.append(chara.Chara(cid, star, 0))
    my = duel_my_buff(gid, uid, defen)
    skills=duel._select_pvp_skills(gid, uid)
    res = chara.gen_team_pic(charalist, star_slot_verbose=False)
    bio = BytesIO()
    res.save(bio, format='PNG')
    base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
    mes = f"[CQ:image,file={base64_str}]"
    buff_msg = f"boost:{my.boost}% 暴击:{my.crit}% 连击:{my.double}% 回复:{my.recover}% 闪避:{my.dodge}%"
    msg = f"\n队伍成员为：{bianzu}\nhp:{my.hp} atk:{my.atk} sp:{my.sp} \n发动中的技能:{' '.join(skills)}\n拥有技能:{' '.join(my.all_skill)}\n{buff_msg}\n{mes}"
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['取消pvp队伍'])
async def set_pvp_group(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    cids = duel._select_pvp_info(gid, uid)
    if not cids:
        await bot.finish(ev, "你尚未设置pvp队伍，无需取消")
    duel._del_pvp_info(gid, uid)
    await bot.send(ev, "取消成功", at_sender=True)

@sv.on_prefix(['pvp'])
async def pvp(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if ev.message[0].type == 'at':
        id2 = int(ev.message[0].data['qq'])
    else:
        await bot.finish(ev, '参数格式错误, 请重试')
    duel = DuelCounter()
    cids1 = duel._select_pvp_info(gid, uid)
    if not cids1:
        await bot.finish(ev, "你尚未设置pvp队伍，无法pvp")
    cids2 = duel._select_pvp_info(gid, id2)
    if not cids1:
        await bot.finish(ev, "对方尚未设置pvp队伍，无法pvp")
    my = duel_my_buff(gid, uid, cids1)
    my.sp += 10
    skill1 = duel._select_pvp_skills(gid, uid)
    # 获取发动技能
    skill1=[i for i in skill1 if i in my.all_skill]
    for i in skill1:
        if my.sp > skill_def_json[i]["sp"]:
            my.sp -= skill_def_json[i]["sp"]
            my.skill.append(i)
    enemy = duel_my_buff(gid, id2, cids2)
    enemy.sp += 10
    # 获取发动技能
    skill2 = duel._select_pvp_skills(gid, id2)
    # 获取发动技能
    skill2 = [i for i in skill2 if i in my.all_skill]
    for i in skill2:
        if enemy.sp > skill_def_json[i]["sp"]:
            enemy.sp -= skill_def_json[i]["sp"]
            enemy.skill.append(i)
    result, log = battle(my, enemy)
    tas_list = []
    msg = f"战斗{'胜利' if result else '失败'}!"
    data = {
        "type": "node",
        "data": {
            "name": "ご主人様",
            "uin": "1587640710",
            "content": msg
        }
    }
    tas_list.append(data)
    tas_list.extend(build_battle_tag_list(log))
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)
