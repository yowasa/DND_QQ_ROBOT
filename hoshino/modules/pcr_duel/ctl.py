from hoshino.typing import CQEvent
from hoshino.typing import CommandSession
from hoshino import Service
from .duelconfig import *
from hoshino.modules.pcr_duel import duel_chara

UNKNOWN = 1000

sv = Service('贵族调整', enable_on_default=False, bundle='贵族游戏', help_=
"""[测试帮助]查看相关帮助
""")

# 测试专用命令
@sv.on_fullmatch(['测试帮助'])
async def manor_help(bot, ev: CQEvent):
    msg = '''
╔                                        ╗
             贵族调整帮助
[变更性格] {角色名} {性格}
[变更技能] {角色名}
[变更偏好] {角色名} {0-100的数值} 越接近0越偏攻 越接近100越偏防
[添加羁绊] {角色名}
[清除羁绊] {角色名}
╚                                        ╝
 '''
    await bot.send(ev, msg)


# @sv.on_fullmatch(['快进一天'])
# async def manor_begin(bot, ev: CQEvent):
#     gid = ev.group_id
#     uid = ev.user_id
#     guid = gid, uid
#     # 副本 签到 低保 约会 决斗 礼物 城市
#     daily_dun_limiter.reset(guid)
#     daily_sign_limiter.reset(guid)
#     daily_zero_get_limiter.reset(guid)
#     daily_date_limiter.reset(guid)
#     daily_duel_limiter.reset(guid)
#     daily_gift_limiter.reset(guid)
#     daily_boss_limiter.reset(guid)
#     daily_manor_limiter.reset(guid)
#     daily_recruit_limiter.reset(guid)
#     daily_stage_limiter.reset(guid)
#     key_gid = gid + 999
#     gkuid = key_gid, uid
#     daily_boss_limiter.reset(gkuid)
#     # 清除boss限制
#     nowyear = datetime.now().year
#     nowmonth = datetime.now().month
#     nowday = datetime.now().day
#     fighttime = str(nowyear) + str(nowmonth) + str(nowday)
#     duel = DuelCounter()
#     CE = CECounter()
#     cidlist = duel._get_cards(gid, uid)
#     for cid in cidlist:
#         CE._del_cardfightinfo(gid, uid, cid, fighttime, 0)
#         CE._del_cardfightinfo(gid, uid, cid, fighttime, 1)
#
#     day = get_user_counter(gid, uid, UserModel.TEST_DAY)
#     day += 1
#     save_user_counter(gid, uid, UserModel.TEST_DAY, day)
#     await bot.send(ev, f'已经刷新所有限制,当前快进天数为{day}', at_sender=True)
#
#
# @sv.on_fullmatch(['进度查询'])
# async def manor_begin(bot, ev: CQEvent):
#     gid = ev.group_id
#     uid = ev.user_id
#     day = get_user_counter(gid, uid, UserModel.TEST_DAY)
#     await bot.send(ev, f'当前快进天数为{day}', at_sender=True)


@sv.on_command("变更技能")
async def change_skill(session: CommandSession):
    bot = session.bot
    ev = session.event
    search_name = session.get('search_name', prompt="请输入要变更技能的角色名")

    chara_id = duel_chara.name2id(search_name)
    if chara_id == UNKNOWN:
        await bot.send(ev, f'未查询到名称为{search_name}的女友信息')
        return

    # 请输入要添加的羁绊信息
    skill_names = session.get('skill_names', prompt="请输入技能名称 用空格隔开")
    skill_li = str(skill_names).strip().split(" ")
    if len(skill_li) != len(set(skill_li)):
        await bot.send(ev, '包含重复技能', at_sender=True)
        return
    for i in skill_li:
        if not skill_def_json.get(i):
            await bot.send(ev, f'找不到技能{i}', at_sender=True)
            return
    char_skill_json[str(chara_id)] = skill_li
    # 持久化
    refresh_char_skill()
    await bot.send(ev, '变更技能成功，使用购买情报查询', at_sender=True)


@sv.on_prefix(['变更性格'])
async def manor_begin(bot, ev: CQEvent):
    msg = str(ev.message).strip().split(" ")
    if not msg:
        await bot.finish(ev, '请在指令后添加角色名', at_sender=True)
    if len(msg) != 2:
        await bot.finish(ev, '请使用[变更偏好] {角色名} {性格} 性格在性格列表中查询', at_sender=True)
    char_name = msg[0]
    xingge = msg[1]
    if not character.get(xingge):
        await bot.finish(ev, f'找不到名为【{xingge}】的性格', at_sender=True)
    chara_id = duel_chara.name2id(char_name)
    if chara_id == UNKNOWN:
        await bot.finish(ev, f'未查询到名称为{msg}的女友信息')
    char_character_json[str(chara_id)] = [xingge]
    # 持久化
    refresh_char_character()
    await bot.send(ev, '变更性格成功，使用购买情报查询', at_sender=True)


@sv.on_prefix(['变更偏好'])
async def manor_begin(bot, ev: CQEvent):
    msg = str(ev.message).strip().split(" ")
    if not msg:
        await bot.finish(ev, '请在指令后添加角色名', at_sender=True)
    if len(msg) != 2:
        await bot.finish(ev, '请使用[变更偏好] {角色名} {0-100的数值} 越接近0越偏攻 越接近100越偏防', at_sender=True)
    char_name = msg[0]
    pian = int(msg[1])
    if pian > 100 or pian < 0:
        await bot.finish(ev, '攻守偏好只能在0-100之间', at_sender=True)
    chara_id = duel_chara.name2id(char_name)
    if chara_id == UNKNOWN:
        await bot.finish(ev, f'未查询到名称为{msg}的女友信息')
    char_style_json[str(chara_id)] = pian
    # 持久化
    refresh_char_style()
    await bot.send(ev, '变更偏好成功，使用购买情报查询', at_sender=True)


@sv.on_command("添加羁绊")
async def dun_adj(session: CommandSession):
    bot = session.bot
    ev = session.event
    search_name = session.get('search_name', prompt="请输入要添加羁绊的角色名")

    chara_id = duel_chara.name2id(search_name)
    if chara_id == UNKNOWN:
        await bot.finish(ev, f'未查询到名称为{search_name}的女友信息')

    # 请输入要添加的羁绊信息
    chetter_names = session.get('chetter_names', prompt="请输入羁绊角色 用空格隔开")
    defen, unknown = chara.roster.parse_team(str(chetter_names))
    if unknown:
        _, name, score = chara.guess_id(unknown)
        if score < 70 and not defen:
            return  # 忽略无关对话
        msg = f'无法识别"{unknown}"' if score < 70 else f'无法识别"{unknown}" 您说的有{score}%可能是{name}'
        await bot.send(ev, msg)
        return
    if len(defen) > 4:
        await bot.send(ev, '羁绊角色不能超过4名', at_sender=True)
        return
    if len(defen) != len(set(defen)):
        await bot.send(ev, '羁绊中包含重复角色', at_sender=True)
        return
    if not char_fetter_json.get(str(chara_id)):
        char_fetter_json[str(chara_id)] = []
    char_fetter_json[str(chara_id)].append(defen)
    # 持久化
    refresh_char_fetter()
    await bot.send(ev, '添加羁绊成功，使用购买情报查询', at_sender=True)


@sv.on_prefix(['清除羁绊'])
async def manor_begin(bot, ev: CQEvent):
    msg = str(ev.message).strip()
    if not msg:
        await bot.finish(ev, '请在指令后添加角色名', at_sender=True)
    chara_id = duel_chara.name2id(msg)
    if chara_id == UNKNOWN:
        await bot.finish(ev, f'未查询到名称为{msg}的女友信息')
    if char_fetter_json.get(str(chara_id)):
        del char_fetter_json[str(chara_id)]
    # 持久化
    refresh_char_fetter()
    await bot.send(ev, '清除羁绊成功，使用购买情报查询', at_sender=True)


@change_skill.args_parser
async def _(session: CommandSession):
    text = session.current_arg_text
    img = session.current_arg_images
    if session.is_first_run:
        if text:
            session.state['search_name'] = text.strip()
        return
    if img:
        session.state[session.current_key] = img
    else:
        session.state[session.current_key] = text


@dun_adj.args_parser
async def _(session: CommandSession):
    text = session.current_arg_text
    img = session.current_arg_images
    if session.is_first_run:
        if text:
            session.state['search_name'] = text.strip()
        return
    if img:
        session.state[session.current_key] = img
    else:
        session.state[session.current_key] = text
