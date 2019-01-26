import character
import formateUtil


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
    sb += f'\n基础属性：{attr_msg}'
    if status == 'gen':
        sb += f'\n状态：生成角色中，请使用.swap交换属性，使用.race选择种族，使用.job选择职业 .gened结束生成'
    if status == 'normal':
        f'\n状态：通常 请愉快的进行游戏吧'
    if status == 'lv_up':
        sb += f'\n状态：升级中，请使用.lvup 查看选择对应的技能或属性'
    sb += f'\n当前属性：{cur_attr}'
    sb += f'\n鉴定值：{check_attr}'
    sb += f'\n通知：你可以选择一个专长'
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
