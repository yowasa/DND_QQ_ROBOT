from .battle import *
from hoshino.util.utils import get_message_text, get_message_at
from .xiuxian_base import *

@sv.on_fullmatch(["#拜入"])
async def _(bot, ev: CQEvent):
    # 拜入宗门
    user = await get_ev_user(bot, ev)
    if user.map not in ZONGMEN.keys():
        await bot.finish(ev, "必须在宗门地图上才能拜入门派", at_sender=True)
    if user.belong != "散修":
        await bot.finish(ev, f"你已经拜入了{user.belong},不可拜入其他宗门！", at_sender=True)
    zongmen = ZONGMEN[user.map]
    content = {"linggen": user.linggen}
    if not eval(zongmen['condition'], content):
        await bot.finish(ev, f"{zongmen['condition_desc']}", at_sender=True)
    user.check_and_start_cd(bot, ev)
    user.belong = user.map
    ct = XiuxianCounter()
    ct._save_user_info(user)
    await bot.finish(ev, f"你成功的拜入了{user.map}", at_sender=True)


@sv.on_fullmatch(["#藏经阁"])
async def _(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    if user.belong == "无":
        await bot.finish(ev, f"你必须拜入宗门才能阅览藏经阁！", at_sender=True)
    if user.map != user.belong:
        await bot.finish(ev, "必须在宗门地图上才能阅览藏经阁！", at_sender=True)
    gongfali = list(CANGJING[user.map].keys())
    li = []
    for i in gongfali:
        item = get_item_by_name(i)
        # gongfa = get_gongfa_by_name(i)
        li.append(f"[{item['type']}]{i}({CANGJING[user.map][i]}帮贡)")
    await bot.finish(ev, "\n" + "\n".join(li), at_sender=True)


@sv.on_prefix(["#学习"])
async def _(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    user = await get_ev_user(bot, ev)
    if user.belong == "无":
        await bot.finish(ev, f"你必须拜入宗门才能学习藏经阁中的功法！", at_sender=True)
    if user.map != user.belong:
        await bot.finish(ev, "必须在宗门地图上才能学习藏经阁中的功法！", at_sender=True)
    msg = get_message_text(ev)
    if msg not in CANGJING[user.belong].keys():
        await bot.finish(ev, f"藏经阁中没有名为[{msg}]的功法", at_sender=True)
    banggong = get_user_counter(gid, uid, UserModel.BANGGONG)
    need = CANGJING[user.belong][msg]
    if banggong < need:
        await bot.finish(ev, f"阅览{msg}需要{need}帮派贡献，你的帮贡不足", at_sender=True)
    item = get_item_by_name(msg)
    gongfa_id = get_user_counter(gid, uid, UserModel.STUDY_GONGFA)
    if gongfa_id:
        # 你正在参悟
        gongfa_name = ITEM_INFO[str(gongfa_id)]["name"]
        return (False, f"你正在参悟{gongfa_name},无法同时参悟")
    if item['type'] == "心法":
        if user.gongfa != "无":
            await bot.finish(ev, f"你已经习得了{user.gongfa},无法学习新的心法(请使用 #废功 自废武功后再学习)", at_sender=True)
    if item['type'] == "功法":
        if user.gongfa2 != "无":
            await bot.finish(ev, f"你已经习得了{user.gongfa2},无法学习新的功法(请使用 #废功 自废武功后再学习)", at_sender=True)
    if item['type'] == "神通":
        if user.gongfa3 != "无":
            await bot.finish(ev, f"你已经习得了{user.gongfa3},无法学习新的神通(请使用 #废功 自废武功后再学习)", at_sender=True)
    gongfa = get_gongfa_by_name(msg)
    content = {"level": user.level, "wuxing": user.wuxing, "linggen": user.linggen, "sharen": user.sharen}
    if eval(gongfa['condition'], content):
        save_user_counter(gid, uid, UserModel.STUDY_GONGFA, int(item['id']))
        add_user_counter(gid, uid, UserModel.BANGGONG, num=-need)
        await bot.finish(ev, f"你开始参悟[{msg}]，请使用#参悟 来研习功法", at_sender=True)
    else:
        await bot.finish(ev, f"你的资质欠佳,无法参悟此功法({gongfa['condition_desc']})", at_sender=True)


# 画符
@sv.on_prefix(["#画符"])
async def _(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    await user.check_cd(bot, ev)
    if user.belong != '蜀山派':
        await bot.finish(ev, "只有蜀山派弟子才能画符！", at_sender=True)
    if user.map != user.belong:
        await bot.finish(ev, "必须在宗门地图上才能画符！", at_sender=True)
    if not daily_huafu_limiter.check([user.uid]):
        await bot.finish(ev, "你今天已经画过符咒了！", at_sender=True)
    names = filter_item_name(type=['符咒'])
    name = random.choice(names)
    item = get_item_by_name(name)
    num = 1
    if user.gongfa3 == "太元符禄":
        num = 2
    if not add_item(user.gid, user.uid, item, num=num):
        await bot.finish(ev, "你背包已经满了！", at_sender=True)
    daily_huafu_limiter.increase([user.uid])
    user.start_cd()
    await bot.finish(ev, f"你获得了符咒【{item['name']}】！", at_sender=True)


@sv.on_prefix(["#俸禄"])
async def _(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    await user.check_cd(bot, ev)
    if user.belong != '混元门':
        await bot.finish(ev, "只有混元门弟子才能领取俸禄！", at_sender=True)
    if user.map != user.belong:
        await bot.finish(ev, "必须在宗门地图上才能领取俸禄！", at_sender=True)
    if not daily_fenglu_limiter.check([user.uid]):
        await bot.finish(ev, "你今天已经领取过俸禄了！", at_sender=True)
    fenglu = FENGLU_MAP[str(user.level)]
    add_user_counter(user.gid, user.uid, UserModel.LINGSHI, fenglu)
    daily_fenglu_limiter.increase([user.uid])
    user.start_cd()
    await bot.finish(ev, f"你获得了{fenglu}灵石的俸禄！", at_sender=True)


MISSION = {
    "1": "扩充武库",
    "2": "材料缴纳",
    "3": "修筑清扫",
    "4": "寻花采药",
    "5": "武学交流",
    "6": "游历大千"
}


@sv.on_prefix(["#放弃任务"])
async def _(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    await user.check_cd(bot, ev)
    id = get_user_counter(user.gid, user.uid, UserModel.MISSION)
    if not id:
        await bot.finish(ev, "你尚未接受任务", at_sender=True)
    else:
        daily_mission_limiter.increase([user.uid])
        save_user_counter(user.gid, user.uid, UserModel.MISSION, 0)
        save_user_counter(user.gid, user.uid, UserModel.MISSION_COMPLETE, 0)
        await bot.finish(ev, "放弃任务成功", at_sender=True)


@sv.on_prefix(["#任务"])
async def _(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    id = get_user_counter(user.gid, user.uid, UserModel.MISSION)
    if id:
        mission_name = MISSION[str(id)]
        suc, result = await _complete(mission_name, user, bot, ev)
        if suc:
            daily_mission_limiter.increase([user.uid])
            save_user_counter(user.gid, user.uid, UserModel.MISSION, 0)
            save_user_counter(user.gid, user.uid, UserModel.MISSION_COMPLETE, 0)
        await bot.finish(ev, result, at_sender=True)
    else:
        await user.check_cd(bot, ev)
        if user.map != user.belong:
            await bot.finish(ev, "必须在宗门才能接受任务", at_sender=True)
        if not daily_mission_limiter.check([user.uid]):
            await bot.finish(ev, "你今日完成任务次数已达上限，无法继续接受任务", at_sender=True)
        li = list(MISSION.keys())
        id = random.choice(li)
        mission_name = MISSION[id]
        result = await _accept(mission_name, user, bot, ev)
        save_user_counter(user.gid, user.uid, UserModel.MISSION, int(id))
        user.start_cd()
        await bot.finish(ev, result, at_sender=True)


mission_register = dict()
complete_register = dict()


async def _accept(name, user, bot, ev):
    func = mission_register.get(name)
    if func:
        return await func(user, bot, ev)
    return "任务未实装"


async def _complete(name, user, bot, ev):
    func = complete_register.get(name)
    if func:
        return await func(user, bot, ev)
    return "任务未实装"


# 注解msg 传入正则表达式进行匹配
def mission_route(item_name):
    def show(func):
        async def warpper(user, bot, ev: CQEvent):
            return await func(user, bot, ev)

        mission_register[item_name] = warpper
        return warpper

    return show


# 注解msg 传入正则表达式进行匹配
def complete_route(item_name):
    def show(func):
        async def warpper(user, bot, ev: CQEvent):
            return await func(user, bot, ev)

        complete_register[item_name] = warpper
        return warpper

    return show


@mission_route("扩充武库")
async def _(user: AllUserInfo, bot, ev: CQEvent):
    return f"你领取了[扩充武库]任务,请在宗门使用#任务 武器 缴纳给宗门一件武器以完成任务"


@complete_route("扩充武库")
async def _(user: AllUserInfo, bot, ev: CQEvent):
    name = get_message_text(ev)
    item = get_item_by_name(name)
    if user.map != user.belong:
        return (False, f"只有在宗门才能缴纳武器")
    if not item:
        return (False, f"未找到名为{name}的道具")
    if item["type"] != "武器":
        return (False, f"请缴纳[武器]!")
    if not check_have_item(user.gid, user.uid, item):
        return (False, f"你身上没有[{name}]!")
    use_item(user.gid, user.uid, item)
    get_lingshi = random.randint(50, 100)
    get_banggong = random.randint(10, 20)
    add_user_counter(user.gid, user.uid, UserModel.LINGSHI, num=get_lingshi)
    add_user_counter(user.gid, user.uid, UserModel.BANGGONG, num=get_banggong)
    return (True, f"你缴纳了武器[{name}]，获得了{get_lingshi}灵石和{get_banggong}帮贡")


@mission_route("材料缴纳")
async def _(user: AllUserInfo, bot, ev: CQEvent):
    return f"你领取了[材料缴纳]任务,请在宗门使用#任务 素材 缴纳给宗门一件素材以完成任务"


@complete_route("材料缴纳")
async def _(user: AllUserInfo, bot, ev: CQEvent):
    name = get_message_text(ev)
    item = get_item_by_name(name)
    if user.map != user.belong:
        return (False, f"只有在宗门才能缴纳素材")
    if not item:
        return (False, f"未找到名为{name}的道具")
    if item["type"] != "素材":
        return (False, f"请缴纳[素材]!")
    if not check_have_item(user.gid, user.uid, item):
        return (False, f"你身上没有[{name}]!")
    use_item(user.gid, user.uid, item)
    get_lingshi = random.randint(50, 100)
    get_banggong = random.randint(10, 20)
    add_user_counter(user.gid, user.uid, UserModel.LINGSHI, num=get_lingshi)
    add_user_counter(user.gid, user.uid, UserModel.BANGGONG, num=get_banggong)
    return (True, f"你缴纳了素材[{name}]，获得了{get_lingshi}灵石和{get_banggong}帮贡")


@mission_route("修筑清扫")
async def _(user: AllUserInfo, bot, ev: CQEvent):
    return f"你领取了[修筑清扫]任务,请在宗门使用#任务 以完成任务"


@complete_route("修筑清扫")
async def _(user: AllUserInfo, bot, ev: CQEvent):
    if user.map != user.belong:
        return (False, f"只有在宗门才能打扫")
    get_banggong = random.randint(10, 20)
    add_user_counter(user.gid, user.uid, UserModel.BANGGONG, num=get_banggong)
    return (True, f"你完成了宗门修筑清扫，获得了{get_banggong}帮贡")


@mission_route("寻花采药")
async def _(user: AllUserInfo, bot, ev: CQEvent):
    return f"你领取了[寻花采药]任务,请前往大千世界或者百花谷使用#任务 完成采药，回到宗门再使用#任务 完成任务"


@complete_route("寻花采药")
async def _(user: AllUserInfo, bot, ev: CQEvent):
    if get_user_counter(user.gid, user.uid, UserModel.MISSION_COMPLETE):
        if user.map != user.belong:
            return (False, f"只有在宗门才能完成任务")
        map = {"混元门": "赭黄精", "狮府": "木枯藤", "百花谷": "玄牝珠", "百炼山庄": "朱果", "蜀山派": "琅琊果"}
        name = map.get(user.belong)
        ex_msg = ""
        if not add_item(user.gid, user.uid, get_item_by_name(name)):
            ex_msg = "(背包已满,只得丢弃)"
        get_banggong = random.randint(10, 20)
        add_user_counter(user.gid, user.uid, UserModel.BANGGONG, num=get_banggong)
        return (True, f"你完成了寻花采药，获得了{get_banggong}帮贡和[{name}]{ex_msg}")
    else:
        if user.map not in ["大千世界", "百花谷"]:
            return (False, f"只有在大千世界或者百花谷才能进行采药")
        user.start_cd()
        save_user_counter(user.gid, user.uid, UserModel.MISSION_COMPLETE, 1)
        return (False, f"经过辛苦的采集，你采集到了足够的药材")


@mission_route("游历大千")
async def _(user: AllUserInfo, bot, ev: CQEvent):
    id_li = [i for i in DAQIAN_MAP.keys() if DAQIAN_MAP[i]['in_level'] <= user.level]
    id = random.choice(id_li)
    save_user_counter(user.gid, user.uid, UserModel.YOULI_DAQIAN, int(id))
    return f"你领取了[游历大千]任务,请前往{DAQIAN_MAP[id]['name']}游历3次,之后前往宗门完成任务"


@complete_route("游历大千")
async def _(user: AllUserInfo, bot, ev: CQEvent):
    if user.map != user.belong:
        return (False, f"只有在宗门才能完成任务")
    id = get_user_counter(user.gid, user.uid, UserModel.YOULI_DAQIAN)
    count = get_user_counter(user.gid, user.uid, UserModel.YOULI_DAQIAN_COUNT)
    if count < 3:
        return (False, f"你游历[{DAQIAN_MAP[str(id)]['name']}]次数不足，无法完成任务")
    save_user_counter(user.gid, user.uid, UserModel.YOULI_DAQIAN, 0)
    save_user_counter(user.gid, user.uid, UserModel.YOULI_DAQIAN_COUNT, 0)
    get_lingshi = random.randint(50, 150)
    get_banggong = random.randint(20, 40)
    add_user_counter(user.gid, user.uid, UserModel.LINGSHI, num=get_lingshi)
    add_user_counter(user.gid, user.uid, UserModel.BANGGONG, num=get_banggong)
    return (True, f"你游历归来，向宗门分享了所思所得，获得了{get_lingshi}灵石和{get_banggong}帮贡")


@mission_route("武学交流")
async def _(user: AllUserInfo, bot, ev: CQEvent):
    id_li = [i for i in QIE_CUO_MAP.keys() if QIE_CUO_MAP[i]['in_level'] <= user.level]
    id = random.choice(id_li)
    save_user_counter(user.gid, user.uid, UserModel.WUXUE, int(id))
    return f"你领取了[武学交流]任务,请寻找{QIE_CUO_MAP[id]['name']}宗门的弟子并与其切磋，之后前往宗门完成任务"


@complete_route("武学交流")
async def _(user: AllUserInfo, bot, ev: CQEvent):
    if user.map != user.belong:
        return (False, f"只有在宗门才能完成任务")
    id = get_user_counter(user.gid, user.uid, UserModel.WUXUE)
    count = get_user_counter(user.gid, user.uid, UserModel.MISSION_COMPLETE)
    if not count:
        return (False, f"你尚未与[{QIE_CUO_MAP[str(id)]['name']}]宗门的人切磋过，无法完成任务")
    save_user_counter(user.gid, user.uid, UserModel.WUXUE, 0)
    get_banggong = random.randint(20, 30)
    add_user_counter(user.gid, user.uid, UserModel.BANGGONG, num=get_banggong)
    return (True, f"你武学交流归来，获得了{get_banggong}帮贡")


# 切磋
@sv.on_prefix(["#切磋"])
async def duanti(bot, ev: CQEvent):
    gid = ev.group_id
    my = await get_ev_user(bot, ev)
    name = get_message_text(ev)
    at = get_message_at(ev)
    ct = XiuxianCounter()
    if at:
        at = at[0]
        enemy = ct._get_user(gid, at)
    else:
        enemy = ct._get_user_by_name(gid, name)
    if not enemy:
        await bot.finish(ev, f"未找到名【{name}】的角色")
    if my.uid == enemy.uid:
        await bot.finish(ev, f"不能自己打自己（恼）")
    id = get_user_counter(my.gid, my.uid, UserModel.WUXUE)
    if not id:
        await bot.finish(ev, f"你尚未接受交流武学的任务，严禁私下切磋！")
    if get_user_counter(my.gid, my.uid, UserModel.MISSION_COMPLETE):
        await bot.finish(ev, f"你已经完成交流武学的任务，严禁私下继续切磋！")
    if enemy.belong != QIE_CUO_MAP[str(id)]['name']:
        await bot.finish(ev, f"你接到的切磋请求是与[{QIE_CUO_MAP[str(id)]['name']}]而不是[{enemy.belong}]！")
    if my.map != enemy.map:
        await bot.finish(ev, f"你找遍了四周也没有发现{enemy.name}的身影，或许他根本不在这里？")

    enemy = AllUserInfo(enemy)
    # 战斗
    my_hp, he_hp, send_msg_li = battle(my, enemy)
    if my_hp > 0 and he_hp <= 0:
        send_msg_li.append(f"{my.name}获得了胜利")
    elif he_hp > 0 and my_hp <= 0:
        send_msg_li.append(f"{enemy.name}获得了胜利")
    else:
        send_msg_li.append(f"二人不分胜负")
    get_jiqiao = random.randint(1, 3)
    my.skill += get_jiqiao
    enemy.skill += get_jiqiao
    send_msg_li.append(f"双方获得了{get_jiqiao}点战斗技巧")
    ct._save_user_info(my)
    ct._save_user_info(enemy)
    save_user_counter(my.gid, my.uid, UserModel.MISSION_COMPLETE, 1)
    await bot.finish(ev, '\n'.join(send_msg_li))

# 试炼
@sv.on_prefix(["#试炼场"])
async def shilian(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    await user.check_cd(bot, ev)
    if user.map != user.belong:
        await bot.finish(ev, "必须在宗门才能试炼", at_sender=True)
    if not daily_shiLian_limiter.check([user.uid]):
        await bot.finish(ev, "你今日试炼次数已达上限，无法继续试炼", at_sender=True)

    my_content = init_content(user)
    enemy_content = init_shilian_content(user)
    # 战斗
    my_hp, he_hp, send_msg_li = battle_base(my_content,enemy_content)
    # 战斗
    if my_hp > 0 and he_hp <= 0:
        lingshi = random.randint(30, 80)
        user.lingshi += lingshi
        add_user_counter(user.gid, user.uid, UserModel.LINGSHI, lingshi)
        send_msg_li.append(f"{user.name}试炼成功，获取{lingshi}灵石奖励")
    elif he_hp > 0 and my_hp <= 0:
        send_msg_li.append(f"{user.name}试炼失败")
    else:
        send_msg_li.append(f"试炼不分胜负")
    daily_shiLian_limiter.increase([user.uid])
    await bot.finish(ev, '\n'.join(send_msg_li))