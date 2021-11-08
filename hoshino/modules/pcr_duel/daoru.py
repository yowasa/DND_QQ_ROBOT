# from hoshino.modules.pcr_duel.duelconfig import *
# from hoshino.modules.pcr_duel import duel_chara
# import random
#
#
# def get_cid_by_name(name):
#     cid = duel_chara.name2id(name)
#     if cid == 1000:
#         print("[{}]匹配失败")
#     return cid
#
#
# with open('input.txt', 'r', encoding='UTF-8') as f:
#     data = f.readlines()
# have_error=False
# for i in data:
#     match1 = re.match(r'(\S*) 【(.*?)】【(.*?)】(\d*?)【(.*?)】.*', i, flags=0)
#     name = match1.group(1)
#     skill = match1.group(2)
#     jiban = match1.group(3)
#     pian = match1.group(4)
#     char = match1.group(5)
#     cid = get_cid_by_name(name)
#     if cid == 1000:
#         have_error=True
#         print("角色名称错误")
#     msg = ""
#     skill = skill.split()
#     if not set(skill) <= skill_def_json.keys():
#         have_error = True
#         msg += " SKILL ERROR!!! "
#     jiban = jiban.split()
#     jiban_ids = []
#     for i in jiban:
#         jid = get_cid_by_name(i)
#         if jid == 1000:
#             have_error = True
#             msg += f" {i}JIBAN ERROR!!! "
#         else:
#             jiban_ids.append(jid)
#     if char not in character.keys():
#         have_error = True
#         msg += " CHAR ERROR!!! "
#     if not pian.isdecimal():
#         have_error = True
#         msg += " PIAN ERROR!!! "
#     print(f"{cid}:{name} 性格:{char} 技能:{skill} 偏好:{pian} 羁绊:{jiban}{msg}")
#     char_character_json[str(cid)]=[char]
#     char_skill_json[str(cid)]=skill
#     char_style_json[str(cid)]=int(pian)
#     char_fetter_json[str(cid)]=[jiban_ids]
#
#
#
# print(have_error)
# if not have_error:
#     # 刷新性格
#     refresh_char_character()
#     # 刷新羁绊
#     refresh_char_fetter()
#     # 刷新偏好
#     refresh_char_style()
#     # 刷新技能
#     refresh_char_skill()
