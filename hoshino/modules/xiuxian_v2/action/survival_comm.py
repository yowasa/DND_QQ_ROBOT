from ..base import *
from ..common import *
from ..config import *


# 生存技能
@sv.on_prefix(["#传送"])
async def go(bot, ev: CQEvent):
    user = await UserDao.get_ev_user(bot, ev)
    name = str(ev.message).strip()
    adress = MAP.get(name)
    if not adress:
        await bot.finish(ev, f"未找到名为「{name}」的地点")
    need_level = adress["in_level"]
    if user.grade < need_level:
        await bot.finish(ev, f"你实力还不足以进入该地图（{name}需要{LEVEL_MAP[str(need_level)]['name']}才能进入）")
    count = UserModelDao.get_user_counter(user.uid, UserModel.CHUANSONG)
    if count <= 0:
        if user.have_item("传送符"):
            user.use_item("传送符")
            UserModelDao.add_user_counter(user.uid, UserModel.CHUANSONG, num=3)
        else:
            await bot.finish(ev, f"你剩余传送次数不足且没有传送符")
    UserModelDao.add_user_counter(user.uid, UserModel.CHUANSONG, num=-1)
    user.local = name
    user.save_user()
    await bot.finish(ev, f"你使用了传送符传送到了[{name}]")


@sv.on_prefix(["#锻造"])
async def _(bot, ev: CQEvent):
    user = await UserDao.get_ev_user(bot, ev)
    user.use_item()
    await user.check_cd(bot, ev)
    item_id = UserModelDao.get_user_counter(user.uid, UserModel.DUANZAO_ITEM)
    if item_id:
        item = ITEM_INFO[str(item_id)]
        cd = UserModelDao.get_user_counter(user.uid, UserModel.DUANZAO_CD)
        cd += 1
        danfang = DUANZAO[item['name']]
        time = danfang['time']
        if user.gongfa3 == "千锤百炼":
            time = 2
        if cd >= time:
            if not ItemDao.add_item(user.uid, item):
                await bot.finish(ev, "请先腾出一格背包空间")
            UserModelDao.save_user_counter(user.uid, UserModel.DUANZAO_CD, 0)
            UserModelDao.ave_user_counter(user.uid, UserModel.DUANZAO_ITEM, 0)
            user.start_cd()
            await bot.finish(ev, f"锻造成功，获得武器[{item['name']}]")
        else:
            user.start_cd()
            UserModelDao.save_user_counter(user.uid, UserModel.DUANZAO_CD, cd)
            left_time = danfang['time'] - cd
            await bot.finish(ev, f"还需{left_time}次[#锻造]指令（无需加武器名）可以获得武器[{item['name']}]")
    if user.belong != "百炼山庄":
        await bot.finish(ev, f"只有百炼山庄可以锻造！")
    msg = get_message_text(ev)
    danfang = DUANZAO.get(msg)
    if not danfang:
        await bot.finish(ev, f"不存在名为[{msg}]的武器锻造方式")
    # 如果立马获取的武器是否有背包空间
    if danfang['time'] == 1:
        if not ItemDao.check_have_space(user.uid):
            await bot.finish(ev, "请先腾出一格背包空间再进行炼制")
    # 检查素材和灵石是否足够
    need_lingshi = danfang['lingshi']
    if user.gongfa3 == "千锤百炼":
        need_lingshi = int(need_lingshi / 2)
    if need_lingshi > user.lingshi:
        await bot.finish(ev, f"你没有足够的灵石为武器注灵，需要{need_lingshi}灵石")
    need_items = danfang['item']
    for i in need_items:
        item = ItemDao.get_item_by_name(i)
        if not ItemDao.check_have_item(user.uid, item):
            await bot.finish(ev, f"锻造{msg}需要{i},你背包中的素材不足")
    user.start_cd()
    # 消耗灵石和材料
    for i in need_items:
        item = ItemDao.get_item_by_name(i)
        ItemDao.use_item(user.uid, item)
    UserModelDao.add_user_counter(user.uid, UserModel.LINGSHI, -need_lingshi)
    # 检查是否可以直接炼制
    get_item = ItemDao.get_item_by_name(msg)
    costmsg = f"你消耗了{need_lingshi}灵石 " + " ".join(need_items)
    if danfang['time'] == 1:
        ItemDao.add_item(user.uid, get_item)
        await bot.finish(ev, f"锻造成功，{costmsg} 获得武器[{get_item['name']}]")
    else:
        left_time = danfang['time'] - 1
        UserModelDao.save_user_counter(user.uid, UserModel.DUANZAO_CD, 1)
        UserModelDao.save_user_counter(user.uid, UserModel.DUANZAO_ITEM, int(get_item['id']))
        await bot.finish(ev, f"{costmsg} 开始锻造{get_item['name']},还需{left_time}次[#锻造]指令（无需加武器名）可以获得武器")


@sv.on_prefix(["#炼宝"])
async def _(bot, ev: CQEvent):
    user = await UserDao.get_ev_user(bot, ev)
    await user.check_cd(bot, ev)
    item_id = UserModelDao.get_user_counter(user.uid, UserModel.LIANBAO_ITEM)
    if item_id:
        item = ITEM_INFO[str(item_id)]
        need = LIANBAO_NEED_LINGQI[item['level']]
        have = UserModelDao.get_user_counter(user.uid, UserModel.LIANBAO_LINGQI)
        if have < need:
            await bot.finish(ev, "当前炼宝并未完成，请在完成提示之后获取")
        if not ItemDao.add_item(user.uid, item):
            await bot.finish(ev, "请先腾出一格背包空间")
        UserModelDao.save_user_counter(user.uid, UserModel.LIANBAO_ITEM, 0)
        UserModelDao.save_user_counter(user.uid, UserModel.LIANBAO_LINGQI, 0)
        user.start_cd()
        await bot.finish(ev, f"炼宝成功，获得法宝[{item['name']}]")
    if user.belong != "狮府":
        await bot.finish(ev, f"只有狮府可以炼宝！")
    msg = get_message_text(ev).split()
    msg = list(set(msg))
    if len(msg) > 3:
        await bot.finish(ev, f"至多以三件不同的装备或法宝作为底物")
    order = [i for i in LIANBAO_NEED_LINGQI.keys()]
    max_level = "凡人"
    max_level_count = 0
    for i in msg:
        item = ItemDao.get_item_by_name(i)
        if not item:
            await bot.finish(ev, f"不存在名为[{i}]的武器或法宝")
        if item['type'] not in ["武器", "法宝"]:
            await bot.finish(ev, f"不存在名为[{i}]的武器或法宝")
        if not ItemDao.check_have_item(user.uid, item):
            await bot.finish(ev, f"你背包中没有[{i}]")
        if item['type'] == 'EX':
            await bot.finish(ev, f"[{item['name']}]无法当作底物")
        if order.index(item['level']) == order.index(max_level):
            max_level_count += 1
        elif order.index(item['level']) > order.index(max_level):
            max_level = item['level']
            max_level_count = 1
    # 消耗物品 开启cd
    user.start_cd()
    for i in msg:
        item = ItemDao.get_item_by_name(i)
        ItemDao.use_item(user.uid, item)
    max_index = order.index(max_level)
    if max_level != "金仙" and user.gongfa3 == "天灵地动":
        max_index += 1
    # 最高品质不足3件
    if max_level_count < 3:
        if max_level_count == 2:
            rd = random.randint(1, 2)
            if rd == 1:
                max_index -= 1
        else:
            rd = random.randint(1, 3)
            if rd == 1:
                max_index -= 1
            elif rd == 2:
                max_index -= 2
    if max_index < 1:
        max_index = 1
    while True:
        pinzhi_get = order[max_index]
        names = filter_item_name(type=['法宝'], level=[pinzhi_get])
        if names:
            break
        else:
            max_index -= 1
    name = random.choice(names)
    fabao_item = ItemDao.get_item_by_name(name)
    UserModelDao.save_user_counter(user.uid, UserModel.LIANBAO_ITEM, int(fabao_item['id']))
    await bot.finish(ev, f"开始炼制法宝，炼制进度会随着你的行动慢慢增加，当炼制成功时会额外提醒，再次使用#炼宝指令获取，你可以使用 #注灵 灵石数量 指令来加速炼制过程")


@sv.on_prefix(["#注灵"])
async def _(bot, ev: CQEvent):
    user = await UserDao.get_ev_user(bot, ev)
    item_id = UserModelDao.get_user_counter(user.uid, UserModel.LIANBAO_ITEM)
    if not item_id:
        await bot.finish(ev, f"当前没有炼制中的法宝！")
    msg = get_message_text(ev)
    if not msg.isdecimal():
        await bot.finish(ev, f"请在 #注灵 指令后加上注入灵石的数量！")
    num = int(msg)
    have_lingshi = UserModelDao.get_user_counter(user.uid, UserModel.LINGSHI)
    if have_lingshi < num:
        await bot.finish(ev, f"你没有足够的灵石！")
    UserModelDao.add_user_counter(user.uid, UserModel.LINGSHI, -num)
    UserModelDao.add_user_counter(user.uid, UserModel.LIANBAO_LINGQI, num)
    item = ITEM_INFO[str(item_id)]
    need = LIANBAO_NEED_LINGQI[item['level']]
    have = UserModelDao.get_user_counter(user.uid, UserModel.LIANBAO_LINGQI)
    ex_msg = ""
    if have >= need:
        ex_msg = "（炼宝已经完成，请再次使用 #炼宝 指令取出）"
    await bot.finish(ev, f"注入{num}成功!{ex_msg}")


@sv.on_prefix(["#炼丹"])
async def _(bot, ev: CQEvent):
    user = await UserDao.get_ev_user(bot, ev)
    await user.check_cd(bot, ev)
    item_id = UserModelDao.get_user_counter(user.uid, UserModel.LIANDAN_ITEM)
    if item_id:
        item = ITEM_INFO[str(item_id)]
        cd = UserModelDao.get_user_counter(user.uid, UserModel.LIANDAN_CD)
        cd += 1
        danfang = DANFANG[item['name']]
        if cd >= danfang['time']:
            num = 1
            if user.gongfa3 == "药神真记":
                if random.randint(1, 5) == 1:
                    num = 2
            if not ItemDao.add_item(user.uid, item, num=num):
                await bot.finish(ev, "请先腾出一格背包空间")
            UserModelDao.save_user_counter(user.uid, UserModel.LIANDAN_CD, 0)
            UserModelDao.save_user_counter(user.uid, UserModel.LIANDAN_ITEM, 0)
            user.start_cd()
            await bot.finish(ev, f"炼丹成功，获得丹药[{item['name']}]*{num}")
        else:
            user.start_cd()
            UserModelDao.save_user_counter(user.uid, UserModel.LIANDAN_CD, cd)
            left_time = danfang['time'] - cd
            await bot.finish(ev, f"还需{left_time}次[#炼丹]指令（无需加丹药名）可以获得丹药[{item['name']}]")
    if user.belong != "百花谷":
        await bot.finish(ev, f"只有百花谷可以炼丹！")
    msg = get_message_text(ev)
    danfang = DANFANG.get(msg)
    if not danfang:
        await bot.finish(ev, f"不存在名为[{msg}]的丹方")
    # 如果立马获取的丹药是否有背包空间
    if danfang['time'] == 1:
        if not ItemDao.check_have_space(user.uid):
            await bot.finish(ev, "请先腾出一格背包空间再进行炼制")
    # 检查素材和灵石是否足够
    need_lingshi = danfang['price']
    if user.gongfa3 == "药神真记":
        need_lingshi = int(need_lingshi / 2)
    if need_lingshi > user.lingshi:
        await bot.finish(ev, f"你没有足够的灵石为丹药注灵，需要{need_lingshi}灵石")
    need_items = danfang['ex_item']
    for i in need_items:
        item = ItemDao.get_item_by_name(i)
        if not ItemDao.check_have_item(user.uid, item):
            await bot.finish(ev, f"炼制{msg}需要{i},你背包中的材料不足")
    user.start_cd()
    # 消耗灵石和材料
    for i in need_items:
        item = ItemDao.get_item_by_name(i)
        ItemDao.use_item(user.uid, item)
    UserModelDao.add_user_counter(user.uid, UserModel.LINGSHI, -need_lingshi)
    # 检查是否可以直接炼制
    get_item = ItemDao.get_item_by_name(msg)
    costmsg = f"你消耗了{need_lingshi}灵石 " + " ".join(need_items)
    if danfang['time'] == 1:
        num = 1
        if user.gongfa3 == "药神真记":
            if random.randint(1, 5) == 1:
                num = 2
        ItemDao.add_item(user.uid, get_item, num=num)
        await bot.finish(ev, f"炼丹成功，{costmsg} 获得丹药[{get_item['name']}]*{num}")
    else:
        left_time = danfang['time'] - 1
        UserModelDao.save_user_counter(user.uid, UserModel.LIANDAN_CD, 1)
        UserModelDao.save_user_counter(user.uid, UserModel.LIANDAN_ITEM, int(get_item['id']))
        await bot.finish(ev, f"{costmsg} 开始炼制{get_item['name']},还需{left_time}次[#炼丹]指令（无需加丹药名）可以获得丹药")


@sv.on_prefix(["#封印"])
async def xiulian(bot, ev: CQEvent):
    my = await UserDao.get_ev_user(bot, ev)
    if not my.gongfa3 == '封魔阵法':
        return
    name = get_message_text(ev)
    at = get_message_at(ev)
    ct = XiuXianCounter()
    if at:
        at = at[0]
        enemy = ct._get_user(at)
    else:
        enemy = ct._get_user_by_name(name)
    if not enemy:
        await bot.finish(ev, f"未找到名【{name}】的角色")
    if my.uid == enemy.uid:
        await bot.finish(ev, f"不能自己封印自己（恼）")
    await my.check_and_start_cd(bot, ev)
    if my.map != enemy.map:
        await bot.finish(ev, f"你找遍了四周也没有发现{enemy.name}的身影，或许他根本不在这里？")
    enemy = AllUserInfo(enemy)
    enemy.start_cd()
    UserModelDao.save_user_counter(my.gid, my.uid, UserModel.SHANGSHI, 2)
    await bot.finish(ev, f"你对{enemy.name}进行了封印，使其直接进入cd")


@sv.on_fullmatch(["#修养"])
async def _(bot, ev: CQEvent):
    uid = ev.user_id
    user = await UserDao.get_ev_user(bot, ev)
    shangshi = UserModelDao.get_user_counter(uid, UserModel.SHANGSHI)
    if not shangshi:
        await bot.finish(ev, f"你没有受伤，无需修养", at_sender=True)
    await user.check_cd_ignore_other(bot, ev)
    time = UserModelDao.get_user_counter(uid, UserModel.XIUYANG_TIME)
    time += 1
    user.start_cd()
    if shangshi == 3:
        need = 1
        if need - time <= 0:
            UserModelDao.save_user_counter(uid, UserModel.SHANGSHI, 2)
            UserModelDao.save_user_counter(uid, UserModel.XIUYANG_TIME, 0)
            await bot.finish(ev, f"经过修养，你的伤势转化为重伤", at_sender=True)
        else:
            UserModelDao.save_user_counter(uid, UserModel.XIUYANG_TIME, time)
            await bot.finish(ev, f"经过修养，你的伤势减轻了（还需要{need - time}次修养转为重伤）", at_sender=True)
    if shangshi == 2:
        need = 2
        if need - time <= 0:
            UserModelDao.save_user_counter(uid, UserModel.SHANGSHI, 1)
            UserModelDao.save_user_counter(uid, UserModel.XIUYANG_TIME, 0)
            await bot.finish(ev, f"经过修养，你的伤势转化为轻伤", at_sender=True)
        else:
            UserModelDao.save_user_counter(uid, UserModel.XIUYANG_TIME, time)
            await bot.finish(ev, f"经过修养，你的伤势减轻了（还需要{need - time}次修养转为轻伤）", at_sender=True)
    if shangshi == 1:
        need = 1
        if need - time <= 0:
            UserModelDao.save_user_counter(uid, UserModel.SHANGSHI, 0)
            UserModelDao.save_user_counter(uid, UserModel.XIUYANG_TIME, 0)
            await bot.finish(ev, f"经过修养，你的伤势完全恢复了", at_sender=True)
        else:
            UserModelDao.save_user_counter(uid, UserModel.XIUYANG_TIME, time)
            await bot.finish(ev, f"经过修养，你的伤势减轻了（还需要{need - time}次修养完全恢复）", at_sender=True)
