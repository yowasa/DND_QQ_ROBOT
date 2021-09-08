# 执行天赋
def do_talnet(user):
    if not user.data.get('triggerTalents'):
        user.data['triggerTalents'] = []
    talents = user.data['天赋']
    matches = [x for x in talents if x not in user.data['triggerTalents']]
    for i in matches:
        talent_i = talent_config[str(i)]
        if talent_i.get('effect'):
            if talent_i.get('condition'):
                if checkCondition(user, talent_i.get('condition')):
                    comm.buff_user(user, talent_i.get('effect'))
                    user.data['triggerTalents'].append(i)