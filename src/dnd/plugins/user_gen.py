import character
from config import *
import formateUtil


def gen(content):
    # 获得用户
    sender = content['sender']
    user_id = sender['user_id']
    comm = content['message']
    comm = comm.replace('.gen ', '')
    if comm == '':
        return '请输入名称'
    if ' ' in comm.strip():
        return '名称中请不要带空格'
    msg = character.gen_user(user_id, comm)
    return msg


def reroll(content):
    # 重新roll点
    sender = content['sender']
    user_id = sender['user_id']
    comm = content['message']
    user = character.get_current_user_info(user_id)
    if user['status'] != 'gen':
        return '用户已经创建完成 不可变更属性'
    user_name = user['name']
    print(user)
    re_roll_time = user.get('re_roll_time')
    if re_roll_time is None:
        re_roll_time = 4
    if re_roll_time == 0:
        return f'角色 {user_name} 已经没有重新roll点次数'
    re_roll_time -= 1
    user['re_roll_time'] = re_roll_time
    attr = character.init_attribute()
    user['attribute'] = attr
    character.refresh(user_id, user)
    return f'角色 {user_name} 重新roll点成功\n新属性 {formateUtil.formate_dic(attr)}\n可重新roll点次数为{re_roll_time}'


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
    user = character.get_current_user_info(user_id)
    if user['status'] != 'gen':
        return '用户已经创建完成 不可变更属性'
    cache = user['attribute'][attr1]
    user['attribute'][attr1] = user['attribute'][attr2]
    user['attribute'][attr2] = cache
    character.refresh(user_id, user)
    return '交换属性成功'


def switch_race(content):
    user_id = content['sender']['user_id']
    comm = content['message']
    comm = comm.replace('.race ', '')
    if comm not in RACE:
        return f'种族{comm}不存在'
    user = character.get_current_user_info(user_id)
    user_name=user.get('name')
    if user.get('status')!='gen':
        return f'{user_name} 已经创建完成 不能再重新选择种族'
    user['race']=comm
    character.refresh(user_id,user)
    return f'选择种族{comm}成功，请使用.attr查看角色状态'


def switch_job(content):
    return '功能未实现'


def switch_sub_race(content):
    user_id = content['sender']['user_id']
    comm = content['message']
    comm = comm.replace('.subrace ', '')
    user = character.get_current_user_info(user_id)
    pc_op=user.get('pc_op')
    if pc_op is None:
        return '当前角色不可选择亚种'
    select_sub_job=pc_op.get('select_sub_job')
    if select_sub_job:
        race=user.get('race')
        sub_race_list=RACE_DESCRIBE.get(race).get('ex_race')
        print(sub_race_list)
        print(sub_race_list.keys())
        print(comm)
        if comm in sub_race_list.keys():
            user['sub_race']=comm
            character.refresh(user_id, user)
            return f'选择亚种{comm}成功,请使用.attr查看角色状态'
    return '当前角色不可选择亚种'
