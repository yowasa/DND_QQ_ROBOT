from hoshino import Service
from hoshino import priv
from hoshino.typing import CQEvent
from .ScoreCounter import ScoreCounter2
from .duelconfig import *

sv_manor = Service('领地管理', enable_on_default=False, manage_priv=priv.SUPERUSER, bundle='领地管理', help_=
"""[领地帮助]查看相关帮助
""")

daily_manor_limiter = DailyAmountLimiter("manor", 1, RESET_HOUR)


class PolicyModel(Enum):
    BALANCE = [0, "保持原样"]
    GENG_INCREASE = [1, "开垦荒地"]
    GENG_DECREASE = [2, "退耕还林"]

    @staticmethod
    def get_by_id(id):
        for i in PolicyModel:
            if i.value[0] == id:
                return i
        return None

    @staticmethod
    def get_by_name(name):
        for i in PolicyModel:
            if i.value[1] == name:
                return i
        return None


class BuildModel(Enum):
    CENTER = {"id": 101, "name": "市政中心", "sw": 1000, "gold": 10000, "area": 10, "time": 1, "limit": 1,
              "desc": "城市管理枢纽只有拥有才能执行行政命令"}
    MARKET = {"id": 102, "name": "贸易市场", "sw": 1000, "gold": 50000, "area": 7, "time": 3, "limit": 10,
              "desc": "城市商业贸易中心，能为你带来不菲的收入（增加金币）"}
    ITEM_SHOP = {"id": 103, "name": "道具商店", "sw": 100, "gold": 10000, "area": 5, "time": 2, "limit": 1,
                 "desc": "神秘的道具商店，只能盲盒购买"}
    TV_STATION = {"id": 104, "name": "报社", "sw": 5000, "gold": 10000, "area": 8, "time": 3, "limit": 10,
                  "desc": "城市的媒体部门，能宣传你的伟业（增加声望）"}

    @staticmethod
    def get_by_id(id):
        for i in BuildModel:
            if i.value['id'] == id:
                return i
        return None

    @staticmethod
    def get_by_name(name):
        for i in BuildModel:
            if i.value['name'] == name:
                return i
        return None


@sv_manor.on_fullmatch(['领地帮助'])
async def manor_help(bot, ev: CQEvent):
    msg = '''
╔                                        ╗  
             领地系统帮助
[接受封地] 准男爵以上可以接受封地，开始管理自己的领地
[领地查询] 查询领地状态
[建筑列表] 查看城市可建设建筑列表
[建造建筑] 建造建筑
[领地结算] 领地指令结算，一天只能执行一次
[政策选择] {政策}可选政策：开垦林地，退耕还林，保持原样 结算时5%比例进行移动
[税率调整] {数值}设置领地征税比例 默认10%
==建筑指令==
[购买道具] 商店指令，花费1w金币随机买一个道具

== 维护指令 ==
[刷新结算] {qq号} 刷新结算次数

注：税收与耕地面积有关，声望与林地面积有关
领地面积为100*爵位
城市面积为领地的1/10
接受封地的第一天只能建造市政中心
初始耕地面积为10%林地为90%

╚                                        ╝
 '''
    await bot.send(ev, msg)


# 爵位等级获取领地面积
def get_all_manor(level):
    return level * 100


# 获取城市面积
def get_city_manor(level):
    return int(get_all_manor(level) * 0.1)


# 获取耕地面积
def get_geng_manor(level, geng):
    return int((get_all_manor(level) - get_city_manor(level)) * (geng / 100))


# 获取耕地税率
def get_geng_profit(gid, uid):
    return get_user_counter(gid, uid, UserModel.TAX_RATIO)


# 获取上缴税费
def get_taxes(gid, uid, level):
    return 2000 + 3000 * level


# 获取建筑情况
def get_all_build_counter(gid, uid):
    i_c = ItemCounter()
    info = i_c._get_build_info(gid, uid)
    build_num_map = {}
    for i in info:
        b_m = BuildModel.get_by_id(i[0])
        build_num_map[b_m] = i[1]
    return build_num_map


# 获取建筑情况
def check_build_counter(gid, uid, b_m: BuildModel):
    i_c = ItemCounter()
    return i_c._get_user_state(gid, uid, b_m.value['id'])


# 建造建筑
def _build_new(gid, uid, b_m: BuildModel):
    num = check_build_counter(gid, uid, b_m)
    num += 1
    i_c = ItemCounter()
    i_c._save_user_state(gid, uid, b_m.value['id'], num)


@sv_manor.on_fullmatch("接受封地")
async def manor_begin(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    # 检查是否已经开启
    if get_user_counter(gid, uid, UserModel.MANOR_BEGIN):
        await bot.finish(ev, "你已经接受了封地，无需再次领封", at_sender=True)
    # 判断是否是准男爵以上
    duel = DuelCounter()
    level = duel._get_level(gid, uid)
    if level == 0:
        msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅。'
        await bot.finish(ev, msg, at_sender=True)
    elif level < 3:
        msg = '必须达到准男爵以上才能接受封地'
        await bot.finish(ev, msg, at_sender=True)

    # 初始化耕地比例
    geng = 10
    save_user_counter(gid, uid, UserModel.GENGDI, geng)
    # 初始化治安
    zhian = 80
    save_user_counter(gid, uid, UserModel.ZHI_AN, zhian)

    # 初始化税率
    shui = 10
    save_user_counter(gid, uid, UserModel.TAX_RATIO, shui)

    all_manor = get_all_manor(level)
    city_manor = get_city_manor(level)
    geng_manor = get_geng_manor(level, geng)

    save_user_counter(gid, uid, UserModel.MANOR_BEGIN, 1)

    # 发送信息
    noblename = get_noblename(level)
    msg = f'''尊敬的{noblename}您好，您成功接受了册封，获得了封地
    领地面积{all_manor}
    城市面积{city_manor}
    耕地面积{geng_manor}
    当然治安状况{zhian}
    耕地税比例为{shui}%
    请认真维护好自己的领地
    '''.strip()
    await bot.finish(ev, msg, at_sender=True)


@sv_manor.on_fullmatch("领地查询")
async def manor_view(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    # 检查是否已经开启
    if not get_user_counter(gid, uid, UserModel.MANOR_BEGIN):
        await bot.finish(ev, "您还未接受封地", at_sender=True)

    # 获取爵位and状态计算
    duel = DuelCounter()
    level = duel._get_level(gid, uid)

    geng = get_user_counter(gid, uid, UserModel.GENGDI)
    all_manor = get_all_manor(level)
    city_manor = get_city_manor(level)
    geng_manor = get_geng_manor(level, geng)
    zhian = get_user_counter(gid, uid, UserModel.ZHI_AN)

    taxes = get_taxes(gid, uid, level)
    gold_sum = 0
    sw_sum = 0
    tax_rate = get_geng_profit(gid, uid)
    geng_gain = geng_manor * tax_rate * 10
    gold_sum += geng_gain
    # 正在建造的建筑查询
    # 建筑收益
    b_c = get_all_build_counter(gid, uid)
    b_msg = []
    total = 0
    for i in b_c.keys():
        total += i.value['area'] * b_c[i]
        b_msg.append(f"{i.value['name']}*{b_c[i]}")
        if i == BuildModel.CENTER:
            continue
        elif i == BuildModel.MARKET:
            market_gold = 20000 * b_c[i]
            gold_sum += market_gold
        elif i == BuildModel.TV_STATION:
            tv_sw = 1500 * b_c[i]
            sw_sum += tv_sw
    p_id = get_user_counter(gid, uid, UserModel.MANOR_POLICY)
    pm = PolicyModel.get_by_id(p_id)
    noblename = get_noblename(level)
    msg = f'''尊敬的{noblename}您好，您的领地状态如下:
领地面积{all_manor}
城市面积{city_manor}
建筑面积{total}
拥有{geng_manor}耕地
当然治安状况是{zhian}
领地耕地税率为{tax_rate}%
预期收入{gold_sum}金币{sw_sum}声望
预期上贡{taxes}金币
采用了{pm.value[1]}政策
拥有建筑:{" ".join(b_msg)}'''
    b_b_id = get_user_counter(gid, uid, UserModel.BUILD_BUFFER)
    if b_b_id:
        b_b = BuildModel.get_by_id(b_b_id)
        b_t = get_user_counter(gid, uid, UserModel.BUILD_CD)
        msg += f"\n当前正在建设{b_b.value['name']},还差{b_t}次结算建造完成"

    await bot.finish(ev, msg, at_sender=True)


@sv_manor.on_fullmatch("建筑列表")
async def build_view(bot, ev: CQEvent):
    msg = "==== 建筑列表 ====\n"
    for i in BuildModel:
        msg += f'''
{i.value['name']}:
花费:{i.value['gold']}金币,{i.value['sw']}声望
限制:最多拥有{i.value['limit']}个
占地面积:{i.value['area']}
建筑时间:{i.value['time']}次领地结算
描述:{i.value['desc']}\n
'''.strip() + '\n\n'
    await bot.finish(ev, msg)


@sv_manor.on_prefix("建造建筑")
async def _build(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    build_name = str(ev.message).strip()
    # 检查是否已经开启
    if not get_user_counter(gid, uid, UserModel.MANOR_BEGIN):
        await bot.finish(ev, "您还未接受封地", at_sender=True)
    if not build_name:
        await bot.finish(ev, "请使用指令 建造建筑 + 建筑名称 ", at_sender=True)
    b_id = get_user_counter(gid, uid, UserModel.BUILD_BUFFER)
    if b_id:
        bm = BuildModel.get_by_id(b_id)
        await bot.finish(ev, f"施工队正在建设{bm.value['name']},无法接受新的委托", at_sender=True)
    b_m = BuildModel.get_by_name(build_name)
    if not b_m:
        await bot.finish(ev, f"未找到名为{build_name}的建筑", at_sender=True)
    if b_m != BuildModel.CENTER and not check_build_counter(gid, uid, BuildModel.CENTER):
        await bot.finish(ev, f"没有行政中心前只能建造市政中心", at_sender=True)
    duel = DuelCounter()
    level = duel._get_level(gid, uid)
    # 检查土地大小是否够用
    build_map = get_all_build_counter(gid, uid)
    total = 0
    for i in build_map.keys():
        total += i.value['area'] * build_map[i]
    city_manor = get_city_manor(level)
    if city_manor < total + b_m.value['area']:
        await bot.finish(ev, f"当前城市面积不足以建设{build_name}", at_sender=True)
    num = check_build_counter(gid, uid, b_m)
    if num + 1 > b_m.value['limit']:
        await bot.finish(ev, f"{build_name}已经达到了可建筑上限", at_sender=True)
    s_c = ScoreCounter2()
    if s_c._get_score(gid, uid) < b_m.value["gold"]:
        await bot.finish(ev, f"你没有足够的金币进行建造", at_sender=True)
    if s_c._get_prestige(gid, uid) < b_m.value["sw"]:
        await bot.finish(ev, f"你没有足够的声望进行建造", at_sender=True)
    s_c._reduce_score(gid, uid, b_m.value["gold"])
    s_c._reduce_prestige(gid, uid, b_m.value["sw"])
    save_user_counter(gid, uid, UserModel.BUILD_BUFFER, b_m.value['id'])
    save_user_counter(gid, uid, UserModel.BUILD_CD, b_m.value['time'])
    # 增加建筑状态
    await bot.finish(ev, f"你大兴土木开始建造了{b_m.value['name']}了,预期花费{b_m.value['time']}次计算时间可以建筑完成", at_sender=True)


@sv_manor.on_fullmatch("领地结算")
async def manor_sign(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    # 检查是否已经开启
    if not get_user_counter(gid, uid, UserModel.MANOR_BEGIN):
        await bot.finish(ev, "您还未接受封地", at_sender=True)
    guid = gid, uid
    if not daily_manor_limiter.check(guid):
        await bot.finish(ev, "你今日已经进行过结算，请明日再来", at_sender=True)
    daily_manor_limiter.increase(guid)
    msg = '\n====领地结算===='
    duel = DuelCounter()
    level = duel._get_level(gid, uid)

    # == 治安结算 ==
    zhian = get_user_counter(gid, uid, UserModel.ZHI_AN)
    # 判定城市拥堵
    build_map = get_all_build_counter(gid, uid)
    total = 0
    for i in build_map.keys():
        total += i.value['area'] * build_map[i]
    city_manor = get_city_manor(level)
    if total / city_manor >= 0.8:
        reduce = random.randint(8, 15)
        zhian -= reduce
        msg += f"\n由于城市过于拥挤,居民怨声载道，治安减少了{reduce}"
    # 判定苛税乘法
    tax_rate = get_user_counter(gid, uid, UserModel.TAX_RATIO)
    if tax_rate < 10:
        add = random.randint(8, 15)
        zhian += add
        msg += f"\n人民安居乐业,生活轻松，治安增加了{add}"
    elif 30 < tax_rate < 50:
        reduce = random.randint(8, 15)
        zhian -= reduce
        msg += f"\n人民朝九晚九，一周六天，工作十分辛苦，心中怨声载道，治安减少了{reduce}"
    elif tax_rate >= 50:
        msg += f"\n人民已经厌倦了领主的暴政,治安减少了{zhian}"
        zhian = 0
    save_user_counter(gid, uid, UserModel.ZHI_AN, zhian)
    # 判定暴乱
    bao_flag = 0
    buffer_flag = 0
    if zhian < 20:
        msg += f"\n领地发生了暴乱，人民不认同你这个领主，当日没有收益"
        bao_flag = 1
    elif zhian < 50:
        rn = random.randint(20, 49)
        if zhian < rn:
            msg += f"\n人民走上街头进行罢工游行示威，拒绝工作和缴纳税款"
            bao_flag = 1
    elif zhian >= 95:
        msg += f"\n治安良好，社会稳定运行,GDP实现了高速增长"
        buffer_flag = 1
    else:
        msg += f"\n领地一片祥和，没有什么特别需要注意的事情"

    gold_sum = 0
    sw_sum = 0
    if not bao_flag:
        # 计算耕地
        geng = get_user_counter(gid, uid, UserModel.GENGDI)
        p_id = get_user_counter(gid, uid, UserModel.MANOR_POLICY)
        p_m = PolicyModel.get_by_id(p_id)
        if p_m == PolicyModel.GENG_INCREASE:
            rn = random.randint(3, 5)
            if geng + rn <= 100:
                geng += rn
            else:
                geng = 100
        if p_m == PolicyModel.GENG_DECREASE:
            rn = random.randint(3, 5)
            if geng - rn <= 0:
                geng = 0
            else:
                geng -= rn
        save_user_counter(gid, uid, UserModel.GENGDI, geng)
        sha_flag = 0
        geng_gold = 0
        if geng >= 80:
            sha_flag = 1
            msg += f"由于你大肆扩张耕地，领地内出现了黄沙天气，农民颗粒无收"

        elif geng >= 50:
            rn = random.randint(50, 79)
            if geng > rn:
                sha_flag = 1
                msg += f"由于你大肆扩张耕地，领地内出现了黄沙天气，农民颗粒无收"
        if not sha_flag:
            area_geng = get_geng_manor(level, geng)
            tax = get_user_counter(gid, uid, UserModel.TAX_RATIO)
            geng_gold = int(area_geng * tax * 10 * random.uniform(0.9, 1.1))
            msg += f"\n收取了耕地税收{geng_gold}金币"

        gold_sum += geng_gold
        # 计算建筑
        # 计算建筑进度
        cd = get_user_counter(gid, uid, UserModel.BUILD_CD)
        if cd != 0:
            cd -= 1
            if cd == 0:
                buffer_build_id = get_user_counter(gid, uid, UserModel.BUILD_BUFFER)
                build = BuildModel.get_by_id(buffer_build_id)
                _build_new(gid, uid, build)
                msg += f"\n施工队报告{build.value['name']}竣工了，已经可以投入使用"
                save_user_counter(gid, uid, UserModel.BUILD_BUFFER, 0)
            save_user_counter(gid, uid, UserModel.BUILD_CD, cd)

        b_c = get_all_build_counter(gid, uid)
        for i in b_c.keys():
            if i == BuildModel.CENTER:
                continue
            elif i == BuildModel.MARKET:
                market_gold = int(20000 * b_c[i] * random.uniform(0.9, 1.1))
                if buffer_flag:
                    market_gold = int(market_gold * 1.1)
                msg += f'\n贸易市场为你带来了额外{market_gold}金币收益'
                gold_sum += market_gold
            elif i == BuildModel.TV_STATION:
                tv_sw = int(1500 * b_c[i] * random.uniform(0.9, 1.1))
                if buffer_flag:
                    tv_sw = int(tv_sw * 1.1)
                sw_sum += tv_sw
                msg += f'\n报社为你带来了额外{tv_sw}声望'
            elif i == BuildModel.ITEM_SHOP:
                ct = b_c[i]
                save_user_counter(gid, uid, UserModel.ITEM_BUY_TIME, ct)
                msg += f'\n道具商店的物品刷新了，可以进行购买'

    # 计算上缴金额
    taxes = get_taxes(gid, uid, level)
    msg += f'\n你接受了封地，要承担相应责任，需要上缴金币{taxes}'
    gold_sum -= taxes
    score_counter = ScoreCounter2()
    score_counter._add_prestige(gid, uid, sw_sum)
    if gold_sum >= 0:
        score_counter._add_score(gid, uid, gold_sum)
    else:
        have_gold = score_counter._get_score(gid, uid)
        if have_gold + gold_sum >= 0:
            score_counter._reduce_score(gid, uid, -gold_sum)
        else:
            score_counter._reduce_score(gid, uid, have_gold)
            sw_reduce = 1000 + 400 * level
            score_counter._reduce_prestige(gid, uid, sw_reduce)
            sw_sum -= sw_reduce
            msg += f'\n由于你没有能力上供金额，被众人嘲笑，声望降低了{sw_reduce}'
    msg += f"\n结算收益为：获得了{gold_sum}金币，{sw_sum}声望。"
    await bot.send(ev, msg, at_sender=True)


@sv_manor.on_prefix("政策选择")
async def manor_policy(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if not check_build_counter(gid, uid, BuildModel.CENTER):
        await bot.finish(ev, f"没有行政中心前无法进行政策选择")
    name = str(ev.message).strip()
    if not name:
        await bot.finish(ev, f'请选择开垦荒地，退耕还林，保持原样其中一种')
    pm = PolicyModel.get_by_name(name)
    if not pm:
        await bot.finish(ev, f'没有找到名为{name}的政策，请选择开垦荒地，退耕还林，保持原样其中一种')
    save_user_counter(gid, uid, UserModel.MANOR_POLICY, pm.value[0])
    await bot.finish(ev, f'你颁布了行政法令，要求{pm.value[1]}')


@sv_manor.on_prefix("税率调整")
async def manor_tax(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if not check_build_counter(gid, uid, BuildModel.CENTER):
        await bot.finish(ev, f"没有行政中心前无法进行税率调整")
    number = str(ev.message).strip()
    if not number:
        await bot.finish(ev, f'请在指令后增加税率（30代表30%税率）')
    if not number.isdigit():
        await bot.finish(ev, f'请在指令后增加"数字"作为税率（30代表30%税率）')
    save_user_counter(gid, uid, UserModel.TAX_RATIO, number)
    await bot.finish(ev, f'你颁布了行政法令，规定耕地征税{number}%')


@sv_manor.on_prefix("购买道具")
async def buy_item(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    num = get_user_counter(gid, uid, UserModel.ITEM_BUY_TIME)
    if num <= 0:
        await bot.finish(ev, f'你的城市没有商店或已经没有购买次数，无法购买道具')
    score_counter = ScoreCounter2()
    score = score_counter._get_score(gid, uid)
    if score < 10000:
        await bot.finish(ev, f'你的金币不足1万，无法购买道具')
    num -= 1
    score_counter._reduce_score(gid, uid, 10000)
    save_user_counter(gid, uid, UserModel.ITEM_BUY_TIME, num)
    item = choose_item()
    add_item(gid, uid, item)
    await bot.finish(ev, f'你花费了1万金币购买到了{item["rank"]}级道具{item["name"]}')


@sv_manor.on_prefix("刷新结算")
async def refresh(bot, ev: CQEvent):
    gid = ev.group_id
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, f"你无权使用投放道具功能", at_sender=True)
    msg = str(ev.message).strip()
    to_id = int(msg)
    guid = gid, to_id
    daily_manor_limiter.reset(guid)
    await bot.finish(ev, f"刷新结算成功")
