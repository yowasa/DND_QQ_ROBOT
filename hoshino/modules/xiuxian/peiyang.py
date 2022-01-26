from .xiuxian_config import *
from .xiuxian_base import *

def get_max_min_zongmen(user):
    min = 0
    max = 0
    for address in MAP.keys():
        if user.level < address['in_level']:
            return max, min
        min = address["lingqi_min"]
        max = address["lingqi_max"]
    return max, min


def cal_get_exp(user):
    address = MAP.get(user.map)
    # 宗门修炼会取能去的最高灵气地图的灵气值
    if address in list(ZONGMEN.keys()):
        max, min = get_max_min_zongmen(user)
    else:
        min = address["lingqi_min"]
    max = address["lingqi_max"]
    lingqi = random.randint(min, max)
    base_speed = XIULIAN_SPEED[len(user.linggen) - 1]
    # 宗门修炼额外获取20%的修炼速度
    if address in list(ZONGMEN.keys()):
        base_speed += 20
    speed = base_speed
    if user.gongfa == '太玄经':
        if 30 - user.wuxing > 0:
            speed += (30 - user.wuxing) * (10 - len(user.linggen))
        return int(lingqi * speed / 100) + 2
    if user.gongfa in ['天罡经', '八九玄功']:
        speed += 30
        if speed > 100:
            speed = 100
    if user.gongfa == '百锻成仙':
        speed = int(speed / 2)
        rd = random.randint(1, 10)
        if rd == 1:
            rd = random.randint(1, 6)
            if rd == 1:
                user.act += 1
            elif rd == 2:
                user.act2 += 1
            elif rd == 3:
                user.hp += 3
            elif rd == 4:
                user.mp += 1
            elif rd == 5:
                user.defen += 1
            elif rd == 6:
                user.defen2 += 1
    return int(lingqi * speed / 100) + 1


def cal_add_shuxing(user):
    if user.gongfa == '天罡经':
        rd = random.randint(1, 3)
        user.defen += rd
        user.defen2 += rd
    if user.gongfa == '八九玄功':
        rd = random.randint(10, 20)
        user.hp += rd


@sv.on_fullmatch(["#修炼"])
async def xiulian(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    if user.level > MAP[user.map]['max_level']:
        await bot.finish(ev, f"此地的灵气浓度不足以支撑你的修炼，请到灵气更加浓郁的地方。")
    if user.map in ZONGMEN.keys() and user.belong != user.map:
        await bot.finish(ev, f"你无法在非自己的宗门的修炼！")
    if (user.level in PINGJING) and user.exp > EXP_NEED_MAP[str(user.level)]:
        await bot.finish(ev, f"你已经到达了当前境界的瓶颈，无法继续获得经验！请使用#突破 来突破当前境界")
    await user.check_cd(bot, ev)
    user.start_cd()
    get_exp = cal_get_exp(user)
    ct = XiuxianCounter()
    if user.exp + get_exp < EXP_NEED_MAP[str(user.level)]:
        user.exp += get_exp
        ct._save_user_info(user)
        await bot.finish(ev, f"开始修炼，本次修炼获得经验值{get_exp}点")
    left_exp = user.exp + get_exp - EXP_NEED_MAP[str(user.level)]
    if (user.level in PINGJING) and left_exp >= 0:
        user.exp = user.exp + get_exp
        ct._save_user_info(user)
        await bot.finish(ev, f"你通过本次修炼到达了当前境界的瓶颈，请使用#突破 来突破当前境界")
    cal_add_shuxing(user)
    user.exp = left_exp
    user.level += 1
    if 2 <= user.level <= 6:
        user.hp += random.randint(5, 20)
        user.act += random.randint(5, 10)
        user.defen += 1
    elif 7 <= user.level <= 9:
        user.hp += random.randint(10, 25)
        user.mp += random.randint(1, 5)
        user.act += random.randint(10, 15)
        user.act2 += random.randint(15, 20)
    elif 10 <= user.level <= 12:
        user.hp += random.randint(25, 40)
        user.mp += random.randint(1, 10)
        user.act += random.randint(15, 20)
        user.act2 += random.randint(20, 25)
    elif 13 <= user.level <= 15:
        user.hp += random.randint(45, 55)
        user.mp += random.randint(1, 10)
        user.act += random.randint(20, 30)
        user.act2 += random.randint(20, 30)
    elif 16 <= user.level <= 18:
        user.hp += random.randint(55, 65)
        user.mp += random.randint(5, 10)
        user.act += random.randint(30, 40)
        user.act2 += random.randint(30, 40)
    elif 19 <= user.level <= 40:
        user.hp += random.randint(65, 80)
        user.mp += random.randint(5, 10)
        user.act += random.randint(30, 40)
        user.act2 += random.randint(30, 40)
    ct._save_user_info(user)
    await bot.finish(ev, f"开始修炼，本次修炼获得经验值{get_exp}点,并突破至{JingJieMap[str(user.level)]}")


@sv.on_fullmatch(["#放弃参悟"])
async def give_up_canwu(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    gongfa = get_user_counter(gid, uid, UserModel.STUDY_GONGFA)
    if not gongfa:
        await bot.finish(ev, "你还没有参悟中的功法，请使用功法书后再进行参悟", at_sender=True)
    gongfa_name = ITEM_INFO[str(gongfa)]['name']
    save_user_counter(gid, uid, UserModel.GONGFA_RATE, 0)
    save_user_counter(gid, uid, UserModel.STUDY_GONGFA, 0)
    await bot.finish(ev, f"你放弃了参悟「{gongfa_name}」。。。", at_sender=True)


@sv.on_fullmatch(["#参悟"])
async def canwu(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    user = await get_ev_user(bot, ev)
    gongfa = get_user_counter(gid, uid, UserModel.STUDY_GONGFA)
    if not gongfa:
        await bot.finish(ev, "你还没有参悟中的功法，请使用功法书后再进行参悟", at_sender=True)
    await user.check_and_start_cd(bot, ev)
    gongfa_name = ITEM_INFO[str(gongfa)]['name']
    gongfa_info = get_gongfa_by_name(gongfa_name)
    content = {"wuxing": user.wuxing}
    speed = int(eval(gongfa_info['speed'], content))
    rate = get_user_counter(gid, uid, UserModel.GONGFA_RATE)
    rate += speed
    if rate < 100:
        save_user_counter(gid, uid, UserModel.GONGFA_RATE, rate)
        await bot.finish(ev, f"你对功法{gongfa_name}的参悟进度提升了{speed}%，目前进度为{rate}%", at_sender=True)
    else:
        save_user_counter(gid, uid, UserModel.GONGFA_RATE, 0)
        save_user_counter(gid, uid, UserModel.STUDY_GONGFA, 0)
        if ITEM_INFO[str(gongfa)]['type'] == '心法':
            user.gongfa = gongfa_name
        if ITEM_INFO[str(gongfa)]['type'] == '功法':
            user.gongfa2 = gongfa_name
        if ITEM_INFO[str(gongfa)]['type'] == '神通':
            user.gongfa3 = gongfa_name
        ct = XiuxianCounter()
        ct._save_user_info(user)
        await bot.finish(ev, f"你彻底参悟了功法{gongfa_name}！", at_sender=True)


@sv.on_prefix(["#废功"])
async def feigong(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg = str(ev.message).strip()
    user = await get_ev_user(bot, ev)
    if msg in ["心法", "功法", "神通"] or msg in [user.gongfa, user.gongfa2, user.gongfa3]:
        await user.check_and_start_cd(bot, ev)
        if msg in ["心法", user.gongfa]:
            user.gongfa = "无"
        if msg in ["功法", user.gongfa2]:
            user.gongfa2 = "无"
        if msg in ["神通", user.gongfa3]:
            user.gongfa3 = "无"
        save_user_counter(gid, uid, UserModel.SHANGSHI, 2)
        ct = XiuxianCounter()
        ct._save_user_info(user)
        flmt.start_cd(uid)
        await bot.finish(ev, f"你自废了功法,身受重伤！", at_sender=True)
    else:
        await bot.finish(ev, f"未找到名为{msg}的功法", at_sender=True)


@sv.on_fullmatch(["#修养"])
async def feigong(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    user = await get_ev_user(bot, ev)
    shangshi = get_user_counter(gid, uid, UserModel.SHANGSHI)
    if not shangshi:
        await bot.finish(ev, f"你没有受伤，无需修养", at_sender=True)

    await user.check_in_fuben(bot, ev)
    await user.check_cd_ignore_other(bot, ev)
    time = get_user_counter(gid, uid, UserModel.XIUYANG_TIME)
    time += 1
    user.start_cd()
    if shangshi == 3:
        need = 1
        if need - time <= 0:
            save_user_counter(gid, uid, UserModel.SHANGSHI, 2)
            save_user_counter(gid, uid, UserModel.XIUYANG_TIME, 0)
            await bot.finish(ev, f"经过修养，你的伤势转化为重伤", at_sender=True)
        else:
            save_user_counter(gid, uid, UserModel.XIUYANG_TIME, time)
            await bot.finish(ev, f"经过修养，你的伤势减轻了（还需要{need - time}次修养转为重伤）", at_sender=True)
    if shangshi == 2:
        need = 2
        if need - time <= 0:
            save_user_counter(gid, uid, UserModel.SHANGSHI, 1)
            save_user_counter(gid, uid, UserModel.XIUYANG_TIME, 0)
            await bot.finish(ev, f"经过修养，你的伤势转化为轻伤", at_sender=True)
        else:
            save_user_counter(gid, uid, UserModel.XIUYANG_TIME, time)
            await bot.finish(ev, f"经过修养，你的伤势减轻了（还需要{need - time}次修养转为轻伤）", at_sender=True)
    if shangshi == 1:
        need = 1
        if need - time <= 0:
            save_user_counter(gid, uid, UserModel.SHANGSHI, 0)
            save_user_counter(gid, uid, UserModel.XIUYANG_TIME, 0)
            await bot.finish(ev, f"经过修养，你的伤势完全恢复了", at_sender=True)
        else:
            save_user_counter(gid, uid, UserModel.XIUYANG_TIME, time)
            await bot.finish(ev, f"经过修养，你的伤势减轻了（还需要{need - time}次修养完全恢复）", at_sender=True)


@sv.on_fullmatch(["#锻体"])
async def duanti(bot, ev: CQEvent):
    ct = XiuxianCounter()
    user = await get_ev_user(bot, ev)
    if (user.level < 2) or (user.level > 6):
        await bot.finish(ev, "只有锻体境可以锻体")
    if user.tizhi >= 100:
        await bot.finish(ev, "锻体境体质上限为100点")
    await user.check_and_start_cd(bot, ev)
    get_tizhi = random.randint(1, 10)
    get_hp = random.randint(1, 3)
    user.tizhi += get_tizhi
    user.hp += get_hp
    user.defen += 1
    if user.tizhi > 100:
        user.tizhi = 100
    ct._save_user_info(user)
    await bot.finish(ev, f'锻体成功，体质增加{get_tizhi}点，hp增加了{get_hp}点')


@sv.on_fullmatch(["#练气"])
async def duanti(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    if (user.level < 7) or (user.level > 9):
        await bot.finish(ev, "只有练气境可以练气")
    if user.lingli >= 100:
        await bot.finish(ev, "练气灵力上限为100点")
    await user.check_and_start_cd(bot, ev)
    ct = XiuxianCounter()
    get_lingli = random.randint(1, 10)
    get_hp = random.randint(1, 3)
    user.lingli += get_lingli
    user.mp += get_hp
    get_act = random.randint(1, 3)
    user.act2 += get_act
    user.defen2 += 1
    if user.lingli > 100:
        user.lingli = 100
    ct._save_user_info(user)
    await bot.finish(ev, f'练气成功，灵力增加{get_lingli}点，mp增加了{get_hp}点,术法攻击力增加{get_act}点')
