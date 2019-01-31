import formate
import user_controller
import character_controller
from config.base_config import *


# 控制人物属性


# 查看当前角色属性
def watch_attribute(content):
    sender = content['sender']
    user_id = sender['user_id']
    user = user_controller.get_user(user_id)
    character_name = user.current_character
    character = character_controller.get_charater(user_id, character_name)

    if character is None:
        return '当前没有角色'
    sb = f'角色：{character.name}'
    race=character.race.name if character.race is not None else None
    sb += f'\n种族：{race}'
    if character.race and character.race.sub_race is not None:
        sb += f' - {character.race.sub_race}'

    job=character.job.name if character.job is not None else None
    sb += f'\n职业：{job}'
    language_msg = formate.formate_list(character.language) if character.language is not None and len(
        character.language) else None
    sb += f'\n语言：{language_msg}'
    sb += f'\n行走速度：{character.speed}'

    attr_msg=formate.formate_dic(character.base_attr)
    sb += f'\n基础属性：{attr_msg}'
    if character.status == 'gen':
        sb += f'\n状态：生成角色中，请使用.swap交换属性，使用.race选择种族，使用.job选择职业 .gened结束生成'
    if character.status == 'normal':
        f'\n状态：正常 请愉快的进行游戏吧'
    if character.status == 'lv_up':
        sb += f'\n状态：升级中，请使用.lvup 查看选择对应的技能或属性'
    cur_attr_msg = formate.formate_dic(character.cur_attr) if character.cur_attr is not None else None
    sb += f'\n当前属性：{cur_attr_msg}'
    check_attr_msg = formate.formate_dic(character.cur_check) if character.cur_check is not None else None
    sb += f'\n鉴定值：{check_attr_msg}'
    skilled_weapon_msg = formate.formate_list(character.skilled_weapon) if character.skilled_weapon is not None and len(
        character.skilled_weapon) else None
    sb += f'\n武器熟练：{skilled_weapon_msg}'

    skilled_armor_msg = formate.formate_list(character.skilled_armor) if character.skilled_armor is not None and len(
        character.skilled_armor) else None
    sb += f'\n盔甲熟練：{skilled_armor_msg}'

    skilled_item_msg = formate.formate_list(character.skilled_item) if character.skilled_item is not None and len(
        character.skilled_item) else None
    sb += f'\n熟练项：{skilled_item_msg}'

    skilled_tool_msg = formate.formate_list(character.skilled_tool) if character.skilled_tool is not None and len(
        character.skilled_tool) else None
    sb += f'\n熟练工具：{skilled_tool_msg}'

    race_skill_msg = formate.formate_list(character.race.race_skill) if character.race and character.race.race_skill is not None and len(
        character.race.race_skill) else None
    sb += f'\n种族技能：{race_skill_msg}'
    if character.notice is not None and len(character.notice):
        sb += f'\n通知：'
        for s in character.notice.values():
            sb += '\n\t' + s.get('msg')
    return sb


# 获得角色列表
def get_user_list(content):
    sender = content['sender']
    user_id = sender['user_id']
    nickname = sender['nickname']
    user = user_controller.get_user(user_id)
    if user is None:
        return '用户下没有角色'
    else:
        if user.user_list is None:
            return '用户下没有角色'
        sb = ''
        for un in user.user_list:
            sb += '\n' + un
        return f'{nickname}用户下的角色有：' + sb


# 切换用户
def switch_user(content):
    sender = content['sender']
    user_id = sender['user_id']
    message = content['message']
    cmd_msg = message.replace('.switch ', '')
    user = user_controller.get_user(user_id)
    if cmd_msg in user.user_list:
        user.current_character=cmd_msg
        user_controller.save_user(user)
        return f'切换角色成功 当前角色为 {cmd_msg}'
    else:
        return '当前用户没有此角色'


# 增加属性
def attr_up(content):
    sender = content['sender']
    user_id = sender['user_id']
    message = content['message']
    cmd_msg = message.replace('.attrup ', '')
    attr_up_list = str(cmd_msg).split(' ')
    if not len(attr_up_list):
        return '请选择要提升的属性值'
    if len(attr_up_list) != len(set(attr_up_list)):
        return '不允许出现重复属性'
    for a in attr_up_list:
        if a not in ATTRIBUTE:
            return f'输入的属性{a}不存在'
    user = user_controller.get_user(user_id)
    character_name = user.current_character
    character = character_controller.get_charater(user_id, character_name)

    if character.notice is not None:
        attr_up = character.notice.get('attr_up')
        if attr_up is not None:
            num = attr_up.get('num')
            if num == len(attr_up_list):

                for a in attr_up_list:
                    character.cur_attr[a] += 1
                character.refresh_check()
                character.notice.pop('attr_up')
                character_controller.save_charater(user_id, character)
                return '变更属性成功'
            else:
                return f'请输入{num}个不同类型的属性'

    return '当前角色不可提升属性'

# 增加语言
def select_language(content):
    sender = content['sender']
    user_id = sender['user_id']
    message = content['message']
    cmd_msg = message.replace('.language ', '')
    language_list = str(cmd_msg).split(' ')
    if not len(language_list):
        return '请选择语言'

    user = user_controller.get_user(user_id)
    character_name = user.current_character
    character = character_controller.get_charater(user_id, character_name)

    if len(language_list) != len(set(language_list)):
        return '不允许出现重复的语言'
    for a in language_list:
        if a not in LANGUAGE:
            return f'输入的属性{a}不存在'
        if a in character.language:
            return f'人物已经具备说 {a} 的能力'
    if character.notice:
        select_language = character.notice.pop('select_language')
        if select_language:
            num = select_language.get('num')
            if num == len(language_list):
                character.language+=language_list
                character_controller.save_charater(user_id, character)
                return '选择语言成功'
            else:
                return f'请输入{num}个不同类型的语言'

    return '当前角色不可选择语言'

def init_equip(content):
    return '功能未实现'

def skilled_item(content):
    return '功能未实现'

def select_style(content):
    return '功能未实现'