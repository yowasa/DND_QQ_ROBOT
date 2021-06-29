import json
import os
import shutil

from PIL import Image

from hoshino import R, Service
from hoshino.service import sucmd
from hoshino.typing import CQEvent
from hoshino.typing import CommandSession
from hoshino.modules.pcr_duel.duelconfig import refresh_config
from hoshino.modules.pcr_duel import duel_chara

UNKNOWN = 1000

sv = Service('自定义DLC', enable_on_default=False, visible=True, help_=
'''=====================
自定义dlc说明
=====================
[增加dlc] 仅维护人员可用
[子定义dlc列表]
[添加女友]
[删除女友]
[角色查询]+女友名

* 添加的dlc和角色不会立即加入可选dlc列表 当你认为角色已经齐全的时候联系骰子管理员进行添加 *
''')


def get_json(name):
    with open(R.get(f'duel/{name}.json').path, 'r',encoding='UTF-8') as f:
        return json.load(f)


def write_json(name, content):
    with open(R.get(f'duel/{name}.json').path, 'w',encoding='UTF-8') as f:
        json.dump(content, fp=f,ensure_ascii=False, indent=4)


# 开始下标
BEGIN_INDEX = 20000


@sucmd('增加dlc', aliases=('添加dlc'), force_private=False)
async def dlc_add(session: CommandSession):
    bot = session.bot
    ev = session.event
    name = session.get('name', prompt='输入dlc名称')
    code = session.get('code', prompt='输入dlc code')
    desc = session.get('desc', prompt='输入dlc描述')
    offset = session.get('offset', prompt='输入dlc 起始编号')
    to = session.get('to', prompt='输入dlc 终止编号')
    content = get_json('dlc_config')
    content[name] = {'code': code, 'index': int(offset),'to':int(to),'desc':desc}
    write_json('dlc_config', content)
    await bot.send(ev, message='添加成功')

@dlc_add.args_parser
async def a_p(session: CommandSession):
    text = session.current_arg_text
    session.state[session.current_key] = text


@sv.on_prefix(['自定义dlc列表'])
async def dlc_list(bot, ev: CQEvent):
    contents = get_json('dlc_config')
    msg = '==== 自定义DLC列表 ====\n'
    for name, content in contents.items():
        msg += f'''{name}dlc:
    编码:{content["code"]} 
    角色id范围：{content["index"]} - {content["to"]}
    介绍：{content["desc"]}

'''
    await bot.send(ev, message=msg)


@sv.on_prefix(['自定义dlc角色删除', '角色删除', '删除角色','沙漠成绩女友'])
async def search_chara(bot, ev: CQEvent):
    msg = str(ev.message)
    if not ev.message:
        await bot.finish(ev, '请通过"自定义dlc角色查询+女友名"来查询')
    chara_id = duel_chara.name2id(msg)
    if int(chara_id) == UNKNOWN:
        await bot.finish(ev, f'未查询到名称未{msg}的女友信息')
    chara= duel_chara.fromid(chara_id).name
    if int(chara_id) < 20000:
        await bot.finish(ev, f'女友{chara.name}不是自定义女友')
    chara = get_json('chara')
    del chara[chara_id]
    delete_ids = get_json('delete_ids')
    delete_ids.append(int(chara_id))
    write_json('delete_ids',delete_ids)
    write_json('chara', chara)
    duel_chara.roster.update()
    refresh_config()
    os.remove(R.img(f'dlc/icon/icon_unit_{chara_id}61.png').path)
    os.remove(R.img(f'dlc/full/{chara_id}31.png').path)
    await bot.send(ev, f'女友 {chara.name} 已经删除')


@sv.on_prefix(['自定义dlc角色查询', '查询角色', "角色查询"])
async def search_chara(bot, ev: CQEvent):
    msg = str(ev.message)
    if not ev.message:
        await bot.finish(ev, '请通过"自定义dlc角色查询+女友名"来查询')
    chara_id = duel_chara.name2id(msg)
    if int(chara_id) == UNKNOWN:
        await bot.finish(ev, f'未查询到名称未{msg}的女友信息')
    chara = duel_chara.fromid(chara_id).name
    if int(chara_id) < 20000:
        await bot.finish(ev, f'女友{chara.name}不是自定义女友')
    chara = get_json('chara')
    result = f"""===自定义女友信息===
    角色id：{chara_id}
    角色名称:{chara[str(chara_id)]}
    角色头像：{R.img(f'dlc/icon/icon_unit_{chara_id}61.png').cqcode}
    角色全图：{R.img(f'dlc/full/{chara_id}31.png').cqcode}
    """
    await bot.send(ev, result)


@sv.on_command('添加dlc角色', aliases=('添加DLC角色', '添加角色','添加女友'))
async def add_chara(session: CommandSession):
    DLC = get_json('dlc_config')
    msg = '选择添加进哪个dlc\n'
    for name, content in DLC.items():
        msg += f'{name}\n'
    choice = session.get('choice', prompt=msg)
    if not DLC.get(choice):
        await session.bot.send(session.event, f"未找到自定义DLC{choice}")
        return
    name = session.get('name', prompt='请输入角色名')
    if duel_chara.name2id(name) != UNKNOWN:
        await session.bot.send(session.event, f"已经存在名为{name}的角色，请加后缀标识避免重复")
        return
    aliases_str = session.get('aliases', prompt='请输入角色别名，用空格隔开')
    aliases = str(aliases_str).strip().split(' ')
    for aliase in aliases:
        if duel_chara.name2id(aliase) != UNKNOWN:
            await session.bot.send(session.event, f"已经存在别名为{aliase}的角色，请勿重复")
            return
    icon = session.get('icon', prompt='请发送角色头像,会从左上角尽可能截取一个正方形区域')
    if type(icon) == list:
        icon = icon[0]
    hash_name = requests_download_url(icon, R.get('img/dlc/cache/').path)
    icon_pic = resize_img(hash_name)
    confirm = session.get('confirm',
                          prompt="生成头像为：\n" + str(R.img(f"dlc/cache/{icon_pic}").cqcode) + '\n确认是否使用上述头像(输入"确认"或者"拒绝")')
    if str(confirm) != "确认":
        await session.bot.send(session.event, f"已终止生成角色，请调整好后再来")
        return
    fullcard = session.get('fullcard', prompt='请发送角色全图')
    if type(fullcard) == list:
        fullcard = fullcard[0]
    full_img = requests_download_url(fullcard, R.get('img/dlc/cache/').path)
    full_pic = trance_2_png(full_img)
    await session.bot.send(session.event, "已收到信息，处理中")
    chara = get_json('chara')
    delete_ids = get_json('delete_ids')
    char_id=0
    for id in delete_ids:
        if int(DLC[choice]['index']) <= int(id) <= int(DLC[choice]['to']):
            char_id=int(id)
            break
    if char_id!=0:
        delete_ids.remove(char_id)
        write_json('delete_ids', delete_ids)
    else:
        count = 0
        for key, values in chara.items():
            if int(DLC[choice]['index']) <= int(key) <= int(DLC[choice]['to']):
                count += 1
        char_id = DLC[choice]['index'] + count
    names = [name]
    names.extend(aliases)
    chara[char_id] = names
    write_json('chara', chara)
    shutil.move(R.img(f'dlc/cache/{icon_pic}').path,
                os.path.join(R.img(f'dlc/icon').path, f'icon_unit_{char_id}61.png'))
    shutil.move(R.img(f'dlc/cache/{full_pic}').path,
                os.path.join(R.img(f'dlc/full').path, f'{char_id}31.png'))
    duel_chara.roster.update()
    refresh_config()
    await session.bot.send(session.event, '生成完成，请通过"自定义dlc角色查询+女友名"来查询添加的内容')


@add_chara.args_parser
async def a_p(session: CommandSession):
    text = session.current_arg_text
    img = session.current_arg_images
    if img:
        session.state[session.current_key] = img
    else:
        session.state[session.current_key] = text


import hashlib
import requests


def requests_download_url(url, path):
    name = url[url.rfind("/") + 1:]
    hash_name = md5(name) + '.jpg'
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        open(os.path.join(path, hash_name), 'wb').write(r.content)
    return hash_name


def md5(str):
    m = hashlib.md5()
    m.update(str.encode("utf8"))
    print(m.hexdigest())
    return m.hexdigest()


def resize_img(hash_name):
    img = Image.open(R.img(f'dlc/cache/{hash_name}').path)
    size = min(img.size)
    cropped = img.crop((0, 0, size, size))  # (left, upper, right, lower)
    cropped = cropped.resize((128, 128),Image.ANTIALIAS)
    re_name = 'icon_' + hash_name.replace('jpg', 'png')
    cropped.save(R.img(f'dlc/cache/{re_name}').path, "PNG")
    return re_name


def trance_2_png(hash_name):
    img = Image.open(R.img(f'dlc/cache/{hash_name}').path)
    re_name = 'full_' + hash_name.replace('jpg', 'png')
    img.save(R.img(f'dlc/cache/{re_name}').path, "PNG")
    return re_name
