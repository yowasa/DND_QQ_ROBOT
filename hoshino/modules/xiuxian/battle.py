from .BossCounter import BossCounter, UserDamageCounter
from .xiuxian_config import *
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


def get_equip_atk(wuqi):
    atk = 0
    div = 0
    if wuqi != "赤手空拳":
        equip = get_equip_by_name(wuqi)
        if equip.get("atk1"):
            atk += equip.get("atk1")
            div += 1
        if equip.get("atk2"):
            atk += equip.get("atk2")
            div += 1
    if div:
        atk = int(atk / div)
    return atk


def init_content(my: AllUserInfo):
    content = {}
    # 初始化属性
    # 最大血量
    content["uid"] = my.uid
    content["gid"] = my.gid
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
    # 境界等级
    content["level"] = my.level
    # 伤害倍率
    content["dmg_rate"] = 1
    # 伤害减免
    content["reduce_rate"] = 1
    # 攻击中毒标识
    content["du_flag"] = 0
    # 中毒加深
    content["du_shang"] = 0
    # 体内毒素
    content["du_count"] = 0
    # 额外伤害
    content["ex_atk"] = 0
    # 武器伤害
    content["equip_atk"] = get_equip_atk(my.wuqi)
    # 灵根
    content["linggen"] = my.linggen

    skill_cd = {}
    content["skills"] = skill_cd

    # 伤害类型
    content["dmg_type"] = 0
    # 武器特性
    equip = get_equip_by_name(my.wuqi)
    skills = []
    # 武器
    if equip:
        if equip.get("skill"):
            skills.extend(equip.get("skill"))
        if equip.get("damage_type"):
            content["dmg_type"] = equip["damage_type"]
        else:
            content["dmg_type"] = 0
    # 法宝
    fabao = get_fabao_by_name(my.fabao)
    if fabao:
        if fabao.get("skill"):
            skills.extend(fabao.get("skill"))
    # 功法
    gongfa = get_gongfa_by_name(my.gongfa2)
    if gongfa:
        if gongfa.get("skill"):
            skills.extend(gongfa.get("skill"))
    skills = list(set(skills))
    for i in skills:
        skill_cd[i] = 0

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
    content["next_dmg_rate"] = []
    content["next_reduce_rate"] = []
    content["next_ex_atk"] = []
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
    return eval(BASE_SKILL[skill]["condition"], content)


# 技能影响
def effect(skill, my_content, enemy_content, turn, logs):
    effect = BASE_SKILL[skill]["effect"]
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
    skill_log = BASE_SKILL[skill].get('log')
    if skill_log:
        skill_log = skill_log.format(**content)
        logs.append(f"{skill_log}")
    if BASE_SKILL[skill].get("cd"):
        my_content["skills"][skill] = BASE_SKILL[skill]["cd"]


# 技能执行引擎
def skill_engine(time: str, my_content, enemy_content, turn: int):
    logs = []
    skill = []
    for i in my_content["skills"].keys():
        if my_content["skills"][i] == 0:
            if BASE_SKILL[i]["time"] == time:
                skill.append(i)
    for i in skill:
        if check_condition(i, my_content, enemy_content, turn):
            cost = BASE_SKILL[i].get("cost") if BASE_SKILL[i].get("cost") else 0
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
    dmg_rate = content_get("dmg_rate", my_content)
    reduce_rate = content_get("reduce_rate", enemy_content)
    du_flag = content_get("du_flag", my_content)
    ex_atk = content_get('ex_atk', my_content)
    # 处理自适应伤害
    if dmg_type == 2:
        dmg_type = 0 if atk1 >= atk2 else 1
    # 术法攻击不会被闪避
    if dmg_type:
        is_dodge = False

    ts = content_get('ts', my_content)
    if ts:
        my_content["damage_log"] += f"无法行动!"
        my_content["total_damage"] = dmg
        return

    boost_tag = ""
    if is_boost:
        atk1 = int(1.5 * atk1)
        boost_tag = "(暴击)"
    if is_dodge and dmg_type == 0:
        my_content["damage_log"] += f"攻击被闪避!"
    else:
        if dmg_type:
            base = atk2 * (100 / (100 + defen2)) * dmg_rate * reduce_rate
            each = deviation(base, 20)
            dmg += each
            my_content["damage_log"] += f"造成了{each}点术法伤害"
        else:
            base = atk1 * (100 / (100 + defen1)) * dmg_rate * reduce_rate
            each = deviation(base, 50) + random.randint(1, 10)
            dmg += each
            my_content["damage_log"] += f"造成了{each}点伤害{boost_tag}"
        if is_double:
            if dmg_type:
                base = atk2 * (100 / (100 + defen2)) * dmg_rate * reduce_rate
                each = deviation(base, 20)
                dmg += each
                my_content["damage_log"] += f",连击造成了{each}点术法伤害 "
            else:
                base = atk1 * (100 / (100 + defen1)) * dmg_rate * reduce_rate
                each = deviation(base, 50)
                dmg += each
                my_content["damage_log"] += f",连击造成了{each}点伤害{boost_tag} "
        if du_flag:
            enemy_content['du_count'] += 10
            if is_double:
                enemy_content['du_count'] += 10
    if not is_dodge and ex_atk:
        ex_dmg = ex_atk
        dmg += ex_dmg
        my_content["damage_log"] += f",额外造成{ex_dmg}附加伤害!"
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


def duel_skill(my, enemy):
    if my['skill'] > enemy['skill']:
        my['boost'] += my['skill'] / enemy['skill'] * 2
        my['dodge'] += my['skill'] / enemy['skill']
    else:
        enemy['boost'] += enemy['skill'] / my['skill'] * 2
        enemy['dodge'] += enemy['skill'] / my['skill']


def cal_yichang(my_content, enemy_content):
    logs = []
    du_count = content_get("du_count", my_content)
    du_shang = content_get("du_shang", enemy_content)
    if du_shang:
        du_count = int(du_count * ((100 + du_shang) / 100))
        my_content["du_count"] = du_count
    if du_count > 0:
        my_content["hp"] -= du_count
        logs.append(f"{my_content['name']}由于中毒受到了{du_count}点伤害")
    return logs

def cal_yichang_boss(my_content, enemy_content,boss):
    logs = []
    du_count = content_get("du_count", my_content)
    du_shang = content_get("du_shang", enemy_content)
    if du_shang:
        du_count = int(du_count * ((100 + du_shang) / 100))
        my_content["du_count"] = du_count
    if boss:
        du_count = int(du_count * 0.6)
    if du_count > 0:
        my_content["hp"] -= du_count
        logs.append(f"{my_content['name']}由于中毒受到了{du_count}点伤害")
    return logs

def battle(my: AllUserInfo, enemy: AllUserInfo):
    my_content = init_content(my)
    enemy_content = init_content(enemy)
    return battle_base(my_content, enemy_content)


def battle_base(my_content, enemy_content):
    logs = []
    # 处理战斗技巧
    duel_skill(my_content, enemy_content)
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
        # 计算异常伤害
        tun_log.extend(cal_yichang(my_content, enemy_content))
        # 计算异常伤害
        tun_log.extend(cal_yichang(enemy_content, my_content))

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
        if turn >= 10:
            logs.append(f'不分胜负')
            return end_battle(logs, my_content, enemy_content)


def end_battle(logs, my_content, enemy_content):
    return my_content['hp'], enemy_content['hp'], logs


def end_battle_boss(logs, my_content, enemy_content,damage):
    return my_content['hp'], enemy_content['hp'], logs,damage

def battle_boss(my: AllUserInfo,boss_name,special):
    my_content = init_content(my)
    # boss content的组装
    boss_content = init_boss_content(my_content['gid'],boss_name)
    return battle_bases(my_content, boss_content,special)


def init_shilian_content(my):
    level = my.level
    for i in LEVEL_FEATURE_MAX.keys():
        if level <= int(i):
            level = int(i)
            break
    feature_max = LEVEL_FEATURE_MAX[str(level)]
    enemy = OtherUserInfo(my)
    for i in feature_max.keys():
        if i == 'name' or i == 'wuqi':
            setattr(enemy, i, feature_max[i])
            continue
        value = getattr(my, i)
        if not value:
            continue
        if value <= feature_max[i]:
            setattr(enemy, i, feature_max[i])
        else:
            attr = (int)(value * random.randint(9, 13) / 10)
            setattr(enemy, i, attr)
    enemy.skill = (int)(my.skill * random.randint(9, 13) / 10)
    jingjie = (JingJieMap[str(level)].split(" "))[0]

    fabaos = filter_item_name(type=['法宝'], level=[jingjie])
    if fabaos:
        enemy.fabao = random.choice(fabaos)

    if jingjie == '元婴':
        jingjie = 'EX'

    gongfas = filter_item_name(type=['心法'], level=[jingjie])
    if gongfas:
        enemy.gongfa = random.choice(gongfas)
    gongfa2s = filter_item_name(type=['功法'], level=[jingjie])
    if gongfa2s:
        enemy.gongfa2 = random.choice(gongfa2s)

    gongfa3s = filter_item_name(type=['神通'], level=[jingjie])
    if gongfa3s:
        enemy.gongfa3 = random.choice(gongfa3s)

    enemy.linggen = get_LingGen()
    # 处理战斗数据
    enemy.duel_battle_info()
    # 处理其他数据
    enemy.other_info()
    return init_content(enemy)


def init_boss_content(gid,boss_name):
    name = boss_name
    boss = BOSS[name]
    name = boss["name"]
    content = {}
    # 初始化属性
    # 最大血量
    content["name"] = name
    content["max_hp"] = boss["hp"]
    content["max_mp"] = boss["mp"]

    # 当前血量
    ct = BossCounter()
    hp = ct._get_hp_by_name(gid, name)
    if not hp:
        ct._save_boss_hp_info(gid, name, boss["hp"])
        content["hp"] = boss["hp"]
    else:
        content["hp"] = hp
    content["mp"] = boss["mp"]
    # 攻击
    content["atk1"] = boss["atk1"]
    content["atk2"] = boss["atk2"]
    # 防御
    content["defen1"] = boss["defen1"]
    content["defen2"] = boss["defen2"]
    # 技巧
    content["skill"] = boss["skill"]
    # 杀人数
    content["sharen"] = boss["sharen"]
    # 境界等级
    content["level"] = boss["level"]
    # 伤害倍率
    content["dmg_rate"] = 1
    # 伤害减免
    content["reduce_rate"] = 1
    # 攻击中毒标识
    content["du_flag"] = 0
    # 中毒加深
    content["du_shang"] = 0
    # 体内毒素
    content["du_count"] = 0
    # 额外伤害
    content["ex_atk"] = 0
    # 武器伤害
    content["equip_atk"] = boss["wuqi"]
    # 灵根
    content["linggen"] = boss["linggen"]

    skill_cd = {}
    content["skills"] = skill_cd

    # 伤害类型
    content["dmg_type"] = 0
    skills = []
    # # 武器特性
    equip = get_equip_by_name(boss["linggen"])
    # # 武器
    if equip:
        if equip.get("skill"):
            skills.extend(equip.get("skill"))
    #     if equip.get("damage_type"):
    #         content["dmg_type"] = equip["damage_type"]
    #     else:
    #         content["dmg_type"] = 0

    # 功法
    gongfa = get_gongfa_by_name(boss["gongfa2"])
    if gongfa:
        if gongfa.get("skill"):
            skills.extend(gongfa.get("skill"))
    if boss['special_skills']:
        for i in boss['special_skills']:
            skills.extend(i)

    skills = list(set(skills))
    for i in skills:
        skill_cd[i] = 0

    content["boost"] = 0
    content["double"] = 0
    content["dodge"] = 0
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
    content["next_dmg_rate"] = []
    content["next_reduce_rate"] = []
    content["next_ex_atk"] = []
    # 初始化
    return content


def battle_bases(my_content, enemy_content,special):
    gid = my_content['gid']
    uid = my_content['uid']
    boss_name = enemy_content['name']
    logs = []
    # 处理战斗技巧
    duel_skill(my_content, enemy_content)
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
    ct = BossCounter()
    start_boss_hp = enemy_content["hp"]

    skills = my_content["skills"]
    if special:
        for i in my_content["skills"].keys():
            if i == "凤羽流苏":
                skills.pop("凤羽流苏")
                logs.append(f"{boss_name}发动技能封禁法宝 凤羽流苏")
                break

    while True:
        turn = turn + 1
        tun_log = [f"第{turn}回合交手"]
        hp_start = 0
        if turn == 1 and get_user_counter(gid, uid, UserModel.FEI_TAO):
            hp_start = my_content["hp"]
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
        # 敌方伤害日志
        tun_log.append(enemy_content["damage_log"])
        # 扣血动作
        my_content["hp"] -= enemy_content["total_damage"]
        # 触发技能
        tun_log.extend(skill_engine("after_damage", my_content, enemy_content, turn))
        tun_log.extend(skill_engine("after_damage", enemy_content, my_content, turn))
        tun_log.extend(skill_engine("battle_end", my_content, enemy_content, turn))
        tun_log.extend(skill_engine("battle_end", enemy_content, my_content, turn))
        # 计算异常伤害
        tun_log.extend(cal_yichang(my_content, enemy_content))
        # 计算异常伤害
        if not special:
            tun_log.extend(cal_yichang(enemy_content, my_content))
        else:
            if turn <= 8:
                tun_log.extend(cal_yichang_boss(enemy_content, my_content,1))
            else:
                tun_log.append(f"超过8回合,{enemy_content['name']}免疫毒伤害")

        tun_log.extend(skill_engine("turn_end", my_content, enemy_content, turn))
        tun_log.extend(skill_engine("turn_end", enemy_content, my_content, turn))
        if hp_start and not special:
            my_content["hp"] = hp_start
            tun_log.extend("由于使用了绯想之桃，第一回合免疫所有伤害")
        logs.append(",".join(tun_log))

        # 每回合保存一次hp
        cur_hp = enemy_content["hp"]
        if special:
            ct._save_boss_hp_info(gid, boss_name, cur_hp)

        # 重置双方造成伤害和回复
        my_content["total_damage"] = 0
        enemy_content["total_damage"] = 0

        # 随机出运势
        my_content["yunshi"] = random.randint(1, 100)
        enemy_content["yunshi"] = random.randint(1, 100)

        # 有人血量归零
        damage_all_hp = start_boss_hp - cur_hp
        if my_content["hp"] <= 0 or enemy_content["hp"] <= 0:
            if not special:
                return end_battle(logs, my_content, enemy_content)
            ud = UserDamageCounter()
            have_damage = ud._get_damage_by_name(gid, uid, boss_name)
            logs.append(f"{my_content['name']}此次共造成{damage_all_hp}点伤害")
            if not have_damage:
                have_damage = 0
            ud._save_user_damage_info(gid, uid, boss_name, damage_all_hp + have_damage)
            return end_battle_boss(logs, my_content, enemy_content,damage_all_hp)
