import random
from hoshino import util
from .xiuxian_config import *


@sv.on_fullmatch(["#修仙手册", "#修仙帮助"])
async def help(bot, ev: CQEvent):
    send_msg = """
#开始修仙 名字（注册账号）
#修炼（随机获得(1-50)/灵根数量的经验）
#游历 (触发随机事件，与当前所在地相关)
#锻体（增加体质，仅锻体期可用）
#对战 名字（PVP，1V1，输掉的人一半概率被击杀）
#前往 地名 (现在有新手村、大千世界、修仙秘境)
=======以下指令不消耗cd=======
#背包 （查看自己拥有的物品）
#使用/丢弃 物品名
#查询（查询自身属性）
以上所有功能除查询外共CD，CD为10分钟，CD期间进行操作减道行1点，道行归零则心魔入体自尽而亡
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
    user.wuqi = "无"
    user.wuxing = 50
    user.lingli = 0
    user.daohang = 20
    user.act = 10
    user.defen = 10
    user.defen2 = 10
    user.hp = 100
    user.mp = 100
    user.skill = 20
    user.tizhi = 20


@sv.on_prefix(["#开始修仙", "#注册账号"])
async def start(bot, ev: CQEvent):
    name = str(ev.message).strip()
    gid = ev.group_id
    uid = ev.user_id
    if not name:
        await bot.finish(ev, "账号名至少为一个字！")
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


@sv.on_fullmatch(["#查询"])
async def query(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if not user:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    time = int(flmt.left_time(uid))
    if time <= 0:
        time = 0
    sendmsg = f"""
道号:{user.name}
灵根:{user.linggen}
境界:{JingJieMap[str(user.level)]}  EXP:{user.exp}
武器:{user.wuqi}  法宝:{user.fabao}
门派:{user.belong}  所在地:{user.map}
体质:{user.tizhi} 悟性:{user.wuxing} 灵力:{user.lingli} 道行:{user.daohang}
攻击:{user.act} 物防:{user.defen} 魔抗:{user.defen2}
生命:{user.hp} 法力:{user.mp} 战斗技巧:{user.skill}
下次操作时间:{time}秒后
""".strip()
    await bot.finish(ev, sendmsg)


@sv.on_fullmatch(["#修炼"])
async def xiulian(bot, ev: CQEvent):
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
    address = MAP.get(user.map)
    if user.level > address['max_level']:
        await bot.finish(ev, f"开始修炼。。。你发现周围的灵气不足以支持你继续精进,是时候考虑去其他地方了。")
    get_exp = int(random.randint(1, 50) / len(user.linggen))
    if get_exp < 2:
        get_exp = 2
    if user.exp + get_exp < EXP_NEED_MAP[str(user.level)]:
        user.exp += get_exp
        ct._save_user_info(user)
        await bot.finish(ev, f"开始修炼，本次修炼获得经验值{get_exp}点")
    left_exp = user.exp + get_exp - EXP_NEED_MAP[str(user.level)]
    user.exp = left_exp
    user.level += 1
    if 8 <= user.level <= 10:
        user.lingli += random.randint(1, 20)
        user.daohang += random.randint(1, 3)
    user.hp += random.randint(1, 10)
    user.act += random.randint(1, 5)
    ct._save_user_info(user)
    await bot.finish(ev, f"开始修炼，本次修炼获得经验值{get_exp}点,并突破至{JingJieMap[str(user.level)]}")


@sv.on_fullmatch(["#锻体"])
async def duanti(bot, ev: CQEvent):
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
    if (user.level < 2) or (user.level > 6):
        await bot.finish(ev, "只有锻体境可以锻体")
    if user.tizhi >= 100:
        await bot.finish(ev, "锻体境体质上限为100点")
    get_tizhi = random.randint(1, 10)
    get_hp = random.randint(1, 3)
    user.tizhi += get_tizhi
    user.hp += get_hp
    if user.tizhi > 100:
        user.tizhi = 100
    ct._save_user_info(user)
    await bot.finish(ev, f'锻体成功，体质增加{get_tizhi}点，hp增加了{get_hp}点')


@sv.on_prefix(["#对战"])
async def duanti(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    my = ct._get_user(gid, uid)
    if not my:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    name = str(ev.message).strip()
    enemy = ct._get_user_by_name(gid, name)
    if not enemy:
        await bot.finish(ev, f"未找到名【{name}】的角色")
    if my.uid == enemy.uid:
        await bot.finish(ev, f"不能自己打自己（恼）")
    if not flmt.check(uid):
        my.daohang -= 1
        if my.daohang < 0:
            delete_user(my)
            await bot.finish(ev, f"道心不稳，爆体而亡!")
        ct._save_user_info(my)
        await util.silence(ev, 10 * 60, skip_su=False)
        await bot.finish(ev, f"做事急躁，有损道心，道行-1，距离下次操作还需要{round(int(flmt.left_time(uid)))}秒")
    flmt.start_cd(uid)
    if my.map != enemy.map:
        await bot.finish(ev, f"你找遍了四周也没有发现{name}的身影，或许他根本不在这里？")
    # 我的伤害
    my_atk = int(int(my.act) * ((100 + int(my.skill)) / 100) * 1.5 * 100 / (100 + int(enemy.defen)))
    # 对方伤害
    he_atk = int(int(enemy.act) * ((100 + int(enemy.skill)) / 100) * 1.5 * 100 / (100 + int(my.defen)))

    my_hp = my.hp
    he_hp = enemy.hp
    my_name = my.name
    he_name = enemy.name

    pk_i = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    send_msg_li = []
    for i in pk_i:
        now_atk1 = he_atk + random.randint(1, 10) - random.randint(1, 20)
        now_atk2 = my_atk + random.randint(1, 10) - random.randint(1, 20)
        if now_atk1 <= 0:
            now_atk1 = 1
        if now_atk2 <= 0:
            now_atk2 = 1
        my_hp = my_hp - now_atk1
        he_hp = he_hp - now_atk2
        if i <= 5:
            send_msg_li.append(f"第{i}回合交手，{my_name}对{he_name}造成{now_atk2}伤害，{he_name}对{my_name}造成{now_atk1}伤害")
        elif i == 6:
            send_msg_li.append('......')
        if my_hp <= 0:
            break
        if he_hp <= 0:
            break
    get_skill = random.randint(1, 3)
    if (my.level != enemy.level) or ((my.skill - enemy.skill) > 10 or (my.skill - enemy.skill) < -10):
        get_skill = 0
    # 我输了
    wanli = get_item_by_name("瞬息万里符")
    if my_hp <= 0 and he_hp > 0:
        msg = my_name + '率先力竭，' + he_name + '赢得了胜利，'
        if random.randint(0, 1):
            if check_have_item(my.gid, my.uid, wanli):
                use_item(my.gid, my.uid, wanli)
                msg += "，就在即将击杀之际" + my_name + '使用[瞬息万里符]逃脱，双方战斗技巧+' + str(get_skill)
                enemy.skill += get_skill
                if enemy.skill > 100:
                    enemy.skill = 100
                my.skill += get_skill
                if my.skill > 100:
                    my.skill = 100
                ct._save_user_info(my)
                ct._save_user_info(enemy)
            else:
                msg += '并顺势斩杀' + my_name + '，战斗技巧+' + str(get_skill)
                enemy.skill += get_skill
                if enemy.skill > 100:
                    enemy.skill = 100
                kill = get_user_counter(enemy.gid, enemy.uid, UserModel.KILL)
                kill += 1
                save_user_counter(enemy.gid, enemy.uid, UserModel.KILL, kill)
                delete_user(my)
                ct._save_user_info(enemy)
        else:
            enemy.skill += get_skill
            if enemy.skill > 100:
                enemy.skill = 100
            my.skill += get_skill
            if my.skill > 100:
                my.skill = 100
            ct._save_user_info(my)
            ct._save_user_info(enemy)
            msg += '但被' + my_name + '侥幸逃脱，未能当场斩杀，双方战斗技巧+' + str(get_skill)
        send_msg_li.append(msg)

    # 对方输了
    if my_hp > 0 and he_hp <= 0:
        msg = he_name + '率先力竭，' + my_name + '赢得了胜利'
        if random.randint(0, 1):
            if check_have_item(enemy.gid, enemy.uid, wanli):
                use_item(enemy.gid, enemy.uid, wanli)
                msg += "，就在即将击杀之际" + he_name + '使用[瞬息万里符]逃脱，双方战斗技巧+' + str(get_skill)
                enemy.skill += get_skill
                if enemy.skill > 100:
                    enemy.skill = 100
                my.skill += get_skill
                if my.skill > 100:
                    my.skill = 100
                ct._save_user_info(my)
                ct._save_user_info(enemy)
            else:
                msg += '并顺势斩杀' + he_name + '，战斗技巧+' + str(get_skill) + f'[CQ:at,qq={enemy.uid}]'
                my.skill += get_skill
                if my.skill > 100:
                    my.skill = 100
                kill = get_user_counter(my.gid, my.uid, UserModel.KILL)
                kill += 1
                save_user_counter(my.gid, my.uid, UserModel.KILL, kill)
                delete_user(enemy)
                ct._save_user_info(my)
        else:
            enemy.skill += get_skill
            if enemy.skill > 100:
                enemy.skill = 100
            my.skill += get_skill
            if my.skill > 100:
                my.skill = 100
            ct._save_user_info(my)
            ct._save_user_info(enemy)
            msg += '但被' + he_name + '侥幸逃脱，未能当场斩杀，双方战斗技巧+' + str(get_skill)
        send_msg_li.append(msg)

    # 同归于尽
    if my_hp <= 0 and he_hp <= 0:
        delete_user(my)
        delete_user(enemy)
        send_msg_li.append('二人力竭而亡，同归于尽' + f'[CQ:at,qq={enemy.uid}]')

    # 不分胜负
    if my_hp >= 0 and he_hp >= 0:
        enemy.skill += get_skill
        my.skill += get_skill
        ct._save_user_info(my)
        ct._save_user_info(enemy)
        send_msg_li.append('二人战斗难舍难分，不分胜负就此罢了,双方战斗技巧+' + str(get_skill))
    await bot.finish(ev, '\n'.join(send_msg_li))


@sv.on_prefix(["#前往"])
async def go(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    user = ct._get_user(gid, uid)
    if not user:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    name = str(ev.message).strip()
    adress = MAP.get(name)
    if not adress:
        await bot.finish(ev, f"未找到名为「{name}」的地点")
    need_level = adress["in_level"]
    if user.level < need_level:
        await bot.finish(ev, f"你的还不足以应对接下来的挑战，请先提升自己的实力吧（{name}需要{JingJieMap[str(need_level)]}才能前往）")

    if not flmt.check(uid):
        user.daohang -= 1
        if user.daohang < 0:
            delete_user(user)
            await bot.finish(ev, f"道心不稳，爆体而亡!")
        ct._save_user_info(user)
        await util.silence(ev, 10 * 60, skip_su=False)
        await bot.finish(ev, f"做事急躁，有损道心，道行-1，距离下次操作还需要{round(int(flmt.left_time(uid)))}秒")
    flmt.start_cd(uid)
    user.map = name
    ct._save_user_info(user)
    await bot.finish(ev, f"这里的事情已经办完了，动身前往{name}")


# 赋予灵根
def get_LingGen():
    ran = random.randint(1, 100)
    if ran < 60:
        len = 5
    elif ran < 80:
        len = 4
    elif ran < 90:
        len = 3
    elif ran < 97:
        len = 2
    else:
        len = 1
    linggen = ['金', '木', '水', '火', '土']
    lg = random.sample(linggen, len)
    str_lg = ''.join(lg)
    return str_lg
