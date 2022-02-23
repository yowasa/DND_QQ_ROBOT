from .UserStatusCounter import UserStatusCounter
from .battle import *
from .xiuxian import get_random_item
from .xiuxian_config import *
from hoshino import util
import random
from .xiuxian_base import *
from .youli import _youli


@sv.on_prefix(["#探索秘境"])
async def start(bot, ev: CQEvent):
    name = str(ev.message).strip()
    if not name:
        await bot.finish(ev, "请选择要探索的秘境")
    mi_jing = FU_BEN[name]
    if not mi_jing:
        await bot.finish(ev, "该秘境不存在,请确认要探索的秘境", at_sender=True)
    gid = ev.group_id
    uid = ev.user_id
    in_fuben = get_user_counter(gid, uid, UserModel.FU_BEN)
    if in_fuben:
        await bot.finish(ev, f"你已在秘境之中", at_sender=True)

    # 有伤势不可进
    shangshi = get_user_counter(gid, uid, UserModel.SHANGSHI)
    if shangshi:
        await bot.finish(ev, f"你身有伤势，无法探索秘境", at_sender=True)

    user = await get_ev_user(bot, ev)
    mijing_map = mi_jing['name']
    user_adress = MAP.get(user.map)
    if mijing_map not in user_adress['able']:
        await bot.finish(ev, f"你当前所在的[{user.map}]只能前往 {'｜'.join(user_adress['able'])}")

    ## 检查是否有进入凭证
    access = mi_jing['access']
    item_info = ITEM_NAME_MAP.get(access)
    counter = ItemCounter()
    num = counter._get_item_num(gid, uid, int(item_info['id']))
    # if num < 1:
    #     await bot.finish(ev, f"背包中没有道具{access}，无法探索秘境", at_sender=True)
    ## 消耗凭证 记录状态
    # counter._add_item(gid, uid, int(item_info['id']), num=-1)
    save_user_counter(gid, uid, UserModel.FU_BEN, 1)
    save_user_counter(gid, uid, UserModel.FU_BEN_EVENT_TIME, 0)

    ct = XiuxianCounter()
    user.map = mijing_map
    ct._save_user_info(user)

    # 记录副本时用户的状态 起始是保存基本属性 现在想存最终面板属性
    st = UserStatusCounter()
    origin_content = init_content(user)
    user.hp = origin_content["max_hp"]
    user.mp = origin_content["max_mp"]
    st._save_user_info(user)
    await bot.finish(ev, f"你已经进入{name}，可以开始你的探索之旅了", at_sender=True)


@sv.on_prefix(["#离开秘境"])
async def start(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    in_fuben = get_user_counter(gid, uid, UserModel.FU_BEN)
    if not in_fuben:
        await bot.finish(ev, f"你并不在秘境之中", at_sender=True)
    save_user_counter(gid, uid, UserModel.FU_BEN, 0)
    user = await get_ev_user(bot, ev)
    user.map = FU_BEN[user.map]['map']
    ct = XiuxianCounter()
    ct._save_user_info(user)
    await bot.finish(ev, f"你已离开秘境", at_sender=True)


@sv.on_fullmatch(["#探索"])
async def start(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    in_fuben = get_user_counter(gid, uid, UserModel.FU_BEN)
    if not in_fuben:
        await bot.finish(ev, f"你并不在秘境之中", at_sender=True)

    user = await get_ev_user(bot, ev)
    mi_jing = FU_BEN[user.map]
    event_time = get_user_counter(gid, uid, UserModel.FU_BEN_EVENT_TIME)
    # 触发boss战
    if event_time >= mi_jing['event_times']:
        boss_name = mi_jing['boss']
        user_status = await get_status_user(bot, ev)
        my_content = init_content(user_status)
        # 当前状态
        my_content = get_cur_status(my_content,user,bot, ev)
        boss_content = init_boss_content(my_content['gid'], boss_name)

        my_content, he_content, send_msg_li = battle_bases(my_content, boss_content, 0)
        my_hp = my_content['hp']
        he_hp = he_content['hp']
        log = ""
        if my_hp <= 0:
            # todo 死亡道具处理 待定
            log += f"{user.name}受到Boss-{boss_name}伤害，陷入濒死状态，被迫结束了此次秘境探索"
            save_user_counter(user.gid, user.uid, UserModel.SHANGSHI, 3)
        if he_hp <= 0:
            bonus = get_random_item(mi_jing['bonus'])
            log += f"{user.name}击败了Boss-{boss_name}，获得了奖励道具[{bonus}]，结束了此次秘境探索"
            item_info = ITEM_NAME_MAP.get(bonus)
            add_item_ignore_limit(user.gid, user.uid, item_info)
        send_msg_li.append(log)
        # 更新状态
        update_status(user, bot, ev)
        await bot.finish(ev, '\n'.join(send_msg_li), at_sender=True)

    # 探索事件
    all_li = mi_jing['event']
    event = get_random_item(all_li)
    result = await _fuben_event(event, user,0, bot, ev)
    add_user_counter(gid, uid, UserModel.FU_BEN_EVENT_TIME, 1)
    await bot.finish(ev, result, at_sender=True)


@sv.on_prefix(["#秘境事件"])
async def start(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg = str(ev.message).strip().split()
    if not msg:
        await bot.finish(ev, "你没有指定事件", at_sender=True)

    event = msg[0]

    cur_event = get_user_counter(gid, uid, UserModel.FU_BEN_EVENT)
    if not cur_event:
        await bot.finish(ev, "你未遇到任何秘境事件", at_sender=True)
    if event != cur_event:
        await bot.finish(ev, "你所遇到的秘境事件不是你指定的事件", at_sender=True)

    if len(msg) < 2:
        await bot.finish(ev, "你未对事件作出回应", at_sender=True)
    anwser = msg[1:]


register = dict()


async def _fuben_event(name, user, anwser, bot, ev):
    func = register.get(name)
    if func:
        return await func(user,anwser,bot, ev)
    return "秘境探索事件未实装"


# 注解msg 传入正则表达式进行匹配
def event_exe(item_name):
    def show(func):
        async def warpper(user, answer, bot, ev: CQEvent):
            return await func(user, answer, bot, ev)

        register[item_name] = warpper
        return warpper

    return show


@event_exe("隐秘之地")
async def qiecuo(user: AllUserInfo, answer, bot, ev: CQEvent):
    st = UserStatusCounter()
    user_status = st._get_user(user.gid, user.uid)
    origin_content = init_content(user)
    user_status.hp += int(origin_content['max_hp'] * 0.3)
    user_status.hp = origin_content['max_hp'] if user_status.hp > origin_content['max_hp'] else user_status.hp
    st._save_user_info(user_status)
    return f"此处安全而又隐蔽，在此稍作歇息,恢复了固定30%最大百分比的HP"



@event_exe("强大禁制")
async def qiecuo(user: AllUserInfo, answer, bot, ev: CQEvent):
    # if not answer:
    #     return "你发现一处散发着强大禁制的地点，是否选择破除此禁制？可选择\n是    否"
    # if answer == '否':
    #     return "你权衡利弊之下，不再去破除此禁制"
    msg ="你发现一处散发着强大禁制的地点，"
    roll = random.randint(1,10)
    st = UserStatusCounter()
    user_status = st._get_user(user.gid, user.uid)
    if roll <= 3:
        user_status.hp = int(user_status.hp*0.8)
        st._save_user_info(user_status)
        msg +="你破除失败，触发了禁制，用尽力气逃了出来，受了轻伤，损失了20%HP"
        return msg
    elif roll <= 7 :
        bonus = "纳戒"
    elif roll <= 8:
        bonus = "绯想之桃"
    elif roll <= 9:
        bonus = "失落之匙碎片"
    else :
        bonus = "千代乐的急救包"
    item_info = ITEM_NAME_MAP.get(bonus)
    add_item_ignore_limit(user.gid, user.uid, item_info)
    msg += f"你花了些许时间破除了此禁制，获得了[{bonus}]"
    return msg


@event_exe("秘境商人")
async def qiecuo(user: AllUserInfo, answer, bot, ev: CQEvent):
    msg = "你遇到了一个奇怪的神秘人，他走进后展开了自己的衣服，里面尽是奇珍异宝"
    item_li = ('灵葫药','还神丹','纳戒','失落之匙碎片')
    i = random.randint(0, len(item_li)-1)
    item = item_li[i]
    lingshi = 300
    if lingshi > user.lingshi:
        msg +="你的灵石不足无法购买，商人见你没有诚意，摆手离去"
        return msg
    add_user_counter(user.gid, user.uid, UserModel.LINGSHI, num=-lingshi)
    msg+=f"花费了{lingshi}灵石购买了{item}"
    if not add_item(user.gid, user.uid, get_item_by_name(item)):
        msg+="(你没有足够的背包空间,只能放弃)"
    return msg


@event_exe("神秘石板")
async def qiecuo(user: AllUserInfo, answer, bot, ev: CQEvent):
    ct = XiuxianCounter()
    msg="你发现一个神秘的石板，你走进前去细细观摩，"
    if user.wuxing > 60 :
        count = random.randint(1,10)
        if count == 1:
            user.act += 2
            feature = "物理攻击力"
        elif count == 2:
            user.defen += 2
            feature = "物防"
        elif count == 3:
            user.act2 += 2
            feature = "术法攻击力"
        elif count == 4:
            user.defen2 += 2
            feature = "魔抗"
        elif count == 5:
            user.skill += 2
            feature = "战斗技巧"
        else :
            msg += "你苦苦参悟，却什么事情都没有发生"
            return msg
        msg += f"感悟成功，{feature}提升1点"
        ct._save_user_info(user)
    else :
        msg+="你苦苦参悟，却什么事情都没有发生"
    return msg


@event_exe("神秘灵泉")
async def qiecuo(user: AllUserInfo, anwser,bot, ev: CQEvent):
    roll = random.randint(1,5)
    st = UserStatusCounter()
    user_status = st._get_user(user.gid, user.uid)
    log = "你发现一个神秘灵泉，强大的灵力，让你变得精力更加充沛，你临时提高了10%的"
    # 临时buff
    if roll == 1:
        user_status.act += int(user_status.act * 0.1)
        log+="物理攻击力"
    elif roll == 2:
        user_status.act2 += int(user_status.act2 * 0.1)
        log += "术法攻击力"
    if roll == 3:
        user_status.defen += int(user_status.defen * 0.1)
        log += "物防"
    elif roll == 4:
        user_status.defen2 += int(user_status.defen2 * 0.1)
        log += "魔抗"
    elif roll == 5:
        user_status.skill += int(user_status.skill * 0.1)
        log += "战斗技巧"
    st._save_user_info(user_status)
    return log


@event_exe("可疑身影")
async def qiecuo(user: AllUserInfo, anwser,bot, ev: CQEvent):
    msg="你发现一个可疑身影，"
    roll = random.randint(1,10)
    if roll > 7 :
        msg += "眉头一皱认为此人过于危险，选择绕道而行"
        count = random.randint(1,10)
        if count < 4:
            await bot.finish(ev, msg)
        else :
            msg += "，然而避开失败，"
    msg += "触发战斗"
    # todo 小怪
    mi_jing = FU_BEN[user.map]
    name_li = mi_jing['little_boss']
    roll = random.randint(0,len(name_li)-1)

    # 战斗
    user = await get_ev_user(bot,ev)
    user_status = await get_status_user(bot, ev)
    my_content = init_content(user_status)
    # 当前状态
    my_content = get_cur_status(my_content,user, bot, ev)
    boss_content = init_boss_content(user_status.gid, name_li[roll])
    my_content, he_content, send_msg_li = battle_bases(my_content, boss_content,0)
    my_hp = my_content['hp']
    he_hp = he_content['hp']
    # 战斗
    send_msg_li.insert(0,msg)
    if my_hp > 0 and he_hp <= 0:
        lingshi = random.randint(30, 80)
        exp = random.randint(15, 20)
        user.lingshi += lingshi
        user.exp+=20
        add_user_counter(user.gid, user.uid, UserModel.LINGSHI, lingshi)
        send_msg_li.append(f"{user.name}战斗胜利，获取{lingshi}灵石奖励,经验增加{exp}点")
        st = UserStatusCounter()
        user_status.hp = my_hp
        user_status.mp = my_content['mp']
        st._save_user_info(user_status)
    elif he_hp > 0 and my_hp <= 0:
        send_msg_li.append(f"{user.name}战斗失败，陷入濒死状态，被迫结束了此次秘境探索")
        save_user_counter(user.gid, user.uid, UserModel.SHANGSHI, 3)
        # 更新状态
        update_status(user,bot, ev)
    else:
        send_msg_li.append(f"战斗不分胜负")
    await bot.finish(ev, '\n'.join(send_msg_li))

@sv.on_fullmatch(["#查询状态"])
async def query(bot, ev: CQEvent):
    user_origin = await get_ev_user(bot, ev)
    in_fuben = get_user_counter(user_origin.gid, user_origin.uid, UserModel.FU_BEN)
    if not in_fuben:
        await bot.finish(ev, "你不在副本中，无法进行此操作")
    user = await get_status_user(bot, ev)
    user_status = await get_status_user_basic(bot, ev)
    sendmsg = f"""
道号:{user.name} 灵根:{user.linggen} 伤势:{user.shangshi_desc} 
境界:{JingJieMap[str(user.level)]}  EXP:{user.exp}
武器:{user.wuqi}  法宝:{user.fabao}
心法:{user.gongfa} 功法:{user.gongfa2} 神通:{user.gongfa3}
门派:{user.belong}  所在地:{user.map}
体质:{user.tizhi} 悟性:{user.wuxing} 灵力:{user.lingli} 道行:{user.daohang}
攻击:{user.battle_atk1} 术法:{user.battle_atk2} 物防:{user.battle_defen1} 魔抗:{user.battle_defen2}
HP:{user_status.hp} MP:{user_status.mp} 战斗技巧:{user.skill}
""".strip()
    await bot.finish(ev, sendmsg)

def update_status(user,bot, ev: CQEvent):
    user.map = FU_BEN[user.map]['map']
    save_user_counter(user.gid, user.uid, UserModel.FU_BEN, 0)
    save_user_counter(user.gid, user.uid, UserModel.FU_BEN_EVENT_TIME, 0)
    ct = XiuxianCounter()
    ct._save_user_info(user)

def get_cur_status(my_content,user_origin,bot, ev: CQEvent):
    st = UserStatusCounter();
    user_status = st._get_user(user_origin.gid, user_origin.uid)
    origin_content = init_content(user_origin)
    my_content["max_hp"] = origin_content["max_hp"]
    my_content["max_mp"] = origin_content["max_mp"]
    my_content["hp"] = user_status.hp
    my_content["mp"] = user_status.mp
    # 攻击
    # my_content["atk1"] = user_status.act
    # my_content["atk2"] = user_status.act2
    # # 防御
    # my_content["defen1"] = user_status.defen
    # my_content["defen2"] = user_status.defen2
    return my_content