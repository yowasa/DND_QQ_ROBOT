from .xiuxian_config import *
from hoshino.util.utils import get_message_text
from .xiuxian_base import *

@sv.on_prefix(["#炼宝"])
async def shangjia(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    await user.check_cd(bot, ev)
    item_id = get_user_counter(user.gid, user.uid, UserModel.LIANBAO_ITEM)
    if item_id:
        item = ITEM_INFO[str(item_id)]
        need = LIANBAO_NEED_LINGQI[item['level']]
        have = get_user_counter(user.gid, user.uid, UserModel.LIANBAO_LINGQI)
        if have < need:
            await bot.finish(ev, "当前炼宝并未完成，请在完成提示之后获取")
        if not add_item(user.gid, user.uid, item):
            await bot.finish(ev, "请先腾出一格背包空间")
        save_user_counter(user.gid, user.uid, UserModel.LIANBAO_ITEM, 0)
        save_user_counter(user.gid, user.uid, UserModel.LIANBAO_LINGQI, 0)
        user.start_cd()
        await bot.finish(ev, f"炼宝成功，获得法宝[{item['name']}]")
    if user.belong!="狮府":
        await bot.finish(ev, f"只有狮府可以炼宝！")
    msg = get_message_text(ev).split()
    msg = list(set(msg))
    if len(msg) > 3:
        await bot.finish(ev, f"至多以三件不同的装备或法宝作为底物")
    order = [i for i in LIANBAO_NEED_LINGQI.keys()]
    max_level = "凡人"
    max_level_count = 0
    for i in msg:
        item = get_item_by_name(i)
        if not item:
            await bot.finish(ev, f"不存在名为[{i}]的武器或法宝")
        if item['type'] not in ["武器", "法宝"]:
            await bot.finish(ev, f"不存在名为[{i}]的武器或法宝")
        if not check_have_item(user.gid, user.uid, item):
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
        item = get_item_by_name(i)
        use_item(user.gid, user.uid, item)
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
    fabao_item = get_item_by_name(name)
    save_user_counter(user.gid, user.uid, UserModel.LIANBAO_ITEM, int(fabao_item['id']))
    await bot.finish(ev, f"开始炼制法宝，炼制进度会随着你的行动慢慢增加，当炼制成功时会额外提醒，再次使用#练宝指令获取，你可以使用 #注灵 灵石数量 指令来加速炼制过程")


@sv.on_prefix(["#注灵"])
async def shangjia(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    item_id = get_user_counter(user.gid, user.uid, UserModel.LIANBAO_ITEM)
    if not item_id:
        await bot.finish(ev, f"当前没有炼制中的法宝！")
    msg = get_message_text(ev)
    if not msg.isdecimal():
        await bot.finish(ev, f"请在 #注灵 指令后加上注入灵石的数量！")
    num = int(msg)
    have_lingshi = get_user_counter(user.gid, user.uid, UserModel.LINGSHI)
    if have_lingshi < num:
        await bot.finish(ev, f"你没有足够的灵石！")
    add_user_counter(user.gid, user.uid, UserModel.LINGSHI, -num)
    add_user_counter(user.gid, user.uid, UserModel.LIANBAO_LINGQI, num)
    item = ITEM_INFO[str(item_id)]
    need = LIANBAO_NEED_LINGQI[item['level']]
    have = get_user_counter(user.gid, user.uid, UserModel.LIANBAO_LINGQI)
    ex_msg = ""
    if have >= need:
        ex_msg = "（练宝已经完成，请再次使用 #练宝 指令取出）"
    await bot.finish(ev, f"注入{num}成功!{ex_msg}")
