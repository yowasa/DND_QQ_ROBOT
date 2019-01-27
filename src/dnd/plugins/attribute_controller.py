import character
import formateUtil
from config import *


# 控制人物属性

# 生成属性并展示
def random_attribute():
    attr = character.init_attribute()
    return formateUtil.formate_dic(attr)


# 查看当前角色属性
def watch_attribute(content):
    sender = content['sender']
    user_id = sender['user_id']
    user = character.get_current_user_info(user_id)
    if user is None:
        return '当前没有角色'
    user_name = user['name']
    attr = user['attribute']
    attr_msg = formateUtil.formate_dic(attr)
    cur_attr = user.get('cur_attr')
    check_attr = user.get('check_attr')
    status = user['status']
    race = user.get('race')
    sub_race = user.get('sub_race')
    job = user.get('job')
    sb = f'角色：{user_name}'
    sb += f'\n种族：{race}'
    if sub_race is not None:
        sb += f' - {sub_race}'
    sb += f'\n职业：{job}'
    language = user.get('language')
    language_msg = formateUtil.formate_list(language) if language is not None and len(
        language) else None
    sb += f'\n语言：{language_msg}'
    speed = user.get('speed')
    sb += f'\n行走速度：{speed}'
    sb += f'\n基础属性：{attr_msg}'
    if status == 'gen':
        sb += f'\n状态：生成角色中，请使用.swap交换属性，使用.race选择种族，使用.job选择职业 .gened结束生成'
    if status == 'normal':
        f'\n状态：通常 请愉快的进行游戏吧'
    if status == 'lv_up':
        sb += f'\n状态：升级中，请使用.lvup 查看选择对应的技能或属性'
    cur_attr_msg = formateUtil.formate_dic(cur_attr) if cur_attr is not None else None
    sb += f'\n当前属性：{cur_attr_msg}'
    check_attr_msg = formateUtil.formate_dic(check_attr) if check_attr is not None else None
    sb += f'\n鉴定值：{check_attr_msg}'
    skilled_weapon = user.get('skilled_weapon')
    skilled_weapon_msg = formateUtil.formate_list(skilled_weapon) if skilled_weapon is not None and len(
        skilled_weapon) else None
    sb += f'\n武器熟练：{skilled_weapon_msg}'

    skilled_eq = user.get('skilled_eq')
    skilled_eq_msg = formateUtil.formate_list(skilled_eq) if skilled_weapon is not None and len(
        skilled_eq) else None
    sb += f'\n盔甲熟練：{skilled_eq_msg}'

    race_skill=user.get('race_skill')
    race_skill_msg = formateUtil.formate_list(race_skill) if skilled_weapon is not None and len(
        race_skill) else None
    sb += f'\n种族技能：{race_skill_msg}'
    pc_op = user.get('pc_op')
    if pc_op is not None and len(pc_op):
        sb += f'\n通知：'
        for s in pc_op.values():
            sb += '\n\t' + s.get('msg')
    return sb


# 获得角色列表
def get_user_list(content):
    sender = content['sender']
    user_id = sender['user_id']
    nickname = sender['nickname']
    dic = character.get_base_user_info(user_id)
    if dic is None:
        return '用户下没有角色'
    else:
        user_list = dic['user_list']
        if user_list is None:
            return '用户下没有角色'
        sb = str()
        print(user_list)
        for un in user_list:
            sb += '\n' + un
        return f'{nickname}用户下的角色有：' + sb


# 切换用户
def switch_user(content):
    sender = content['sender']
    user_id = sender['user_id']
    message = content['message']
    cmd_msg = message.replace('.switch ', '')
    dic = character.get_base_user_info(user_id)
    user_list = dic.get('user_list')
    if cmd_msg in user_list:
        dic['current_user'] = cmd_msg
        character.update_base_user_info(user_id, dic)
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
    user = character.get_current_user_info(user_id)
    pc_op = user.get('pc_op')
    if pc_op is not None:
        attr_up = pc_op.get('attr_up')
        if attr_up is not None:
            num = attr_up.get('num')
            if num == len(attr_up_list):
                cur_attr = user.get('cur_attr')
                for a in attr_up_list:
                    cur_attr[a] += 1
                user['check_attr'] = character.refresh_check_list(cur_attr)
                pc_op.pop('attr_up')
                character.update_user(user_id, user)
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

    user = character.get_current_user_info(user_id)
    language = user.get('language')
    if len(language_list) != len(set(language_list)):
        return '不允许出现重复的语言'
    for a in language_list:
        if a not in LANGUAGE:
            return f'输入的属性{a}不存在'
        if a in language:
            return f'人物已经具备说 {a} 的能力'
    pc_op = user.get('pc_op')
    if pc_op is not None:
        select_language = pc_op.get('select_language')
        if select_language is not None:
            num = select_language.get('num')
            if num == len(language_list):
                language+=language_list
                pc_op.pop('select_language')
                character.update_user(user_id, user)
                return '选择语言成功'
            else:
                return f'请输入{num}个不同类型的语言'

    return '当前角色不可选择语言'
