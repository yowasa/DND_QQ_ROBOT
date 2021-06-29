import json

with open('D:/Resources/duel/chara.json', 'r',encoding='UTF-8') as f:
    info1=json.load(f)
with open('D:/Resources/duel/chara_back.json', 'r',encoding='UTF-8') as f:
    info2=json.load(f)
info={**info1,**info2}
with open('D:/Resources/duel/test.json', 'w',encoding='UTF-8') as f:
    json.dump(info, fp=f,ensure_ascii=False,indent=4)