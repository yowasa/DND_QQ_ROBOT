from hoshino.typing import CQEvent
from hoshino.typing import CommandSession
from . import duel_chara
from . import sv
from .ScoreCounter import ScoreCounter2
from .duelconfig import *


# 测试专用命令
@sv.on_fullmatch(['测试帮助'])
async def manor_help(bot, ev: CQEvent):
    msg = '''
╔                                        ╗
             测试帮助
[快速决斗] 模拟进行一次决斗 直接获得收益
[快进一天] 快进一天
[进度查询] 查看当前快进进度
[调整副本] 调整副本数值
╚                                        ╝
 '''
    await bot.send(ev, msg)


@sv.on_fullmatch(['快进一天'])
async def manor_begin(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    guid = gid, uid
    # 副本 签到 低保 约会 决斗 礼物 城市
    daily_dun_limiter.reset(guid)
    daily_sign_limiter.reset(guid)
    daily_zero_get_limiter.reset(guid)
    daily_date_limiter.reset(guid)
    daily_duel_limiter.reset(guid)
    daily_gift_limiter.reset(guid)
    daily_boss_limiter.reset(guid)
    daily_manor_limiter.reset(guid)
    daily_recruit_limiter.reset(guid)
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

    day = get_user_counter(gid, uid, UserModel.TEST_DAY)
    day += 1
    save_user_counter(gid, uid, UserModel.TEST_DAY, day)
    await bot.send(ev, f'已经刷新所有限制,当前快进天数为{day}', at_sender=True)


@sv.on_fullmatch(['进度查询'])
async def manor_begin(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    day = get_user_counter(gid, uid, UserModel.TEST_DAY)
    await bot.send(ev, f'当前快进天数为{day}', at_sender=True)


YIN_NAME_LI = ["好感", "需求战力", "金币", "声望", "经验", "万能碎片", "随机碎片", "副本币"]
YIN_KEY_LI = ["add_favor", "recommend_ce_adj", "gold_adj", "sw_adj", "add_exp_adj", "fragment_w_adj",
              "fragment_c_adj", "dun_score_adj"]
NAN_LI = ["简单", "困难", "地狱"]


@sv.on_command("调整副本")
async def dun_adj(session: CommandSession):
    bot = session.bot
    ev = session.event
    dun_name = session.get('dun_name', prompt="请输入要修改的副本名")
    with open('/Users/yowasa/workspace/DND_QQ_ROBOT/hoshino/modules/pcr_duel/dungeon.json', 'r',
              encoding='UTF-8') as fa:
        dungeonlist = json.load(fa, strict=False)

    findnum = 0
    for dungeon in dungeonlist:
        if str(dun_name) == str(dungeonlist[dungeon]['name']):
            findnum = dungeon
            break
    if findnum == 0:
        await bot.finish(ev, f"未找到名为{dun_name}的副本", at_sender=True)
    content = session.get('content', prompt="请输入要修改的内容(好感,需求战力,金币,声望,经验,万能碎片,随机碎片,副本币)")
    content = str(content).strip()
    if content not in YIN_NAME_LI:
        await bot.finish(ev, f"未找到名为{content}的内容", at_sender=True)

    nandu = None
    if content != "好感":
        nandu = str(session.get('nandu', prompt="请输入要修改的难度(简单,困难,地狱)")).strip()
        if nandu not in NAN_LI:
            await bot.finish(ev, f"未找到名为{nandu}的难度", at_sender=True)
    if content == "好感":
        old = dungeonlist[findnum]["add_favor"]
        new_value = str(session.get('new_value', prompt=f"原有的好感是{old},请输入新的好感值"))
        if not new_value.isdecimal():
            await bot.finish(ev, f"请输入数字", at_sender=True)
        dungeonlist[findnum]["add_favor"] = int(new_value)
        with open('/Users/yowasa/workspace/DND_QQ_ROBOT/hoshino/modules/pcr_duel/dungeon.json', 'w',
                  encoding='UTF-8') as fp:
            json.dump(dungeonlist, fp=fp, ensure_ascii=False)

    else:
        nandu_index = NAN_LI.index(nandu)
        yingshe_index = YIN_NAME_LI.index(content)
        comm = YIN_KEY_LI[yingshe_index]
        old = dungeonlist[findnum][comm][nandu_index]
        new_value = str(session.get('new_value', prompt=f"原有的[{nandu}]难度的{content}是{old},请输入新的{content}"))
        if not new_value.isdecimal():
            await bot.finish(ev, f"请输入数字", at_sender=True)
        dungeonlist[findnum][comm][nandu_index] = int(new_value)
        with open('/Users/yowasa/workspace/DND_QQ_ROBOT/hoshino/modules/pcr_duel/dungeon.json', 'w',
                  encoding='UTF-8') as fp:
            json.dump(dungeonlist, fp=fp, ensure_ascii=False)
    await bot.send(ev, f"修改成功", at_sender=True)


@dun_adj.args_parser
async def _(session: CommandSession):
    text = session.current_arg_text
    img = session.current_arg_images
    if img:
        session.state[session.current_key] = img
    else:
        session.state[session.current_key] = text
