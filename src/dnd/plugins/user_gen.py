import user_controller
import character_controller
from character_dto import *


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


def reroll(content):
    # 重新roll点
    sender = content['sender']
    nickname = sender['nickname']
    user_id = sender['user_id']
    user = user_controller.get_user(user_id)
    character_name = user.current_character
    character = character_controller.get_charater(user_id, character_name)
    if character is None:
        return f'{nickname} 请先创建角色'
    if character.status != 'gen':
        return '用户已经创建完成 不可变更属性'
    if character.re_roll_time <= 0:
        return f'角色 {user_name} 已经没有重新roll点次数'
    character.re_roll_time -= 1
    attr = character_controller.init_attribute()
    character.base_attr = attr
    character.refresh()
    character_controller.save_charater(user_id, character)
    return f'角色 {character_name} 重新roll点成功\n新属性 {formate.formate_dic(attr)}\n可重新roll点次数为{character.re_roll_time}'


def switch_race(content):
    user_id = content['sender']['user_id']
    comm = content['message']
    comm = comm.replace('.race ', '')
    if comm not in RACE:
        return f'种族{comm}不存在'
    user = user_controller.get_user(user_id)
    character_name = user.current_character
    character = character_controller.get_charater(user_id, character_name)

    if character.status != 'gen':
        return f'{character.name} 已经创建完成 不能再重新选择种族'
    character.race = Race({})
    character.race.name = comm
    character.refresh()
    character_controller.save_charater(user_id, character)
    return f'选择种族{comm}成功，请使用.attr查看角色状态'


def switch_job(content):
    return '功能未实现'


def switch_sub_race(content):
    user_id = content['sender']['user_id']
    comm = content['message']
    comm = comm.replace('.subrace ', '')
    user = user_controller.get_user(user_id)
    character_name = user.current_character
    character = character_controller.get_charater(user_id, character_name)

    if character.notice is None:
        return '当前角色不可选择亚种'
    select_sub_job = character.notice.pop('select_sub_job')
    if select_sub_job:
        race = character.race.name
        sub_race_list = RACE_DESCRIBE.get(race).get('ex_race')
        if comm in sub_race_list.keys():
            character.race.sub_race = comm
            character.refresh()
            character_controller.save_charater(user_id, character)
            return f'选择亚种{comm}成功,请使用.attr查看角色状态'
    return '当前角色不可选择亚种'

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

def swap(content):
    # 交换属性
    comm = content['message']
    comm = comm.replace('.swap ', '')
    attr_list = comm.split(' ')
    attr1 = attr_list[0]
    if attr1 not in ATTRIBUTE:
        return f'不存在 {attr1} 这种属性'
    attr2 = attr_list[1]
    if attr2 not in ATTRIBUTE:
        return f'不存在 {attr2} 这种属性'
    if attr1 == attr2:
        return '请输入两种不同的属性'
    user_id = content['sender']['user_id']
    user = user_controller.get_user(user_id)
    character_name = user.current_character
    character = character_controller.get_charater(user_id, character_name)

    if character.status != 'gen':
        return '用户已经创建完成 不可变更属性'
    cache = character.base_attr[attr1]
    character.base_attr[attr1] = character.base_attr[attr2]
    character.base_attr[attr2] = cache
    character.refresh()
    character_controller.save_charater(user_id, character)
    return '交换属性成功'