from .xiuxian_config import *
from hoshino import util
import random

# 游历

EVENT_MAP = {
    "新手村": {"与人切磋": 40, "高人指点": 20, "帮助村民": 10, "游山玩水": 10, "乐不思蜀": 10, "以文会友": 5, "仙人奇遇": 5},
    "大千世界": {"尘世征战": 40, "降妖除魔": 20, "红尘历练": 15, "深山灵泉": 10, "毒沼泥潭": 10, "断崖密室": 5},
    "修仙秘境": {"无": 100}
}


@sv.on_fullmatch(["#游历"])
async def youli(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if not user:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    if not flmt.check(uid):
        user.daohang -= 1
        if user.daohang < 0:
            delete_user(user)
            await bot.finish(ev, f"道心不稳，爆体而亡!")
        ct._save_user_info(user)
        await util.silence(ev, 10 * 60, skip_su=False)
        await bot.finish(ev, f"做事急躁，有损道心，道行-1，距离下次操作还需要{round(int(flmt.left_time(uid)))}秒")
    flmt.start_cd(uid)
    all_li = EVENT_MAP[user.map]
    rn = random.randint(1, 100)
    total = 0
    msg = ""
    for i in all_li.keys():
        total += all_li[i]
        if rn <= total:
            msg = i
            break
    result = await _youli(msg, bot, ev)
    await bot.send(ev, result, at_sender=True)


register = dict()


async def _youli(name, bot, ev):
    func = register.get(name)
    if func:
        return await func(bot, ev)
    return "游历未实装"


# 注解msg 传入正则表达式进行匹配
def msg_route(item_name):
    def show(func):
        async def warpper(bot, ev: CQEvent):
            return await func(bot, ev)

        register[item_name] = warpper
        return warpper

    return show


@msg_route("无")
async def wu(bot, ev: CQEvent):
    return f"这里人数太少,无法游历。"


@msg_route("与人切磋")
async def qiecuo(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if not user:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    user.exp += 5
    ct._save_user_info(user)
    return f"你与村里的道友切磋了一下，获得了5点经验值。"


@msg_route("高人指点")
async def qiecuo(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if not user:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    if user.skill < 30:
        user.skill += 1
    ct._save_user_info(user)
    return f"你偶遇贵人，略微传授了你两招，战斗技巧略微提升了。"


@msg_route("帮助村民")
async def qiecuo(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    kills = get_user_counter(gid, uid, UserModel.KILL)
    kills -= 1
    save_user_counter(gid, uid, UserModel.KILL, kills)
    return f"你扶了老奶奶过马路，感觉名声变好了一些"


@msg_route("游山玩水")
async def qiecuo(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if not user:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    get_wuxing = 0
    if user.wuxing < 70:
        get_wuxing = random.randint(1, 5)
        user.wuxing += get_wuxing
    ct._save_user_info(user)
    return f"你四处游山玩水，对自然的感悟加深了（悟性+{get_wuxing}）。"


@msg_route("乐不思蜀")
async def qiecuo(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if not user:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    get_wuxing = 0
    if user.wuxing > 20:
        get_wuxing = random.randint(1, 5)
        user.wuxing -= get_wuxing
    ct._save_user_info(user)
    return f"你沉溺于这里安逸的环境，不思进取（悟性-{get_wuxing}）。"


@msg_route("以文会友")
async def qiecuo(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if not user:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    user.daohang += 2
    ct._save_user_info(user)
    return f"你与朋友进行了论道（道行+2）。"


@msg_route("仙人奇遇")
async def qiecuo(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    item = get_item_by_name("瞬息万里符")
    result = add_item(gid, uid, item, num=1)
    if result:
        return f"你偶遇了一位仙人，对你十分赏识，送了你[瞬息万里符],保你平安。"
    else:
        return f"你偶遇了一位仙人，对你十分赏识，送了你[瞬息万里符],保你平安，但是你背包已经满了，只得放弃"


@msg_route("尘世征战")
async def qiecuo(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if not user:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    user.exp += 10
    ct._save_user_info(user)
    return f"你参与了尘世的战争，帮助其获得了战争的胜利（经验+10）。"


@msg_route("降妖除魔")
async def qiecuo(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    lingshi = get_user_counter(gid, uid, UserModel.LINGSHI)
    get_lingshi = random.randint(5, 10)
    lingshi += get_lingshi
    save_user_counter(gid, uid, UserModel.LINGSHI, lingshi)
    return f"你除掉了祸害一方的妖魔，从妖魔身体上提炼了{get_lingshi}个灵石。"


@msg_route("红尘历练")
async def qiecuo(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if not user:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    user.daohang += 3
    ct._save_user_info(user)
    return f"你结识了尘世间的伴侣，度过了一段如梦般的时光（道行+3）。"


@msg_route("深山灵泉")
async def qiecuo(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if not user:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    get_lingli = 0
    if user.lingli < 100:
        get_lingli = 3
        user.lingli += get_lingli

    ct._save_user_info(user)
    return f"你前往探索一出深山，发现了充满灵力的泉水（灵力+{get_lingli}）。"


@msg_route("毒沼泥潭")
async def qiecuo(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if not user:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    user.lingli -= 3
    if user.lingli < 0:
        user.lingli = 0
    ct._save_user_info(user)
    return f"你强行读过了一出泥沼之地，发现自己重了沼毒，花费灵力进行驱散（灵力-3）。"


@msg_route("断崖密室")
async def qiecuo(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    item = get_item_by_name("造化丸")
    result = add_item(gid, uid, item, num=1)
    if result:
        return f"你在一出断崖下找到了仙人曾经居住的洞穴,一番探索后找到了[造化丸]。"
    else:
        return f"你在一出断崖下找到了仙人曾经居住的洞穴,一番探索后找到了[造化丸]，但是你背包已经满了，只得放弃"
