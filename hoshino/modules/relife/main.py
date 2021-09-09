# 人生重开模拟器
import random

from hoshino import Service
from hoshino.typing import CQEvent, CommandSession
from . import comm
from . import event
from .RelifeCounter import RelifeCounter
from .condition import checkCondition
from hoshino.util import FreqLimiter

_flmt = FreqLimiter(3)
"""
人生重开模拟器相关功能
"""

sv = Service('人生重开模拟器', enable_on_default=True, bundle='人生重开模拟器', help_=
'''[人生重开]
[下一年]
[下十年]
[分配属性]
''')


# 判断初始属性点增益
def judge_attribute_buff(choose_talent_li):
    sum = 0
    for i in choose_talent_li:
        if comm.talent_config[i].get('status'):
            sum += comm.talent_config[i].get('status')
    return sum


# 随机分割数字
def random_split(sum, num):
    z = []
    ret = random.sample(range(1, sum), num - 1)
    ret.append(0)
    ret.append(sum)
    ret.sort()
    for i in range(len(ret) - 1):
        z.append(ret[i + 1] - ret[i])
    return z


@sv.on_command("重置人生")
async def relife_start(session: CommandSession):
    bot = session.bot
    ev = session.event
    uid = ev.user_id
    gid = ev.group_id
    counter = RelifeCounter()
    user = counter._get_relife(gid, uid)
    user.state = 0
    counter._save_relife(user)
    await bot.send(ev, f"人生信息已经重置，请发送'人生重开'开启新的人生", at_sender=True)


@sv.on_command("人生重开")
async def relife_start(session: CommandSession):
    bot = session.bot
    ev = session.event
    uid = ev.user_id
    gid = ev.group_id
    counter = RelifeCounter()
    user = counter._get_relife(gid, uid)
    if user.state != 0:
        await bot.send(ev, f"你当前人生还未结束，请先度过余生", at_sender=True)
        return
        # 获取重开次数
    time = user.re_time
    # 随机天赋
    ratain_talent = user.talent
    talent_li = []
    if session.state.get('talent_li'):
        talent_li = session.state.get('talent_li')
    else:
        radom_num = 10
        chi = comm.talent_config.keys()
        if ratain_talent != 0:
            radom_num -= 1
            talent_li.append(ratain_talent)
            chi.remove(ratain_talent)
        random_result = random.sample(chi, radom_num)
        talent_li.extend(random_result)
        session.state['talent_li'] = talent_li
    talent_choose_msg = '\n'.join(
        [f"{index}.{comm.talent_config[i]['name']}({comm.talent_config[i]['description']})" for index, i in
         enumerate(talent_li)])

    choose_talent = session.get('choose_talent', prompt=f"你已经重开了{time}次人生,请选择你的初始天赋(发送三个数字用空格隔开)\n{talent_choose_msg}")
    choose_talent = str(choose_talent).strip()
    choose_talent_li = choose_talent.split(" ")
    if len(choose_talent_li) < 3:
        del session.state['choose_talent']
        session.get('choose_talent',
                    prompt=f"请选择'3'个天赋(发送三个数字用空格隔开)：\n{talent_choose_msg}")
    talnet_li = []
    for i in choose_talent_li:
        i = talent_li[int(i)]
        talnet_li.append(i)
        if comm.talent_config[i].get('exclusive'):
            for j in comm.talent_config[i].get('exclusive'):
                if j in choose_talent_li:
                    session.get('choose_talent',
                                prompt=f"天赋{comm.talent_config[i]['name']}与天赋{comm.talent_config[j]['name']}不能共存 请重新请选择'3'个天赋(发送三个数字用空格隔开)：\n{talent_choose_msg}")

    # 天赋选择完成
    # 开始分配属性点
    attribute_max = 20 + judge_attribute_buff(talnet_li)
    if attribute_max > 0:
        random_attr = random_split(attribute_max, 4)
    else:
        random_attr = [0, 0, 0, 0]
    await bot.send(ev,
                   f"已为你随机分配属性点,可以通过'分配属性'变更\n颜值:{random_attr[0]} 智力:{random_attr[1]} 体质{random_attr[2]} 家境:{random_attr[3]}",
                   at_sender=True)

    user.data['天赋'] = talnet_li
    user.data['初始属性和'] = attribute_max
    user.data['颜值'] = random_attr[0]
    user.data['智力'] = random_attr[1]
    user.data['体质'] = random_attr[2]
    user.data['家境'] = random_attr[3]
    user.data['快乐'] = 5
    # 事件
    user.data['事件'] = []
    # 消息log
    user.data['msg_log'] = []
    # 已经触发的天赋
    user.data['triggerTalents'] = []
    # 存活标识
    user.data['存活'] = 1
    # 初始化年龄
    user.data['年龄'] = -1
    # 状态 0 等待重开 1 等待分配点数 2 正在进行人生
    user.state = 1
    counter._save_relife(user)
    return


@sv.on_command("分配属性")
async def attr_set(session: CommandSession):
    bot = session.bot
    ev = session.event
    uid = ev.user_id
    gid = ev.group_id
    counter = RelifeCounter()
    user = counter._get_relife(gid, uid)
    if user.state != 1:
        if user.state == 0:
            await bot.send(ev, "请先重开人生再分配属性", at_sender=True)
        if user.state == 2:
            await bot.send(ev, "已经开始的人生无法分配属性", at_sender=True)
        return
    total = user.data['初始属性和']
    chr = session.get("颜值", prompt=f"请输入你分配给颜值的属性值(剩余属性为{total})")
    if not str(chr).isdecimal():
        del session.state['颜值']
        session.get("颜值", prompt=f"请输入正确的'数字'分配给颜值(剩余属性为{total})")
    chr = int(chr)
    if chr > total:
        del session.state['颜值']
        session.get("颜值", prompt=f"你分配的颜值大于可分配属性，请重新输入(剩余属性为{total})")
    total -= chr

    _int = session.get("智力", prompt=f"请输入你分配给智力的属性值(剩余属性为{total})")
    if not str(_int).isdecimal():
        del session.state['智力']
        session.get("智力", prompt=f"请输入正确的'数字'分配给智力(剩余属性为{total})")
    _int = int(_int)
    if _int > total:
        del session.state['智力']
        session.get("智力", prompt=f"你分配的智力大于可分配属性，请重新输入(剩余属性为{total})")
    total -= _int

    _str = session.get("体质", prompt=f"请输入你分配给体质的属性值(剩余属性为{total})")
    if not str(_str).isdecimal():
        del session.state['体质']
        session.get("体质", prompt=f"请输入正确的'数字'分配给体质(剩余属性为{total})")
    _str = int(_str)
    if _str > total:
        del session.state['体质']
        session.get("体质", prompt=f"你分配的体质大于可分配属性，请重新输入(剩余属性为{total})")
    total -= _str
    mny = total
    confirm = session.get("确认", prompt=f"当前属性为\n颜值:{chr} 智力:{_int} 体质{_str} 家境:{mny}\n请回复'确认'完成变更")
    if str(confirm).strip() == '确认':
        user.data['颜值'] = chr
        user.data['智力'] = _int
        user.data['体质'] = _str
        user.data['家境'] = mny
        counter._save_relife(user)
        await bot.send(ev, "已完成分配", at_sender=True)
    else:
        await bot.send(ev, "已取消分配", at_sender=True)


def summary(user):
    data = {
        "CHR": [
            {"judge": "地狱", "grade": 0},
            {"min": 1, "judge": "折磨", "grade": 0},
            {"min": 2, "judge": "不佳", "grade": 0},
            {"min": 4, "judge": "普通", "grade": 0},
            {"min": 7, "judge": "优秀", "grade": 1},
            {"min": 9, "judge": "罕见", "grade": 2},
            {"min": 11, "judge": "逆天", "grade": 3},
        ],
        "MNY": [
            {"judge": "地狱", "grade": 0},
            {"min": 1, "judge": "折磨", "grade": 0},
            {"min": 2, "judge": "不佳", "grade": 0},
            {"min": 4, "judge": "普通", "grade": 0},
            {"min": 7, "judge": "优秀", "grade": 1},
            {"min": 9, "judge": "罕见", "grade": 2},
            {"min": 11, "judge": "逆天", "grade": 3},
        ],
        "SPR": [
            {"judge": "地狱", "grade": 0},
            {"min": 1, "judge": "折磨", "grade": 0},
            {"min": 2, "judge": "不幸", "grade": 0},
            {"min": 4, "judge": "普通", "grade": 0},
            {"min": 7, "judge": "幸福", "grade": 1},
            {"min": 9, "judge": "极乐", "grade": 2},
            {"min": 11, "judge": "天命", "grade": 3},
        ],
        "INT": [
            {"judge": "地狱", "grade": 0},
            {"min": 1, "judge": "折磨", "grade": 0},
            {"min": 2, "judge": "不佳", "grade": 0},
            {"min": 4, "judge": "普通", "grade": 0},
            {"min": 7, "judge": "优秀", "grade": 1},
            {"min": 9, "judge": "罕见", "grade": 2},
            {"min": 11, "judge": "逆天", "grade": 3},
            {"min": 21, "judge": "识海", "grade": 3},
            {"min": 131, "judge": "元神", "grade": 3},
            {"min": 501, "judge": "仙魂", "grade": 3},
        ],
        "STR": [
            {"judge": "地狱", "grade": 0},
            {"min": 1, "judge": "折磨", "grade": 0},
            {"min": 2, "judge": "不佳", "grade": 0},
            {"min": 4, "judge": "普通", "grade": 0},
            {"min": 7, "judge": "优秀", "grade": 1},
            {"min": 9, "judge": "罕见", "grade": 2},
            {"min": 11, "judge": "逆天", "grade": 3},
            {"min": 21, "judge": "凝气", "grade": 3},
            {"min": 101, "judge": "筑基", "grade": 3},
            {"min": 401, "judge": "金丹", "grade": 3},
            {"min": 1001, "judge": "元婴", "grade": 3},
            {"min": 2001, "judge": "仙体", "grade": 3},
        ],
        "AGE": [
            {"judge": "胎死腹中", "grade": 0},
            {"min": 1, "judge": "早夭", "grade": 0},
            {"min": 10, "judge": "少年", "grade": 0},
            {"min": 18, "judge": "盛年", "grade": 0},
            {"min": 40, "judge": "中年", "grade": 0},
            {"min": 60, "judge": "花甲", "grade": 1},
            {"min": 70, "judge": "古稀", "grade": 1},
            {"min": 80, "judge": "杖朝", "grade": 2},
            {"min": 90, "judge": "南山", "grade": 2},
            {"min": 95, "judge": "不老", "grade": 3},
            {"min": 100, "judge": "修仙", "grade": 3},
            {"min": 500, "judge": "仙寿", "grade": 3},
        ],
        "SUM": [
            {"judge": "地狱", "grade": 0},
            {"min": 41, "judge": "折磨", "grade": 0},
            {"min": 50, "judge": "不佳", "grade": 0},
            {"min": 60, "judge": "普通", "grade": 0},
            {"min": 80, "judge": "优秀", "grade": 1},
            {"min": 100, "judge": "罕见", "grade": 2},
            {"min": 110, "judge": "逆天", "grade": 3},
            {"min": 120, "judge": "传说", "grade": 3},
        ]
    }

    eff_li = ["SPR", "MNY", "CHR", "STR", "INT", "AGE", "SUM"]
    key_li = ["快乐", "家境", "颜值", "体质", "智力", "年龄", "总评"]
    user.data['总评'] = user.data["快乐"] * 2 + user.data["家境"] + user.data["颜值"] + user.data["体质"] + user.data["智力"] + \
                      user.data["年龄"] * 0.5

    msg_li = []
    for type in eff_li:
        length = len(data[type])
        index = eff_li.index(type)
        value = user.data[key_li[index]]
        while length:
            length -= 1
            case = data[type][length]
            if not case.get('min'):
                break
            if value >= case.get('min'):
                break
        msg_li.append(f'{key_li[index]}:{user.data[key_li[index]]}({case.get("judge")})')
    return '\n'.join(msg_li)


@sv.on_fullmatch("下一年")
async def next_year(bot, ev: CQEvent):
    uid = ev.user_id
    gid = ev.group_id
    guid = gid, uid
    if not _flmt.check(guid):
        await bot.send(ev, '不要请求这么快！', at_sender=True)
        return

    counter = RelifeCounter()
    user = counter._get_relife(gid, uid)
    if user.state == 0 or not user.data.get('存活'):
        await bot.finish(ev, "请先使用'人生重开'指令", at_sender=True)
    start_age = user.data['年龄']
    msg_li = pass_year(user, 1)
    counter._save_relife(user)
    result_li = []
    for i in msg_li:
        start_age += 1
        result_li.append(f'{start_age}岁:{i}')
    await bot.send(ev, '\n' + '\n\n'.join(result_li), at_sender=True)
    if user.data['存活'] == 0:
        user.state = 0
        msg = summary(user)
        await bot.send(ev, f'\n{msg}', at_sender=True)
    counter._save_relife(user)


@sv.on_fullmatch("下十年")
async def next_ten_year(bot, ev: CQEvent):
    uid = ev.user_id
    gid = ev.group_id
    guid = gid, uid
    if not _flmt.check(guid):
        await bot.send(ev, '不要请求这么快！', at_sender=True)
        return
    counter = RelifeCounter()
    user = counter._get_relife(gid, uid)
    if user.state == 0 or not user.data.get('存活'):
        await bot.send(ev, "请先使用'人生重开'指令", at_sender=True)
    start_age = user.data['年龄']
    msg_li = pass_year(user, 10)
    counter._save_relife(user)
    result_li = []
    for i in msg_li:
        start_age += 1
        result_li.append(f'{start_age}岁:{i}')
    await bot.send(ev, '\n' + '\n\n'.join(result_li), at_sender=True)
    if user.data['存活'] == 0:
        user.state = 0
        user.re_time += 1
        msg = summary(user)
        await bot.send(ev, f'\n{msg}', at_sender=True)
    counter._save_relife(user)


# 执行天赋
def do_talnet(user):
    talents = user.data['天赋']
    matches = [x for x in talents if x not in user.data['triggerTalents']]
    for i in matches:
        talent_i = comm.talent_config[str(i)]
        if talent_i.get('effect'):
            if talent_i.get('condition'):
                if checkCondition(user, talent_i.get('condition')):
                    comm.buff_user(user, talent_i.get('effect'))
                    user.data['triggerTalents'].append(i)


# 度过n年
def pass_year(user, num):
    user.state = 1
    msg_li = []
    for i in range(num):
        # 年龄+1
        next_age(user)
        # 天赋判定
        do_talnet(user)
        # 事件判定
        desc = event.do_event(user)
        msg_li.append(desc)
        if user.data['存活'] == 0:
            break
    return msg_li


# 增长一岁
def next_age(user):
    user.data['年龄'] += 1
    return user.data['年龄']
