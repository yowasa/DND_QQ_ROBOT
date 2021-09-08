import os
import json

data_dir = os.path.join(os.path.dirname(__file__), 'config')
with open(os.path.join(data_dir, 'age.json'), 'r', encoding='UTF-8') as f:
    age_config = json.load(f)
with open(os.path.join(data_dir, 'events.json'), 'r', encoding='UTF-8') as f:
    event_config = json.load(f)
with open(os.path.join(data_dir, 'talents.json'), 'r', encoding='UTF-8') as f:
    talent_config = json.load(f)

# 角色增益
def buff_user(user, buff_dict):
    if buff_dict:
        for i in buff_dict.keys():
            eff_li = ["SPR", "MNY", "CHR", "STR", "INT",'LIF']
            key_li = ["快乐", "家境", "颜值", "体质", "智力",'存活']
            index = eff_li.index(i)
            user.data[key_li[index]] += buff_dict[i]