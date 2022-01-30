from .xiuxian_config import *
from .xiuxian_base import *
from hoshino.util.utils import get_message_text, get_message_at


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
#
#
# @sv.on_prefix(['#充值'])
# async def my_item(bot, ev: CQEvent):
#     gid = ev.group_id
#     uid = ev.user_id
#     msg = str(ev.message).strip()
#     if not msg.isdecimal():
#         await bot.finish(ev, f"请输入充值数字", at_sender=True)
#     num = int(msg)
#     add_user_counter(gid, uid, UserModel.LINGSHI, num)
#     await bot.finish(ev, f"充值{num}灵石成功", at_sender=True)

@sv.on_prefix(["#传送"])
async def go(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    name = str(ev.message).strip()
    adress = MAP.get(name)
    count = get_user_counter(user.gid, user.uid, UserModel.CHUANSONG)
    if count <= 0:
        item = get_item_by_name("传送符")
        if check_have_item(user.gid, user.uid, item):
            use_item(user.gid, user.uid, item)
            add_user_counter(user.gid, user.uid, UserModel.CHUANSONG, num=3)
        else:
            await bot.finish(ev, f"你剩余传送次数不足且没有传送符")
    if not adress:
        await bot.finish(ev, f"未找到名为「{name}」的地点")
    need_level = adress["in_level"]
    if user.level < need_level:
        await bot.finish(ev, f"你实力还不足以进入该地图（{name}需要{JingJieMap[str(need_level)]}才能进入）")
    add_user_counter(user.gid, user.uid, UserModel.CHUANSONG, num=-1)
    user.map = name
    ct = XiuxianCounter()
    ct._save_user_info(user)
    await bot.finish(ev, f"你使用了传送符传送到了[{name}]")


@sv.on_fullmatch(['#背包'])
async def my_item(bot, ev: CQEvent):
    counter = ItemCounter()
    gid = ev.group_id
    uid = ev.user_id
    items = counter._get_item(gid, uid)
    max = get_max_count(gid, uid)
    count = count_item(gid, uid)
    lingshi = get_user_counter(gid, uid, UserModel.LINGSHI)
    banggong = get_user_counter(gid, uid, UserModel.BANGGONG)
    msg = f"\n道具列表 {count}/{max} 灵石:{lingshi} 帮贡:{banggong}"
    item_li = []
    for i in items:
        ITEM_INFO[str(i[0])]['num'] = i[1]
        item_li.append(ITEM_INFO[str(i[0])])
    item_li = sorted(item_li, key=lambda x: ['消耗品', '心法', '功法', '神通', '武器', '法宝', '丹药', '符咒', '素材', '道具'].index(x['type']),
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
    elif item_info['type'] in ['丹药', "消耗品"]:
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


@sv.on_prefix(["#卸下"])
async def canwu(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg = str(ev.message).strip()
    user = await get_ev_user(bot, ev)
    if msg not in ["武器", "法宝"] and msg not in [user.wuqi, user.fabao]:
        await bot.finish(ev, f"未找到名为[{msg}]的穿戴中的武器或法宝", at_sender=True)
    ct = XiuxianCounter()
    if msg in [user.wuqi, "武器"]:
        old_wuqi = user.wuqi
        if user.wuqi == "赤手空拳":
            await bot.finish(ev, f"你没有武器可以卸下", at_sender=True)
        item = get_item_by_name(user.wuqi)
        if add_item(gid, uid, item, 1):
            user.wuqi = "赤手空拳"
            ct._save_user_info(user)
            await bot.finish(ev, f"卸下{old_wuqi}成功", at_sender=True)
        else:
            await bot.finish(ev, f"请至少腾出一格背包空间", at_sender=True)

    if msg in [user.fabao, "法宝"]:
        old_fabao = user.fabao
        if user.fabao == "无":
            await bot.finish(ev, f"你没有法宝可以卸下", at_sender=True)
        item = get_item_by_name(user.fabao)
        if add_item(gid, uid, item, 1):
            user.fabao = "无"
            ct._save_user_info(user)
            await bot.finish(ev, f"卸下{old_fabao}成功", at_sender=True)
        else:
            await bot.finish(ev, f"请至少腾出一格背包空间", at_sender=True)


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
    content = {"level": user.level, "wuxing": user.wuxing, "linggen": user.linggen, "tizhi": user.tizhi,
               "sharen": user.sharen}
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
    user.exp += 500
    ct._save_user_info(user)
    return (True, f"你服用了补天丹，感觉到灵力喷涌而出，获得了500点EXP")


@msg_route("定神香")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if user.level < 19:
        return (False, f"你当前的境界无法吸收定神香")
    user.exp += 800
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


@msg_route("混元丹")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if get_user_counter(gid, uid, UserModel.HUNYUAN):
        return (False, f"你已经服用了混元丹,无需多次服用")
    save_user_counter(gid, uid, UserModel.HUNYUAN, 1)
    return (True, f"你服用了混元丹,突破到结丹更容易成功")


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


@msg_route("赤血丹")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if user.hp > 400:
        return (False, f"你已经足够强壮,赤血丹对你没有效果了")
    if user.level < 7:
        return (False, f"你现在境界还无法吸收赤血丹，请至少达到练气期")
    user.hp += 20
    ct._save_user_info(user)
    return (True, f"你使用了赤血丹,增加了20HP上限。")


@msg_route("涤魂丹")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if user.mp > 200:
        return (False, f"你法力足够雄厚,涤魂丹对你没有效果了")
    if user.level < 13:
        return (False, f"你现在境界还无法吸收涤魂丹，请至少达到结丹期")
    user.mp += 10
    ct._save_user_info(user)
    return (True, f"你使用了涤魂丹,增加了10MP上限。")


@msg_route("无极散")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if user.defen > 80:
        return (False, f"你已经足够强壮,无极散对你没有效果了")
    if user.level < 13:
        return (False, f"你现在境界还无法吸收无极散，请至少达到结丹期")
    user.defen += 5
    ct._save_user_info(user)
    return (True, f"你使用了无极散,物理防御增加了5点。")


@msg_route("月华露")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if user.defen2 > 80:
        return (False, f"你已经足够强壮,月华露对你没有效果了")
    if user.level < 13:
        return (False, f"你现在境界还无法吸收月华露，请至少达到结丹期")
    user.defen2 += 5
    ct._save_user_info(user)
    return (True, f"你使用了月华露,术法防御增加了5点。")


@msg_route("悟道丸")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if user.wuxing > 80:
        return (False, f"你已经足够聪明,悟道丸对你没有效果了")
    user.wuxing += 5
    ct._save_user_info(user)
    return (True, f"你使用了悟道丸,悟性增加了5点。")


@msg_route("水猴子的感恩礼盒")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if not check_have_space(gid, uid):
        return (False, f"至少保有一格背包空间")
    lingshi = get_user_counter(gid, uid, UserModel.LINGSHI)
    if lingshi < 50:
        return (False, f"开启盒子需要50灵石")
    add_user_counter(gid, uid, UserModel.LINGSHI, num=-50)
    rd = random.randint(1, 100)
    msg = "你打开了盒子，发现了"
    if rd <= 74:
        names = filter_item_name(type=['武器', '法宝', '心法', '功法', '神通', '素材', '符咒'],
                                 level=['凡人', '锻体', '练气', '筑基', '结丹', '金丹'])
        name = random.choice(names)
        item = get_item_by_name(name)
        add_item(gid, uid, item)
        msg += f"{name}"
    elif rd <= 99:
        add_user_counter(gid, uid, UserModel.LINGSHI, 10)
        msg += f"老太太的菜篮子（内含你被碰瓷亏的10灵石）"
    else:
        get_lingshi = random.randint(300, 500)
        add_user_counter(gid, uid, UserModel.LINGSHI, get_lingshi)
        msg += f"村口胡了国士无双人的钱包（内含{get_lingshi}灵石）"
    return (True, msg)


@msg_route("燃魂丹")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if get_user_counter(gid, uid, UserModel.RANHUN):
        return (False, "你已经服用过了燃魂丹，无法服用多个")
    save_user_counter(gid, uid, UserModel.RANHUN, 1)
    return (True, "你服用了燃魂丹 下一次主动对战战斗力翻倍 自己必定死亡")

@msg_route("焕体丹-中")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    luck = random.randint(1,5)
    msg = "你使用了焕体丹-中，"
    if luck == 1:
        user.mp += 50
        msg += " mp增加了50点。"
    elif luck <= 2:
        user.hp += 150
        msg += " hp增加了150点。"
    else :
        user.wuxing += 20
        msg += " 悟性增加了20点。"
    ct._save_user_info(user)
    return (True, msg)

@msg_route("风水混元丹")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    luck = random.randint(1,2)
    msg = "你使用了风水混元丹，"
    if luck == 1:
        user.act += 20
        user.act2 += 20
        msg += "物理法术攻击力提升了20点。"
    else:
        user.defen += 20
        user.defen2 += 20
        msg += "物理法术防御力提升了20点。"
    ct._save_user_info(user)
    return (True, msg)

@msg_route("洗髓丹-新")
async def choose_girl(msg, bot, ev: CQEvent):
    if not msg:
        return (False, f"你没有指定灵根")
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    linggen = msg[0]
    user.linggen = linggen
    ct._save_user_info(user)
    return (True, f"洗髓丹-新，灵根变为[{linggen}]")

@msg_route("洗髓丹-减")
async def choose_girl(msg, bot, ev: CQEvent):
    if not msg:
        return (False, f"你没有指定灵根")
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    linggen = str(msg[0][0]).split()
    linggen = str(linggen[0])
    if linggen not in user.linggen:
        return (False, f"你没有{linggen}灵根，请重新指定")
    user.linggen = user.linggen.replace(linggen,'')
    ct._save_user_info(user)
    return (True, f"你使用了洗髓丹-减，灵根变为[{user.linggen}]")

@msg_route("洗髓丹-增")
async def choose_girl(msg, bot, ev: CQEvent):
    if not msg:
        return (False, f"你没有指定灵根")
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    linggen = str(msg[0][0]).split()
    linggen = str(linggen[0])
    if linggen in user.linggen:
        return (False, f"你已拥有{linggen}灵根，请重新指定")
    user.linggen = user.linggen + linggen
    ct._save_user_info(user)
    return (True, f"你使用了洗髓丹-增，灵根变为[{user.linggen}]")

@msg_route("法宝盒子-元婴")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    names = filter_item_name(type=['法宝'], level=['元婴'])
    name = random.choice(names)
    fabao_item = get_item_by_name(name)
    add_item(user.gid, user.uid, fabao_item)
    return (True, f"你使用了法宝盒子-元婴，获得法宝 {name}")

@msg_route("灵石盒子-大")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    lingshi = random.randint(1500,2000)
    add_user_counter(gid, uid, UserModel.LINGSHI, lingshi)
    return (True, f"你使用了灵石盒子-大，增加{lingshi}灵石]")

@msg_route("灵石盒子-中")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    lingshi = random.randint(1000,1500)
    add_user_counter(gid, uid, UserModel.LINGSHI, lingshi)
    return (True, f"你使用了灵石盒子-中，增加{lingshi}灵石]")

@msg_route("灵石盒子-小")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    lingshi = random.randint(500,1000)
    add_user_counter(gid, uid, UserModel.LINGSHI, lingshi)
    return (True, f"你使用了灵石盒子-小，增加{lingshi}灵石]")

@msg_route("新年礼盒")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    lingshi = 666
    add_user_counter(gid, uid, UserModel.LINGSHI, lingshi)
    return (True, f"来自小天道的祝福，获得{lingshi}灵石，祝你新年快乐，平安喜乐！")

@msg_route("风水造化丹")
async def choose_girl(msg, bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    msg = "你使用了风水造化丹，"
    user.act += 20
    user.hp +=20
    msg += "HP提升了20点 物理攻击力提升了20点。"
    ct._save_user_info(user)
    return (True, msg)