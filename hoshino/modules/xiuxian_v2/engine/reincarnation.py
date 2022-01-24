from hoshino.modules.xiuxian_v2.common import *


# 处理轮回buff
def his_buff(user: AllUserInfo):
    # 记录最大等级
    his_map = UserHistoryModelDao.get_all_user_history(user.uid)
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
def _(user: AllUserInfo, his_map):
    # 悟性 气感 神识 体质 灵力 +10
    user.attr.spiritual += 10
    user.attr.comprehension += 10
    user.attr.constitution += 10
    user.attr.magic_power += 10
    user.attr.perception += 10
    # 寿元+20
    user.attr.age_max += 20
    return "此子乃大能转世,资质极佳"


@condition_route("前世记忆")
def _(user, his_map):
    if his_map.get(UserHistory.RESTART_ABILITY) == 0:
        return False
    if random.randint(1, 20) > 1:
        return False
    return True


@effect_route("前世记忆")
def _(user: AllUserInfo, his_map):
    get_ability_by_name()
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
    user.attr.constitution += 20
    user.attr.hp += 200
    user.attr.defend1 += 15
    user.attr.atk1 += 10
    return f"此人天生神力,极度强壮!"


@condition_route("魔神之心")
def _(user, his_map):
    if his_map.get(UserHistory.MAX_MP) < 500:
        return False
    if his_map.get(UserHistory.MAX_DEFEND2) < 100:
        return False
    if random.randint(1, 20) > 1:
        return False
    return True


@effect_route("魔神之心")
def _(user: AllUserInfo, his_map):
    user.attr.magic_power += 20
    user.attr.perception += 20
    user.attr.mp += 100
    user.attr.defend2 += 15
    user.attr.atk2 += 10
    return f"此人气感极佳，未入仙界先得灵气"


@condition_route("心如明镜")
def _(user, his_map):
    if random.randint(1, 50) > 1:
        return False
    return True


@effect_route("心如明镜")
def _(user: AllUserInfo, his_map):
    UserModelDao.add_user_counter(user.uid, UserModel.JINDANSHA, 3)
    return f"此人心如明镜,没有心魔"


@condition_route("职业特性")
def _(user, his_map):
    return True


@effect_route("先天特性")
def _(user: AllUserInfo, his_map):
    names = ["大盗圣人", "道法自然"]
    name = random.choice(names)
    user.ability.append(name)
    return f"由于先天特性获得了能力{name}"
