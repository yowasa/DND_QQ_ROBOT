from hoshino.util.utils import get_message_at, get_message_text
from .battle import *
from .xiuxian_base import *

@sv.on_prefix(["#护法"])
async def hufa(bot, ev: CQEvent):
    gid = ev.group_id
    my = await get_ev_user(bot, ev)
    if my.level < 18:
        await bot.finish(ev, f"只有达到金丹后期才能为他人护法")
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
        await bot.finish(ev, f"不能对自己护法（恼）")
    if get_user_counter(enemy.gid, enemy.uid, UserModel.HUFA_NUM) >= 4:
        await bot.finish(ev, f"对方已经有足够人员护法")
    await my.check_and_start_cd(bot, ev)
    add_user_counter(enemy.gid, enemy.uid, UserModel.HUFA_NUM, num=1)
    await bot.finish(ev, f"你为{enemy.name}进行护法，压制了对方对心魔")


@sv.on_fullmatch(["#斩心魔"])
async def zhanmo(bot, ev: CQEvent):
    my = await get_ev_user(bot, ev)
    if (my.level != 18) or (my.exp < EXP_NEED_MAP[str(my.level)]):
        await bot.finish(ev, "你当前还未到金丹瓶颈")

    num = get_user_counter(my.gid, my.uid, UserModel.JINDANSHA)
    if num >= 3:
        await bot.finish(ev, "你已经无心魔可斩。。")
    rates = [0.8, 1.0, 1.2]
    rate = rates[num]
    hufa = get_user_counter(my.gid, my.uid, UserModel.HUFA_NUM)
    rate = rate - hufa * 0.05
    enemy = await get_ev_user(bot, ev)
    enemy.name = '心魔'
    enemy.battle_hp = int(enemy.battle_hp * rate)
    enemy.battle_mp = int(enemy.battle_mp * rate)
    enemy.battle_atk1 = int(enemy.battle_atk1 * rate)
    enemy.battle_atk2 = int(enemy.battle_atk2 * rate)
    enemy.battle_defen1 = int(enemy.battle_defen1 * rate)
    enemy.battle_defen2 = int(enemy.battle_defen2 * rate)
    my_hp, he_hp, send_msg_li = battle(my, enemy)

    if my_hp > 0 and he_hp <= 0:
        save_user_counter(my.gid, my.uid, UserModel.HUFA_NUM, 0)
        add_user_counter(my.gid, my.uid, UserModel.JINDANSHA, 1)
        left = 2 - num
        await bot.finish(ev, '\n'.join(send_msg_li) + f"\n你成功斩除了心魔!还剩{left}个心魔(护法清空)", at_sender=True)
    else:
        my.exp = 0
        ct = XiuxianCounter()
        ct._save_user_info(my)
        save_user_counter(my.gid, my.uid, UserModel.HUFA_NUM, 0)
        save_user_counter(my.gid, my.uid, UserModel.SHANGSHI, 3)
        save_user_counter(my.gid, my.uid, UserModel.JINDANSHA, 0)
        await bot.finish(ev, '\n'.join(send_msg_li) + "\n你斩除心魔失败了。。经验清空，护法清空，进入濒死状态，心魔数量重置。。。", at_sender=True)


@sv.on_fullmatch(["#突破"])
async def xiulian(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    if (user.level not in PINGJING) or (user.exp < EXP_NEED_MAP[str(user.level)]):
        await bot.finish(ev, "你当前还未遇到瓶颈")
    await user.check_in_fuben(bot, ev)
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
    eat = get_user_counter(user.gid, user.uid, UserModel.HUNYUAN)
    if eat:
        save_user_counter(user.gid, user.uid, UserModel.HUNYUAN, 0)
        need += 20
    if rd > need:
        user.exp = 0
        return (False, f"突破失败，经验清空！")
    if eat:
        user.defen += 5
        user.defen2 += 5
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
    if count < 3:
        return (False, f"不驱除心魔，如何碎丹，使用#斩心魔 击杀心魔3次，每击杀金丹后期以可以释放一次心魔")
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
