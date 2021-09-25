from hoshino.typing import CQEvent
from . import sv
from .duelconfig import *
from .ScoreCounter import ScoreCounter2
from . import duel_chara


@sv.on_fullmatch(['天气帮助'])
async def manor_help(bot, ev: CQEvent):
    msg = '''
╔                                        ╗  
             天气帮助
[今日天气] [天气一览]
[天气效果] {天气名}
╚                                        ╝
 '''
    await bot.send(ev, msg)


# 今日天气
@sv.on_fullmatch(['今日天气', '当前天气'])
async def now_weather(bot, ev: CQEvent):
    git = ev.group_id
    model = get_weather(git)
    msg = f'''
当前天气为:{model.value['name']}
效果:{model.value['desc']}
     '''
    await bot.send(ev, msg, at_sender=True)


# 天气效果
@sv.on_prefix(['天气效果'])
async def weather_help(bot, ev: CQEvent):
    name = str(ev.message).strip()
    model = WeatherModel.get_by_name(name)
    if not model:
        await bot.finish(ev, f"未找到名为{name}的天气", at_sender=True)
    msg = f'''
天气:{model.value['name']}
效果:{model.value['desc']}
     '''
    await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch('天气一览')
async def item_all(bot, ev: CQEvent):
    tas_list = []
    data = {
        "type": "node",
        "data": {
            "name": "ご主人様",
            "uin": "1587640710",
            "content": "====== 天气一览 ======"
        }
    }
    tas_list.append(data)
    for i in WeatherModel:
        msg = f"""{i.value['name']}
效果：{i.value['desc']}
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


@sv.on_fullmatch(['快速决斗'])
async def manor_begin(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    # weather = get_weather(gid)
    # if weather != WeatherModel.FENGYU:
    #     return
    guid = gid, uid
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    level = duel._get_level(gid, uid)
    if not daily_duel_limiter.check(guid):
        await bot.finish(ev, '今天的决斗次数已经超过上限了哦，明天再来吧。', at_sender=True)
    wingold = 1000 + (level * 200)
    winSW = WinSWBasics - LoseSWBasics
    score_counter._add_score(gid, uid, wingold)
    score_counter._add_prestige(gid, uid, winSW)
    CE = CECounter()
    bangdin = CE._get_guaji(gid, uid)
    bd_msg = ''
    if bangdin:
        bd_info = duel_chara.fromid(bangdin)
        card_level = add_exp(gid, uid, bangdin, WIN_EXP)
        nvmes = get_nv_icon_with_fashion(gid, uid, bangdin)
        bd_msg = f"\n您绑定的女友{bd_info.name}获得了{WIN_EXP}点经验，{card_level[2]}\n{nvmes}"
    daily_duel_limiter.increase(guid)
    num = get_user_counter(gid, uid, UserModel.DUEL_COIN)
    num += 1
    save_user_counter(gid, uid, UserModel.DUEL_COIN, num)
    await bot.send(ev, f'快速决斗成功，获得{wingold}金币，{winSW}声望，1枚决斗币。' + bd_msg, at_sender=True)
