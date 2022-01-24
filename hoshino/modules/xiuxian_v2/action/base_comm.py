from ..base import *
from ..common import *


# 基础操作
@sv.on_fullmatch(["#修仙手册", "#修仙帮助"])
async def help(bot, ev: CQEvent):
    send_msg = """
#开始修仙 名字 (注册账号)
#修炼 (依据所在地点的灵气和自身修炼速度获取经验)
#突破 (突破当前境界)
#游历 (触发随机事件，与当前所在地相关)
#对战 名字（PVP，会死人的）
#前往 地名 (切换所在地)
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


@sv.on_prefix(["#开始修仙", "#注册账号"])
async def _(bot, ev: CQEvent):
    name = get_message_text(ev)
    uid = ev.user_id
    if not name:
        await bot.finish(ev, "账号名至少为一个字！")
    if len(name) > 5:
        await bot.finish(ev, "账号名不要超过5个字！")
    user = UserDao.get_full_user(uid)
    if user:
        await bot.finish(ev, f"你已经有账号了，账号名为{user.name}")
    ct = XiuXianCounter()
    user = ct._get_user_by_name(name)
    if user:
        await bot.finish(ev, "用户名已存在，注册失败，请稍后重试！")
    if not die_flmt.check(uid):
        await bot.finish(ev, f"死亡cd中，还剩{round(int(die_flmt.left_time(uid)))}秒")
    user, spec = UserDao.init_user(uid, name)
    ex_msg = ""
    if spec:
        ex_msg = "\n" + "\n".join(spec)
    await bot.finish(ev, f'拥有{user.magic_root}灵根的{name}已正式进入修仙界{ex_msg}')


@sv.on_fullmatch(["#查询"])
async def _(bot, ev: CQEvent):
    user = await UserDao.get_ev_user(bot, ev)
    sendmsg = f"""
道号:{user.name} 灵根:{user.magic_root} 寿元:{user.attr.age_max} 伤势:{user.shangshi_desc} 
境界:{LEVEL_MAP[str(user.grade)]['name']}{user.level}层  EXP:{user.exp}
武器:{user.arms} 衣服:{user.armor} 法宝:{user.magic_weapon}
神识:{user.use_spiritual}/{user.attr.spiritual}功法:{' '.join(user.ability)}
门派:{user.belong}  所在地:{user.local}
悟性:{user.attr.comprehension} 体质:{user.attr.constitution} 灵力:{user.attr.magic_power} 气感:{user.attr.perception} 
HP:{user.battle_hp} MP:{user.battle_mp}
攻击:{user.battle_atk1} 术法:{user.battle_atk2} 物防:{user.battle_defend1} 魔抗:{user.battle_defend2}
暴击:{user.battle_boost} 连击:{user.battle_double} 闪避:{user.battle_dodge}
""".strip()
    await bot.finish(ev, sendmsg)


@sv.on_prefix(["#前往"])
async def go(bot, ev: CQEvent):
    user = await UserDao.get_ev_user(bot, ev)
    destination = get_message_text(ev)
    address = MAP.get(destination)
    if not address:
        await bot.finish(ev, f"未找到名为「{destination}」的地点")
    user_adress = MAP.get(user.local)
    if destination not in user_adress['able']:
        await bot.finish(ev, f"你当前所在的[{user.local}]只能前往 {'｜'.join(user_adress['able'])}")
    need_level = address["in_level"]
    if user.level < need_level:
        await bot.finish(ev, f"你的还不足以应对接下来的挑战，请先提升自己的实力吧（{destination}需要{LEVEL_MAP[str(need_level)]['name']}才能前往）")
    # 进宗门（从宗门所在大地图去宗门）
    belong_flag = 0
    if destination == user.belong and user.local == ZONGMEN.get(user.belong)["map"]:
        belong_flag = 1
    # 出宗门
    if user.local == user.belong and destination == ZONGMEN.get(user.belong)["map"]:
        belong_flag = 1
    await user.check_cd(bot, ev)
    if not ("千里神行" in user.ability or belong_flag):
        user.start_cd()
    user.local = destination
    user.save_user()
    await bot.finish(ev, f"这里的事情已经办完了，动身前往{destination}")


