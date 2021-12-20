from .xiuxian_config import *
from hoshino.util.utils import get_message_text
from .xiuxian_base import *

@sv.on_prefix(["#炼丹"])
async def shangjia(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    await user.check_cd(bot, ev)
    item_id = get_user_counter(user.gid, user.uid, UserModel.LIANDAN_ITEM)
    if item_id:
        item = ITEM_INFO[str(item_id)]
        cd = get_user_counter(user.gid, user.uid, UserModel.LIANDAN_CD)
        cd += 1
        danfang = DANFANG[item['name']]
        if cd >= danfang['time']:
            num = 1
            if user.gongfa3 == "药神真记":
                if random.randint(1, 5) == 1:
                    num = 2
            if not add_item(user.gid, user.uid, item, num=num):
                await bot.finish(ev, "请先腾出一格背包空间")
            save_user_counter(user.gid, user.uid, UserModel.LIANDAN_CD, 0)
            save_user_counter(user.gid, user.uid, UserModel.LIANDAN_ITEM, 0)
            user.start_cd()
            await bot.finish(ev, f"炼丹成功，获得丹药[{item['name']}]*{num}")
        else:
            user.start_cd()
            save_user_counter(user.gid, user.uid, UserModel.LIANDAN_CD, cd)
            left_time = danfang['time'] - cd
            await bot.finish(ev, f"还需{left_time}次[#炼丹]指令（无需加丹药名）可以获得丹药[{item['name']}]")
    if user.belong!="百花谷":
        await bot.finish(ev, f"只有百花谷可以炼丹！")
    msg = get_message_text(ev)
    danfang = DANFANG.get(msg)
    if not danfang:
        await bot.finish(ev, f"不存在名为[{msg}]的丹方")
    # 如果立马获取的丹药是否有背包空间
    if danfang['time'] == 1:
        if not check_have_space(user.gid, user.uid):
            await bot.finish(ev, "请先腾出一格背包空间再进行炼制")
    # 检查素材和灵石是否足够
    need_lingshi = danfang['price']
    if user.gongfa3 == "药神真记":
        need_lingshi = int(need_lingshi / 2)
    if need_lingshi > user.lingshi:
        await bot.finish(ev, f"你没有足够的灵石为丹药注灵，需要{need_lingshi}灵石")
    need_items = danfang['ex_item']
    for i in need_items:
        item = get_item_by_name(i)
        if not check_have_item(user.gid, user.uid, item):
            await bot.finish(ev, f"炼制{msg}需要{i},你背包中的材料不足")
    user.start_cd()
    # 消耗灵石和材料
    for i in need_items:
        item = get_item_by_name(i)
        use_item(user.gid, user.uid, item)
    add_user_counter(user.gid, user.uid, UserModel.LINGSHI, -need_lingshi)
    # 检查是否可以直接炼制
    get_item = get_item_by_name(msg)
    costmsg = f"你消耗了{need_lingshi}灵石 " + " ".join(need_items)
    if danfang['time'] == 1:
        num = 1
        if user.gongfa3 == "药神真记":
            if random.randint(1, 5) == 1:
                num = 2
        add_item(user.gid, user.uid, get_item, num=num)
        await bot.finish(ev, f"炼丹成功，{costmsg} 获得丹药[{get_item['name']}]*{num}")
    else:
        left_time = danfang['time'] - 1
        save_user_counter(user.gid, user.uid, UserModel.LIANDAN_CD, 1)
        save_user_counter(user.gid, user.uid, UserModel.LIANDAN_ITEM, int(get_item['id']))
        await bot.finish(ev, f"{costmsg} 开始炼制{get_item['name']},还需{left_time}次[#炼丹]指令（无需加丹药名）可以获得丹药")
