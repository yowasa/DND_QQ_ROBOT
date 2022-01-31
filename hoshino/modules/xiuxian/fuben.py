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
    if num < 1:
        await bot.finish(ev, f"背包中没有道具{access}，无法探索秘境", at_sender=True)
    ## 消耗凭证 记录状态
    counter._add_item(gid, uid, int(item_info['id']), num=-1)
    save_user_counter(gid, uid, UserModel.FU_BEN, 1)
    save_user_counter(gid, uid, UserModel.FU_BEN_EVENT_TIME, 0)

    ct = XiuxianCounter()
    user.map = mijing_map
    ct._save_user_info(user)

    # 记录副本时用户的状态
    st = UserStatusCounter()
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

    # todo
    user = await get_ev_user(bot, ev)
    mi_jing = FU_BEN[user.map]
    event_time = get_user_counter(gid, uid, UserModel.FU_BEN_EVENT_TIME)
    # 触发boss战
    if event_time >= mi_jing['event_times']:
        boss_name = mi_jing['boss']
        my_hp, he_hp, send_msg_li = battle_boss(user)
        log = ""
        if my_hp <= 0:
            # todo 死亡道具处理
            log += f"{user.name}受到Boss-{boss_name}伤害，陷入濒死状态，被迫结束了此次秘境探索"

        if he_hp <= 0:
            save_group_counter(gid, GroupModel.YUANDAN_BOSS, 1)
            bonus = get_random_item(mi_jing['bonus'])
            log += f"{user.name}击败了Boss-{boss_name}，获得了奖励道具[{bonus}]，结束了此次秘境探索"
        send_msg_li.append(log)
        # 更新状态
        save_user_counter(gid, uid, UserModel.FU_BEN, 0)
        user = await get_ev_user(bot, ev)
        user.map = FU_BEN[user.map]['map']
        save_user_counter(gid, uid, UserModel.FU_BEN_EVENT_TIME, 0)
        ct = XiuxianCounter()
        ct._save_user_info(user)
        await bot.send(ev, send_msg_li, at_sender=True)

    # 探索事件
    all_li = mi_jing['event']
    event = get_random_item(all_li)
    result = await _youli(event, user, bot, ev)
    add_user_counter(gid, uid, UserModel.FU_BEN_EVENT_TIME, 1)
    await bot.send(ev, result, at_sender=True)


@sv.on_prefix(["#秘境事件"])
async def start(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg = str(ev.message).strip().split()
    if not msg:
        await bot.send(ev, "你没有指定事件", at_sender=True)

    event = msg[0]

    cur_event = get_user_counter(gid, uid, UserModel.FU_BEN_EVENT)
    if not cur_event:
        await bot.send(ev, "你未遇到任何秘境事件", at_sender=True)
    if event != cur_event:
        await bot.send(ev, "你所遇到的秘境事件不是你指定的事件", at_sender=True)

    if len(msg) < 2:
        await bot.send(ev, "你未对事件作出回应", at_sender=True)
    anwser = msg[1:]


register = dict()


async def _fuben_event(name, user, anwser, bot, ev):
    func = register.get(name)
    if func:
        return await func(user, bot, anwser, ev)
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
    user_status.hp += int(user.hp * 0.3)
    user_status.hp = user.hp if user_status.hp > user.hp else user_status.hp
    st._save_user_info(user_status)
    return f"此处安全而又隐蔽，在此稍作歇息,恢复了固定30%最大百分比的HP"


@event_exe("可疑身影")
async def qiecuo(user: AllUserInfo, answer, bot, ev: CQEvent):


    return f"帮助村民击退了附近的野兽，获取5点经验"


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
        user_status.hp -= int(user_status.hp*0.2)
        st._save_user_info(user_status)
        msg +="你破除失败，触发了禁制，用尽力气逃了出来，受了轻伤，损失了20%HP"
        return msg
    elif roll <= 6 :
        bonus = "纳戒"
    elif roll <= 9:
        bonus = "失落之匙碎片"
    else :
        bonus = "千代乐的急救包"
    item_info = ITEM_INFO[bonus]
    add_item_ignore_limit(user.gid, user.uid, item_info)
    msg += f"你花了些许时间破除了此禁制，获得了[{bonus}]"
    return msg


@event_exe("秘境商人")
async def qiecuo(user: AllUserInfo, answer, user_status, bot, ev: CQEvent):
    msg = "你一个奇怪的神秘人，向你招手，走进后展开了自己的衣服咧嘴笑，里面尽是奇珍异宝"
    item_li = ('灵葫药','还神丹','纳戒')
    i = random.randint(0, len(item_li)-1)
    item = item_li[i]
    lingshi = 300
    if lingshi > user.lingshi:
        msg +="你的灵石不足无法购买，商人见你没有诚意，摆手离去"
        return msg
    add_user_counter(user.gid, user.uid, UserModel.LINGSHI, num=-lingshi)
    msg+=f"花费了{lingshi}灵石购买了{answer}"
    if not add_item(user.gid, user.uid, get_item_by_name(item)):
        msg+="(你没有足够的背包空间,只能放弃)"
    return msg


@event_exe("神秘石板")
async def qiecuo(user: AllUserInfo, answer, user_status, bot, ev: CQEvent):
    ct = XiuxianCounter()
    msg="你发现一个神秘的石板，你走进前去细细观摩，"
    if user.wuxing > 60 :
        count = random.randint(1,10)
        if count == 1:
            user.atk += 1
            feature = "物理攻击力"
        elif count == 2:
            user.defen += 1
            feature = "物防"
        elif count == 3:
            user.atk2 += 1
            feature = "术法攻击力"
        else :
            msg += "你苦苦参悟，却什么事情都没有发生"
            return msg
        msg += f"感悟成功，{feature}提升一点"
        ct._save_user_info(user)
    else :
        msg+="你苦苦参悟，却什么事情都没有发生"
    return msg


@event_exe("神秘灵泉")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    roll = random.randint(1,6)
    return f"帮助村民击退了附近的野兽，获取5点经验"


@event_exe("狭路相逢")
async def qiecuo(user: AllUserInfo, anwser,user_status,bot, ev: CQEvent):
    my_content = init_content(user_status)
    enemy_content = init_shilian_content(user)
    # 战斗
    my_hp, he_hp, send_msg_li = battle_base(my_content, enemy_content)
    # 战斗
    if my_hp > 0 and he_hp <= 0:
        lingshi = random.randint(30, 80)
        user.lingshi += lingshi
        add_user_counter(user.gid, user.uid, UserModel.LINGSHI, lingshi)
        send_msg_li.append(f"{user.name}试炼成功，获取{lingshi}灵石奖励")
    elif he_hp > 0 and my_hp <= 0:
        send_msg_li.append(f"{user.name}试炼失败")
    else:
        send_msg_li.append(f"试炼不分胜负")
    await bot.finish(ev, '\n'.join(send_msg_li))
