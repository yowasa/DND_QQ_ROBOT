from .xiuxian_config import *


# @sv.on_prefix(['#获取'])
# async def my_item(bot, ev: CQEvent):
#     gid = ev.group_id
#     uid = ev.user_id
#     msg = str(ev.message).strip().split()
#     item_info = ITEM_NAME_MAP.get(msg[0])
#     if not item_info:
#         await bot.finish(ev, f"未找到名称为{msg[0]}的道具", at_sender=True)
#     ct = XiuxianCounter()
#     user = ct._get_user(gid, uid)
#     if not user:
#         await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
#     result = add_item(gid, uid, item_info)
#     if result:
#         await bot.finish(ev, "获取成功")
#     else:
#         await bot.finish(ev, "获取失败,请检查背包空间")


@sv.on_fullmatch(['#背包'])
async def my_item(bot, ev: CQEvent):
    counter = ItemCounter()
    gid = ev.group_id
    uid = ev.user_id
    items = counter._get_item(gid, uid)
    msg = "\n==== 道具列表 ===="
    item_li = []
    for i in items:
        ITEM_INFO[str(i[0])]['num'] = i[1]
        item_li.append(ITEM_INFO[str(i[0])])
    item_li = sorted(item_li, key=lambda x: ['心法', '功法', '神通', '武器', '法宝', '丹药', '符咒', '素材'].index(x['type']),
                     reverse=True)
    for i in item_li:
        msg += f"\n【{i['type']}】{i['name']} *{i['num']}"
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['#道具效果'])
async def consume_item(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg = str(ev.message).strip().split()
    item_info = ITEM_NAME_MAP.get(msg[0])
    if not item_info:
        await bot.finish(ev, f"未找到名称为{msg[0]}的道具", at_sender=True)
    counter = ItemCounter()
    num = counter._get_item_num(gid, uid, int(item_info['id']))
    if num < 1:
        await bot.finish(ev, f"背包中没有{msg[0]}", at_sender=True)
    await bot.finish(ev, f"【{item_info['type']}】{item_info['name']}:{item_info['desc']}", at_sender=True)


@sv.on_prefix(['#使用'])
async def consume_item(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg = str(ev.message).strip().split()
    item_info = ITEM_NAME_MAP.get(msg[0])
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if not user:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    if not item_info:
        await bot.finish(ev, f"未找到名称为{msg[0]}的道具", at_sender=True)
    counter = ItemCounter()
    num = counter._get_item_num(gid, uid, int(item_info['id']))
    if num < 1:
        await bot.finish(ev, f"背包中道具{msg[0]}数量不足", at_sender=True)
    if item_info['type'] in ['功法', '心法', '神通']:
        result = await study(bot, ev, item_info['name'])
    elif item_info['type'] == '武器':
        result = await equip(bot, ev, item_info['name'])
    elif item_info['type'] == '法宝':
        result = await equip_fa(bot, ev, item_info['name'])
    elif item_info['type'] == '丹药':
        result = await _use_item(msg[0], msg[1:], bot, ev)
    else:
        result = (False, f"【{item_info['type']}】{item_info['name']}:{item_info['desc']}")

    suc_num = 0
    if result[0]:
        suc_num += 1
        counter._add_item(gid, uid, int(item_info['id']), num=-1)
    await bot.send(ev, result[1], at_sender=True)


@sv.on_prefix(['#丢弃'])
async def consume_item(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg = str(ev.message).strip().split()
    item_info = ITEM_NAME_MAP.get(msg[0])
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if not user:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    if not item_info:
        await bot.finish(ev, f"未找到名称为{msg[0]}的道具", at_sender=True)
    counter = ItemCounter()
    num = counter._get_item_num(gid, uid, int(item_info['id']))
    if num < 1:
        await bot.finish(ev, f"背包中道具{msg[0]}数量不足", at_sender=True)
    counter._add_item(gid, uid, int(item_info['id']), num=-1)
    await bot.send(ev, f"你丢弃掉了一个「{msg[0]}」", at_sender=True)


register = dict()


# 使用道具
async def _use_item(name, msg, bot, ev):
    func = register.get(name)
    if func:
        return await func(msg, bot, ev)
    return (False, "道具未实装")


# 注解msg 传入正则表达式进行匹配
def msg_route(item_name):
    def show(func):
        async def warpper(msg, bot, ev: CQEvent):
            return await func(msg, bot, ev)

        register[item_name] = warpper
        return warpper

    return show


# 学习功法
async def study(bot, ev, param):
    gid = ev.group_id
    uid = ev.user_id
    item = get_item_by_name(param)
    gongfa_id = get_user_counter(gid, uid, UserModel.STUDY_GONGFA)
    if gongfa_id:
        # 你正在参悟
        gongfa_name = ITEM_INFO[str(gongfa_id)]["name"]
        return (False, f"你正在参悟{gongfa_name},无法同时参悟")
    user = get_full_user(gid, uid)
    if item['type'] == "心法":
        if user.gongfa != "无":
            return (False, f"你已经习得了{user.gongfa},无法学习新的心法(请使用 #废功 自废武功后再学习)")
    if item['type'] == "功法":
        if user.gongfa2 != "无":
            return (False, f"你已经习得了{user.gongfa2},无法学习新的功法(请使用 #废功 自废武功后再学习)")
    if item['type'] == "神通":
        if user.gongfa3 != "无":
            return (False, f"你已经习得了{user.gongfa3},无法学习新的神通(请使用 #废功 自废武功后再学习)")
    gongfa = get_gongfa_by_name(param)
    content = {"level": user.level, "wuxing": user.wuxing, "linggen": user.linggen, "sharen": user.sharen}
    if eval(gongfa['condition'], content):
        save_user_counter(gid, uid, UserModel.STUDY_GONGFA, int(item['id']))
        return (True, f"你开始参悟[{param}]，请使用#参悟 来研习功法")
    else:
        return (False, f"你的资质欠佳,无法参悟此功法({gongfa['condition_desc']})")


# 装备
async def equip(bot, ev, param):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = get_full_user(gid, uid)
    equip = get_equip_by_name(param)
    content = {"level": user.level, "wuxing": user.wuxing, "linggen": user.linggen, "tizhi": user.tizhi,
               "defen1": user.defen, "defen2": user.defen2, "daohang": user.daohang, "sharen": user.sharen}
    if eval(equip['condition'], content):
        desc = get_item_by_name(param)['desc']
        if user.wuqi != '赤手空拳':
            item = get_item_by_name(user.wuqi)
            if add_item(gid, uid, item, 1):
                user.wuqi = param
                ct._save_user_info(user)
                return (True, f"装备{param}成功({desc})")
            else:
                return (False, f"请至少腾出一格背包空间")
        else:
            user.wuqi = param
            ct._save_user_info(user)
            return (True, f"装备{param}成功({desc})")
    else:
        return (False, f"你当前的实力难以驾驭此武器({equip['condition_desc']})")


# 装备法宝
async def equip_fa(bot, ev, param):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = get_full_user(gid, uid)
    equip_fa = get_fabao_by_name(param)
    content = {"level": user.level, "wuxing": user.wuxing, "linggen": user.linggen, "tizhi": user.tizhi, "sharen": user.sharen}
    if eval(equip_fa['condition'], content):
        desc = get_item_by_name(param)['desc']
        if user.fabao != '无':
            item = get_item_by_name(user.fabao)
            if add_item(gid, uid, item, 1):
                user.fabao = param
                ct._save_user_info(user)
                return (True, f"装备{param}成功({desc})")
            else:
                return (False, f"请至少腾出一格背包空间")
        else:
            user.fabao = param
            ct._save_user_info(user)
            return (True, f"装备{param}成功({desc})")
    else:
        return (False, f"你当前的实力难以驾驭此法宝({equip_fa['condition_desc']})")


# =========== 丹药 ============
@msg_route("淬骨丹")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    user.exp += 50
    ct._save_user_info(user)
    return (True, f"你服用了淬骨丹，感觉到灵力喷涌而出，获得了50点EXP")


@msg_route("合气丹")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if user.level < 7:
        return (False, f"你当前的境界无法吸收合气丹")
    user.exp += 100
    ct._save_user_info(user)
    return (True, f"你服用了合气丹，感觉到灵力喷涌而出，获得了100点EXP")


@msg_route("培元丹")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if user.level < 10:
        return (False, f"你当前的境界无法吸收培元丹")
    user.exp += 150
    ct._save_user_info(user)
    return (True, f"你服用了培元丹，感觉到灵力喷涌而出，获得了150点EXP")


@msg_route("纯阳丹")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if user.level < 13:
        return (False, f"你当前的境界无法吸收纯阳丹")
    user.exp += 200
    ct._save_user_info(user)
    return (True, f"你服用了纯阳丹，感觉到灵力喷涌而出，获得了200点EXP")


@msg_route("造化丸")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if user.level < 16:
        return (False, f"你当前的境界无法吸收造化丸")
    user.exp += 300
    ct._save_user_info(user)
    return (True, f"你服用了造化丸，感觉到灵力喷涌而出，获得了300点EXP")


@msg_route("补天丹")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if user.level < 16:
        return (False, f"你当前的境界无法吸收补天丹")
    user.exp += 800
    ct._save_user_info(user)
    return (True, f"你服用了补天丹，感觉到灵力喷涌而出，获得了800点EXP")


@msg_route("定神香")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if user.level < 19:
        return (False, f"你当前的境界无法吸收定神香")
    user.exp += 1600
    ct._save_user_info(user)
    return (True, f"你服用了定神香，感觉到灵力喷涌而出，获得了800点EXP")


@msg_route("洗髓丹")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if user.level > 12:
        return (False, f"你当已然结丹，无法再使用洗髓丹")
    linggen = get_LingGen()
    user.linggen = linggen
    ct._save_user_info(user)
    return (True, f"你服用了洗髓丹,灵根变为[{linggen}]")


@msg_route("涅槃丹")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    user.exp = 0
    user.level = 1
    user.map = "新手村"
    user.wuxing = random.randint(10, 70)
    user.lingli = 0
    user.act = 10
    user.defen = 10
    user.defen2 = 10
    user.hp = random.randint(60, 100)
    user.mp = random.randint(60, 100)
    user.skill = random.randint(5, 20)
    user.tizhi = random.randint(10, 20)
    user.act2 = 0
    ct._save_user_info(user)
    return (True, f"你服用了涅槃丹,感觉胸口剧痛,灵力从你身上散出,昏死了过去，再次醒来已经功力尽失，为了安全起见回到了新手村。")


@msg_route("筑基丹")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if get_user_counter(gid, uid, UserModel.ZHUJIDAN):
        return (False, f"你已经服用了筑基丹,无需多次服用")
    save_user_counter(gid, uid, UserModel.ZHUJIDAN, 1)
    return (True, f"你服用了筑基丹,筑基更容易成功")


@msg_route("金疮药")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    shangshi = get_user_counter(gid, uid, UserModel.SHANGSHI)
    if not shangshi:
        return (False, f"你没有受伤")
    if shangshi > 1:
        return (False, f"你受伤过重，金疮药无法帮助你减轻伤势！")
    save_user_counter(gid, uid, UserModel.SHANGSHI, 0)
    return (True, f"你使用了金疮药,恢复了伤势。")


@msg_route("小还丹")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    shangshi = get_user_counter(gid, uid, UserModel.SHANGSHI)
    if not shangshi:
        return (False, f"你没有受伤")
    if shangshi > 2:
        return (False, f"你受伤过重，小还丹无法帮助你减轻伤势！")
    save_user_counter(gid, uid, UserModel.SHANGSHI, 0)
    return (True, f"你使用了小还丹,恢复了伤势。")


@msg_route("回魂丹")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    shangshi = get_user_counter(gid, uid, UserModel.SHANGSHI)
    if not shangshi:
        return (False, f"你没有受伤")
    save_user_counter(gid, uid, UserModel.SHANGSHI, 0)
    return (True, f"你使用了回魂丹,恢复了伤势。")