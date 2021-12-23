from .xiuxian_config import *


# 处理轮回buff
def his_buff(user):
    # 记录最大等级
    his_map = get_all_user_history(user.gid, user.uid)
    msg_li = []
    max_level = his_map.get(UserHistory.MAX_LEVEL)
    max_count = int(max_level / 10) + 1
    eff_li = []
    for i in condition_register.keys():
        if max_count <= 0:
            break
        func = condition_register.get(i)
        if func(user, his_map):
            eff_li.append(i)
            max_count -= 1
    for i in eff_li:
        func = effect_register.get(i)
        msg_li.append(func(user, his_map))
    return msg_li


condition_register = dict()
effect_register = dict()


# 注解msg 传入正则表达式进行匹配
def condition_route(item_name):
    def show(func):
        def warpper(user, his_map):
            return func(user, his_map)

        condition_register[item_name] = warpper
        return warpper

    return show


# 注解msg 传入正则表达式进行匹配
def effect_route(item_name):
    def show(func):
        def warpper(user, his_map):
            return func(user, his_map)

        effect_register[item_name] = warpper
        return warpper

    return show


@condition_route("大能转世")
def _(user, his_map):
    max_level = his_map.get(UserHistory.MAX_LEVEL)
    if his_map.get(UserHistory.MAX_LEVEL) <= 15:
        return False
    limit = max_level - 15
    if random.randint(1, 25) <= limit:
        return True
    return False


@effect_route("大能转世")
def _(user, his_map):
    user.wuxing = 70
    user.lingli = 0
    user.daohang = 20
    user.act = 10
    user.defen = 10
    user.defen2 = 10
    user.hp = 100
    user.mp = 100
    user.skill = 20
    user.tizhi = 20
    return "此子乃大能转世,资质极佳"


@condition_route("前世记忆")
def _(user, his_map):
    if his_map.get(UserHistory.RESTART_XINFA) == 0:
        return False
    if his_map.get(UserHistory.RESTART_GONGFA) == 0:
        return False
    if his_map.get(UserHistory.RESTART_SHENTONG) == 0:
        return False
    if random.randint(1, 20) > 1:
        return False
    return True


@effect_route("前世记忆")
def _(user: AllUserInfo, his_map):
    id_li = [his_map.get(UserHistory.RESTART_XINFA), his_map.get(UserHistory.RESTART_GONGFA),
             his_map.get(UserHistory.RESTART_SHENTONG)]
    item_id = random.choice(id_li)
    item = ITEM_INFO[str(item_id)]
    if item['type'] == "心法":
        user.gongfa = item['name']
    elif item['type'] == "功法":
        user.gongfa2 = item['name']
    elif item['type'] == "神通":
        user.gongfa3 = item['name']
    return f"此人觉醒了部分前世的记忆，领悟了[{item['type']}]{item['name']}"


@condition_route("仙人遗蜕")
def _(user, his_map):
    if his_map.get(UserHistory.RESTART_LINGSHI) < 100:
        return False
    if his_map.get(UserHistory.RESTART_ITEM) == 0:
        return False
    if random.randint(1, 20) > 1:
        return False
    return True


@effect_route("仙人遗蜕")
def _(user: AllUserInfo, his_map):
    get_lingshi = his_map.get(UserHistory.RESTART_LINGSHI)
    add_user_counter(user.gid, user.uid, UserModel.LINGSHI, get_lingshi)
    item_id = his_map.get(UserHistory.RESTART_ITEM)
    item = ITEM_INFO[str(item_id)]
    add_item_ignore_limit(user.gid, user.uid, item)
    return f"此人发现了仙人遗蜕，获得了遗留下来的{get_lingshi}灵石和[{item['type']}]{item['name']}"


@condition_route("魔神之体")
def _(user, his_map):
    if his_map.get(UserHistory.MAX_HP) < 1000:
        return False
    if his_map.get(UserHistory.MAX_DEFEN1) < 100:
        return False
    if random.randint(1, 20) > 1:
        return False
    return True


@effect_route("魔神之体")
def _(user: AllUserInfo, his_map):
    user.tizhi = 150
    user.hp += 200
    user.defen += 20
    return f"此人天生神力,极度强壮!"


@condition_route("魔神之心")
def _(user, his_map):
    if his_map.get(UserHistory.MAX_MP) < 500:
        return False
    if his_map.get(UserHistory.MAX_DEFEN2) < 100:
        return False
    if random.randint(1, 20) > 1:
        return False
    return True


@effect_route("魔神之心")
def _(user: AllUserInfo, his_map):
    user.lingli = 150
    user.mp += 100
    user.defen2 += 25
    user.act2 = 30
    return f"此人气感极佳，未入仙界先得灵气"


@condition_route("道法自然")
def _(user, his_map):
    if random.randint(1, 50) > 1:
        return False
    return True


@effect_route("道法自然")
def _(user: AllUserInfo, his_map):
    user.gongfa3 = '大罗洞观'
    user.daohang += 30
    return f"此人对天地理解极深，领悟[神通]大罗洞观"


@condition_route("心如明镜")
def _(user, his_map):
    if random.randint(1, 50) > 1:
        return False
    return True


@effect_route("心如明镜")
def _(user: AllUserInfo, his_map):
    add_user_counter(user.gid, user.uid, UserModel.JINDANSHA, 3)
    return f"此人心如明镜,没有心魔"





