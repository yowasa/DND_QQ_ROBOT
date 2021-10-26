import re
from hoshino.typing import CQEvent
from . import sv
from .ScoreCounter import ScoreCounter2
from .battle import *


@sv.on_fullmatch(['副本系统帮助', '副本帮助'])
async def dun_help(bot, ev: CQEvent):
    msg = '''
╔                                        ╗  
             副本系统帮助
[编队{队伍名/角色名}进入{难度}副本]
[副本信息]
[关卡信息] {关卡名称}
[发动技能] {空格隔开的技能名称}
[进入关卡] {关卡名称}
[我的副本币]
[副本商城]
[购买物品] {物品名}
[兑换装备] {装备名}
╚                                        ╝
 '''.strip()
    await bot.send(ev, msg)


@sv.on_rex(f'^编队(.*)进入(.*)副本$')
async def in_dun(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    weather = get_weather(gid)
    if weather == WeatherModel.ZHI:
        return
    CE = CECounter()
    # 处理输入数据
    match = ev['match']
    if match.group(2):
        dun_nd = str(match.group(2)).strip()
    else:
        dun_nd = '简单'

    if dun_nd == '简单':
        dun_model = 0
    elif dun_nd == '困难':
        dun_model = 1
    elif dun_nd == '地狱':
        dun_model = 2
    else:
        await bot.finish(ev, '请输入正确的副本难度(简单/困难/地狱)', at_sender=True)
    defen = str(match.group(1)).strip()
    defen = re.sub(r'[?？，,_]', '', defen)
    if not defen:
        await bot.finish(ev, '请发送"编队+女友名/队伍名+进入(简单/困难/地狱)副"，无需+号', at_sender=True)
    # 查询是否是队伍
    teamlist = CE._get_teamlist(gid, uid, defen)
    if teamlist != 0:
        defen = []
        for i in teamlist:
            cid = i[0]
            defen.append(cid)
    else:
        defen, unknown = chara.roster.parse_team(defen)
        if unknown:
            _, name, score = chara.guess_id(unknown)
            if score < 70 and not defen:
                return  # 忽略无关对话
            msg = f'无法识别"{unknown}"' if score < 70 else f'无法识别"{unknown}" 您说的有{score}%可能是{name}'
            await bot.finish(ev, msg)
        if len(defen) > 5:
            await bot.finish(ev, '编队不能多于5名角色', at_sender=True)
        if len(defen) != len(set(defen)):
            await bot.finish(ev, '编队中含重复角色', at_sender=True)
    guid = gid, uid
    if not daily_dun_limiter.check(guid):
        await bot.finish(ev, '超出进入副本上限', at_sender=True)
    # 获取编队战力与信息
    duel = DuelCounter()
    for cid in defen:
        c = chara.fromid(cid)
        nvmes = get_nv_icon(cid)
        owner = duel._get_card_owner(gid, cid)
        if owner == 0:
            await bot.send(ev, f'{c.name}现在还是单身哦，快去约到她吧。{nvmes}', at_sender=True)
            return
        if uid != owner:
            msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法编队哦。'
            await bot.send(ev, msg)
            return
    my = duel_my_buff(gid, uid, defen)
    dun = DunInfo()
    dun.gid = gid
    dun.uid = uid
    dun.cids = defen
    dun.dun_model = dun_model
    dun.left_hp = my.hp
    dun.left_sp = my.max_sp
    if get_weather(gid) == WeatherModel.CANGTIAN:
        dun.left_sp = my.max_sp + 10
    dun.use_skill = my.all_skill
    dun.now_dun = None
    dun.from_dun = None
    dun.able_dun = ['春之小径']
    CE._save_dun_info(dun)
    daily_dun_limiter.increase(guid)
    await bot.send(ev, "进入副本成功！使用[副本信息]查看可以前往的关卡，使用 [进入关卡 {关卡名}] 进行推进副本流程", at_sender=True)


def get_albe_stage(dun):
    able_li = []
    if dun.from_dun:
        able_li.append(dun.from_dun)
    if dun.now_dun:
        able_li.append(dun.now_dun)
    if dun.able_dun:
        able_li.extend(dun.able_dun)
    return list(set(able_li))


@sv.on_fullmatch("副本信息")
async def check_road(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    guid = gid, uid
    if daily_dun_limiter.check(guid):
        await bot.finish(ev, '请先进入副本再查看信息', at_sender=True)
    CE = CECounter()
    dun = CE._select_dun_info(gid, uid)
    able_li = get_albe_stage(dun)
    msg = '可前往的关卡有:\n' + '\n'.join(able_li)
    defen = dun.cids
    my = duel_my_buff(gid, uid, defen)
    resp = f"""队伍信息
hp:{dun.left_hp}/{my.maxhp} atk:{my.atk} sp:{dun.left_sp}
发动中的技能:{' '.join(dun.use_skill) if dun.use_skill else ''}
可发动的技能:{' '.join(my.all_skill)}
boost:{my.boost}% 暴击:{my.crit}% 连击:{my.double}% 回复:{my.recover} 闪避:{my.dodge}%
{msg}"""
    await bot.finish(ev, resp, at_sender=True)


@sv.on_prefix("关卡信息")
async def stage_info(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg = str(ev.message).strip().strip()
    CE = CECounter()
    dun = CE._select_dun_info(gid, uid)
    able_li = get_albe_stage(dun)
    if msg not in able_li:
        await bot.finish(ev, f'你没有前往"{msg}"关卡的路径', at_sender=True)
    hard = dun.dun_model
    resp = f"""{msg}
hp:{dungeonlist[msg]["hp"][hard]} atk:{dungeonlist[msg]["atk"][hard]}
技能:{' '.join(dungeonlist[msg]["skill"][hard])}
boost:{dungeonlist[msg]["buff"][hard][0]}% 暴击:{dungeonlist[msg]["buff"][hard][1]}% 连击:{dungeonlist[msg]["buff"][hard][2]}% 回复:{dungeonlist[msg]["buff"][hard][3]} 闪避{dungeonlist[msg]["buff"][hard][4]}%
掉落
金币：{dungeonlist[msg]['drop']["gold"][hard]} 声望：{dungeonlist[msg]['drop']["sw"][hard]} exp:{dungeonlist[msg]['drop']["exp"][hard]} 好感：{dungeonlist[msg]['drop']["favor"][hard]}
{dungeonlist[msg]["desc"]}"""
    await bot.finish(ev, resp, at_sender=True)


@sv.on_prefix("发动技能")
async def in_stage(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    msg = str(ev.message).strip()
    guid = gid, uid
    if daily_dun_limiter.check(guid):
        await bot.finish(ev, '请先进入副本', at_sender=True)
    # 校验人员完整
    duel = DuelCounter()
    CE = CECounter()
    dun = CE._select_dun_info(gid, uid)
    defen = dun.cids
    for cid in defen:
        c = chara.fromid(cid)
        nvmes = get_nv_icon(cid)
        owner = duel._get_card_owner(gid, cid)
        if owner == 0:
            await bot.send(ev, f'{c.name}现在还是单身哦，快去约到她吧。{nvmes}', at_sender=True)
            return
        if uid != owner:
            msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法进入关卡'
            await bot.send(ev, msg)
            return
    if not msg:
        dun.use_skill = []
        await bot.send(ev, "已取消发动的所有技能")
        return
    my = duel_my_buff(gid, uid, defen)
    msg_li = str(msg).split(" ")
    for i in msg_li:
        if not skill_def_json.get(i):
            await bot.send(ev, f"未找到名为{i}的技能")
            return
        if i not in my.all_skill:
            await bot.send(ev, f"发动技能失败，你队伍中没有会{i}技能的角色,请使用 '发动技能 空格隔开的技能名' 重新设定")
            return
    dun.use_skill = msg_li
    CE._save_dun_info(dun)
    await bot.send(ev, "发动技能成功", at_sender=True)


@sv.on_prefix("进入关卡")
async def in_stage(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    stage = str(ev.message).strip().strip()
    weather = get_weather(gid)
    if weather == WeatherModel.ZHI:
        return
    guid = gid, uid
    if daily_dun_limiter.check(guid):
        await bot.finish(ev, '请先进入副本再进入关卡', at_sender=True)
    CE = CECounter()
    dun = CE._select_dun_info(gid, uid)
    able_li = get_albe_stage(dun)
    if stage not in able_li:
        await bot.finish(ev, f'你没有前往"{stage}"关卡的路径', at_sender=True)
    duel = DuelCounter()
    # 校验人员完整
    defen = dun.cids
    charalist = []
    bianzu = ''
    for cid in defen:
        c = chara.fromid(cid)
        nvmes = get_nv_icon(cid)
        owner = duel._get_card_owner(gid, cid)
        if owner == 0:
            await bot.send(ev, f'{c.name}现在还是单身哦，快去约到她吧。{nvmes}', at_sender=True)
            return
        if uid != owner:
            msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦，您无法进入关卡'
            await bot.send(ev, msg)
            return
        star = CE._get_cardstar(gid, uid, cid)
        charalist.append(chara.Chara(cid, star, 0))
        bianzu = bianzu + f"{c.name} "
    if dun.left_hp <= 0:
        msg = f'请将自己的hp回复至0以上再进入关卡！'
        await bot.send(ev, msg)
        return
    my = duel_my_buff(gid, uid, defen)
    # 校验副本限制
    if not daily_stage_limiter.check(guid):
        await bot.send(ev, '今天的副本次数已经超过上限了哦，明天再来吧。', at_sender=True)
        return
    if not daily_stage_limiter.check(guid):
        await bot.send(ev, '今天的副本次数已经超过上限了哦，明天再来吧。', at_sender=True)
        return

    if weather == WeatherModel.CHUANWU:
        rd = random.randint(1, 10)
        if rd == 1:
            daily_stage_limiter.increase(guid, num=2)
        elif rd < 10:
            daily_stage_limiter.increase(guid)
    else:
        daily_stage_limiter.increase(guid)
    # 获取发动技能
    left_sp = dun.left_sp
    use_skill = []
    for i in dun.use_skill:
        if i not in my.all_skill:
            await bot.send(ev, f"发动技能失败，你队伍中没有会{i}技能的角色,请使用 '发动技能 空格隔开的技能名' 重新设定")
            return
        if left_sp >= skill_def_json[i]["sp"]:
            use_skill.append(i)
        else:
            continue
        left_sp -= skill_def_json[i]["sp"]
    my.hp = dun.left_hp
    my.sp = left_sp
    my.skill = use_skill
    dungeon = dungeonlist[stage]
    hard = dun.dun_model
    enemy = duel_enemy_buff(defen, dungeon['hp'][hard], dungeon['sp'], dungeon['atk'][hard], dungeon['buff'][hard],
                            dungeon['skill'][hard])
    # 拼接开始文案
    res = chara.gen_team_pic(charalist, star_slot_verbose=False)
    bio = BytesIO()
    res.save(bio, format='PNG')
    base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
    mes = f"[CQ:image,file={base64_str}]"
    msg1 = f"编组成功{bianzu}\n开始进入{stage}\n，开始战斗{mes}"
    tas_list = []
    data = {
        "type": "node",
        "data": {
            "name": "ご主人様",
            "uin": "1587640710",
            "content": msg1
        }
    }
    tas_list.append(data)
    success, logs = battle(my, enemy)
    dun.left_hp = my.hp
    dun.left_sp = my.sp
    # 发现新道路
    if dun.now_dun != stage:
        dun.from_dun = dun.now_dun
        dun.now_dun = stage
    if success:
        new_buff = sum_character(defen, "勤奋")
        road_map = dungeon_road.get(stage)
        if road_map:
            rn = random.randint(1, 10)
            total = 0
            for i in road_map.keys():
                total += road_map[i]
                if rn <= total:
                    dun.able_dun.append(i)
                    dun.able_dun = list(set(dun.able_dun))
                    break
            if len(road_map.keys()) > 1:
                rn = random.randint(1, 5)
                if rn <= new_buff:
                    new_road = random.choice([i for i in road_map.keys()])
                    dun.able_dun.append(new_road)
                    dun.able_dun = list(set(dun.able_dun))
    cangtian_msg = ""
    dun.left_sp = my.max_sp
    if get_weather(gid) == WeatherModel.CANGTIAN:
        dun.left_sp = my.max_sp + 10
    if not success:
        if get_weather(gid) == WeatherModel.HUANGSHA:
            dun.left_hp = my.maxhp
            cangtian_msg = "\n由于天气效果hp回复至满值"
    CE._save_dun_info(dun)
    battle_tags = build_battle_tag_list(log)
    tas_list.extend(battle_tags)
    # 战斗失败
    if not success:
        msg = ''
        msg = msg + "您战斗失败了，副本次数-1"
        if weather == WeatherModel.MEIYU:
            rd = random.randint(1, 5)
            if rd == 1:
                daily_stage_limiter.increase(guid, -1)
                msg = msg + "由于天气效果，恢复了一次副本次数"
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
        return
    # 计算掉落buff增益
    diaoluo_buff = sum_character(defen, "元气")
    # 计算恢复次数buff
    huifu_buff = sum_character(defen, "勤奋") * 5
    # 计算资源获取buff
    ziyuan_buff = 1 + (sum_character(defen, "傲娇") * 10) / 100

    rd = random.randint(1, 100)
    if rd <= huifu_buff:
        daily_stage_limiter.increase(guid, num=-1)
        await bot.send(ev, "触发了连破buff，副本次数回复一次", at_sender=True)
    # 战斗胜利
    msg = "战斗胜利了！\n"
    max_card = 0
    for cid in defen:
        get_exp = dungeon['drop']['exp'][hard]
        duel._add_favor(gid, uid, cid, dungeon['drop']['favor'][hard])
        card_level = add_exp(gid, uid, cid, get_exp)
        if card_level[1] >= 50:
            max_card += 1
    msg = msg + f"您的女友{bianzu}获得了{get_exp}点经验，{dungeon['drop']['favor'][hard]}点好感\n"
    if max_card == 5:
        rn = random.randint(1, 100)
        if rn <= 1:
            item = get_item_by_name("天命之子")
            add_item(gid, uid, item)
            await bot.send(ev,
                           f"[CQ:at,qq={uid}]一直以来已经到达到达瓶颈的你突然感受到了天的声音，恭喜你，你是被选中之人，获得了{item['rank']}级道具{item['name']},经验池已被清空\n")

    # 增加副本币
    get_dun_score = hard + 1
    CE._add_dunscore(gid, uid, get_dun_score)
    msg = msg + f"您获得了{get_dun_score}副本币\n"

    get_money = int(dungeon['drop']['gold'][hard] * ziyuan_buff)
    get_SW = int(dungeon['drop']['sw'][hard] * ziyuan_buff)
    item_msg = ''
    if dungeon['drop'].get("item"):
        item_info = dungeon['drop']["item"][hard]
        rn = random.randint(1, 100)
        if rn <= item_info['rate'] + diaoluo_buff:
            item_name = random.choice(item_info['items'])
            item = get_item_by_name(item_name)
            add_item(gid, uid, item)
            item_msg = f"你获得了{item['rank']}级道具{item['name']}!\n"

    score_counter = ScoreCounter2()
    score_counter._add_prestige(gid, uid, get_SW)
    score_counter._add_score(gid, uid, get_money)

    msg = msg + f"您获得了{get_money}金币和{get_SW}声望\n{item_msg}"
    # 战斗胜利增加1，3，5点修炼度
    add_xiu = [1, 3, 5]
    for j in defen:
        CE._add_fragment_num(gid, uid, j, add_xiu[hard])

    msg = msg + "您获得的战利品为：\n"
    dun_get_favor = random.randint(1, 3)
    gift_list = ''
    # 获取礼物
    for x in range(dun_get_favor):
        select_gift = random.choice(list(GIFT_DICT.keys()))
        gfid = GIFT_DICT[select_gift]
        duel._add_gift(gid, uid, gfid)
        gift_list = gift_list + f"[{select_gift}] "
    msg = msg + f'获得了礼物:{gift_list}\n'

    # 获取装备
    dun_get_equip = 0
    rn = random.randint(1, 100)
    if rn <= dungeon['drop']['equip']['rate'][hard]:
        dun_get_equip = 1
    equip_list = ''
    # 判断是否触发贤者之石
    ic = ItemCounter()
    count = ic._get_user_info(gid, uid, UserModel.EQUIP_UP)
    flag = 0
    if count > 0:
        flag = 1
        count -= 1
        ic._save_user_info(gid, uid, UserModel.EQUIP_UP, count)
    if dun_get_equip > 0:
        for y in range(dun_get_equip):
            qu_li = dungeon['drop']['equip']['quality']
            qu = cal_qu(qu_li, hard)
            if flag:
                # 触发贤者之石
                if qu < 5:
                    qu += 1
                gecha = get_gecha_info("红魔的夜宴")
                for i in gecha['gecha']['equip'].keys():
                    if i == str(qu):
                        get_ids = gecha['gecha']['equip'][i]
                        break
                equip_info = add_equip_info(gid, uid, qu, get_ids)
                equip_list = equip_list + f"{equip_info['model']}品质{equip_info['type']}:{equip_info['name']}\n"
            else:
                down_list = dungeon['drop']['equip']['able_li']
                equip_info = add_equip_info(gid, uid, qu, down_list)
                equip_list = equip_list + f"{equip_info['model']}品质{equip_info['type']}:{equip_info['name']}\n"
    if equip_list:
        msg = msg + f"获得了装备:\n{equip_list}"
    msg += cangtian_msg
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


# 获取装备品质
def cal_qu(qu_li, hard):
    le = len(qu_li)
    total = le * (le + 1) / 2
    t = 0
    tag = 0
    if hard == 0:
        rn = random.randint(1, total)
        for i in range(le):
            t += le - i
            if t <= rn:
                tag = i
    elif hard == 1:
        rn = random.randint(1, le)
        for i in range(le):
            t += 1
            if t <= rn:
                tag = i
    else:
        rn = random.randint(1, total)
        for i in range(le):
            t += i
            if t <= rn:
                tag = i
    return qu_li[tag]


@sv.on_prefix(['购买物品'])
async def buy_item(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    if not args:
        await bot.send(ev, '请输入购买物品+物品名称。', at_sender=True)
        return
    name = args[0]
    itemMap = {"红药水": 3, "蓝药水": 5, "零时迷子": 50}
    if name not in itemMap.keys():
        await bot.finish(ev, '只能购买 红药水-3 蓝药水-5 零时迷子-50', at_sender=True)
    CE = CECounter()
    myscore = CE._get_dunscore(gid, uid)
    price = itemMap[name]
    if myscore <= price:
        await bot.finish(ev, f'副本币不足，购买{name}需要副本币{price},当前副本币{myscore}', at_sender=True)
    CE._add_dunscore(gid, uid, -price)
    item = get_item_by_name(name)
    add_item(gid, uid, item)
    msg = f'\n您花费了{price}副本币，买到了[{name}]哦，\n欢迎下次惠顾。'
    await bot.send(ev, msg, at_sender=True)


# 每日精选装备
def sample_euqip():
    # N:5
    # R:4
    # SR:3
    # SSR:2
    # UR:1
    nowyear = datetime.now().year
    nowmonth = datetime.now().month
    nowday = datetime.now().day
    seed = nowyear * 10000 + nowmonth * 100 + nowday
    random.seed(seed)
    N_li = [i for i in equip_info.keys() if equip_info[i]['level'] == 1]
    R_li = [i for i in equip_info.keys() if equip_info[i]['level'] == 2]
    SR_li = [i for i in equip_info.keys() if equip_info[i]['level'] == 3]
    SSR_li = [i for i in equip_info.keys() if equip_info[i]['level'] == 4]
    UR_li = [i for i in equip_info.keys() if equip_info[i]['level'] == 5]
    MR_li = [i for i in equip_info.keys() if equip_info[i]['level'] == 6]
    result_li = []
    result_li.extend(random.sample(N_li, 5))
    result_li.extend(random.sample(R_li, 4))
    result_li.extend(random.sample(SR_li, 3))
    result_li.extend(random.sample(SSR_li, 2))
    result_li.extend(random.sample(UR_li, 1))
    if random.randint(1, 100) == 1:
        result_li.extend(random.sample(MR_li, 1))
    return result_li


# 装备售价
equip_price_li = [2, 5, 10, 20, 50, 200]


@sv.on_fullmatch(['副本商城'])
async def equip_shop(bot, ev: CQEvent):
    # 每天随机 可选
    li = sample_euqip()
    # 价格
    # N:2 R:5 SR:10 SSR:20 UR:50

    tas_list = []
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    myscore = CE._get_dunscore(gid, uid)
    msg_t = f"您的副本币为{myscore}，每日可以兑换装备5次"
    # 合并转发：
    data = {
        "type": "node",
        "data": {
            "name": "ご主人様",
            "uin": "1587640710",
            "content": msg_t
        }
    }
    tas_list.append(data)
    msg = ''
    for equip_id in li:
        info = equip_info[equip_id]
        price = equip_price_li[info['level'] - 1]
        desc = get_equip_desc(info)
        msg = msg + f"装备信息：{desc}\n售价(副本币)：{price}\n"
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


@sv.on_prefix(['兑换装备'])
async def buy_equip(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().strip()
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    # 判定每日上限
    guid = gid, uid
    if not daily_equip_limiter.check(guid):
        await bot.send(ev, '今天的兑换次数已经超过上限了哦，明天再来吧。', at_sender=True)
        return
    if not args:
        await bot.send(ev, '请输入兑换装备+装备名称。', at_sender=True)
        return
    li = sample_euqip()
    name_map = {equip_info[i]['name']: equip_info[i]['eid'] for i in li}
    eid = name_map.get(args)
    if not eid:
        await bot.send(ev, f'今日商城没有名为"{args}"的装备，请使用"副本商城"指令检查', at_sender=True)
        return
    price = equip_price_li[equip_info[str(eid)]['level'] - 1]
    myscore = CE._get_dunscore(gid, uid)
    if myscore < price:
        await bot.finish(ev, f'副本币不足，兑换[{args}]需要副本币{price},当前副本币{myscore}', at_sender=True)

    CE._add_dunscore(gid, uid, -price)
    CE._add_equip(gid, uid, eid, 1)
    desc = get_equip_desc(equip_info[str(eid)])
    msg = f"兑换装备成功！({desc})"
    await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch(['我的副本币', '查看副本币', '查副本币', '查询副本币', '副本币查询'])
async def get_my_dunscore(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    CE = CECounter()
    myscore = CE._get_dunscore(gid, uid)
    await bot.send(ev, f"您的副本币为{myscore}", at_sender=True)
