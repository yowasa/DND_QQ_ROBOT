from .xiuxian_config import *
from hoshino import util
import random

# 游历

EVENT_MAP = {
    "新手村": {"小试牛刀": 45, "高人指点": 30, "尊老爱幼": 5, "游山玩水": 5, "玩物丧志": 5, "一剑西来": 5, "恐怖如斯": 5},
    "大千世界": {"比武招亲": 20, "悬赏缉凶": 35, "锻炼身体": 10, "物尽其用": 5, "摸金校尉": 5, "灵猫报恩": 5, "误入洞天": 5, "红尘之伴": 5, "落难老妇": 5,
             "坐而论道": 5},
    "修仙秘境": {"指点之光": 20, "奇珍异兽": 40, "行侠仗义": 5, "灵猫报恩": 5, "无妄之灾": 5, "福地洞天": 5, "怪谈棋局": 5, "花妖向葵": 5, "求仙之伴": 5,
             "碧水寒潭": 5},
    '无尽之海': {"交谈心得": 32, "仙府机缘": 40, "黄粱一梦": 5, "剑冢遇险": 5, "名胜古景": 5, "神秘商人": 5, "比划比划": 5, "秘境之伴": 3},
    '苍穹神州': {"捕捉小兽": 52, "井中洞天": 5, "女仆咖啡": 5, "灵药风波": 5, "妙手空空": 5, "棋逢对手": 5, "沙中淘金": 5, "神秘商人": 5, "圣人传经": 5,
             "心魔历练": 5, "神州之伴": 3},
    '九天十国': {"人面兽心": 52, "沉迷赌博": 5, "黑白无常": 5, "狗头人兽": 5, "妖兽侵扰": 10, "乌云笼罩": 3, "神秘商人": 5, "水猴赠礼": 15},
    '洪荒大陆': {"无": 100},
    '诸天万界': {"无": 100},
    '灵寰福址': {"无": 100},
    '混沌绝地': {"无": 100},
    '荧惑仙境': {"无": 100},
}


@sv.on_fullmatch(["#游历"])
async def youli(bot, ev: CQEvent):
    user = await get_ev_user(bot, ev)
    await user.check_and_start_cd(bot, ev)
    all_li = EVENT_MAP[user.map]
    rn = random.randint(1, 100)
    total = 0
    msg = ""
    for i in all_li.keys():
        total += all_li[i]
        if rn <= total:
            msg = i
            break
    result = await _youli(msg, user, bot, ev)
    await bot.send(ev, result, at_sender=True)


register = dict()


async def _youli(name, user, bot, ev):
    func = register.get(name)
    if func:
        return await func(user, bot, ev)
    return "游历未实装"


# 注解msg 传入正则表达式进行匹配
def msg_route(item_name):
    def show(func):
        async def warpper(user, bot, ev: CQEvent):
            return await func(user, bot, ev)

        register[item_name] = warpper
        return warpper

    return show


@msg_route("无")
async def wu(user, bot, ev: CQEvent):
    return f"这里人数太少,无法游历。"


@msg_route("小试牛刀")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    user.exp += 5
    ct._save_user_info(user)
    return f"帮助村民击退了附近的野兽，获取5点经验"


@msg_route("高人指点")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    user.skill += 1
    ct._save_user_info(user)
    return f"在村口看到高人打出闪电五连鞭，心有所悟，获取1点战斗技巧。"


@msg_route("尊老爱幼")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    add_user_counter(user.gid, user.uid, UserModel.KILL, num=-1)
    return f"你（强行）扶老奶奶过马路，一时名声大噪，名声提高了"


@msg_route("游山玩水")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ex_msg = ""
    if not add_item(user.gid, user.uid, get_item_by_name("玄牝珠")):
        ex_msg = "(背包已满,只得丢弃)"
    return f"水光洌艳晴方好，山色空门雨亦奇，大自然鬼斧神工，令你心中澎湃不已，在这里发现了一个玄牝珠{ex_msg}"


@msg_route("玩物丧志")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    get_wuxing = 1
    if user.wuxing < 10:
        get_wuxing = 0
    user.wuxing -= get_wuxing
    ct._save_user_info(user)
    return f"游商为村子带来一种名为麻将的游戏，你沉迷其中无法自拔，“断幺九，一番，1000点”，悟性-{get_wuxing}"


@msg_route("一剑西来")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    get_num = 1
    if user.daohang > 100:
        get_num = 0
    user.daohang += get_num
    ct._save_user_info(user)
    return f"你看见有人御剑飞过，心里充满了向往，“嗟乎，大丈夫生当如此”，道心更加坚定了。"


@msg_route("恐怖如斯")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    get_num = 1
    if user.daohang < 1:
        get_num = 0
    user.daohang -= get_num
    ct._save_user_info(user)
    return f"你看到一群人围殴一位单灵根天才，从村东头打到村西头，不禁感叹道修仙界恐怖如斯，道心降低了。"


@msg_route("比武招亲")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    get_num = random.randint(5, 10)
    user.exp += get_num
    ct._save_user_info(user)
    return f"你参加了一场比武招亲，抱得美人归。——“每出一个新电视剧，女人就会换一个道侣，男人就不一样，男人只会——多一个”，增加{get_num}点经验"


@msg_route("悬赏缉凶")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    get_num = random.randint(10, 15)
    add_user_counter(user.gid, user.uid, UserModel.LINGSHI, num=get_num)
    return f"帮助官府追捕逃犯，获得了一些报酬+{get_num}灵石"


@msg_route("锻炼身体")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    get_num = random.randint(1, 3)
    user.skill += get_num
    ct._save_user_info(user)
    return f"在屋里对着剑谱练剑，你的战斗技巧略微提升了 获取{get_num}点战斗技巧"


@msg_route("物尽其用")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ex_msg = ""
    if not add_item(user.gid, user.uid, get_item_by_name("朱果")):
        ex_msg = "(背包已满,只得丢弃)"
    return f"你把松鼠收藏的灵果一扫而空，气愤的小松鼠追了你十八里地，你获得了朱果{ex_msg}"


@msg_route("摸金校尉")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ex_msg = ""
    if not add_item(user.gid, user.uid, get_item_by_name("悟道丸")):
        ex_msg = "(背包已满,只得丢弃)"
    return f"你跋山涉水终于找到藏宝图所示地点，挖开后发现了精美的盒子，获得了[悟道丸]{ex_msg}"


@msg_route("灵猫报恩")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    equip_li = filter_item_name(type=['武器'], level=['凡人', '锻体'])
    equip_name = random.choice(equip_li)
    ex_msg = ""
    if not add_item(user.gid, user.uid, get_item_by_name(equip_name)):
        ex_msg = "(背包已满,只得丢弃)"
    return f"你捡来的小猫不知从哪里叼来一把武器，“据说猫的修行有三个阶段，猫在变、猫在练、猫报恩”，获得{equip_name}{ex_msg}"


@msg_route("坐而论道")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    msg = "你游历在外忽见一名风度翩翩的白衣公子在抚琴清唱，吸引来了众多灵珍异兽，你在好奇之余发现对方停下了奏乐并朝你招手，他发现你也是一名修仙者并邀请你与之论道,"
    if user.wuxing < 50:
        get_num = random.randint(1, 5)
        user.wuxing += get_num
        msg += f"你修行上的困惑得到了解答，忽感一阵明悟，回过神来身边已无一人，悟性+{get_num}"
        ct = XiuxianCounter()
        ct._save_user_info(user)
    else:
        equip_li = filter_item_name(type=['心法', '功法', '神通'], level=['凡人', '锻体', '练气'])
        equip_name = random.choice(equip_li)
        ex_msg = ""
        if not add_item(user.gid, user.uid, get_item_by_name(equip_name)):
            ex_msg = "(背包已满,只得丢弃)"
        msg += f"你高谈阔论与这位白衣公子相谈甚欢，忽感一阵明悟回过神来身边已无一人,获得{equip_name}{ex_msg}"
    return msg


@msg_route("碧水寒潭")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    msg = "你偶然进入一处异境，这里冰天雪地但有一处潭水仍泛着碧波，你观察了一下发现潭水下泛着异光，你决定潜下去一探究竟..."
    if user.tizhi < 100 or user.battle_defen2 < 20:
        msg += "由于你无法忍受这渗骨的寒气，你不得不退出此处."
    else:
        equip_li = filter_item_name(type=['法宝'], level=['凡人', '锻体', '练气'])
        equip_name = random.choice(equip_li)
        ex_msg = ""
        if not add_item(user.gid, user.uid, get_item_by_name(equip_name)):
            ex_msg = "(背包已满,只得丢弃)"
        msg += f"你潜水到潭底深处，发现果然有异宝在此！获得{equip_name}{ex_msg}"
    return msg


@msg_route("误入洞天")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    item = get_item_by_name("筑基丹")
    if check_have_item(user.gid, user.uid, item):
        item = get_item_by_name("淬骨丹")
    ex_msg = ""
    if not add_item(user.gid, user.uid, item):
        ex_msg = "(背包已满,只得丢弃)"
    return f"你误入一处洞天，一位身着围裙，头戴蜜桃黑帽，养着一头水蓝色长发的翘臀女子发现了你，邀请你和她进行一场弹幕游戏，并在你临走时送了一份礼物。你得到了{item['name']}{ex_msg}"


@msg_route("红尘之伴")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    item = get_item_by_name("淬骨丹")
    ex_msg = ""
    if not add_item(user.gid, user.uid, item):
        ex_msg = "(背包已满,只得丢弃)"
    save_user_counter(user.gid, user.uid, UserModel.HONGCHEN, 1)
    return f"一名身穿沉重盔甲的武者不小心掉进了一口井，你帮助他从井里上来，他为了感谢你，送了你一颗丹药，并希望接下来的旅途多多关照，获得了道具{item['name']}{ex_msg}"


@msg_route("指点之光")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    get_num = random.randint(10, 20)
    user.exp += get_num
    ct._save_user_info(user)
    return f"你独自练功被某气功师看见，他告诉你“你应该这么打”，获取{get_num}点经验"


@msg_route("奇珍异兽")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    get_num = random.randint(15, 25)
    add_user_counter(user.gid, user.uid, UserModel.LINGSHI, num=get_num)
    return f"你帮助亮真人照顾他的灵兽“水猴子”，得到一些酬劳。获取{get_num}灵石"


@msg_route("行侠仗义")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    get_num = random.randint(1, 3)
    user.skill += get_num
    ct._save_user_info(user)
    return f"遇到一窝贼寇正在抢劫他人，单枪匹马将对方打的落花流水，战斗技巧+{get_num}"


@msg_route("狗头人兽")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    equip_li = filter_item_name(type=['武器'], level=['锻体', '练气'])
    equip_name = random.choice(equip_li)
    ex_msg = ""
    if not add_item(user.gid, user.uid, get_item_by_name(equip_name)):
        ex_msg = "(背包已满,只得丢弃)"
    return f"你在野外的一间废弃书院门口遇到了一只人模狗样，系着红色围脖的妖兽，妖兽见你之后，发出一声怪叫便逃走了，“Rua” ，并落下了一件它的宝贝，获得{equip_name}{ex_msg}"


@msg_route("无妄之灾")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    get_num = random.randint(1, 2)
    if user.hp < 60:
        get_num = 0
    user.hp -= get_num
    ct._save_user_info(user)
    return f"两位大能为求突破，决一死战杀生证道，你不幸被卷入其中，受了内伤，“看热闹不能离太近”，HP属性降低{get_num}点。"


@msg_route("福地洞天")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    get_num = random.randint(1, 4)
    if user.daohang > 100:
        get_num = 0
    user.daohang += get_num
    ct._save_user_info(user)
    return f"找到一处灵力充沛的地点便在此修炼。增加{get_num}道心"


@msg_route("怪谈棋局")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    rd = random.randint(1, 2)
    msg = ""
    if rd == 1:
        item = get_item_by_name("赤血丹")
        result = add_item(user.gid, user.uid, item)
        msg += f"棋局胜利，你旗胜一招，赢得了棋局，抬起头来却发现对方已不见了踪影，周围的浓雾也已然散去只留下座位上的一个布袋,获得了道具{item['name']}"
        if not result:
            msg += "(背包已满,只得丢弃)"
    else:
        msg += f"棋局失败，你棋差一招，输掉了棋局，对方发出悠长的笑声，何周围的浓雾一同消散。"
    return f"你在山中庭间休息时，突然浓雾弥漫，一名用斗笠遮挡面容，声音嘶哑的人走来向你搭话，邀你来下一局棋。{msg}"


@msg_route("花妖向葵")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ex_msg = ""
    if not add_item(user.gid, user.uid, get_item_by_name("赭黄精")):
        ex_msg = "(背包已满,只得丢弃)"
    return f"你路过一处花田时，花丛中一朵向阳花突然化身为人，她向你露出微笑，并留下了一颗丹药作为礼物获得了道具赭黄精{ex_msg}"


@msg_route("求仙之伴")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    item = get_item_by_name("淬骨丹")
    if get_user_counter(user.gid, user.uid, UserModel.HONGCHEN):
        item = get_item_by_name("合气丹")
    ex_msg = ""
    if not add_item(user.gid, user.uid, item):
        ex_msg = "(背包已满,只得丢弃)"
    save_user_counter(user.gid, user.uid, UserModel.QIUXIAN, 1)
    return f"一名身穿沉重盔甲的武者在与一头凶恶的邪兽战斗，你帮助了武者，两人合伙击退了邪兽，他为了感谢你，送了你一颗丹药，并希望接下来的旅途多多关照,获得了道具{item['name']}{ex_msg}"


@msg_route("交谈心得")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    get_num = random.randint(15, 25)
    user.exp += get_num
    ct._save_user_info(user)
    return f"遇到兴趣相通的道友促膝长谈获得一些功法心得经验，增加{get_num}点经验"


@msg_route("仙府机缘")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    rd = random.randint(1, 100)
    if rd <= 20:
        names = filter_item_name(type=["武器", "功法", "法宝", "材料", "符咒"], level=['凡人', '锻体', '练气'])
        name = random.choice(names)
    else:
        get_num = random.randint(20, 40)
        add_user_counter(user.gid, user.uid, UserModel.LINGSHI, get_num)
        return f"发现陨落的高人洞府 发现有所遗留，获取{get_num}灵石"
    item = get_item_by_name(name)
    ex_msg = ""
    if not add_item(user.gid, user.uid, item):
        ex_msg = "(背包已满,只得丢弃)"
    return f"发现陨落的高人洞府 发现有所遗留，获取道具{item['name']}{ex_msg}"


@msg_route("黄粱一梦")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    rd = random.randint(1, 4)
    if rd == 1:
        get_num = random.randint(1, 3)
        if user.act > 100:
            get_num = 0
        user.act += get_num
        ex_msg = f"增加了{get_num}点物理攻击力"
    elif rd == 1:
        get_num = random.randint(1, 3)
        if user.act2 > 100:
            get_num = 0
        user.act2 += get_num
        ex_msg = f"增加了{get_num}点术法攻击力"
    elif rd == 3:
        get_num = 1
        if user.defen > 40:
            get_num = 0
        user.defen += get_num
        ex_msg = f"增加了{get_num}点物理防御力"
    else:
        get_num = 1
        if user.defen2 > 40:
            get_num = 0
        user.defen2 += get_num
        ex_msg = f"增加了{get_num}点术法防御力"
    return f"你睡觉做了个梦，尝尽轮回喜怒悲哀后醒来感悟颇多，{ex_msg}"


@msg_route("剑冢遇险")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ex_msg = ""
    if not add_item(user.gid, user.uid, get_item_by_name("琅琊果")):
        ex_msg = "(背包已满,只得丢弃)"
    save_user_counter(user.gid, user.uid, UserModel.SHANGSHI, 1)
    return f"与人探索一个剑冢，不小心失散且触发了禁制！大量机关傀儡禁制被触发拼命逃出，逃出之时发现路边一处暗室有宝物气息，为取宝物耽搁了时间，身受轻伤，获得琅邪果{ex_msg}"


@msg_route("名胜古景")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    get_num = random.randint(1, 3)
    user.skill += get_num
    ct._save_user_info(user)
    return f"路上看到古色古香的建筑，进去发现里面有一副战斗的壁画。你感悟到一些东西，战斗技巧+{get_num}"


@msg_route("神秘商人")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    lingshi = get_user_counter(user.gid, user.uid, UserModel.LINGSHI)
    rd = random.randint(100, 300)
    if count_item(user.gid, user.uid) >= get_max_count(user.gid, user.uid):
        return f"偶遇一个神秘怪人，向你兜售一件神秘物品，但是你背包已经没用空间了，只得罢了。"
    if lingshi < rd:
        return f"偶遇一个神秘怪人，向你兜售一件神秘物品，一番讨价还价之后开价{rd}灵石，但是你没有这么多灵石，只得罢了。"
    left = lingshi - rd
    save_user_counter(user.gid, user.uid, UserModel.LINGSHI, left)
    names = filter_item_name(type=['心法', '功法', '神通', '材料', '符咒'], level=['凡人', '锻体', '练气', '筑基', '结丹', '金丹'])
    name = random.choice(names)
    item = get_item_by_name(name)
    ex_msg = ""
    if not add_item(user.gid, user.uid, item):
        ex_msg = "(背包已满,只得丢弃)"
    return f"偶遇一个神秘怪人，向你兜售一件神秘物品，一番讨价还价之后你花费{rd}灵石，获取道具{item['name']}{ex_msg}"


@msg_route("比划比划")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    item = get_item_by_name("瞬息万里符")
    ex_msg = ""
    if not add_item(user.gid, user.uid, item):
        ex_msg = "(背包已满,只得丢弃)"
    return f"两位筑基老怪“比划比划”之后留下的遗物，渡鸦：“咱俩比划比划”，无爱：“来”。获得一张［瞬息万里符］{ex_msg}"


@msg_route("秘境之伴")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    item = get_item_by_name("淬骨丹")
    if get_user_counter(user.gid, user.uid, UserModel.QIUXIAN):
        item = get_item_by_name("纯阳丹")
    ex_msg = ""
    if not add_item(user.gid, user.uid, item):
        ex_msg = "(背包已满,只得丢弃)"
    save_user_counter(user.gid, user.uid, UserModel.MIJING, 1)
    return f"一名身穿沉重盔甲的武者在一处遗迹前解密，百思不得其解，你帮助了他，两人一起破除了遗迹的秘密，他为了感谢你，与你分享了遗迹里的宝物，并希望接下来的旅途多多关照,获得了道具{item['name']}{ex_msg}"


@msg_route("捕捉小兽")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    msg = "接取市集悬赏抓捕金纹狐一只,"
    rd = random.randint(1, 10)
    if rd <= 4:
        get_exp = random.randint(25, 30)
        user.exp += get_exp
        ct = XiuxianCounter()
        ct._save_user_info(user)
        msg += f"用了些小手段终于抓住这只狡猾的小动物,但是准备交给市集的时候发现只剩一个被咬坏的笼子.经验增加{get_exp}"
    elif rd <= 8:
        get_lingshi = random.randint(30, 60)
        add_user_counter(user.gid, user.uid, UserModel.LINGSHI, get_lingshi)
        msg += f"交给了市集获取到一笔灵石,灵石+{get_lingshi}"
    else:
        msg += "你找了很久也没有看到小狐的踪迹，毫无收获的回来"
    return msg


@msg_route("女仆咖啡")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    get_num = 1
    if user.act > 180:
        get_num = 0
    user.act += get_num
    ct._save_user_info(user)
    return f"在女仆咖啡厅吃饭的给女仆打赏出手大方，女仆给你了些杀必死（增加{get_num}点物理攻击力）"


@msg_route("灵药风波")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    get_num = random.randint(1, 3)
    if user.hp > 500:
        get_num = 0
    user.hp -= get_num
    ct._save_user_info(user)
    return f"出门遇见两波人马抢夺灵药，两波人大打出手，你趁乱将灵药偷走.（hp+{get_num}点）"


@msg_route("妙手空空")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    lingshi = get_user_counter(user.gid, user.uid, UserModel.LINGSHI)
    get_num = 20
    if lingshi < 20:
        get_num = lingshi
    add_user_counter(user.gid, user.uid, UserModel.LINGSHI, num=-get_num)

    return f"你在路上被人撞到,回去后身上一些灵石被顺走，并留下一个画着鬼脸的纸条，你的拳头硬了（灵石-{get_num}）"


@msg_route("落难老妇")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    lingshi = get_user_counter(user.gid, user.uid, UserModel.LINGSHI)
    get_num = 10
    if lingshi < 10:
        get_num = lingshi
    add_user_counter(user.gid, user.uid, UserModel.LINGSHI, num=-get_num)

    return f"你见到一名老妇人不慎摔倒在地，你好心将其扶起，却被她诬告是你撞到的她，在众人围观之下你不得不掏出灵石破财挡债（灵石-{get_num}）"


@msg_route("棋逢对手")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    get_num = random.randint(1, 3)
    user.skill += get_num
    ct._save_user_info(user)
    return f"遇到旗鼓相当的对手，友好切磋了一番。战斗技巧+{get_num}"


@msg_route("沙中淘金")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    lingshi = get_user_counter(user.gid, user.uid, UserModel.LINGSHI)
    if count_item(user.gid, user.uid) >= get_max_count(user.gid, user.uid):
        return f"你在黑市闲逛，路过一个邋遢男人摊前无意间发现一件被埋没的灵宝，但是你背包已经没用空间了，只得罢了。"
    if lingshi < 50:
        return f"你在黑市闲逛，路过一个邋遢男人摊前无意间发现一件被埋没的灵宝，但是你身上连20灵石也拿不出来，只得罢了。"
    left = lingshi - 50
    save_user_counter(user.gid, user.uid, UserModel.LINGSHI, left)
    names = filter_item_name(type=['武器', '法宝'], level=['凡人', '锻体', '练气'])
    name = random.choice(names)
    item = get_item_by_name(name)
    ex_msg = ""
    if not add_item(user.gid, user.uid, item):
        ex_msg = "(背包已满,只得丢弃)"
    return f"你在黑市闲逛，路过一个邋遢男人摊前无意间发现一件被埋没的灵宝,你以十分低廉的价格从男人手中获取，灵石-50，获取道具{item['name']}{ex_msg}"


@msg_route("圣人传经")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    get_num = random.randint(1, 3)
    if user.act > 200:
        get_num = 0
    user.act2 += get_num
    ct._save_user_info(user)
    return f"你偶然遇见一个大能在开坛演法,增加了{get_num}点术法攻击力"


@msg_route("心魔历练")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    ct = XiuxianCounter()
    rd = random.randint(1, 2)
    get_num = 1 if rd == 1 else -1
    user.act += get_num
    ct._save_user_info(user)
    return f"打坐时遇到心魔入侵（道心增加{get_num}点）"


@msg_route("神州之伴")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    item = get_item_by_name("淬骨丹")
    if get_user_counter(user.gid, user.uid, UserModel.HONGCHEN) and get_user_counter(user.gid, user.uid,
                                                                                     UserModel.QIUXIAN) and get_user_counter(
        user.gid, user.uid, UserModel.MIJING) and not get_user_counter(user.gid, user.uid, UserModel.SHENZHOU):
        item = get_item_by_name("风束者")
    ex_msg = ""
    if not add_item(user.gid, user.uid, item):
        ex_msg = "(背包已满,只得丢弃)"
    save_user_counter(user.gid, user.uid, UserModel.SHENZHOU, 1)
    return f"你探索到了一处神秘的地下古城，在那里，一名身穿沉重盔甲的武者正在与一位身形巨大的巨人展开厮杀，你帮助了他，两人一起击败了巨人，武者与你共享美酒，并赠予你了礼物，感谢一路的旅途，“赞美太阳！”,获得了道具{item['name']}{ex_msg}"


@msg_route("井中洞天")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    item = get_item_by_name("木枯藤")
    ex_msg = ""
    if not add_item(user.gid, user.uid, item):
        ex_msg = "(背包已满,只得丢弃)"
    return f"这口井里面散发着强大而又邪恶的气息，进入探索后获得道具{item['name']}{ex_msg}"


@msg_route("人面兽心")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    rd = random.randint(1, 100)
    msg = '在城里寻找机缘时发现一个鬼鬼祟祟的人，发现是一个邪道魔修，与之交战,'
    if rd <= 40:
        get_exp = random.randint(25, 30)
        user.exp += get_exp
        ct = XiuxianCounter()
        ct._save_user_info(user)
        add_user_counter(user.gid, user.uid, UserModel.LINGSHI, num=20)
        msg += f"他一个大意没有闪，你抓住此破绽击杀了他，并得到一些物品（20灵石 +{get_exp}经验）"
    elif rd <= 90:
        get_lingshi = random.randint(40, 70)
        add_user_counter(user.gid, user.uid, UserModel.LINGSHI, num=get_lingshi)
        ex_msg = ""
        if not add_item(user.gid, user.uid, get_item_by_name("淬骨丹")):
            ex_msg = "(背包已满,只得丢弃)"
        msg += f"此人颇有些手段，及时赶来的其他道友将其拿下（+{get_lingshi}灵石）得到物品淬骨丹{ex_msg}"
    else:
        save_user_counter(user.gid, user.uid, UserModel.SHANGSHI, 1)
        msg += "诡异的攻击和身法让你防不胜防，不小心被他打伤并让他遁走了(变为轻伤)"
    return msg


@msg_route("沉迷赌博")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    get_wuxing = random.randint(1, 2)
    get_hp = random.randint(1, 5)
    if user.wuxing < 10:
        get_wuxing = 0
    if user.hp > 900:
        get_hp = 0
    user.wuxing -= get_wuxing
    user.hp += get_hp
    ct = XiuxianCounter()
    ct._save_user_info(user)
    return f"在金碧辉煌赌坊里纸醉金迷，出来时已是夜深。悟性降低{get_wuxing}点 血量提高{get_hp}点"


@msg_route("黑白无常")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    rd = random.randint(0, 1)
    msg = "误入一个秘境，在通过一扇门时，突然有一黑一白两人出现在面前你选择先下手为强，"
    if rd:
        save_user_counter(user.gid, user.uid, UserModel.SHANGSHI, 2)
        msg += "只听到这长江天险后，便是江东铁壁后便被此人击成重伤，不得已逃跑。"
    else:
        save_user_counter(user.gid, user.uid, UserModel.SHANGSHI, 2)
        counter = ItemCounter()
        items = counter._get_item(user.gid, user.uid)
        total_count = 0
        item_li = []
        for i in items:
            item_li += [i[0]] * i[1]
            total_count += i[1]
        if item_li:
            item_id = random.choice(item_li)
            item = ITEM_INFO[str(item_id)]
            use_item(user.gid, user.uid, item)
            ex_msg = f"丢失了物品{item['name']}"
        msg += f"你只听到一声劫敌迎战，措手不及之后便被击伤，只能暂且退让，退走后发现身上少了一件东西（轻伤，{ex_msg}）"
    return msg


@msg_route("妖兽侵扰")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    rd = random.randint(1, 10)
    if rd <= 6:
        name = "凡铁"
    elif rd <= 9:
        name = "精铁"
    else:
        name = "玄铁"
    item = get_item_by_name(name)
    ex_msg = ""
    if not add_item(user.gid, user.uid, item):
        ex_msg = "(背包已满,只得丢弃)"
    return f"此城的一位长老拜托你调查附近边界的妖兽活跃问题。清理了附近的兽群并得到了一块{name}{ex_msg}"


@msg_route("乌云笼罩")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    msg = "一股恶风突然兴起，各路大能杀生证道夺取那晋级的一线机缘。许些时间过后，漂浮在修仙界的乌云已经消逝，看其模样，也许不期还会卷土从来，此处战斗的痕迹证明着今日的惨痛损失。"
    rd = random.randint(1, 100)
    if rd <= 40:
        name = filter_item_name(type=['武器'], level=['金丹'])
        if not add_item(user.gid, user.uid, get_item_by_name(name)):
            ex_msg = "(背包已满,只得丢弃)"
        msg += f"你过去捡漏发现了无爱之遗,获得了{name}{ex_msg}"
    elif rd <= 80:
        name = "合气丹"
        if not add_item(user.gid, user.uid, get_item_by_name(name)):
            ex_msg = "(背包已满,只得丢弃)"
        msg += f"你过去捡漏发现了地灵殿主之遗,获得了{name}{ex_msg}"
    else:
        name = "瞬息万里符"
        if not add_item(user.gid, user.uid, get_item_by_name(name)):
            ex_msg = "(背包已满,只得丢弃)"
        msg += f"你过去捡漏发现了不卷上人之遗,获得了{name}{ex_msg}"
    return msg


@msg_route("水猴赠礼")
async def qiecuo(user: AllUserInfo, bot, ev: CQEvent):
    item = get_item_by_name("水猴子的感恩礼盒")
    ex_msg = ""
    if not add_item(user.gid, user.uid, item):
        ex_msg = "(背包已满,只得丢弃)"
    return f"因为你曾经对水猴子的悉心照料，水猴子送给了你一份礼物，获得【水猴子的感恩礼盒】一份（来自水猴子的礼物，不知道里面有什么，消耗50灵石打开）{ex_msg}"
