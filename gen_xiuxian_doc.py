# 生成一般文档
import os
import json

# 文件路径
FILE_PATH = os.path.dirname(__file__)
FILE_PATH = os.path.join(FILE_PATH, 'hoshino/modules/xiuxian')

# 物品列表
with open(os.path.join(FILE_PATH, 'config/item_info.json'), 'r', encoding='UTF-8') as fa:
    ITEM_INFO = json.load(fa, strict=False)
ITEM_NAME_MAP = {ITEM_INFO[i]["name"]: ITEM_INFO[i] for i in ITEM_INFO.keys()}

# 物品列表
with open(os.path.join(FILE_PATH, 'config/equipment.json'), 'r', encoding='UTF-8') as fa:
    EQUIPMENT_INFO = json.load(fa, strict=False)

# 功法列表
with open(os.path.join(FILE_PATH, 'config/gongfa.json'), 'r', encoding='UTF-8') as fa:
    GONGFA_INFO = json.load(fa, strict=False)

# 法宝列表
with open(os.path.join(FILE_PATH, 'config/fabao.json'), 'r', encoding='UTF-8') as fa:
    FABAO_INFO = json.load(fa, strict=False)

# 丹方
with open(os.path.join(FILE_PATH, 'config/danfang.json'), 'r', encoding='UTF-8') as fa:
    DANFANG = json.load(fa, strict=False)

# 锻造
with open(os.path.join(FILE_PATH, 'config/duanzao.json'), 'r', encoding='UTF-8') as fa:
    DUANZAO = json.load(fa, strict=False)
# 特效
with open(os.path.join(FILE_PATH, 'config/base_skill.json'), 'r', encoding='UTF-8') as fa:
    BASE_SKILL = json.load(fa, strict=False)

# 藏经阁
with open(os.path.join(FILE_PATH, 'config/cangjing.json'), 'r', encoding='UTF-8') as fa:
    CANGJING = json.load(fa, strict=False)

result_li = []
# for item in ITEM_NAME_MAP.values():
#     if item['type'] != "法宝":
#         continue
#     name = item['name']
#     gongfa = FABAO_INFO[name]
#     tiaojian = "无"
#     if gongfa.get('condition_desc'):
#         tiaojian = gongfa.get('condition_desc')
#     msg = f"{name}\n条件：{tiaojian}\n效果：{item['desc']}"
#     result_li.append(msg)

# for item in ITEM_NAME_MAP.values():
#     if item['type'] != "丹药":
#         continue
#     name = item['name']
#     msg = f"{name}\n效果：{item['desc']}"
#     result_li.append(msg)

# 锻造
# for name in DUANZAO.keys():
#     item_li=DUANZAO[name]['item']
#     item_msg="无"
#     if item_msg:
#         item_msg=" ".join(item_li)
#     msg = f"{name}\n需要时间：{DUANZAO[name]['time']}\n需要灵石：{DUANZAO[name]['lingshi']}\n需要素材：{item_msg}"
#     result_li.append(msg)


for name in DANFANG.keys():
    item_li = DANFANG[name]['ex_item']
    item_msg = "无"
    if item_msg:
        item_msg = " ".join(item_li)
    msg = f"{name}\n需要时间：{DANFANG[name]['time']}\n需要灵石：{DANFANG[name]['price']}\n需要素材：{item_msg}"
    result_li.append(msg)

print("\n\n".join(result_li))
