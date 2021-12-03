from .xiuxian_config import *


@sv.on_fullmatch(["#突破"])
async def xiulian(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    if (user.level not in PINGJING) or (user.exp < EXP_NEED_MAP[str(user.level)]):
        await bot.finish(ev, "你当前还未遇到瓶颈")
    await user.check_and_start_cd(bot, ev)
    sucess, log = await tupo(str(user.level), user, bot, ev)
    if sucess:
        user.exp = 0
        user.level += 1
    ct = XiuxianCounter()
    ct._save_user_info(user)
    await bot.finish(ev, log, at_sender=True)


register = dict()


# 使用道具
async def tupo(name, user, bot, ev):
    func = register.get(name)
    if func:
        return await func(user, bot, ev)
    return (False, "无法突破")


# 注解msg 传入正则表达式进行匹配
def msg_route(item_name):
    def show(func):
        async def warpper(user, bot, ev: CQEvent):
            return await func(user, bot, ev)

        register[item_name] = warpper
        return warpper

    return show


# 凡人突破
@msg_route("1")
async def _level_up(user: AllUserInfo, bot, ev: CQEvent):
    user.hp += random.randint(1, 10)
    user.act += random.randint(1, 5)
    return (True, f"你成功突破到了锻体！")


# 锻体突破
@msg_route("6")
async def _level_up(user: AllUserInfo, bot, ev: CQEvent):
    rd = random.randint(1, 100)
    need = 90 + int(user.tizhi / 20)
    if rd > need:
        return (False, f"突破失败，请重新突破")
    user.hp += int(0.2 * user.hp)
    user.act += int(0.2 * user.act)
    user.act2 += 10
    return (True, f"你成功突破到了练气！")


# 练气突破
@msg_route("9")
async def _level_up(user: AllUserInfo, bot, ev: CQEvent):
    rd = random.randint(1, 100)
    need = 50 + int(user.lingli / 10)
    eat = get_user_counter(user.gid, user.uid, UserModel.ZHUJIDAN)
    if eat:
        save_user_counter(user.gid, user.uid, UserModel.ZHUJIDAN, 0)
        need = 100
        user.defen += 5
        user.defen2 += 5
    if rd > need:
        user.exp = 0
        return (False, f"突破失败，经验清空！")
    user.hp += int(0.1 * user.hp)
    user.mp += int(0.1 * user.mp)
    user.act += int(0.1 * user.act)
    user.act2 += int(0.1 * user.act2)
    user.defen += int(0.1 * user.defen)
    user.defen2 += int(0.1 * user.defen2)
    return (True, f"你成功突破到了筑基！")


# 筑基突破
@msg_route("12")
async def _level_up(user: AllUserInfo, bot, ev: CQEvent):
    rd = random.randint(1, 100)
    need = 50
    if rd > need:
        user.exp = 0
        return (False, f"突破失败，经验清空！")
    user.hp += int(0.1 * user.hp)
    user.mp += int(0.1 * user.mp)
    user.act += int(0.1 * user.act)
    user.act2 += int(0.1 * user.act2)
    user.defen += int(0.1 * user.defen)
    user.defen2 += int(0.1 * user.defen2)
    return (True, f"你成功突破到了结丹！")


# 结丹突破
@msg_route("15")
async def _level_up(user: AllUserInfo, bot, ev: CQEvent):
    rd = random.randint(1, 100)
    need = 20
    item_1 = get_item_by_name("琅琊果")
    item_2 = get_item_by_name("木枯藤")
    item_3 = get_item_by_name("玄牝珠")
    item_4 = get_item_by_name("朱果")
    item_5 = get_item_by_name("赭黄精")
    have_1 = check_have_item(user.gid, user.uid, item_1)
    have_2 = check_have_item(user.gid, user.uid, item_2)
    have_3 = check_have_item(user.gid, user.uid, item_3)
    have_4 = check_have_item(user.gid, user.uid, item_4)
    have_5 = check_have_item(user.gid, user.uid, item_5)
    if have_1:
        need += 10
        use_item(user.gid, user.uid, item_1)
    if have_2:
        need += 10
        use_item(user.gid, user.uid, item_2)
    if have_3:
        need += 10
        use_item(user.gid, user.uid, item_3)
    if have_4:
        need += 10
        use_item(user.gid, user.uid, item_4)
    if have_5:
        need += 10
        use_item(user.gid, user.uid, item_5)
    if rd > need:
        user.exp = 0
        return (False, f"突破失败，经验清空！(天才地宝各损失1份)")
    if have_1:
        user.act += 20
    if have_2:
        user.hp += 50
    if have_3:
        user.mp += 30
    if have_4:
        user.act2 += 20
    if have_5:
        user.defen += 10
        user.defen2 += 10
    user.hp += int(0.1 * user.hp)
    user.mp += int(0.1 * user.mp)
    user.act += int(0.1 * user.act)
    user.act2 += int(0.1 * user.act2)
    user.defen += int(0.1 * user.defen)
    user.defen2 += int(0.1 * user.defen2)
    return (True, f"你成功突破到了金丹！(天才地宝各损失1份)")


# 金丹突破
@msg_route("18")
async def _level_up(user: AllUserInfo, bot, ev: CQEvent):
    count = get_user_counter(user.gid, user.uid, UserModel.JINDANSHA)
    if count < 5:
        return (False, f"不经历生死，如何碎丹，需要与金丹后期生死战5场以上")
    user.hp += int(0.1 * user.hp)
    user.mp += int(0.1 * user.mp)
    user.act += int(0.1 * user.act)
    user.act2 += int(0.1 * user.act2)
    user.defen += int(0.1 * user.defen)
    user.defen2 += int(0.1 * user.defen2)
    return (True, f"你成功突破到了元婴！")


# 元婴突破
@msg_route("21")
async def _level_up(user: AllUserInfo, bot, ev: CQEvent):
    return (False, f"v1.4版本再来突破吧")
    rd = random.randint(1, 100)
    need = 80 + int(user.lingli / 10)
    if rd > need:
        user.exp = 0
        return (False, f"突破失败，经验清空！")
    user.hp += int(0.1 * user.hp)
    user.mp += int(0.1 * user.mp)
    user.act += int(0.1 * user.act)
    user.act2 += int(0.1 * user.act2)
    user.defen += int(0.1 * user.defen)
    user.defen2 += int(0.1 * user.defen2)
    return (True, f"你成功突破到了筑基！")


# 化神突破
@msg_route("24")
async def _level_up(user: AllUserInfo, bot, ev: CQEvent):
    rd = random.randint(1, 100)
    need = 80 + int(user.lingli / 10)
    if rd > need:
        user.exp = 0
        return (False, f"突破失败，经验清空！")
    user.hp += int(0.1 * user.hp)
    user.mp += int(0.1 * user.mp)
    user.act += int(0.1 * user.act)
    user.act2 += int(0.1 * user.act2)
    user.defen += int(0.1 * user.defen)
    user.defen2 += int(0.1 * user.defen2)
    return (True, f"你成功突破到了筑基！")


# 洞虚突破
@msg_route("27")
async def _level_up(user: AllUserInfo, bot, ev: CQEvent):
    rd = random.randint(1, 100)
    need = 80 + int(user.lingli / 10)
    if rd > need:
        user.exp = 0
        return (False, f"突破失败，经验清空！")
    user.hp += int(0.1 * user.hp)
    user.mp += int(0.1 * user.mp)
    user.act += int(0.1 * user.act)
    user.act2 += int(0.1 * user.act2)
    user.defen += int(0.1 * user.defen)
    user.defen2 += int(0.1 * user.defen2)
    return (True, f"你成功突破到了筑基！")


# 大成突破
@msg_route("30")
async def _level_up(user: AllUserInfo, bot, ev: CQEvent):
    return (False, f"你已大成，无需突破，请前往[混沌绝地]准备雷劫")


# 渡劫突破
@msg_route("31")
async def _level_up(user: AllUserInfo, bot, ev: CQEvent):
    rd = random.randint(1, 100)
    need = 80 + int(user.lingli / 10)
    if rd > need:
        user.exp = 0
        return (False, f"突破失败，经验清空！")
    user.hp += int(0.2 * user.hp)
    user.mp += int(0.2 * user.mp)
    user.act += int(0.2 * user.act)
    user.act2 += int(0.2 * user.act2)
    user.defen += int(0.2 * user.defen)
    user.defen2 += int(0.2 * user.defen2)
    return (True, f"你成功突破到了筑基！")


# 天仙突破
@msg_route("34")
async def _level_up(user: AllUserInfo, bot, ev: CQEvent):
    rd = random.randint(1, 100)
    need = 80 + int(user.lingli / 10)
    if rd > need:
        user.exp = 0
        return (False, f"突破失败，经验清空！")
    user.hp += int(0.2 * user.hp)
    user.mp += int(0.2 * user.mp)
    user.act += int(0.2 * user.act)
    user.act2 += int(0.2 * user.act2)
    user.defen += int(0.2 * user.defen)
    user.defen2 += int(0.2 * user.defen2)
    return (True, f"你成功突破到了筑基！")


# 真仙突破
@msg_route("37")
async def _level_up(user: AllUserInfo, bot, ev: CQEvent):
    rd = random.randint(1, 100)
    need = 80 + int(user.lingli / 10)
    if rd > need:
        user.exp = 0
        return (False, f"突破失败，经验清空！")
    user.hp += int(0.2 * user.hp)
    user.mp += int(0.2 * user.mp)
    user.act += int(0.2 * user.act)
    user.act2 += int(0.2 * user.act2)
    user.defen += int(0.2 * user.defen)
    user.defen2 += int(0.2 * user.defen2)
    return (True, f"你成功突破到了筑基！")


# 金仙突破
@msg_route("40")
async def _level_up(user: AllUserInfo, bot, ev: CQEvent):
    return (False, f"穹顶之上，无法突破")
