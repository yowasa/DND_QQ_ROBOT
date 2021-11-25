import random

from hoshino import Service, priv
from hoshino.typing import CQEvent
from .XiuxianCounter import *
from hoshino.util import FreqLimiter

sv = Service('修仙', manage_priv=priv.SUPERUSER, enable_on_default=False, visible=True, bundle='修仙', help_=
'''[#修仙手册] 查询修仙帮助
''')

JingJieMap = {
    "1": '凡人',
    "2": '锻体 1阶',
    "3": '锻体 2阶',
    "4": '锻体 3阶',
    "5": '锻体 4阶',
    "6": '锻体 5阶',
    "7": '炼气 初期',
    "8": '炼气 中期',
    "9": '炼气 后期',
    "10": '筑基 初期',
    "11": '筑基 中期',
    "12": '筑基 后期',
}

EXP_NEED_MAP = {
    "1": 10,
    "2": 50,
    "3": 50,
    "4": 50,
    "5": 50,
    "6": 50,
    "7": 10,
    "8": 10,
    "9": 10,
    "10": 200,
    "11": 200,
    "12": 200,
}
# 时间限制
flmt = FreqLimiter(600)


@sv.on_fullmatch(["#修仙手册", "#修仙帮助"])
async def help(bot, ev: CQEvent):
    send_msg = """
#开始修仙 名字（注册账号）
#修炼（随机获得(1-50)/灵根数量的经验）
#锻体（增加体质，仅锻体期可用）
#对战 名字（PVP，1V1，谁死谁删号）
#查询（查询自身属性）
以上所有功能共用CD，但查询不实际消耗CD，CD期间进行操作减道行1点并禁言10分钟，道行归零则心魔入体自尽而亡，并禁言30分钟
"""
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


@sv.on_prefix(["#开始修仙"])
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
道号：{user.name}
灵根：{user.linggen}
境界：{JingJieMap[str(user.level)]}
武器：{user.wuqi}
所在地：{user.map}
门派：{user.belong}
体质:{user.tizhi} 悟性:{user.wuxing} 灵力:{user.lingli} 道行：{user.daohang}
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
            ct._del_user(user.gid, user.uid)
            await bot.finish(ev, f"道心不稳，爆体而亡!")
        ct._save_user_info(user)
        await bot.finish(ev, f"做事急躁，有损道心，道行-1，距离下次操作还需要{round(int(flmt.left_time(uid)))}秒")
    flmt.start_cd(uid)
    get_exp = int(random.randint(1, 50) / len(user.linggen))
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
            ct._del_user(user.gid, user.uid)
            await bot.finish(ev, f"道心不稳，爆体而亡!")
        ct._save_user_info(user)
        await bot.finish(ev, f"做事急躁，有损道心，道行-1，距离下次操作还需要{round(int(flmt.left_time(uid)))}秒")
    flmt.start_cd(uid)
    if (user.level < 2) or (user.level > 6):
        await bot.finish(ev, "只有锻体境可以锻体")
    if user.tizhi >= 100:
        await bot.finish(ev, "锻体境体质上限为100点")
    get_tizhi = random.randint(1, 10)
    user.tizhi += get_tizhi
    if user.tizhi > 100:
        user.tizhi = 100
    await bot.finish(ev, f'锻体成功，体质增加{get_tizhi}点')


@sv.on_prefix(["#对战"])
async def duanti(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    ct = XiuxianCounter()
    my = ct._get_user(gid, uid)
    if not my:
        await bot.finish(ev, "江湖上还没有过您的传说，请先注册账号")
    if not flmt.check(uid):
        my.daohang -= 1
        if my.daohang < 0:
            ct._del_user(my.gid, my.uid)
            await bot.finish(ev, f"道心不稳，爆体而亡!")
        ct._save_user_info(my)
        await bot.finish(ev, f"做事急躁，有损道心，道行-1，距离下次操作还需要{round(int(flmt.left_time(uid)))}秒")
    flmt.start_cd(uid)
    name = str(ev.message).strip()
    enemy = ct._get_user_by_name(gid, name)
    if not enemy:
        await bot.finish(ev, f"未找到名【{name}】的角色")
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
    # 我输了
    if my_hp <= 0 and he_hp > 0:
        msg = my_name + '率先力竭，' + he_name + '赢得了胜利，'
        if random.randint(0, 1):
            msg += '并顺势斩杀' + my_name + '，战斗技巧+' + str(get_skill)
            enemy.skill += get_skill
            ct._del_user(my.gid, my.uid)
            ct._save_user_info(enemy)
        else:
            enemy.skill += get_skill
            my.skill += get_skill
            ct._save_user_info(my)
            ct._save_user_info(enemy)
            msg += '但被' + my_name + '侥幸逃脱，未能当场斩杀，双方战斗技巧+' + str(get_skill)
        send_msg_li.append(msg)

    # 对方输了
    if my_hp > 0 and he_hp <= 0:
        msg = he_name + '率先力竭，' + my_name + '赢得了胜利'
        if random.randint(0, 1):
            msg += '并顺势斩杀' + he_name + '，战斗技巧+' + str(get_skill)
            my.skill += get_skill
            ct._del_user(enemy.gid, enemy.uid)
            ct._save_user_info(my)
        else:
            enemy.skill += get_skill
            my.skill += get_skill
            ct._save_user_info(my)
            ct._save_user_info(enemy)
            msg += '但被' + he_name + '侥幸逃脱，未能当场斩杀，双方战斗技巧+' + str(get_skill)
        send_msg_li.append(msg)

    # 同归于尽
    if my_hp <= 0 and he_hp <= 0:
        ct._del_user(enemy.gid, enemy.uid)
        ct._del_user(my.gid, my.uid)
        send_msg_li.append('二人力竭而亡，同归于尽')
    # 不分胜负
    if my_hp >= 0 and he_hp >= 0:
        enemy.skill += get_skill
        my.skill += get_skill
        ct._save_user_info(my)
        ct._save_user_info(enemy)
        send_msg_li.append('二人战斗难舍难分，不分胜负就此罢了,双方战斗技巧+' + str(get_skill))
    await bot.finish(ev, '\n'.join(send_msg_li))


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
