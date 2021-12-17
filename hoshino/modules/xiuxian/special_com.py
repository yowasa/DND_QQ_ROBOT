from .xiuxian_config import *
from hoshino.util.utils import get_message_at, get_message_text
from .xiuxian_base import *

@sv.on_prefix(["#封印"])
async def xiulian(bot, ev: CQEvent):
    gid = ev.group_id
    my = await get_ev_user(bot, ev)
    if not my.gongfa3 == '封魔阵法':
        return
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
        await bot.finish(ev, f"不能自己封印自己（恼）")
    await my.check_and_start_cd(bot, ev)
    if my.map != enemy.map:
        await bot.finish(ev, f"你找遍了四周也没有发现{enemy.name}的身影，或许他根本不在这里？")
    enemy = AllUserInfo(enemy)
    enemy.start_cd()
    save_user_counter(my.gid, my.uid, UserModel.SHANGSHI, 2)
    await bot.finish(ev, f"你对{enemy.name}进行了封印，使其直接进入cd")


@sv.on_prefix(["#切换心法"])
async def xiulian(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    if user.gongfa3 != '左右互搏':
        return
    if user.wuxing > 20:
        await bot.finish(ev, f"你的悟性太高，无法使用左右互搏")
    await user.check_and_start_cd(bot, ev)
    id = get_user_counter(user.gid, user.uid, UserModel.ZUOYOU_XINFA)
    gongfa = '无'
    if id:
        gongfa = ITEM_INFO[str(id)]['name']
    store = 0
    if user.gongfa != '无':
        item = get_item_by_name(user.gongfa)
        store = int(item['id'])
    user.gongfa = gongfa
    ct = XiuxianCounter()
    ct._save_user_info(user)
    save_user_counter(user.gid, user.uid, UserModel.ZUOYOU_XINFA, store)
    await bot.finish(ev, f"切换心法成功，当前心法为{user.gongfa}")


@sv.on_prefix(["#切换功法"])
async def xiulian(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    if user.gongfa3 != '左右互搏':
        return
    if user.wuxing > 20:
        await bot.finish(ev, f"你的悟性太高，无法使用左右互搏")
    await user.check_and_start_cd(bot, ev)
    id = get_user_counter(user.gid, user.uid, UserModel.ZUOYOU_GONGFA)
    gongfa = '无'
    if id:
        gongfa = ITEM_INFO[str(id)]['name']
    store = 0
    if user.gongfa2 != '无':
        item = get_item_by_name(user.gongfa2)
        store = int(item['id'])
    user.gongfa2 = gongfa
    ct = XiuxianCounter()
    ct._save_user_info(user)
    save_user_counter(user.gid, user.uid, UserModel.ZUOYOU_GONGFA, store)
    await bot.finish(ev, f"切换功法成功，当前功法为{user.gongfa2}")
