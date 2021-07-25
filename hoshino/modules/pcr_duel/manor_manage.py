from hoshino import priv
from hoshino.typing import CQEvent
from . import sv
from .ScoreCounter import ScoreCounter2
from .duelconfig import *


class PolicyModel(Enum):
    BALANCE = [0, "保持原样", "保持领地现有的发展情况"]
    GENG_INCREASE = [1, "开垦荒地", "增加领地的耕地面积"]
    GENG_DECREASE = [2, "退耕还林", "增加领地的林地面积"]
    STRONG_BUILD = [3, "加强建设", "消耗50点繁荣度，结算时建造进度额外增加一次结算,繁荣度不足则不会生效"]
    STRONG_TEC = [4, "加强科研", "消耗50点繁荣度，结算时科研进度额外增加一次结算,繁荣度不足则不会生效"]
    CATCH_ALL_FISH = [5, "竭泽而渔", "消耗30点繁荣度，结算时耕地收益增加50%,繁荣度不足则不会生效"]
    AGRICULTURAL_SUBSIDIES = [6, "农业补贴", "增加10点繁荣度，结算时耕地收益减少50%"]
    POVERTY_ALLEVIATION_POLICIES = [7, "扶贫政策", "放弃耕地收益，额外支付领地面积*100的金币，增加20点繁荣度"]

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


@sv.on_fullmatch(['领地帮助'])
async def manor_help(bot, ev: CQEvent):
    msg = '''
╔                                        ╗  
             领地系统帮助
[接受封地] 准男爵以上可以接受封地，开始管理自己的领地
[领地查询] 查询领地状态
[建筑列表] 查看城市可建设建筑列表
[建造建筑] {建筑名称} 建造建筑
[拆除建筑] {建筑名称} 拆除建筑
[领地结算] 领地指令结算，一天只能执行一次
[政策选择] {政策} 设置领地政策，不再次设置则会一直采用当前政策
[政策列表] 查看可选择的政策及效果
[税率调整] {数值}设置领地征税比例 默认10%
==建筑指令==
[购买道具] 道具商店指令，花费1w金币随机买一个道具
[装备熔炼] {熔炼等级} 装备工坊指令，使用4个低等级装备熔炼一个更高等级的装备 等级越高失败率越高
[科技列表] 科技研究所指令，查看科技列表级效果
[我的科技] 科技研究所指令，查看自己已经研发的科技成果
[科技研发] 科技研究所指令，研发新科技


注：税收与耕地面积有关，但耕地太多可能会有负面影响
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
def get_city_manor(gid, uid, level):
    if check_technolog_counter(gid, uid, TechnologyModel.SATELLITE_CITY):
        return int(get_all_manor(level) * 0.125)
    return int(get_all_manor(level) * 0.1)


# 获取耕地面积
def get_geng_manor(gid, uid, level, geng):
    return int((get_all_manor(level) - get_city_manor(gid, uid, level)) * (geng / 100))


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


@sv.on_fullmatch(['接受封地', '开启领地'])
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
    city_manor = get_city_manor(gid, uid, level)
    geng_manor = get_geng_manor(gid, uid, level, geng)

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


@sv.on_fullmatch(["领地查询", "查询领地", "我的领地"])
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
    city_manor = get_city_manor(gid, uid, level)
    geng_manor = get_geng_manor(gid, uid, level, geng)
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
        elif i == BuildModel.HUANBAO:
            area_geng = get_geng_manor(gid, uid, level, geng)
            area_city = get_city_manor(gid, uid, level)
            area_all = get_all_manor(level)
            lin = area_all - area_geng - area_city
            get_sw = lin * 5
            sw_sum += get_sw
    p_id = get_user_counter(gid, uid, UserModel.MANOR_POLICY)
    pm = PolicyModel.get_by_id(p_id)
    noblename = get_noblename(level)
    now_fanrong = get_user_counter(gid, uid, UserModel.PROSPERITY_INDEX)
    msg = f'''尊敬的{noblename}您好，您的领地状态如下:
繁荣度为{now_fanrong}
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
    t_b_id = get_user_counter(gid, uid, UserModel.TECHNOLOGY_BUFFER)
    if t_b_id:
        t_b = TechnologyModel.get_by_id(t_b_id)
        t_t = get_user_counter(gid, uid, UserModel.TECHNOLOGY_CD)
        msg += f"\n当前正在研发{t_b.value['name']},还差{t_t}次结算研发完成"

    await bot.finish(ev, msg, at_sender=True)


@sv.on_fullmatch(["建筑列表", "建筑一览"])
async def build_view(bot, ev: CQEvent):
    tas_list = []
    data = {
        "type": "node",
        "data": {
            "name": "ご主人様",
            "uin": "1587640710",
            "content": "==== 建筑列表 ===="
        }
    }
    tas_list.append(data)
    for i in BuildModel:
        msg = f'''
{i.value['name']}:
花费:{i.value['gold']}金币,{i.value['sw']}声望
限制:最多拥有{i.value['limit']}个
占地面积:{i.value['area']}
建筑时间:{i.value['time']}次领地结算
描述:{i.value['desc']}
'''.strip()
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content": msg
            }
        }
        tas_list.append(data)
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)


@sv.on_prefix("拆除建筑")
async def _build(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    build_name = str(ev.message).strip()
    # 检查是否已经开启
    if not get_user_counter(gid, uid, UserModel.MANOR_BEGIN):
        await bot.finish(ev, "您还未接受封地", at_sender=True)
    if not build_name:
        await bot.finish(ev, "请使用指令 拆除建筑 + 建筑名称 ", at_sender=True)
    b_m = BuildModel.get_by_name(build_name)
    if not b_m:
        await bot.finish(ev, f"未找到名为{build_name}的建筑", at_sender=True)
    b_id = get_user_counter(gid, uid, UserModel.BUILD_BUFFER)
    if b_id == b_m.value['id']:
        save_user_counter(gid, uid, UserModel.BUILD_BUFFER, 0)
        save_user_counter(gid, uid, UserModel.BUILD_CD, 0)
        await bot.finish(ev, f"施工队停止建造了{b_m.value['name']}", at_sender=True)
    num = check_build_counter(gid, uid, b_m)
    if num == 0:
        await bot.finish(ev, f"你领地内没有{b_m.value['name']}", at_sender=True)
    num -= 1
    i_c = ItemCounter()
    i_c._save_user_state(gid, uid, b_m.value['id'], num)
    await bot.finish(ev, f"施工队对{b_m.value['name']}进行了爆破，随着一声巨响，这栋建筑永远的消失了", at_sender=True)


@sv.on_prefix("建造建筑")
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
    city_manor = get_city_manor(gid, uid, level)
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


@sv.on_fullmatch("领地结算")
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
    msg = '\n==== 领地结算 ===='
    duel = DuelCounter()
    level = duel._get_level(gid, uid)

    # 繁荣度增减
    fanrong = 0
    now_fanrong = get_user_counter(gid, uid, UserModel.PROSPERITY_INDEX)
    fan_buff = 1 + (now_fanrong / 1000)
    # 治安结算
    zhian = get_user_counter(gid, uid, UserModel.ZHI_AN)
    # 判定城市拥堵
    build_map = get_all_build_counter(gid, uid)
    total = 0
    for i in build_map.keys():
        total += i.value['area'] * build_map[i]
    city_manor = get_city_manor(gid, uid, level)
    yongdu = 0.8
    if check_technolog_counter(gid, uid, TechnologyModel.ROAD_PLANNING):
        yongdu = 0.9
    if total / city_manor >= yongdu:
        reduce = random.randint(8, 15)
        zhian -= reduce
        msg += f"\n由于城市过于拥挤,居民怨声载道，治安减少了{reduce}"
    # 判定苛税乘法
    tax_rate = get_user_counter(gid, uid, UserModel.TAX_RATIO)
    if tax_rate <= 10:
        add = random.randint(3, 8) + (10 - tax_rate)
        # 轻税额外增加繁荣度
        fanrong += random.randint(2, 4) + int(0.5 * (10 - tax_rate))
        zhian += add
        if zhian >= 100:
            zhian = 100
        msg += f"\n人民安居乐业,生活轻松，治安增加了{add}"
    elif 30 < tax_rate <= 50:
        # 苛税依据苛税水平扣减繁荣度
        fanrong -= random.randint(3, 5) + int(0.5 * (tax_rate - 30))
        reduce = random.randint(8, 15) + int(0.5 * (tax_rate - 30))
        zhian -= reduce
        if zhian < 0:
            zhian = 0
        msg += f"\n人民朝九晚九，一周六天，工作十分辛苦，心中怨声载道，治安减少了{reduce}"
    elif tax_rate > 50:
        msg += f"\n人民已经厌倦了领主的暴政,治安减少了{zhian}"
        zhian = 0
        # 巨量收税大幅扣减繁荣度
        fanrong -= random.randint(15, 20)
    else:
        # 正常税率以20为分界线增加或减少繁荣
        fanrong += int(0.2 * (20 - tax_rate))

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
        # 治安良好随机增加繁荣度
        fanrong += random.randint(3, 5)
        buffer_flag = 1

    gold_sum = 0
    sw_sum = 0
    p_id = get_user_counter(gid, uid, UserModel.MANOR_POLICY)
    p_m = PolicyModel.get_by_id(p_id)
    if bao_flag:
        # 暴乱繁荣无条件-10
        fanrong -= 10
    else:
        # 计算耕地
        geng = get_user_counter(gid, uid, UserModel.GENGDI)
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
        sha_ex = 80
        sha_min = 50
        if check_technolog_counter(gid, uid, TechnologyModel.SAND_FIX):
            sha_ex = 90
            sha_min = 60
        if geng >= sha_ex:
            sha_flag = 1
            msg += f"由于你大肆扩张耕地，领地内出现了黄沙天气，农民颗粒无收"

        elif geng >= sha_min:
            rn = random.randint(sha_min, sha_ex - 1)
            if geng > rn:
                sha_flag = 1
                msg += f"由于你大肆扩张耕地，领地内出现了黄沙天气，农民颗粒无收"
        if not sha_flag:
            # 正常收获 随机增加繁荣度 且耕地面积越大越高
            fanrong += random.randint(1, 3) + int(geng / 10)
            area_geng = get_geng_manor(gid, uid, level, geng)
            tax = get_user_counter(gid, uid, UserModel.TAX_RATIO)
            geng_gold = int(area_geng * tax * 10 * random.uniform(0.9, 1.1) * fan_buff)
            if p_m == PolicyModel.CATCH_ALL_FISH:
                if now_fanrong >= 30:
                    now_fanrong -= 30
                    geng_gold = int(1.5 * geng_gold)
            if p_m == PolicyModel.AGRICULTURAL_SUBSIDIES:
                fanrong += 10
                geng_gold = int(0.5 * geng_gold)
            if p_m == PolicyModel.POVERTY_ALLEVIATION_POLICIES:
                fanrong += 10
                geng_gold = -get_all_manor(level) * 100
            msg += f"\n耕地收入为{geng_gold}金币"

        gold_sum += geng_gold
        # 计算建筑进度
        cd = get_user_counter(gid, uid, UserModel.BUILD_CD)
        if cd != 0:
            cd -= 1
            if p_m == PolicyModel.STRONG_BUILD:
                if now_fanrong >= 50:
                    now_fanrong -= 50
                    cd = 0 if cd - 1 < 0 else cd - 1
            if cd <= 0:
                buffer_build_id = get_user_counter(gid, uid, UserModel.BUILD_BUFFER)
                build = BuildModel.get_by_id(buffer_build_id)
                build_num = check_build_counter(gid, uid, build)
                build_num += 1
                i_c = ItemCounter()
                i_c._save_user_state(gid, uid, build.value['id'], build_num)
                msg += f"\n施工队报告{build.value['name']}竣工了，已经可以投入使用"
                save_user_counter(gid, uid, UserModel.BUILD_BUFFER, 0)
            save_user_counter(gid, uid, UserModel.BUILD_CD, cd)

        # 计算科研进度
        t_cd = get_user_counter(gid, uid, UserModel.TECHNOLOGY_CD)
        if t_cd != 0:
            t_cd -= 1
            if p_m == PolicyModel.STRONG_TEC:
                if now_fanrong >= 50:
                    now_fanrong -= 50
                    t_cd = 0 if t_cd - 1 < 0 else t_cd - 1
            if t_cd == 0:
                buffer_technology_id = get_user_counter(gid, uid, UserModel.TECHNOLOGY_BUFFER)
                technology = TechnologyModel.get_by_id(buffer_technology_id)
                i_c = ItemCounter()
                i_c._save_user_state(gid, uid, technology.value['id'], 1)
                msg += f"\n科研队报告{technology.value['name']}已经研发成功了！"
                save_user_counter(gid, uid, UserModel.TECHNOLOGY_BUFFER, 0)
            save_user_counter(gid, uid, UserModel.TECHNOLOGY_CD, t_cd)
        # 计算建筑收益
        b_c = get_all_build_counter(gid, uid)
        for i in b_c.keys():
            # 每有一个类建筑 增加1点繁荣度
            fanrong += b_c[i]
            if i == BuildModel.CENTER:
                continue
            elif i == BuildModel.MARKET:
                rate = 1.0
                if check_technolog_counter(gid, uid, TechnologyModel.MONETARY_POLICY):
                    rate = 1.5
                market_gold = int(rate * 20000 * b_c[i] * random.uniform(0.9, 1.1) * fan_buff)
                if buffer_flag:
                    market_gold = int(market_gold * 1.1)
                msg += f'\n贸易市场为你带来了额外{market_gold}金币收益'
                gold_sum += market_gold
            elif i == BuildModel.TV_STATION:
                rate = 1.0
                if check_technolog_counter(gid, uid, TechnologyModel.MANIPULATION):
                    rate = 1.5
                tv_sw = int(rate * 1500 * b_c[i] * random.uniform(0.9, 1.1) * fan_buff)
                if buffer_flag:
                    tv_sw = int(tv_sw * 1.1)
                sw_sum += tv_sw
                msg += f'\n报社为你带来了额外{tv_sw}声望'
            elif i == BuildModel.ITEM_SHOP:
                if check_technolog_counter(gid, uid, TechnologyModel.BRANCH_STORE):
                    save_user_counter(gid, uid, UserModel.ITEM_BUY_TIME, 2)
                else:
                    save_user_counter(gid, uid, UserModel.ITEM_BUY_TIME, 1)
                msg += f'\n道具商店的物品刷新了，可以进行购买'
            elif i == BuildModel.POLICE_OFFICE:
                ct = b_c[i]
                zhian += ct * 10
                if zhian >= 100:
                    zhian = 100
                save_user_counter(gid, uid, UserModel.ZHI_AN, zhian)
                msg += f'\n警察局为你提高了{ct * 10}点治安，当前治安为{zhian}'
            elif i == BuildModel.HUANBAO:
                area_geng = get_geng_manor(gid, uid, level, geng)
                area_city = get_city_manor(gid, uid, level)
                area_all = get_all_manor(level)
                lin = area_all - area_geng - area_city
                get_sw = int(lin * 5 * random.uniform(0.9, 1.1) * fan_buff)
                sw_sum += get_sw
                msg += f"\n环保局致力于维护林地，让领地环境变得更好，声望上升了{get_sw}"
            elif i == BuildModel.DIZHI:
                ct = b_c[i]
                item = get_item_by_name("藏宝图")
                add_item(gid, uid, item, num=ct)
                msg += f'\n地质部门的人开始对领地进行勘测，你获得了{ct}张{item["name"]}'
            elif i == BuildModel.KELA:
                rn = random.randint(1, 20)
                if rn == 1:
                    item = get_item_by_name("咲夜怀表")
                else:
                    item = get_item_by_name("零时迷子")
                add_item(gid, uid, item)
                msg += f'\n科拉深井继续向地心钻探，你获得了{item["rank"]}级道具{item["name"]}'
            elif i == BuildModel.FISSION_CENTER:
                rn = random.randint(1, 20)
                if rn == 1:
                    item = get_item_by_name("四重存在")
                elif rn == 2:
                    item = get_item_by_name("好事成双")
                else:
                    item = get_item_by_name("有效分裂")
                add_item(gid, uid, item, num=2)
                msg += f'\n裂变中心正常运转，你获得了2个{item["rank"]}级道具{item["name"]}'

    # 更新繁荣度
    now_fanrong += fanrong
    if now_fanrong < 0:
        now_fanrong = 0
    elif now_fanrong > 1000:
        now_fanrong = 1000
    save_user_counter(gid, uid, UserModel.PROSPERITY_INDEX, now_fanrong)
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


@sv.on_prefix(["政策选择", "选择政策", "发布政策"])
async def manor_policy(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if not check_build_counter(gid, uid, BuildModel.CENTER):
        await bot.finish(ev, f"没有行政中心前无法进行政策选择")
    name = str(ev.message).strip()
    if not name:
        await bot.finish(ev, f'请选择[政策一览]中的其中一项政策')
    pm = PolicyModel.get_by_name(name)
    if not pm:
        await bot.finish(ev, f'没有找到名为{name}的政策，请选择[政策一览]中的其中一项政策')
    save_user_counter(gid, uid, UserModel.MANOR_POLICY, pm.value[0])
    await bot.finish(ev, f'你颁布了行政法令，要求{pm.value[1]}')


@sv.on_prefix(["政策列表", "政策一览"])
async def manor_policy_view(bot, ev: CQEvent):
    tas_list = []
    data = {
        "type": "node",
        "data": {
            "name": "ご主人様",
            "uin": "1587640710",
            "content": "==== 政策一览 ===="
        }
    }
    tas_list.append(data)
    for pm in PolicyModel:
        msg = f'''
{pm.value[1]}
详情:{pm.value[2]}
    '''.strip()
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content": msg
            }
        }
        tas_list.append(data)
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)


@sv.on_prefix(["税率调整", "调整税率"])
async def manor_tax(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if not check_build_counter(gid, uid, BuildModel.CENTER):
        await bot.finish(ev, f"没有行政中心前无法进行税率调整")
    number = str(ev.message).strip()
    if not number:
        await bot.finish(ev, f'请在指令后增加税率（30代表30%税率）')
    if not number.isdecimal():
        await bot.finish(ev, f'请在指令后增加"数字"作为税率（30代表30%税率）')
    save_user_counter(gid, uid, UserModel.TAX_RATIO, number)
    await bot.finish(ev, f'你颁布了行政法令，规定耕地征税{number}%')


from hoshino.typing import CommandSession


@sv.on_command("购买道具")
async def buy_item(session: CommandSession):
    bot = session.bot
    ev = session.event
    gid = ev.group_id
    uid = ev.user_id
    num = get_user_counter(gid, uid, UserModel.ITEM_BUY_TIME)
    if num <= 0:
        await bot.finish(ev, f'你的城市没有商店或已经没有购买次数，无法购买道具')

    score_counter = ScoreCounter2()
    score = score_counter._get_score(gid, uid)
    if score < 10000:
        await bot.finish(ev, f'你的金币不足1万，无法购买道具')
    if check_technolog_counter(gid, uid, TechnologyModel.TRANSPARENT_TRADE):
        if not session.state['item']:
            item = choose_item()
            session.state['item'] = item["name"]
            jieshou = session.get('jieshou', prompt=f'商店老板拿出的道具为{item["rank"]}级道具{item["name"]},是否要购买(是|否)回答其他内容默认为是')
        jieshou = session.get('jieshou')
        if jieshou != '否':
            item = get_item_by_name(session.state['item'])
            score_counter._reduce_score(gid, uid, 10000)
            add_item(gid, uid, item)
            num -= 1
            save_user_counter(gid, uid, UserModel.ITEM_BUY_TIME, num)
            await bot.finish(ev, f'你花费了1万金币购买到了{item["rank"]}级道具{item["name"]}')
        else:
            num -= 1
            save_user_counter(gid, uid, UserModel.ITEM_BUY_TIME, num)
            await bot.finish(ev, f'你一脸嫌弃的看着老板拿出的道具，拒绝了购买')

    num -= 1
    score_counter._reduce_score(gid, uid, 10000)
    save_user_counter(gid, uid, UserModel.ITEM_BUY_TIME, num)
    item = choose_item()
    add_item(gid, uid, item)
    await bot.finish(ev, f'你花费了1万金币购买到了{item["rank"]}级道具{item["name"]}')


@buy_item.args_parser
async def _(session: CommandSession):
    text = session.current_arg_text
    img = session.current_arg_images
    if session.is_first_run:
        session.state['item'] = 0
        return
    if img:
        session.state[session.current_key] = img
    else:
        session.state[session.current_key] = text


@sv.on_prefix("刷新结算")
async def refresh(bot, ev: CQEvent):
    gid = ev.group_id
    msg = str(ev.message).strip()
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, f"你无权使用投放道具功能", at_sender=True)
    try:
        fa_uid = int(msg[0])
    except ValueError:
        fa_uid = int(ev.message[0].data['qq'])
    except:
        await bot.finish(ev, '参数格式错误')
    to_id = fa_uid
    guid = gid, to_id
    daily_manor_limiter.reset(guid)
    await bot.finish(ev, f"刷新结算成功")


@sv.on_prefix(["装备熔炼", "熔炼装备"])
async def equip_fuse(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    num = check_build_counter(gid, uid, BuildModel.EQUIP_CENTER)
    if num <= 0:
        await bot.finish(ev, f'你的城市没有装备工坊，无法熔炼装备')
    modelname = args[0]
    if len(args) != 1:
        await bot.finish(ev, '请输入 装备熔炼+装备等级(N/R/SR/SSR/UR/MR) 中间用空格隔开。', at_sender=True)
    with open(os.path.join(FILE_PATH, 'equipment.json'), 'r', encoding='UTF-8') as fa:
        equiplist = json.load(fa, strict=False)
    equiplevel = 0
    for i in equiplist:
        if str(modelname) == str(equiplist[i]['model']):
            equiplevel = equiplist[i]['level']
            break
    if equiplevel == 0:
        await bot.finish(ev, '请输入正确的装备等级(N/R/SR/SSR/UR/MR)。', at_sender=True)
    CE = CECounter()
    equip_list = CE._get_equip_list(gid, uid)
    if len(equip_list) > 0:
        need = 4  # 需要的装备数量
        if equiplevel == 6:
            need = 2  # 如果使用MR熔炼，则消耗变为2
        if check_technolog_counter(gid, uid, TechnologyModel.REFINING_TECHNOLOGY):
            need -= 1

        # 统计是否拥有足够数量的装备
        have_num = 0
        filter_equip = []
        for i in equip_list:
            equipinfo = get_equip_info_id(i[0])
            if equipinfo['level'] == equiplevel:
                have_num += i[1]
                filter_equip.append(i)
        if have_num < need:
            await bot.finish(ev, f'你没有足够数量等级为{modelname}的装备,需求数量为{need}', at_sender=True)
        # 消耗掉对应装备
        for i in filter_equip:
            equipinfo = get_equip_info_id(i[0])
            equipnum = i[1]
            if equipnum >= need:
                deletenum = 0 - need
                CE._add_equip(gid, uid, equipinfo['eid'], deletenum)
                break
            else:
                deletenum = 0 - equipnum
                need -= equipnum
                CE._add_equip(gid, uid, equipinfo['eid'], deletenum)
        # 获取更高一级的装备
        eid = equiplevel
        if equiplevel <= 5:
            eid = equiplevel + 1
        rate = [100, 100, 80, 60, 30, 40]
        rn = random.randint(1, 100)
        if rn <= rate[equiplevel - 1]:
            e_li = equiplist[str(eid)]["eid"]
            awardequip_info = add_equip_info(gid, uid, eid, e_li)
            await bot.finish(ev,
                             f"你获得了{awardequip_info['model']}品质的{awardequip_info['type']}:{awardequip_info['name']}",
                             at_sender=True)
        else:
            await bot.finish(ev, f'凯丽鼓励你再接再力，总有一天能出货的（熔炼失败）', at_sender=True)
    else:
        await bot.finish(ev, f'你背包中没有装备', at_sender=True)


@sv.on_fullmatch(["科技列表", "科技一览"])
async def technology_li(bot, ev: CQEvent):
    tas_list = []
    data = {
        "type": "node",
        "data": {
            "name": "ご主人様",
            "uin": "1587640710",
            "content": "====== 科技列表 ======"
        }
    }
    tas_list.append(data)
    for i in TechnologyModel:
        msg = f'''
{i.value['name']}
花费:{i.value['gold']}金币,{i.value['sw']}声望
研发时间:{i.value['time']}次领地结算
描述:{i.value['desc']}
    '''.strip()
        data = {
            "type": "node",
            "data": {
                "name": "ご主人様",
                "uin": "1587640710",
                "content": msg
            }
        }
        tas_list.append(data)
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=tas_list)


@sv.on_fullmatch(["我的科技", "科技查询", "查询科技", "领地科技"])
async def technology_my(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    num = check_build_counter(gid, uid, BuildModel.TECHNOLOGY_CENTER)
    if num <= 0:
        await bot.finish(ev, f'你的城市没有科技研究所，无法查看科技树', at_sender=True)
    msg = "\n====== 我的科技 ======"
    for i in TechnologyModel:
        if check_technolog_counter(gid, uid, i):
            msg += f"\n{i.value['name']}"
    await bot.finish(ev, msg, at_sender=True)


# [科技研发] 科技研究所指令，研发新科技

@sv.on_prefix(["科技研发", "研发科技"])
async def technology_new(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    if not check_build_counter(gid, uid, BuildModel.TECHNOLOGY_CENTER):
        await bot.finish(ev, f'你的城市没有科技研究所，无法进行科技研发', at_sender=True)
    technology_name = str(ev.message).strip()
    # 检查是否已经开启
    if not technology_name:
        await bot.finish(ev, "请使用指令 科技研发 + 科技名称 ", at_sender=True)

    t_id = get_user_counter(gid, uid, UserModel.TECHNOLOGY_BUFFER)
    if t_id:
        tm = TechnologyModel.get_by_id(t_id)
        await bot.finish(ev, f"研发人员正在研究{tm.value['name']},无法接受新的委托", at_sender=True)
    t_m = TechnologyModel.get_by_name(technology_name)
    if not t_m:
        await bot.finish(ev, f"未找到名为{technology_name}的科技", at_sender=True)

    s_c = ScoreCounter2()
    if s_c._get_score(gid, uid) < t_m.value["gold"]:
        await bot.finish(ev, f"你没有足够的金币进行研发", at_sender=True)
    if s_c._get_prestige(gid, uid) < t_m.value["sw"]:
        await bot.finish(ev, f"你没有足够的声望进行研发", at_sender=True)
    s_c._reduce_score(gid, uid, t_m.value["gold"])
    s_c._reduce_prestige(gid, uid, t_m.value["sw"])
    save_user_counter(gid, uid, UserModel.TECHNOLOGY_BUFFER, t_m.value['id'])
    save_user_counter(gid, uid, UserModel.TECHNOLOGY_CD, t_m.value['time'])
    # 增加研发状态
    await bot.finish(ev, f"你的科研团队开始研究{t_m.value['name']}了,预期花费{t_m.value['time']}次计算时间可以研究完成", at_sender=True)
