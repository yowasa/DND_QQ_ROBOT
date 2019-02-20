from filter import msg_route
from tool.dnd_db import *
from handler.dice_handler import init_attribute
import base.formate as fmt

ATTRIBUTE = ['力量', '体质', '敏捷', '智力', '感知', '魅力']

attr_type = {
    '可选': 1,
    '基础': 2,
    '当前': 3,
    '临时': 4
}

character_status = {
    '选择属性': 10,
}


# 生成角色
@msg_route(r'.gen ', need_user=True)
def gen(content):
    # 获得用户
    cmd_msg = content['cmd_msg']
    user = content.get('sys_user')

    if not cmd_msg or cmd_msg == '':
        return '请输入名称'

    character = Character.get_or_none(Character.user_id == int(user.id), Character.name == cmd_msg)
    if character:
        return f'角色{cmd_msg}已存在'
    character = Character(name=cmd_msg)
    character.user_id = user.id
    character.status = 10
    character.save()
    user.cur_character_id = character.id
    user.save()
    for _ in range(5):
        attr_dict = init_attribute()
        attr = fmt.dict2attr(attr_dict)
        attr.character_id = character.id
        attr.attr_type = 1
        attr.save()

    return f'生成角色 {character.name} 成功 使用.guid 操作查看创建指引\n'


sex_list = ['男', '女', '扶她', '秀吉']


@msg_route(r'.guid', need_character=True)
def guid_gen(content):
    user = content.get('sys_user')
    character = content.get('sys_character')
    if not character:
        return '当前没有角色'
    sb = f'角色：{character.name}'
    if character.status == 10:
        sb += '\n从以下属性中根据编号选择一组属性使用 .choose + 编号 选择一组属性使用'
        query = Attribute.select().where(Attribute.character_id == character.id, Attribute.attr_type == 1)
        inx = 0
        for s in query:
            inx += 1
            attr_dict = fmt.attr2dict(s)
            msg = fmt.attr_dict2str(attr_dict)
            sb += f'\n{inx} : {msg}'
    if character.status == 11:
        sb += '\n从以下种族中选择一个种族 .choose + 编号'
    return sb


@msg_route(r'.choose ', need_character=True)
def guid_choose(content):
    user = content.get('sys_user')
    character = content.get('sys_character')
    cmd_msg = content.get('cmd_msg')
    if character.status == 10:
        choose_num = int(cmd_msg)
        query = Attribute.select().where(Attribute.character_id == character.id, Attribute.attr_type == 1)
        flag = False
        inx = 0
        for s in query:
            inx += 1
            if inx == choose_num:
                flag = True
                s.attr_type = 2
                s.save()
            s.delete()
        if flag:
            character.status = 11
            character.save()
            return '选择属性成功,在角色创建完成之前可以任意调用.swap 交换你的属性值'
        return '请选择正确的数字'


@msg_route(r'.attr', need_character=True)
def watch_attribute(content):
    user = content.get('sys_user')
    character = content.get('sys_character')
    if not character:
        return '当前没有角色'

    sb = f'角色：{character.name}'
    if character.status > 10:
        attr = Attribute.get(Attribute.character_id == character.id, Attribute.attr_type == 2)
        attr_dict = fmt.attr2dict(attr)
        msg = fmt.attr_dict2str(attr_dict)
        sb = "基础属性为:"
        sb += "\n" + msg
    return sb
#     race = character.race.name if character.race is not None else None
#     sb += f'\n种族：{race}'
#     if character.race and character.race.sub_race is not None:
#         sb += f' - {character.race.sub_race}'
#
#     job = character.job.name if character.job is not None else None
#     sb += f'\n职业：{job}'
#     language_msg = formate.formate_list(character.language) if character.language is not None and len(
#         character.language) else None
#     sb += f'\n语言：{language_msg}'
#     sb += f'\n行走速度：{character.speed}'
#
#     attr_msg = formate.formate_dic(character.base_attr)
#     sb += f'\n基础属性：{attr_msg}'
#     if character.status == 'gen':
#         sb += f'\n状态：生成角色中，请使用.swap交换属性，使用.race选择种族，使用.job选择职业 .gened结束生成'
#     if character.status == 'normal':
#         f'\n状态：正常 请愉快的进行游戏吧'
#     if character.status == 'lv_up':
#         sb += f'\n状态：升级中，请使用.lvup 查看选择对应的技能或属性'
#     cur_attr_msg = formate.formate_dic(character.cur_attr) if character.cur_attr is not None else None
#     sb += f'\n当前属性：{cur_attr_msg}'
#     check_attr_msg = formate.formate_dic(character.cur_check) if character.cur_check is not None else None
#     sb += f'\n鉴定值：{check_attr_msg}'
#     skilled_weapon_msg = formate.formate_list(character.skilled_weapon) if character.skilled_weapon is not None and len(
#         character.skilled_weapon) else None
#     sb += f'\n武器熟练：{skilled_weapon_msg}'
#
#     skilled_armor_msg = formate.formate_list(character.skilled_armor) if character.skilled_armor is not None and len(
#         character.skilled_armor) else None
#     sb += f'\n盔甲熟練：{skilled_armor_msg}'
#
#     skilled_item_msg = formate.formate_list(character.skilled_item) if character.skilled_item is not None and len(
#         character.skilled_item) else None
#     sb += f'\n熟练项：{skilled_item_msg}'
#
#     skilled_tool_msg = formate.formate_list(character.skilled_tool) if character.skilled_tool is not None and len(
#         character.skilled_tool) else None
#     sb += f'\n熟练工具：{skilled_tool_msg}'
#
#     race_skill_msg = formate.formate_list(
#         character.race.race_skill) if character.race and character.race.race_skill is not None and len(
#         character.race.race_skill) else None
#     sb += f'\n种族技能：{race_skill_msg}'
#     if character.notice is not None and len(character.notice):
#         sb += f'\n通知：'
#         for s in character.notice.values():
#             sb += '\n\t' + s.get('msg')
#     return sb
#
#
#
# # 选择种族
# @msg_route(r'.race ', need_character=True)
# def switch_race(content):
#     comm = content['cmd_msg']
#     if comm not in RACE:
#         return f'种族{comm}不存在'
#     user = content['sys_user']
#     character = content['sys_character']
#
#     if character.status != 'gen':
#         return f'{character.name} 已经创建完成 不能再重新选择种族'
#     character.race = Race({})
#     character.race.name = comm
#     character.refresh()
#     character_controller.save_charater(user.user_id, character)
#     return f'选择种族{comm}成功，请使用.attr查看角色状态'
#
#
# # 选择职业
# @filter(r'.job ')
# def switch_job(content):
#     user_id = content['sender']['user_id']
#     comm = content['message']
#     comm = comm.replace('.job ', '')
#     if comm not in JOB:
#         return f'职业{comm}不存在'
#     user = user_controller.get_user(user_id)
#     character_name = user.current_character
#     character = character_controller.get_charater(user_id, character_name)
#
#     if character.status != 'gen':
#         return f'{character.name} 已经创建完成 不能再重新选择职业'
#     character.job = Job({})
#     character.job.name = comm
#     character.refresh()
#     character_controller.save_charater(user_id, character)
#     return f'选择职业{comm}成功，请使用.attr查看角色状态'
#
#
# # 选择亚种
# @msg_route(r'.subrace ', need_character=True)
# def switch_sub_race(content):
#     comm = content['message']
#     comm = comm.replace('.subrace ', '')
#     user = content['sys_user']
#     character = content['sys_character']
#
#     if character.notice is None:
#         return '当前角色不可选择亚种'
#     select_sub_job = character.notice.pop('select_sub_job')
#     if select_sub_job:
#         race = character.race.name
#         sub_race_list = RACE_DESCRIBE.get(race).get('ex_race')
#         if comm in sub_race_list.keys():
#             character.race.sub_race = comm
#             character.refresh()
#             character_controller.save_charater(user.user_id, character)
#             return f'选择亚种{comm}成功,请使用.attr查看角色状态'
#     return '当前角色不可选择亚种'
#
#
# # 删除角色
# @msg_route(r'.drop ')
# def drop(content):
#     # 获得用户
#     sender = content['sender']
#     user_id = sender['user_id']
#     comm = content['message']
#     comm = comm.replace('.drop ', '')
#     if comm == '':
#         return '请输入名称'
#     if ' ' in comm.strip():
#         return '名称种请不要带空格'
#     msg = character_controller.drop(user_id, comm)
#     return msg
#
#
# # 交换属性
# @msg_route('.swap', need_character=True)
# def swap(content):
#     # 交换属性
#     comm = content['cmd_msg']
#     attr_list = comm.split(' ')
#     attr1 = attr_list[0]
#     if attr1 not in ATTRIBUTE:
#         return f'不存在 {attr1} 这种属性'
#     attr2 = attr_list[1]
#     if attr2 not in ATTRIBUTE:
#         return f'不存在 {attr2} 这种属性'
#     if attr1 == attr2:
#         return '请输入两种不同的属性'
#     user = content['sys_user']
#     character = content['sys_character']
#
#     if character.status != 'gen':
#         return '用户已经创建完成 不可变更属性'
#     cache = character.base_attr[attr1]
#     character.base_attr[attr1] = character.base_attr[attr2]
#     character.base_attr[attr2] = cache
#     character.refresh()
#     character_controller.save_charater(user.user_id, character)
#     return '交换属性成功'
#
#
# # 设定性别
# @msg_route(r'.sex ', need_character=True)
# def set_sex(content):
#     user = content['sys_user']
#     character = content['sys_character']
#     cmd_msg = content['cmd_msg']
#     if character.status != 'gen':
#         return '用户已经创建完成 不可变更属性'
#     if cmd_msg not in ['男', '女', '扶她', '秀吉']:
#         return f'请选择正确的性别'
#     character.sex = cmd_msg
#     character_controller.save_charater(user.user_id, character)
#     return f'设置性别 {cmd_msg} 成功'
#
#
# # 增加背景描述
# @filter(r'.desc ', need_character=True)
# def set_desc(content):
#     user = content['sys_user']
#     character = content['sys_character']
#     cmd_msg = content['cmd_msg']
#     if character.status != 'gen':
#         return '用户已经创建完成 不可变更属性'
#     if not character.background:
#         return f'请先选择背景'
#     character.background.desc = cmd_msg
#     character_controller.save_charater(user.user_id, character)
#     return f'增加背景描述成功'
#
#
# # 查看当前角色卡
# @filter(r'.attr', need_character=True)
# def watch_attribute(content):
#     character = content['sys_character']
#
#     if character is None:
#         return '当前没有角色'
#     sb = f'角色：{character.name}'
#     race = character.race.name if character.race is not None else None
#     sb += f'\n种族：{race}'
#     if character.race and character.race.sub_race is not None:
#         sb += f' - {character.race.sub_race}'
#
#     job = character.job.name if character.job is not None else None
#     sb += f'\n职业：{job}'
#     language_msg = formate.formate_list(character.language) if character.language is not None and len(
#         character.language) else None
#     sb += f'\n语言：{language_msg}'
#     sb += f'\n行走速度：{character.speed}'
#
#     attr_msg = formate.formate_dic(character.base_attr)
#     sb += f'\n基础属性：{attr_msg}'
#     if character.status == 'gen':
#         sb += f'\n状态：生成角色中，请使用.swap交换属性，使用.race选择种族，使用.job选择职业 .gened结束生成'
#     if character.status == 'normal':
#         f'\n状态：正常 请愉快的进行游戏吧'
#     if character.status == 'lv_up':
#         sb += f'\n状态：升级中，请使用.lvup 查看选择对应的技能或属性'
#     cur_attr_msg = formate.formate_dic(character.cur_attr) if character.cur_attr is not None else None
#     sb += f'\n当前属性：{cur_attr_msg}'
#     check_attr_msg = formate.formate_dic(character.cur_check) if character.cur_check is not None else None
#     sb += f'\n鉴定值：{check_attr_msg}'
#     skilled_weapon_msg = formate.formate_list(character.skilled_weapon) if character.skilled_weapon is not None and len(
#         character.skilled_weapon) else None
#     sb += f'\n武器熟练：{skilled_weapon_msg}'
#
#     skilled_armor_msg = formate.formate_list(character.skilled_armor) if character.skilled_armor is not None and len(
#         character.skilled_armor) else None
#     sb += f'\n盔甲熟練：{skilled_armor_msg}'
#
#     skilled_item_msg = formate.formate_list(character.skilled_item) if character.skilled_item is not None and len(
#         character.skilled_item) else None
#     sb += f'\n熟练项：{skilled_item_msg}'
#
#     skilled_tool_msg = formate.formate_list(character.skilled_tool) if character.skilled_tool is not None and len(
#         character.skilled_tool) else None
#     sb += f'\n熟练工具：{skilled_tool_msg}'
#
#     race_skill_msg = formate.formate_list(
#         character.race.race_skill) if character.race and character.race.race_skill is not None and len(
#         character.race.race_skill) else None
#     sb += f'\n种族技能：{race_skill_msg}'
#     if character.notice is not None and len(character.notice):
#         sb += f'\n通知：'
#         for s in character.notice.values():
#             sb += '\n\t' + s.get('msg')
#     return sb

# 查看简版人物卡
