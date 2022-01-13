from .battle import *
from hoshino.util.utils import get_message_at, get_message_text
from .xiuxian_base import *
from .zhuansheng import his_buff


@sv.on_fullmatch(["#修仙手册", "#修仙帮助"])
async def help(bot, ev: CQEvent):
    send_msg = """
#开始修仙 名字 (注册账号)
#修炼 (依据所在地点的灵气和自身修炼速度获取经验)
#突破 (突破当前境界)
#游历 (触发随机事件，与当前所在地相关)
#对战 名字（PVP，会死人的）
#前往 地名 (切换所在地)
#锻体（增加体质，仅锻体期可用）
#练气（增加灵力，仅练气期可用）
==== 宗门指令 ====
#拜入 (在宗门地图，自己是散修的情况下 可以拜入)
#任务 (在宗门地图接受任务，一天至多完成10次）
#俸禄 (每天可以领取一次 混元门专属)
#炼丹 丹药名（百花谷专属，炼制丹药，需要灵石，有的丹药需要素材）
#锻造 武器名（百炼山庄专属 锻造武器，需要灵石和素材）
#炼宝 武器/法宝（狮府专属 炼制法宝 需要武器或法宝 和时间积累灵气 也可以#注灵 催熟）
#画符 (每天可以画一次 蜀山派专属)
#藏经阁 查看门派可以学习的功法
#学习 学习藏经阁中的功法
==== 以下操作不消耗cd ====
#查询 (查看个人状态)
#t (查看操作间隔)
#背包 (查看背包)
#道具效果 物品名 (查看持有道具的说明)
#使用 物品名(使用物品)
#丢弃 物品名(丢弃物品)
#卸下 装备或法宝
#放弃参悟
#上架 物品名 价格 （上架物品，每人最多上架一个）
#下架（下架物品）
#查价 物品名（查询该物品最低的三个价格）
#购买 物品名（购买物品，找最低价格的上架物品购买）
以上所有功能除查询外共CD，CD为10分钟，CD期间进行操作减道行1点，道行归零则心魔入体爆体而亡
死亡一小时CD
""".strip()
    await bot.finish(ev, send_msg)


def init_user(user):
    user.exp = 0
    user.level = 1
    user.belong = "散修"
    user.map = "新手村"
    user.gongfa = "无"
    user.fabao = "无"
    user.wuqi = "赤手空拳"
    user.wuxing = random.randint(10, 70)
    user.lingli = 0
    user.daohang = random.randint(10, 20)
    user.act = 10
    user.defen = 10
    user.defen2 = 10
    user.hp = random.randint(60, 100)
    user.mp = random.randint(60, 100)
    user.skill = random.randint(5, 20)
    user.tizhi = random.randint(10, 20)
    user.act2 = 0
    user.gongfa2 = '无'
    user.gongfa3 = '无'


@sv.on_prefix(["#开始修仙", "#注册账号"])
async def start(bot, ev: CQEvent):
    name = str(ev.message).strip()
    gid = ev.group_id
    uid = ev.user_id
    if not name:
        await bot.finish(ev, "账号名至少为一个字！")
    if len(name) > 5:
        await bot.finish(ev, "账号名不要超过5个字！")
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if user:
        await bot.finish(ev, f"你已经有账号了，账号名为{user.name}")
    user = ct._get_user_by_name(gid, name)
    if user:
        await bot.finish(ev, "用户名已存在，注册失败，请稍后重试！")
    if not die_flmt.check(uid):
        await bot.finish(ev, f"死亡cd中，还剩{round(int(die_flmt.left_time(uid)))}秒")
    my_linggen = get_LingGen()
    user = UserInfo()
    user.gid = gid
    user.uid = uid
    user.name = name
    user.linggen = my_linggen
    init_user(user)
    spec = his_buff(user)
    ex_msg = ""
    if spec:
        ex_msg = "\n" + "\n".join(spec)
    ct._save_user_info(user)
    await bot.finish(ev, f'拥有{my_linggen}灵根的{name}已正式进入修仙界{ex_msg}')


@sv.on_fullmatch(["#time", "#TIME", "#T", "#t"])
async def query(bot, ev: CQEvent):
    uid = ev.user_id
    time = int(flmt.left_time(uid))
    if time < 0:
        time = 0
    await bot.finish(ev, f"下次操作时间:{time}秒后", at_sender=True)


@sv.on_fullmatch(["#查询"])
async def query(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    sendmsg = f"""
道号:{user.name} 灵根:{user.linggen} 伤势:{user.shangshi_desc} 
境界:{JingJieMap[str(user.level)]}  EXP:{user.exp}
武器:{user.wuqi}  法宝:{user.fabao}
心法:{user.gongfa} 功法:{user.gongfa2} 神通:{user.gongfa3}
门派:{user.belong}  所在地:{user.map}
体质:{user.tizhi} 悟性:{user.wuxing} 灵力:{user.lingli} 道行:{user.daohang}
攻击:{user.battle_atk1} 术法:{user.battle_atk2} 物防:{user.battle_defen1} 魔抗:{user.battle_defen2}
HP:{user.battle_hp} MP:{user.battle_mp} 战斗技巧:{user.skill}
""".strip()
    await bot.finish(ev, sendmsg)


def cal_is_die(my):
    if my.gongfa3 == "脱峰式":
        rd = random.randint(1, 2)
        if rd == 1:
            return False, f"{my.name}在被即将击杀之际使用了[脱峰式]成功逃脱"
    wanli = get_item_by_name("瞬息万里符")
    if check_have_item(my.gid, my.uid, wanli):
        use_item(my.gid, my.uid, wanli)
        return False, f"{my.name}在被即将击杀之际使用了[瞬息万里符]成功逃脱"
    else:
        return True, f"{my.name}被击杀"


# 舔包结算
def tianbao(my, enemy):
    log = ""
    # 基础概率
    need_base = 50
    # 杀人数
    eme_kill = get_user_counter(enemy.gid, enemy.uid, UserModel.KILL)
    if eme_kill < 0:
        eme_kill = 0
    # 杀人每多一个就多20%概率
    need = need_base + eme_kill * 20
    # 获得道具的个数
    num = 0
    if need >= 100:
        num += int(need / 100)
        need = need % 100
    rd = random.randint(1, 100)
    if rd < need:
        num += 1
    counter = ItemCounter()
    items = counter._get_item(enemy.gid, enemy.uid)
    total_count = 0
    item_li = []
    for i in items:
        item_li += [i[0]] * i[1]
        total_count += i[1]
    # 加入身上的装备道具
    if enemy.wuqi != "赤手空拳":
        item = get_item_by_name(enemy.wuqi)
        item_li.append(int(item['id']))
        total_count += 1
    if enemy.fabao != "无":
        item = get_item_by_name(enemy.fabao)
        item_li.append(int(item['id']))
        total_count += 1
    if total_count < num:
        num = total_count
    get_li = random.sample(item_li, num)
    if get_li:
        log += "抢夺了对方的"
    for i in get_li:
        item = ITEM_INFO[str(i)]
        log += f"[{item['name']}]"
        if not add_item(my.gid, my.uid, item):
            log += "(背包已满 已丢弃)"
    lingshi = get_user_counter(enemy.gid, enemy.uid, UserModel.LINGSHI)
    get_lingshi = int(lingshi / 2)
    add_user_counter(my.gid, my.uid, UserModel.LINGSHI, get_lingshi)
    log += f"抢夺了{enemy.name}{get_lingshi}灵石"
    return log


# 杀人结算
def kill_user_cal(my, enemy):
    log = ""
    # 增加杀人计数器
    add_user_counter(my.gid, my.uid, UserModel.KILL)
    if my.level == 18 and enemy.level >= 18:
        add_user_counter(my.gid, my.uid, UserModel.JINDANSHA)
        log += f"{my.name}释放了心中的心魔，感觉体内的金丹有所松动"
    if my.gongfa3 == "化功大法":
        my.exp += enemy.exp
        log += f",{my.name}使用[化功大法]获取了{enemy.exp}点经验"
    if my.gongfa3 == "吸星大法" and my.level <= enemy.level:
        my.act += 1
        my.act2 += 1
        get_hp = random.randint(10, 20)
        my.hp += get_hp
        log += f"{my.name}使用了吸星大法，获取了{get_hp}点HP和1点物理术法攻击力"
    if enemy.gongfa3 == "天轮毒诀":
        log += f"{my.name}中了天轮毒，永久降低10%的生命上限！"
        my.hp = int(0.9 * my.hp)
    ct = XiuxianCounter()
    ct._save_user_info(my)
    # 舔包
    log += tianbao(my, enemy)
    # 敌人死亡
    delete_user(enemy)
    return log


def cal_shangshi(my_rate, my):
    log = ""
    if my_rate <= 0:
        save_user_counter(my.gid, my.uid, UserModel.SHANGSHI, 3)
        log += f"{my.name}陷入濒死 "
    elif my_rate < 0.1:
        save_user_counter(my.gid, my.uid, UserModel.SHANGSHI, 2)
        log += f"{my.name}受了重伤 "
    elif my_rate < 0.3:
        save_user_counter(my.gid, my.uid, UserModel.SHANGSHI, 1)
        log += f"{my.name}受了轻伤 "
    return log


@sv.on_prefix(["#对战"])
async def duanti(bot, ev: CQEvent):
    gid = ev.group_id
    my = await get_ev_user(bot, ev)
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
        await bot.finish(ev, f"不能自己打自己（恼）")

    # 判断境界
    min = 1
    for i in PINGJING:
        if my.level > i:
            min = i
        else:
            break
    if enemy.level <= min:
        if not check_have_item(my.gid, my.uid, get_item_by_name("下界符")):
            await bot.finish(ev, f"没有[下界符]不能对战境界低于自己的人")
    if enemy.gongfa3 == "缩地成寸":
        if get_user_counter(enemy.gid, enemy.uid, UserModel.SUODI) > 0:
            await bot.finish(ev, f"你知道对方在这，但对方使用缩地成寸躲了起来,无法对战")
    await my.check_and_start_cd(bot, ev)
    if my.map != enemy.map:
        await bot.finish(ev, f"你找遍了四周也没有发现{enemy.name}的身影，或许他根本不在这里？")
    if enemy.gongfa3 == '狡兔三窟':
        if random.randint(1, 5) == 1:
            await bot.finish(ev, f"你找遍了四周也没有发现{enemy.name}的身影，或许他根本不在这里？")
    if enemy.level <= min:
        use_item(my.gid, my.uid, get_item_by_name("下界符"))
    if enemy.gongfa3 == "缩地成寸":
        add_user_counter(enemy.gid, enemy.uid, UserModel.SUODI, num=5)
    enemy = AllUserInfo(enemy)
    # check使用燃魂丹标识
    flag = get_user_counter(my.gid, my.uid, UserModel.RANHUN)
    if flag:
        my.battle_hp = my.battle_hp * 2
        my.battle_mp = my.battle_mp * 2
        my.battle_atk1 = my.battle_atk1 * 2
        my.battle_atk2 = my.battle_atk1 * 2
        my.battle_defen1 = my.battle_defen1 * 2
        my.battle_defen2 = my.battle_defen2 * 2
    # 战斗
    my_hp, he_hp, send_msg_li = battle(my, enemy)
    skill_max = my.skill if my.skill > enemy.skill else enemy.skill
    skill_min = my.skill if my.skill < enemy.skill else enemy.skill
    skill_rate = skill_max / skill_min if skill_max / skill_min < 5 else 5
    log = ""
    my_die_flag = False
    if my_hp <= 0:
        my_die_flag, log_my = cal_is_die(my)
        log += log_my
    he_die_flag = False
    if he_hp <= 0:
        he_die_flag, log_he = cal_is_die(enemy)
        log += log_he
        log += f"[CQ:at,qq={enemy.uid}]"
    if my_hp > 0 and he_hp > 0:
        log += "二人战斗难舍难分，不分胜负就此罢了。"
    if not my_die_flag and flag:
        my_die_flag = True
        log += f"{my.name}由于服用了燃魂丹，魂力耗尽而亡。。"
    get_skill = random.randint(1, 3)
    # 相差50%战斗技巧无法获得技巧值
    if skill_rate >= 1.5:
        get_skill = 0
    my.skill += get_skill
    enemy.skill += get_skill
    ct._save_user_info(my)
    ct._save_user_info(enemy)
    # 伤势判断
    my_rate = my_hp / my.hp
    if enemy.gongfa3 == '啼血神殇' and my_rate > 0.3:
        my_rate = 0.25
    he_rate = he_hp / enemy.hp
    if my.gongfa3 == '啼血神殇' and he_rate > 0.3:
        he_rate = 0.25
    if my_die_flag and he_die_flag:
        delete_user(enemy)
        delete_user(my)
    elif he_die_flag and not my_die_flag:
        log += kill_user_cal(my, enemy)
        log += cal_shangshi(my_rate, my)
    elif not he_die_flag and my_die_flag:
        log += kill_user_cal(enemy, my)
        log += cal_shangshi(he_rate, enemy)
    else:
        log += cal_shangshi(my_rate, my)
        log += cal_shangshi(he_rate, enemy)
    send_msg_li.append(log)
    await bot.finish(ev, '\n'.join(send_msg_li))


@sv.on_prefix(["#前往"])
async def go(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    destination = str(ev.message).strip()
    address = MAP.get(destination)
    if not address:
        await bot.finish(ev, f"未找到名为「{destination}」的地点")
    user_adress = MAP.get(user.map)
    if destination not in user_adress['able']:
        await bot.finish(ev, f"你当前所在的[{user.map}]只能前往 {'｜'.join(user_adress['able'])}")
    need_level = address["in_level"]
    if user.level < need_level:
        await bot.finish(ev, f"你的还不足以应对接下来的挑战，请先提升自己的实力吧（{destination}需要{JingJieMap[str(need_level)]}才能前往）")
    # 进宗门（从宗门所在大地图去宗门）
    if destination == user.belong and user.map == ZONGMEN.get(user.belong)["map"] :
        gotoDestination( user, destination)
        await bot.finish(ev, f"这里的事情已经办完了，动身前往{destination}")
    # 出宗门
    if user.map == user.belong and destination == ZONGMEN.get(user.belong)["map"] :
        gotoDestination( user, destination)
        await bot.finish(ev, f"这里的事情已经办完了，动身前往{destination}")
    await user.check_cd(bot, ev)
    if user.gongfa3 != "千里神行":
        user.start_cd()
    gotoDestination(user, destination)
    await bot.finish(ev, f"这里的事情已经办完了，动身前往{destination}")

def gotoDestination(user:AllUserInfo, destination:str):
    user.map = destination
    ct = XiuxianCounter()
    ct._save_user_info(user)


@sv.on_fullmatch(["#元旦限定Boss"])
async def specialNewYear(bot, ev: CQEvent):
    gid = ev.group_id
    my = await get_ev_user(bot, ev)
    await my.check_and_start_cd(bot, ev)
    if get_group_counter(gid, GroupModel.YUANDAN_BOSS) > 0 :
        await bot.finish(ev, f"Boss已被击败，活动结束")
    # check使用燃魂丹标识
    # flag = get_user_counter(my.gid, my.uid, UserModel.RANHUN)
    # if flag:
    #     my.battle_hp = my.battle_hp * 2
    #     my.battle_mp = my.battle_mp * 2
    #     my.battle_atk1 = my.battle_atk1 * 2
    #     my.battle_atk2 = my.battle_atk1 * 2
    #     my.battle_defen1 = my.battle_defen1 * 2
    #     my.battle_defen2 = my.battle_defen2 * 2

    # 战斗
    my_hp, he_hp, send_msg_li = battle_boss(my)
    log=""
    if my_hp <= 0:
        log += f"{my.name}受到伤害，HP减为0，弱小的你还需要继续修炼，等待你的下次挑战"

    if he_hp <= 0:
        save_group_counter(gid, GroupModel.YUANDAN_BOSS, 1)
        log += f"{my.name}击败了Boss，你的声名将响彻修仙界"

    send_msg_li.append(log)
    user = await get_ev_user(bot, ev)
    luck = random.randint(1,10)
    # 80%概率拿灵石
    if luck > 2:
        lingshi = random.randint(10,50)
        user.lingshi += lingshi
        add_user_counter(user.gid, user.uid, UserModel.LINGSHI, lingshi)
        send_msg_li.append(f"天道见你勇气可嘉，给予{lingshi}块灵石以示鼓励")
    else:
        luck = random.randint(1, 8)
        if luck > 5 :
            if user.skill < 80 :
                user.skill += 1
                send_msg_li.append("天道见你勇气可嘉，奖励1点战斗技巧以示鼓励")
        elif luck == 3 :
            list = ['木枯藤','赭黄精','朱果','琅琊果','玄牝珠']
            item = random.choice(list)
            if add_item(user.gid, user.uid, get_item_by_name(item)):
                send_msg_li.append(f"天道见你勇气可嘉，给予{item}以示鼓励")
        elif luck == 2 :
            if user.daohang < 100 :
                user.daohang += 1
                send_msg_li.append("天道见你勇气可嘉，奖励1点道行以示鼓励")
        elif luck == 1 :
            user.hp += 2
            send_msg_li.append("天道见你勇气可嘉，奖励2点HP 以示鼓励")
        elif luck == 4:
            user.mp += 1
            send_msg_li.append("天道见你勇气可嘉，奖励1点MP 以示鼓励")
    ct = XiuxianCounter()
    ct._save_user_info(user)

    await bot.finish(ev, '\n'.join(send_msg_li))


@sv.on_fullmatch(["#天榜"])
async def specialNewYear(bot, ev: CQEvent):
    gid = ev.group_id
    ct = UserDamageCounter()
    name = "元旦限定"
    boss = BOSS[name]
    map = ct._get_damage_by_boss(gid , boss['name'])
    logs = []
    logs.append("#天榜")
    us = XiuxianCounter()
    count = 0
    cur_user = await get_ev_user(bot, ev)
    haveme = 0
    for i in map:
        user = us._get_user(gid,i[0])
        if cur_user.uid == i[0] :
            logs.append(f"{user.name} 共计造成{i[1]}点伤害 **")
            haveme = 1
        else:
            logs.append(f"{user.name} 共计造成{i[1]}点伤害")
        count+=1
        if count == 10 :
            break
    if not haveme:
        damage = ct._get_damage_by_name(gid, cur_user.uid, boss['name'])
        logs.append(f"{cur_user.name} 共计造成{damage}点伤害 **")
    await bot.finish(ev, '\n'.join(logs))

@sv.on_prefix(["#领取奖励"])
async def specialNewYear(bot, ev: CQEvent):
    gid = ev.group_id
    name = str(ev.message).strip()
    boss_bonus = BOSS_BONUS[name]
    bonus = boss_bonus['bonus']
    logs = []
    cur_user = await get_ev_user(bot, ev)
    if get_user_counter(gid,cur_user.uid, UserModel.YUANDAN_LIHE) > 0 :
        await bot.finish(ev, "你已领取过奖励")
    count = 0
    have_me = 0
    ct = UserDamageCounter()
    map = ct._get_damage_by_boss(gid, boss_bonus['name'])
    logs.append("#天榜奖励")
    for i in map:
        count += 1
        if cur_user.uid == i[0] :
            have_me = 1
            ## 标记领取过了
            add_user_counter(gid,cur_user.uid,UserModel.YUANDAN_LIHE,1)
            break
        if count == 10 :
            break
    if not have_me:
        await bot.finish(ev, "你未进入天榜，请继续修炼加油")
    if count == 1 or count == 2 or count == 3 :
        for i in bonus:
            if count > 3:
                break
            add_item_ignore_limit(gid,cur_user.uid, ITEM_NAME_MAP.get(i))
            logs.append(f"你获得了奖励道具 {i}")
            count += 1
    else:
        add_item_ignore_limit(gid, cur_user.uid, ITEM_NAME_MAP.get(bonus[count - 2]))
        logs.append(f"你获得了奖励道具 {bonus[count - 2]}")
    await bot.finish(ev, '\n'.join(logs))

@sv.on_prefix(["#经验兑换"])
async def exp_change_feature(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    feature_name = str(ev.message).strip().split()
    level_true = 0
    for key in EXP_FEATURE.keys():
        if key == str(user.level) :
            exp_feature = EXP_FEATURE[str(user.level)]
            level_true = 1
    # 境界不足
    if not level_true:
        await bot.finish(ev, f"你的境界未达标，不能使用经验兑换属性")
    # 经验不足
    if user.exp < exp_feature['cost']:
        await bot.finish(ev, f"你的经验不足{exp_feature['cost']}点，无法兑换属性")

    feature = exp_feature[feature_name[0]]
    name = feature['feature']
    ct = XiuxianCounter()
    for i in dir(user):
        if i == name:
            value = getattr(user,i)
            if value >= feature['max']:
                await bot.finish(ev, f"{user.name}的{feature_name[0]}属性已至上限，不予兑换提升")
            value += feature['upgrade']
            is_max = 0
            if value >= feature['max']:
                is_max = 1
            setattr(user, name, value)
            user.exp -= exp_feature['cost']
            ct._save_user_info(user)
            if is_max :
                await bot.finish(ev, f"{user.name}使用了{exp_feature['cost']}点经验，使{feature_name[0]}属性提至上限")
            await bot.finish(ev, f"{user.name}使用了{exp_feature['cost']}点经验，使{feature_name[0]}属性提升了{feature['upgrade']}点")
    await bot.finish(ev, f"此属性不在经验兑换内，请另外选择属性")