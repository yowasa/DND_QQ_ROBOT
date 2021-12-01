from hoshino.modules.xiuxian.xiuxian_config import *
import random


# 数值随机波动10%
def deviation(value, rang):
    double_range = 2 * rang
    rd = random.randint(0, double_range)
    dev = 1 + (rd - rang) / 100
    return int(value * dev)


# 初始化buff
def get_hp_mp(my: AllUserInfo):
    hp = my.battle_hp
    mp = my.battle_mp
    if my.shangshi == 1:
        hp = int(0.7 * hp)
    elif my.shangshi == 2:
        hp = int(0.3 * hp)
        mp = int(0.5 * mp)
    elif my.shangshi == 3:
        hp = 0
        mp = 0
    return hp, mp


def init_content(my: AllUserInfo):
    content = {}
    # 初始化属性
    # 最大血量
    content["name"] = my.name
    content["max_hp"] = my.battle_hp
    content["max_mp"] = my.battle_mp
    # 当前血量
    content["hp"], content["mp"] = get_hp_mp(my)
    # 攻击
    content["atk1"] = my.battle_atk1
    content["atk2"] = my.battle_atk2
    # 防御
    content["defen1"] = my.battle_defen1
    content["defen2"] = my.battle_defen2
    # 技巧
    content["skill"] = my.skill
    # 杀人数
    content["sharen"] = my.sharen

    skill_cd = {}
    content["skills"] = skill_cd
    content["effect"] = {}

    # 伤害类型
    content["dmg_type"] = 0
    # 武器特性
    equip = get_equip_by_name(my.wuqi)
    if equip:
        if equip.get("effect"):
            content["effect"][equip["name"]] = equip.get("effect")
            skill_cd[equip["name"]] = 0
        if equip.get("damage_type"):
            content["dmg_type"] = equip["damage_type"]
    # 法宝
    fabao = get_fabao_by_name(my.fabao)
    if fabao:
        if fabao.get("effect"):
            content["effect"][fabao["name"]] = fabao.get("effect")
            skill_cd[fabao["name"]] = 0

    # 功法
    gongfa = get_gongfa_by_name(my.gongfa2)
    if gongfa:
        if gongfa.get("effect"):
            content["effect"][gongfa["name"]] = gongfa.get("effect")
            skill_cd[gongfa["name"]] = 0

    content["boost"] = my.battle_boost
    content["double"] = my.battle_double
    content["dodge"] = my.battle_dodge
    # buff标识
    content["is_boost"] = False
    content["is_double"] = False
    content["is_dodge"] = False
    # 跳过战斗阶段标识
    content["ts"] = False
    # 总伤害
    content["total_damage"] = 0
    # 运势
    content["yunshi"] = random.randint(1, 100)
    # buffer_state
    content["next_atk1"] = []
    content["next_atk2"] = []
    content["next_defen1"] = []
    content["next_defen2"] = []
    content["next_ts"] = []
    content["next_ts"] = []
    content["next_boost"] = []
    content["next_double"] = []
    content["next_dodge"] = []
    content["next_is_boost"] = []
    content["next_is_double"] = []
    content["next_is_dodge"] = []
    # 初始化
    return content


# 组装计算所需的上下文
def build_content(my_content, enemy_content, turn):
    content = {}
    for i in my_content.keys():
        content["my_" + i] = my_content[i]
    for i in enemy_content.keys():
        content["enemy_" + i] = enemy_content[i]
    content["turn"] = turn
    return content


# 校验触发技能
def check_condition(skill, my_content, enemy_content, turn):
    content = build_content(my_content, enemy_content, turn)
    return eval(my_content["effect"][skill]["condition"], content)


# 技能影响
def effect(skill, my_content, enemy_content, turn, logs):
    effect = my_content["effect"][skill]["effect"]
    content = build_content(my_content, enemy_content, turn)
    my = effect.get("my")
    if my:
        for i in my.keys():
            if my[i]["type"] == "const":
                my_content[i] = my[i]["value"]
            elif my[i]["type"] == "exec":
                my_content[i] = eval(my[i]["value"], content)
    enemy = effect.get("enemy")
    if enemy:
        for i in enemy.keys():
            if enemy[i]["type"] == "const":
                enemy_content[i] = enemy[i]["value"]
            elif enemy[i]["type"] == "exec":
                enemy_content[i] = eval(enemy[i]["value"], content)

    my_next = effect.get("my_next")
    if my_next:
        for i in my_next.keys():
            if my_next[i]["type"] == "const":
                my_content[i].extend(my_next[i]["value"])
            elif my_next[i]["type"] == "exec":
                li = [eval(j, content) for j in my_next[i]["value"]]
                my_content[i].extend(li)
    enemy_next = effect.get("enemy_next")
    if enemy_next:
        for i in enemy_next.keys():
            if enemy_next[i]["type"] == "const":
                enemy_content[i].extend(enemy_next[i]["value"])
            elif enemy_next[i]["type"] == "exec":
                li = [eval(j, content) for j in enemy_next[i]["value"]]
                enemy_content[i].extend(li)
    content = build_content(my_content, enemy_content, turn)
    skill_log = my_content["effect"][skill].get('log')
    if skill_log:
        skill_log = skill_log.format(**content)
        logs.append(f"{skill_log}")
    if my_content["effect"][skill].get("cd"):
        my_content["skills"][skill] = my_content["effect"][skill]["cd"]


# 技能执行引擎
def skill_engine(time: str, my_content, enemy_content, turn: int):
    logs = []
    skill = []
    for i in my_content["skills"].keys():
        if my_content["skills"][i] == 0:
            if my_content["effect"][i]["time"] == time:
                skill.append(i)
    for i in skill:
        if check_condition(i, my_content, enemy_content, turn):
            cost = my_content["effect"][i].get("cost") if my_content["effect"][i].get("cost") else 0
            if cost > my_content['mp']:
                continue
            else:
                my_content['mp'] -= cost
                effect(i, my_content, enemy_content, turn, logs)
    return logs


# 决斗引擎
def content_get(param, my_content):
    if my_content.get("next_" + param):
        return my_content.get("next_" + param).pop()
    else:
        return my_content.get(param)


# 模拟计算应该造成多少伤害
def duel_buff(my_content, enemy_content):
    # 初始化dmg_log
    my_content["damage_log"] = f"{my_content['name']}"
    # 基础atk
    dmg = 0
    atk1 = content_get("atk1", my_content)
    atk2 = content_get("atk2", my_content)
    defen1 = content_get("defen1", enemy_content)
    defen2 = content_get("defen2", enemy_content)
    is_boost = content_get("is_boost", my_content)
    is_dodge = content_get("is_dodge", enemy_content)
    is_double = content_get("is_double", my_content)
    dmg_type = content_get("dmg_type", my_content)
    # 处理自适应伤害
    if dmg_type == 2:
        dmg_type = 0 if defen1 <= defen2 else 1
    # 术法攻击不会被闪避
    if dmg_type:
        is_dodge = False

    ts = content_get('ts', my_content)
    if ts:
        my_content["damage_log"] += f"无法行动!"
        my_content["total_damage"] = dmg
        return
        # 倍率加成

    boost_tag = ""
    if is_boost:
        atk1 = int(1.5 * atk1)
        atk2 = int(1.5 * atk2)
        boost_tag = "(暴击)"
    if is_dodge:
        my_content["damage_log"] += f"攻击被闪避!"
    else:
        if dmg_type:
            base = atk2 * (100 / (100 + defen2))
            each = deviation(base, 20)
            dmg += each
            my_content["damage_log"] += f"造成了{each}点术法伤害{boost_tag}"
        else:
            base = atk1 * (100 / (100 + defen1))
            each = deviation(base, 50) + random.randint(1, 10)
            dmg += each
            my_content["damage_log"] += f"造成了{each}点伤害{boost_tag}"

        if is_double:
            if dmg_type:
                base = atk2 * (100 / (100 + defen2))
                each = deviation(base, 20)
                dmg += each
                my_content["damage_log"] += f",连击造成了{each}点术法伤害{boost_tag} "
            else:
                base = atk1 * (100 / (100 + defen1))
                each = deviation(base, 50)
                dmg += each
                my_content["damage_log"] += f",连击造成了{each}点伤害{boost_tag} "
    my_content["total_damage"] = dmg


def judge_damage(my_content, enemy_content):
    # 判断我方 boost 连击 闪避
    judge_rate(my_content)
    # 判断地方 boost 连击 闪避
    judge_rate(enemy_content)
    # 计算伤害
    duel_buff(my_content, enemy_content)
    duel_buff(enemy_content, my_content)


# 判断是否触发战斗特征
def judge_rate(content):
    judge_li = ["boost", "double", "dodge"]
    for i in judge_li:
        value = content_get(i, content)
        rd = random.randint(1, 100)
        content["is_" + i] = (rd <= value)


def battle(my: AllUserInfo, enemy: AllUserInfo):
    logs = []
    my_content = init_content(my)
    enemy_content = init_content(enemy)
    # 战斗开始
    logs.append(f"{my_content['name']}HP:{my_content['hp']}\t {enemy_content['name']}HP:{enemy_content['hp']}")
    # 触发技能
    # 有人血量归零
    if my_content["hp"] <= 0 or enemy_content["hp"] <= 0:
        return end_battle(logs, my_content, enemy_content)
    turn = 0
    # 准备log
    pre_pare_log = []
    pre_pare_log.extend(skill_engine("init", my_content, enemy_content, turn))
    pre_pare_log.extend(skill_engine("init", enemy_content, my_content, turn))
    pre_pare_log.extend(skill_engine("prepare", my_content, enemy_content, turn))
    pre_pare_log.extend(skill_engine("prepare", enemy_content, my_content, turn))
    pre_pare_log.extend(skill_engine("begin", my_content, enemy_content, turn))
    pre_pare_log.extend(skill_engine("begin", enemy_content, my_content, turn))
    if pre_pare_log:
        logs.append(','.join(pre_pare_log))
    while True:
        turn = turn + 1
        tun_log = [f"第{turn}回合交手"]
        # 技能cd-1
        for i in my_content["skills"].keys():
            if my_content["skills"][i] > 0:
                my_content["skills"][i] -= 1
        for i in enemy_content["skills"].keys():
            if enemy_content["skills"][i] > 0:
                enemy_content["skills"][i] -= 1

        # 伤害计算前触发技能
        tun_log.extend(skill_engine("before_damage", my_content, enemy_content, turn))
        tun_log.extend(skill_engine("before_damage", enemy_content, my_content, turn))

        # 判定伤害触发
        judge_damage(my_content, enemy_content)
        # 我方伤害日志
        tun_log.append(my_content["damage_log"])
        # 扣血动作
        enemy_content["hp"] -= my_content["total_damage"]
        # 地方伤害日志
        tun_log.append(enemy_content["damage_log"])
        # 扣血动作
        my_content["hp"] -= enemy_content["total_damage"]
        # 触发技能
        tun_log.extend(skill_engine("after_damage", my_content, enemy_content, turn))
        tun_log.extend(skill_engine("after_damage", enemy_content, my_content, turn))
        tun_log.extend(skill_engine("battle_end", my_content, enemy_content, turn))
        tun_log.extend(skill_engine("battle_end", enemy_content, my_content, turn))
        tun_log.extend(skill_engine("turn_end", my_content, enemy_content, turn))
        tun_log.extend(skill_engine("turn_end", enemy_content, my_content, turn))
        logs.append(",".join(tun_log))

        # 重置双方造成伤害和回复
        my_content["total_damage"] = 0
        enemy_content["total_damage"] = 0
        # 随机出运势
        my_content["yunshi"] = random.randint(1, 100)
        enemy_content["yunshi"] = random.randint(1, 100)
        # 有人血量归零
        if my_content["hp"] <= 0 or enemy_content["hp"] <= 0:
            return end_battle(logs, my_content, enemy_content)
        if turn > 10:
            logs.append(f'不分胜负')
            return end_battle(logs, my_content, enemy_content)


def end_battle(logs, my_content, enemy_content):
    return my_content['hp'], enemy_content['hp'], logs
