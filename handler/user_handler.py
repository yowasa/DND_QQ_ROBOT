from filter import msg_route
from tool.dnd_db import *


# 获得用户下角色列表
@msg_route(r'\s*\.ul', need_user=True)
def get_user_list(content):
    nickname = content['sender']['nickname']
    user = content['sys_user']
    cha_list = []
    query = Character.select().where(Character.user_id == user.id)
    for s in query:
        cha_list.append(s.name)
    sb = ''
    for un in cha_list:
        sb += '\n' + un
    return f'{nickname}用户下的角色有：' + sb


# 切换用户角色
@msg_route(r'\s*\.switch ', need_user=True)
def switch_user(content):
    cmd_msg = content['cmd_msg']
    user = content['sys_user']
    character = Character.get_or_none(Character.user_id == user.id, Character.name == cmd_msg)
    if character:
        user.cur_character_id = character.id
        user.save()
        return f'切换角色成功 当前角色为 {cmd_msg}'
    return '当前用户没有此角色'


# 删除角色
@msg_route(r'\s*\.drop ', need_character=True)
def drop(content):
    cmd_msg = content.get('cmd_msg')
    if not cmd_msg or cmd_msg == '':
        return '请输入名称'
    user = content.get('sys_user')
    sys_character = content.get('sys_character')
    character = Character.get_or_none(Character.name == cmd_msg, Character.user_id == user.id)
    if not character:
        return f'角色 {cmd_msg} 不存在，无需删除'
    cha_id = character.id
    character.delete_instance()
    # 清空属性关联的信息
    delete_ref(cha_id)
    # 更改用户当前角色
    if user.cur_character_id == cha_id:
        other_cha = Character.get_or_none(Character.user_id == user.id)
        if other_cha:
            user.cur_character_id = other_cha.id
        else:
            user.cur_character_id = None
        user.save()
        return f'删除角色 {cmd_msg} 成功，当前角色为{other_cha.name if other_cha else "None" }\n'
    else:
        user.cur_character_id
        return f'删除角色 {cmd_msg} 成功，当前角色为{sys_character.name}\n'


# 删除角色关联内容
def delete_ref(cha_id):
    # 删除属性
    Attribute.delete().where(Attribute.character_id == cha_id).execute()
    CharacterLanguage.delete().where(CharacterLanguage.character_id == cha_id).execute()
    CharacterSkill.delete().where(CharacterSkill.character_id == cha_id).execute()
    CharacterSkilled.delete().where(CharacterSkilled.character_id == cha_id).execute()
