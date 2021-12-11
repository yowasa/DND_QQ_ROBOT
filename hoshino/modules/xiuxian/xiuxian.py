from .battle import *
from hoshino.util.utils import get_message_at, get_message_text


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
==== 以下操作不消耗cd ====
#查询 (查看个人状态)
#time (查看操作间隔)
#背包 (查看背包)
#道具效果 物品名 (查看持有道具的说明)
#使用 物品名(使用物品)
#丢弃 物品名(丢弃物品)
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
    ct._save_user_info(user)
    await bot.finish(ev, f'拥有{my_linggen}灵根的{name}已正式进入修仙界')


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
    if my.gongfa3 == "吸星大法":
        my.act += 1
        my.act2 += 1
        get_hp = random.randint(1, 20)
        my.hp += get_hp
        log += f"{my.name}使用了吸星大法，获取了{get_hp}点HP和1点物理术法攻击力"
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
    await my.check_and_start_cd(bot, ev)
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
    if my.map != enemy.map:
        await bot.finish(ev, f"你找遍了四周也没有发现{enemy.name}的身影，或许他根本不在这里？")
    if enemy.gongfa3 == '狡兔三窟':
        if random.randint(1, 5) == 1:
            await bot.finish(ev, f"你找遍了四周也没有发现{enemy.name}的身影，或许他根本不在这里？")
    if enemy.level <= min:
        use_item(my.gid, my.uid, get_item_by_name("下界符"))
    enemy = AllUserInfo(enemy)
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
    name = str(ev.message).strip()
    adress = MAP.get(name)
    if not adress:
        await bot.finish(ev, f"未找到名为「{name}」的地点")
    user_adress = MAP.get(user.map)
    if name not in user_adress['able']:
        await bot.finish(ev, f"你当前所在的[{user.map}]只能前往 {'｜'.join(user_adress['able'])}")
    need_level = adress["in_level"]
    if user.level < need_level:
        await bot.finish(ev, f"你的还不足以应对接下来的挑战，请先提升自己的实力吧（{name}需要{JingJieMap[str(need_level)]}才能前往）")
    await user.check_cd(bot, ev)
    if user.gongfa3 != "千里神行":
        user.start_cd()
    user.map = name
    ct = XiuxianCounter()
    ct._save_user_info(user)
    await bot.finish(ev, f"这里的事情已经办完了，动身前往{name}")
