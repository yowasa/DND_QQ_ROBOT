import user_controller
import character_controller
from character_dto import *
from job_config import JOB
from msg import filter


# 生成角色
@filter(r'.gen ')
def gen(content):
    # 获得用户
    sender = content['sender']
    user_id = sender['user_id']
    comm = content['message']
    comm = comm.replace('.gen ', '')
    if comm == '':
        return '请输入名称'
    if ' ' in comm.strip():
        return '名称种请不要带空格'
    msg = character_controller.gen_user(user_id, comm)
    return msg


# 重新骰点
@filter(r'.reroll', need_character=True)
def reroll(content):
    nickname = content['sender']['nickname']
    # 重新roll点
    user = content.get('sys_user')
    character = content.get('sys_character')
    if character:
        return f'{nickname} 请先创建角色'
    if character.status != 'gen':
        return '用户已经创建完成 不可变更属性'
    if character.re_roll_time <= 0:
        return f'角色 {user_name} 已经没有重新roll点次数'
    character.re_roll_time -= 1
    attr = character_controller.init_attribute()
    character.base_attr = attr
    character.refresh()
    character_controller.save_charater(user.user_id, character)
    return f'角色 {character_name} 重新roll点成功\n新属性 {formate.formate_dic(attr)}\n可重新roll点次数为{character.re_roll_time}'


# 选择种族
@filter(r'.race ', need_character=True)
def switch_race(content):
    comm = content['cmd_msg']
    if comm not in RACE:
        return f'种族{comm}不存在'
    user = content['sys_user']
    character = content['sys_character']

    if character.status != 'gen':
        return f'{character.name} 已经创建完成 不能再重新选择种族'
    character.race = Race({})
    character.race.name = comm
    character.refresh()
    character_controller.save_charater(user.user_id, character)
    return f'选择种族{comm}成功，请使用.attr查看角色状态'


# 选择职业
@filter(r'.job ')
def switch_job(content):
    user_id = content['sender']['user_id']
    comm = content['message']
    comm = comm.replace('.job ', '')
    if comm not in JOB:
        return f'职业{comm}不存在'
    user = user_controller.get_user(user_id)
    character_name = user.current_character
    character = character_controller.get_charater(user_id, character_name)

    if character.status != 'gen':
        return f'{character.name} 已经创建完成 不能再重新选择职业'
    character.job = Job({})
    character.job.name = comm
    character.refresh()
    character_controller.save_charater(user_id, character)
    return f'选择职业{comm}成功，请使用.attr查看角色状态'


# 选择亚种
@filter(r'.subrace ', need_character=True)
def switch_sub_race(content):
    comm = content['message']
    comm = comm.replace('.subrace ', '')
    user = content['sys_user']
    character = content['sys_character']

    if character.notice is None:
        return '当前角色不可选择亚种'
    select_sub_job = character.notice.pop('select_sub_job')
    if select_sub_job:
        race = character.race.name
        sub_race_list = RACE_DESCRIBE.get(race).get('ex_race')
        if comm in sub_race_list.keys():
            character.race.sub_race = comm
            character.refresh()
            character_controller.save_charater(user.user_id, character)
            return f'选择亚种{comm}成功,请使用.attr查看角色状态'
    return '当前角色不可选择亚种'


# 删除角色
@filter(r'.drop ')
def drop(content):
    # 获得用户
    sender = content['sender']
    user_id = sender['user_id']
    comm = content['message']
    comm = comm.replace('.drop ', '')
    if comm == '':
        return '请输入名称'
    if ' ' in comm.strip():
        return '名称种请不要带空格'
    msg = character_controller.drop(user_id, comm)
    return msg


# 交换属性
@filter('.swap', need_character=True)
def swap(content):
    # 交换属性
    comm = content['cmd_msg']
    attr_list = comm.split(' ')
    attr1 = attr_list[0]
    if attr1 not in ATTRIBUTE:
        return f'不存在 {attr1} 这种属性'
    attr2 = attr_list[1]
    if attr2 not in ATTRIBUTE:
        return f'不存在 {attr2} 这种属性'
    if attr1 == attr2:
        return '请输入两种不同的属性'
    user = content['sys_user']
    character = content['sys_character']

    if character.status != 'gen':
        return '用户已经创建完成 不可变更属性'
    cache = character.base_attr[attr1]
    character.base_attr[attr1] = character.base_attr[attr2]
    character.base_attr[attr2] = cache
    character.refresh()
    character_controller.save_charater(user.user_id, character)
    return '交换属性成功'


# 设定性别
@filter(r'.sex ', need_character=True)
def set_sex(content):
    user = content['sys_user']
    character = content['sys_character']
    cmd_msg = content['cmd_msg']
    if character.status != 'gen':
        return '用户已经创建完成 不可变更属性'
    if cmd_msg not in ['男', '女', '扶她', '秀吉']:
        return f'请选择正确的性别'
    character.sex = cmd_msg
    character_controller.save_charater(user.user_id, character)
    return f'设置性别 {cmd_msg} 成功'


# 增加背景描述
@filter(r'.desc ', need_character=True)
def set_desc(content):
    user = content['sys_user']
    character = content['sys_character']
    cmd_msg = content['cmd_msg']
    if character.status != 'gen':
        return '用户已经创建完成 不可变更属性'
    if not character.background:
        return f'请先选择背景'
    character.background.desc = cmd_msg
    character_controller.save_charater(user.user_id, character)
    return f'增加背景描述成功'
