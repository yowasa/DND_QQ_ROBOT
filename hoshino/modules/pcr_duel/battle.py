from hoshino.modules.pcr_duel.duelconfig import *
import random


# 数值随机波动10%
def deviation(dmg):
    rd = random.randint(0, 20)
    dev = 1 + (rd - 10) / 100
    return int(dmg * dev)


# 初始化buff
def init_content(my: Attr):
    content = {}

    # 初始化属性
    content["max_hp"] = my.maxhp
    content["hp"] = my.hp
    content["sp"] = my.sp
    content["max_sp"] = my.max_sp
    content["atk"] = my.atk
    content["preempt"] = my.preempt
    content["boost"] = my.boost
    content["crit"] = my.crit
    content["double"] = my.double
    content["recover"] = my.recover
    content["dodge"] = my.dodge
    # 伤害倍率
    content["atk_rate"] = 1
    # 减伤效果
    content["reduce_rate"] = 1
    # 额外伤害
    content["ex_atk"] = 0
    # 额外伤害倍率
    content["ex_atk_rate"] = 1
    # 血量流失
    content["liushi_hp"] = 0
    # 回复倍率
    content["recover_rate"] = 1
    # 暴击倍率
    content["crit_rate"] = 2
    # 跳过战斗阶段标识
    content["ts"] = False
    content["chuanjia"] = False
    content["next_chuanjia"] = []
    content["next_ts"] = []
    content["next_crit_rate"] = []
    content["next_recover_rate"] = []
    content["next_liushi_hp"] = []
    content["next_ex_atk"] = []
    content["next_reduce_rate"] = []
    content["next_atk_rate"] = []
    content["next_preempt"] = []
    content["next_boost"] = []
    content["next_crit"] = []
    content["next_double"] = []
    content["next_recover"] = []
    content["next_dodge"] = []

    content["is_boost"] = False
    content["is_crit"] = False
    content["is_double"] = False
    content["is_recover"] = False
    content["is_dodge"] = False

    content["next_is_boost"] = []
    content["next_is_crit"] = []
    content["next_is_double"] = []
    content["next_is_recover"] = []
    content["next_is_dodge"] = []
    skill_cd = {}
    for i in my.skill:
        skill_cd[i] = 0
    content["skills"] = skill_cd
    all_skill_cd = {}
    for i in my.all_skill:
        all_skill_cd[i] = 0
    content["all_skill"] = all_skill_cd
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
    return eval(skill_def_json[skill]["condition"], content)


# 技能影响
def effect(skill, my_content, enemy_content, turn, prefix, logs):
    effect = skill_def_json[skill]["effect"]
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
    skill_log = skill_def_json[skill]['log']
    skill_log = skill_log.format(**content)
    logs.append(f"{prefix}触发了技能【{skill}】,{skill_log}")
    if skill_def_json[skill].get("cd"):
        my_content["skills"][skill] = skill_def_json[skill]["cd"]


# 技能执行引擎
def skill_engine(time: str, my_content, enemy_content, turn: int, prefix=""):
    logs = []
    skill = []
    for i in my_content["skills"].keys():
        if my_content["skills"][i] == 0:
            if skill_def_json[i]["time"] == time:
                skill.append(i)
    for i in skill:
        if check_condition(i, my_content, enemy_content, turn):
            cost = skill_def_json[i].get("cost") if skill_def_json[i].get("cost") else 0
            if cost > my_content['sp']:
                continue
            else:
                my_content['sp'] -= cost
                effect(i, my_content, enemy_content, turn, prefix, logs)
    return logs


# 决斗引擎
def content_get(param, my_content):
    if my_content.get("next_" + param):
        return my_content.get("next_" + param).pop()
    else:
        return my_content.get(param)


# 模拟计算应该造成多少伤害
def duel_buff(my_content, enemy_content, prefix):
    # 初始化dmg_log
    my_content["damage_log"] = []
    # 基础atk
    dmg = 0
    atk = content_get("atk", my_content)
    atk_rate = content_get("atk_rate", my_content)
    reduce_rate = content_get("reduce_rate", enemy_content)
    is_boost = content_get("is_boost", my_content)
    is_dodge = content_get("is_dodge", enemy_content)
    is_crit = content_get("is_crit", my_content)
    crit_rate = content_get("crit_rate", my_content)
    is_double = content_get("is_double", my_content)
    ex_atk = content_get('ex_atk', my_content)
    ex_atk_rate = content_get('ex_atk_rate', my_content)
    ts = content_get('ts', my_content)
    chuanjia = content_get('chuanjia', my_content)
    if chuanjia:
        reduce_rate = 1
    if ts:
        my_content["damage_log"].append(f"{prefix}战斗阶段跳过")
        my_content["total_damage"] = dmg
        return
        # 倍率加成
    atk = int(atk * atk_rate)
    if is_boost:
        atk = int(1.5 * atk)
        my_content["damage_log"].append(prefix + "触发了boost强化，本轮基础atk增加50%")
    if is_dodge:
        my_content["damage_log"].append(f"{prefix}攻击被闪避！")
    else:
        if is_crit:
            rd_dmg = deviation(crit_rate * atk * reduce_rate)
            dmg += rd_dmg
            my_content["damage_log"].append(f"{prefix}造成了暴击，造成了{rd_dmg}点伤害!")
        else:
            rd_dmg = deviation(atk * reduce_rate)
            dmg += rd_dmg
            my_content["damage_log"].append(f"{prefix}造成了{rd_dmg}点伤害")
        if is_double:
            my_content["damage_log"].append(f"{prefix}触发了连击!")
            if content_get("is_crit", my_content):
                rd_dmg = deviation(2 * atk * reduce_rate)
                dmg += rd_dmg
                my_content["damage_log"].append(f"{prefix}造成了暴击，造成了{rd_dmg}点伤害!")
            else:
                rd_dmg = deviation(atk * reduce_rate)
                dmg += rd_dmg
                my_content["damage_log"].append(f"{prefix}造成了{rd_dmg}点伤害")
        if ex_atk:
            ex_dmg=ex_atk*ex_atk_rate
            dmg += ex_dmg
            my_content["damage_log"].append(f"{prefix}造成额外{ex_dmg}附加伤害!")
    my_content["total_damage"] = dmg


def judge_damage(my_content, enemy_content):
    # 判断我方 boost 连击 暴击 闪避 恢复
    judge_rate(my_content)
    # 判断地方 boost 连击 暴击 闪避 恢复
    judge_rate(enemy_content)
    # 计算伤害
    duel_buff(my_content, enemy_content, "我方")
    duel_buff(enemy_content, my_content, "敌方")


# 判断是否触发战斗特征
def judge_rate(content):
    judge_li = ["boost", "crit", "double", "dodge", "recover"]
    for i in judge_li:
        value = content_get(i, content)
        rd = random.randint(1, 100)
        content["is_" + i] = (rd <= value)


# 处理回合结束时的debuff
def duel_debuff(prefix, my_content, enemy_content):
    log = []
    liushi_hp = content_get("liushi_hp", my_content)
    my_content['hp'] -= liushi_hp
    if liushi_hp:
        log.append(f"{prefix}生命值流失{liushi_hp}点")
    return log


def battle(my: Attr, enemy: Attr):
    logs = []
    my_content = init_content(my)
    enemy_content = init_content(enemy)
    # 战斗开始
    logs.append(f"战斗开始")
    logs.append(f"我方hp:{my.hp}\t 敌方hp:{enemy.hp}")
    # 触发技能
    turn = 0
    first=random.randint(0,1)
    if first:
        logs.extend(skill_engine("init", my_content, enemy_content, turn, prefix="我方"))
        logs.extend(skill_engine("init", enemy_content, my_content, turn, prefix="敌方"))
        logs.extend(skill_engine("prepare", my_content, enemy_content, turn, prefix="我方"))
        logs.extend(skill_engine("prepare", enemy_content, my_content, turn, prefix="敌方"))
        logs.extend(skill_engine("begin", my_content, enemy_content, turn, prefix="我方"))
        logs.extend(skill_engine("begin", enemy_content, my_content, turn, prefix="敌方"))
    else:
        logs.extend(skill_engine("init", enemy_content, my_content, turn, prefix="敌方"))
        logs.extend(skill_engine("init", my_content, enemy_content, turn, prefix="我方"))
        logs.extend(skill_engine("prepare", enemy_content, my_content, turn, prefix="敌方"))
        logs.extend(skill_engine("prepare", my_content, enemy_content, turn, prefix="我方"))
        logs.extend(skill_engine("begin", enemy_content, my_content, turn, prefix="敌方"))
        logs.extend(skill_engine("begin", my_content, enemy_content, turn, prefix="我方"))

    # 先攻鉴定
    rd = random.randint(1, my_content["preempt"] + enemy_content["preempt"])
    flag = rd <= my_content["preempt"]
    logs.append("先攻检定位" + ("我方" if flag else "敌方") + "先攻!")
    while True:
        turn = turn + 1
        logs.append(f"【第{turn}回合】")
        # 技能cd-1
        for i in my_content["skills"].keys():
            if my_content["skills"][i] > 0:
                my_content["skills"][i] -= 1
        for i in enemy_content["skills"].keys():
            if enemy_content["skills"][i] > 0:
                enemy_content["skills"][i] -= 1

        # 伤害计算前触发技能
        if flag:
            logs.extend(skill_engine("before_damage", my_content, enemy_content, turn, prefix="我方"))
            logs.extend(skill_engine("before_damage", enemy_content, my_content, turn, prefix="敌方"))
        else:
            logs.extend(skill_engine("before_damage", enemy_content, my_content, turn, prefix="敌方"))
            logs.extend(skill_engine("before_damage", my_content, enemy_content, turn, prefix="我方"))

        # 判定伤害触发
        judge_damage(my_content, enemy_content)

        # 伤害计算时
        if flag:
            logs.extend(skill_engine("damage", my_content, enemy_content, turn, prefix="我方"))
            logs.extend(skill_engine("damage", enemy_content, my_content, turn, prefix="敌方"))
        else:
            logs.extend(skill_engine("damage", enemy_content, my_content, turn, prefix="敌方"))
            logs.extend(skill_engine("damage", my_content, enemy_content, turn, prefix="我方"))

        # 伤害判定后
        if flag:
            # 伤害日志
            logs.extend(my_content["damage_log"])
            # 同步血量
            my.hp = my_content["hp"]
            my.sp = my_content["sp"]
            # 扣血动作
            enemy_content["hp"] -= my_content["total_damage"]
            # 触发技能
            logs.extend(skill_engine("after_damage", my_content, enemy_content, turn, prefix="我方"))
            # 判定死亡
            if enemy_content["hp"] <= 0:
                logs.append("敌方血量归0，战斗胜利！")
                return end_battle(True, logs, turn, my, enemy, my_content, enemy_content)

            # 伤害日志
            logs.extend(enemy_content["damage_log"])
            # 扣血动作
            my_content["hp"] -= enemy_content["total_damage"]
            # 同步血量
            my.hp = my_content["hp"]
            my.sp = my_content["sp"]
            logs.extend(skill_engine("after_damage", enemy_content, my_content, turn, prefix="敌方"))
            if my_content["hp"] <= 0:
                logs.append("我方血量归0，战斗失败...")
                return end_battle(False, logs, turn, my, enemy, my_content, enemy_content)
        else:
            # 伤害日志
            logs.extend(enemy_content["damage_log"])
            # 扣血动作
            my_content["hp"] -= enemy_content["total_damage"]
            # 同步血量
            my.hp = my_content["hp"]
            my.sp = my_content["sp"]
            logs.extend(skill_engine("after_damage", enemy_content, my_content, turn, prefix="敌方"))
            if my_content["hp"] <= 0:
                logs.append("我方血量归0，战斗失败...")
                return end_battle(False, logs, turn, my, enemy, my_content, enemy_content)

            # 伤害日志
            logs.extend(my_content["damage_log"])
            # 同步血量
            my.hp = my_content["hp"]
            my.sp = my_content["sp"]
            # 扣血动作
            enemy_content["hp"] -= my_content["total_damage"]
            # 触发技能
            logs.extend(skill_engine("after_damage", my_content, enemy_content, turn, prefix="我方"))
            if enemy_content["hp"] <= 0:
                logs.append("敌方血量归0，战斗胜利！")
                return end_battle(True, logs, turn, my, enemy, my_content, enemy_content)
        # 开始判定回复
        if flag:
            logs.extend(skill_engine("before_recover", my_content, enemy_content, turn, prefix="我方"))
            if content_get("is_recover", my_content):
                atk = content_get("atk", my_content)
                hp_add = deviation(atk) * content_get("recover_rate", my_content)
                my_content["hp"] += hp_add
                my.hp = my_content["hp"]
                logs.append(f"我方触发了恢复，hp增加了{hp_add}")
            logs.extend(skill_engine("after_recover", my_content, enemy_content, turn, prefix="我方"))
            logs.extend(skill_engine("before_recover", enemy_content, my_content, turn, prefix="敌方"))
            if content_get("is_recover", enemy_content):
                atk = content_get("atk", enemy_content)
                hp_add = deviation(atk) * content_get("recover_rate", enemy_content)
                enemy_content["hp"] += hp_add
                logs.append(f"敌方触发了恢复，hp增加了{hp_add}")
            logs.extend(skill_engine("after_recover", enemy_content, my_content, turn, prefix="敌方"))
        else:
            logs.extend(skill_engine("before_recover", enemy_content, my_content, turn, prefix="敌方"))
            if content_get("is_recover", enemy_content):
                atk = content_get("atk", enemy_content)
                hp_add = deviation(atk) * content_get("recover_rate", enemy_content)
                enemy_content["hp"] += hp_add
                logs.append(f"敌方触发了恢复，hp增加了{hp_add}")
            logs.extend(skill_engine("after_recover", enemy_content, my_content, turn, prefix="敌方"))
            logs.extend(skill_engine("before_recover", my_content, enemy_content, turn, prefix="我方"))
            if content_get("is_recover", my_content):
                atk = content_get("atk", my_content)
                hp_add = deviation(atk) * content_get("recover_rate", my_content)
                my_content["hp"] += hp_add
                my.hp = my_content["hp"]
                logs.append(f"我方触发了恢复，hp增加了{hp_add}")
            logs.extend(skill_engine("after_recover", my_content, enemy_content, turn, prefix="我方"))
        # 回合结束
        if flag:
            logs.extend(skill_engine("turn_end", my_content, enemy_content, turn, prefix="我方"))
            logs.extend(duel_debuff('敌方', enemy_content, my_content))
            if enemy_content["hp"] <= 0:
                logs.append("敌方血量归0，战斗胜利！")
                return end_battle(True, logs, turn, my, enemy, my_content, enemy_content)
            logs.extend(skill_engine("turn_end", enemy_content, my_content, turn, prefix="敌方"))
            logs.extend(duel_debuff('我方', my_content, enemy_content))
            if my_content["hp"] <= 0:
                logs.append("我方血量归0，战斗失败！")
                return end_battle(False, logs, turn, my, enemy, my_content, enemy_content)
        else:
            logs.extend(skill_engine("turn_end", enemy_content, my_content, turn, prefix="敌方"))
            logs.extend(duel_debuff('我方', my_content, enemy_content))
            if my_content["hp"] <= 0:
                logs.append("我方血量归0，战斗失败！")
                return end_battle(False, logs, turn, my, enemy, my_content, enemy_content)
            logs.extend(skill_engine("turn_end", my_content, enemy_content, turn, prefix="我方"))
            logs.extend(duel_debuff('敌方', enemy_content, my_content))
            if enemy_content["hp"] <= 0:
                logs.append("敌方血量归0，战斗胜利！")
                return end_battle(True, logs, turn, my, enemy, my_content, enemy_content)
        my_content["hp"] = int(my_content["hp"])
        enemy_content["hp"] = int(enemy_content["hp"])
        logs.append(f'第{turn}回合结束===\n我方剩余hp:{my_content["hp"]}，sp:{my_content["sp"]} \n敌方剩余hp:{enemy_content["hp"]}，sp:{enemy_content["sp"]}')
        if turn >= 30:
            logs.append(f'回合数超过30 自动判负。。。。')
            return end_battle(False, logs, turn, my, enemy, my_content, enemy_content)


def end_battle(success, logs, turn, my, enemy, my_content, enemy_content):
    if success:
        logs.extend(skill_engine("end", my_content, enemy_content, turn, prefix="我方"))
    else:
        logs.extend(skill_engine("end", enemy_content, my_content, turn, prefix="敌方"))
    my.hp = my_content["hp"]
    my.sp = my_content["sp"]
    enemy.hp = enemy_content["hp"]
    enemy.sp = enemy_content["sp"]
    return success, logs

# my = Attr(1000, 1000, 100, 5)
# my.skill = ["月计时"]
#
# enemy = Attr(1000, 1000, 100, 5)
#
# result, log = battle(my, enemy)
#
# print("\n".join(log))
