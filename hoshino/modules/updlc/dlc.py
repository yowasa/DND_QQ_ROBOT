import hashlib
import json
import os
import shutil

import requests
from PIL import Image

from hoshino import R, Service, priv
from hoshino.modules.pcr_duel import duel_chara
from hoshino.config import pcr_duel as cfg
from hoshino.modules.pcr_duel import duelconfig
from hoshino.typing import CQEvent
from hoshino.typing import CommandSession

UNKNOWN = 1000

sv = Service('自定义DLC', manage_priv=priv.SUPERUSER, enable_on_default=False, visible=True, bundle='贵族功能', help_=
'''[增加dlc] 仅维护人员可用
[子定义dlc列表]
[添加女友]
[更新女友]
[删除女友]
[角色查询]+女友名
[添加时装]
[更新时装]
* 该功能模块仅维护组可以打开 *
''')


def get_json(name):
    with open(R.get(f'duel/{name}.json').path, 'r', encoding='UTF-8') as f:
        return json.load(f)


def write_json(name, content):
    with open(R.get(f'duel/{name}.json').path, 'w', encoding='UTF-8') as f:
        json.dump(content, fp=f, ensure_ascii=False, indent=4)


# 开始下标
BEGIN_INDEX = 20000

@sv.on_command('增加时装',aliases=('添加时装'))
async def fashion_add(session: CommandSession):
    bot = session.bot
    ev = session.event
    search_name=session.get('search_name', prompt='请输入要添加时装的角色名')
    chara_id = duel_chara.name2id(search_name)
    if chara_id == UNKNOWN:
        await bot.finish(ev, f'未查询到名称为{search_name}的女友信息')
    chara_info=duel_chara.fromid(chara_id)

    fashioninfo = duelconfig.get_fashion(chara_id)
    number = len(fashioninfo)
    if number>=3:
        await bot.finish(ev, f'女友{chara_info.name}已经存在3件以上时装，无法继续添加')
    name = session.get('name', prompt='输入时装名称')
    for each in fashioninfo:
        if each['name']==name:
            await bot.finish(ev, f'时装名{name}已经存在,请换一个')
    img = session.get('imgs', prompt='输入时装图片（不要太大，否则会限制发送无法展示）')
    if type(img) == list:
        img = img[0]
    fid=len(cfg.fashionlist)+1

    info={
        "fid": fid,
        "name": name,
        "cid": chara_id,
        "pay_score": 50000+number*50000,
        "pay_sw": 500+number*500,
        "favor": 50+number*50,
        "add_ce": 100+number*100,
        "xd_flag": 0,
        "content": "时装商城购买"
    }
    cfg.fashionlist[str(fid)]=info
    cfg.save_fashion()
    hash_name = requests_download_url(img, R.get('img/dlc/cache/').path)
    shutil.move(R.img(f'dlc/cache/{hash_name}').path,
                os.path.join(R.img(f'dlc/fashion').path, f'{fid}.jpg'))
    await bot.send(session.event, f"添加时装成功")

@sv.on_command('修改时装',aliases=('更新时装'))
async def fashion_update(session: CommandSession):
    bot = session.bot
    ev = session.event
    search_name=session.get('search_name', prompt='请输入要更新时装的角色名')
    chara_id = duel_chara.name2id(search_name)
    if chara_id == UNKNOWN:
        await bot.finish(ev, f'未查询到名称为{search_name}的女友信息')
    name = session.get('name', prompt='输入时装名称')

    fashioninfo = duelconfig.get_fashion(chara_id)
    fid=-1
    for each in fashioninfo:
        if each['name']==name:
            fid=each['fid']
            break
    if fid<0:
        await bot.finish(ev, f'未找到时装名为"{name}"的时装')

    new_name = session.get('new_name', prompt=f'输入新的时装名称（原名称为{name}）')
    for each in fashioninfo:
        if each['name']==name and each['fid']!=fid:
            await bot.finish(ev, f'时装名{name}已经存在,请换一个')
    img = session.get('imgs', prompt='输入时装图片（不要太大，否则会限制发送无法展示）')
    if type(img) == list:
        img = img[0]
    old=cfg.fashionlist[str(fid)]

    info={
        "fid": fid,
        "name": new_name,
        "cid": chara_id,
        "pay_score": old['pay_score'],
        "pay_sw": old['pay_sw'],
        "favor": old['favor'],
        "add_ce": old['add_ce'],
        "xd_flag": 0,
        "content": "时装商城购买"
    }
    cfg.fashionlist[str(fid)]=info
    cfg.save_fashion()
    hash_name = requests_download_url(img, R.get('img/dlc/cache/').path)
    shutil.move(R.img(f'dlc/cache/{hash_name}').path,
                os.path.join(R.img(f'dlc/fashion').path, f'{fid}.jpg'))
    await bot.send(session.event, f"更新时装成功")


@fashion_add.args_parser
async def _(session: CommandSession):
    text = session.current_arg_text
    img = session.current_arg_images
    if session.is_first_run:
        if text:
            session.state['search_name'] = text.strip()
        return
    if img:
        session.state[session.current_key] = img
    else:
        session.state[session.current_key] = text

@fashion_update.args_parser
async def _(session: CommandSession):
    text = session.current_arg_text
    img = session.current_arg_images
    if session.is_first_run:
        if text:
            session.state['search_name'] = text.strip()
        return
    if img:
        session.state[session.current_key] = img
    else:
        session.state[session.current_key] = text

@sv.on_command('增加dlc', aliases=('添加dlc'))
async def dlc_add(session: CommandSession):
    bot = session.bot
    ev = session.event
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '只有超管可以增加dlc。', at_sender=True)
    name = session.get('name', prompt='输入dlc名称')
    code = session.get('code', prompt='输入dlc code')
    desc = session.get('desc', prompt='输入dlc描述')
    offset = session.get('offset', prompt='输入dlc 起始编号')
    to = session.get('to', prompt='输入dlc 终止编号')
    confirm = session.get('confirm',
                          prompt='确认生成dlc吗(回复"确认"生成)')
    if str(confirm) != "确认":
        await session.bot.send(session.event, f"已终止生成角色，请调整好后再来")
        return
    content = get_json('dlc_config')
    content[name] = {'code': code, 'index': int(offset), 'to': int(to), 'desc': desc}
    write_json('dlc_config', content)
    cfg.refresh_config()
    await bot.send(ev, message='添加成功')


@dlc_add.args_parser
async def ad_p(session: CommandSession):
    text = session.current_arg_text
    img = session.current_arg_images
    if img:
        session.state[session.current_key] = img
    else:
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


@sv.on_prefix(['自定义dlc角色删除', '角色删除', '删除角色', '删除女友'])
async def search_chara(bot, ev: CQEvent):
    msg = str(ev.message)
    if not msg:
        await bot.finish(ev, '请通过"自定义dlc角色查询+女友名"来查询')
    chara_id = duel_chara.name2id(msg)
    if chara_id == UNKNOWN:
        await bot.finish(ev, f'未查询到名称为{msg}的女友信息')
    chara = duel_chara.fromid(chara_id)
    old_name=chara.name
    if chara_id < 20000:
        await bot.finish(ev, f'女友{chara.name}不是自定义女友')
    chara_json = get_json('chara')
    del chara_json[str(chara_id)]
    delete_ids = get_json('delete_ids')
    delete_ids.append(chara_id)
    write_json('delete_ids', delete_ids)
    write_json('chara', chara_json)
    cfg.refresh_chara()
    duel_chara.roster.update()
    cfg.refresh_config()
    os.remove(R.img(f'dlc/icon/icon_unit_{chara_id}61.png').path)
    os.remove(R.img(f'dlc/full/{chara_id}31.png').path)
    await bot.send(ev, f'女友 {old_name} 已经删除')


@sv.on_prefix(['自定义dlc角色查询', '查询角色', "角色查询"])
async def search_chara(bot, ev: CQEvent):
    msg = str(ev.message)
    if not ev.message:
        await bot.finish(ev, '请通过"自定义dlc角色查询+女友名"来查询')
    chara_id = duel_chara.name2id(msg)
    if int(chara_id) == UNKNOWN:
        await bot.finish(ev, f'未查询到名称未{msg}的女友信息')
    chara = duel_chara.fromid(chara_id)
    chara_json = get_json('chara')
    result = f"""===女友信息===
    角色id：{chara_id}
    角色名称:{chara_json[str(chara_id)]}
    角色头像：{R.img(f'dlc/icon/icon_unit_{chara_id}61.png').cqcode}
    角色全图：{R.img(f'dlc/full/{chara_id}31.png').cqcode}
    """
    await bot.send(ev, result)


@sv.on_command('更新女友', aliases=('更新角色', '角色更新', '女友更新'))
async def dlc_update(session: CommandSession):
    bot = session.bot
    ev = session.event
    search_name = session.get('search_name', prompt="输入女友名称")
    search_chara_id = duel_chara.name2id(search_name)
    if search_chara_id == UNKNOWN:
        await bot.finish(ev, f'未查询到名称为{search_name}的女友信息')
    search_chara = duel_chara.fromid(search_chara_id)
    confirm_search = session.get('confirm_search',
                                 prompt=f'确认要更新的女友为{search_chara.name}(输入"确认"或者"拒绝")：\n' + str(
                                     search_chara.icon.cqcode))
    if str(confirm_search) != "确认":
        await bot.finish(session.event, f"已终止")

    name = session.get('name', prompt=f'请输入新角色名(原名为：{search_chara.name})')
    if name not in search_chara.name_li:
        if duel_chara.name2id(name) != UNKNOWN:
            await session.bot.send(session.event, f"已经存在名为{name}的角色，请加后缀标识避免重复")
            return
    aliases_str = session.get('aliases', prompt=f'请输入角色别名，用空格隔开(原别名为{" ".join(search_chara.name_li[1:])})')
    aliases = str(aliases_str).strip().split(' ')
    for aliase in aliases:
        if aliase not in search_chara.name_li:
            if duel_chara.name2id(aliase) != UNKNOWN:
                await session.bot.finish(session.event, f"已经存在别名为{aliase}的角色，请勿重复")
    icon = session.get('icon', prompt=f'请发送角色头像,会从左上角尽可能截取一个正方形区域(原头像为{search_chara.icon.cqcode})')
    if type(icon) == list:
        icon = icon[0]
    hash_name = requests_download_url(icon, R.get('img/dlc/cache/').path)
    icon_pic = resize_img(hash_name)
    confirm = session.get('confirm',
                          prompt="生成头像为：\n" + str(R.img(f"dlc/cache/{icon_pic}").cqcode) + '\n确认是否使用上述头像(输入"确认"或者"拒绝")')
    if str(confirm) != "确认":
        await session.bot.send(session.event, f"已终止生成角色，请调整好后再来")
        return
    fullcard = session.get('fullcard', prompt=f"请发送角色全图,原图为{R.img(f'dlc/full/{search_chara_id}31.png').cqcode}")
    if type(fullcard) == list:
        fullcard = fullcard[0]
    full_img = requests_download_url(fullcard, R.get('img/dlc/cache/').path)
    full_pic = trance_2_png(full_img)
    await session.bot.send(session.event, "已收到信息，处理中")
    chara_json = get_json('chara')
    char_id = search_chara_id

    names = [name]
    names.extend(aliases)
    chara_json[char_id] = names
    write_json('chara', chara_json)
    shutil.move(R.img(f'dlc/cache/{icon_pic}').path,
                os.path.join(R.img(f'dlc/icon').path, f'icon_unit_{char_id}61.png'))
    shutil.move(R.img(f'dlc/cache/{full_pic}').path,
                os.path.join(R.img(f'dlc/full').path, f'{char_id}31.png'))
    cfg.refresh_chara()
    duel_chara.roster.update()
    cfg.refresh_config()
    await session.bot.send(session.event, '生成完成，请通过"自定义dlc角色查询+女友名"来查询添加的内容')


@dlc_update.args_parser
async def u_p(session: CommandSession):
    text = session.current_arg_text
    img = session.current_arg_images
    if session.is_first_run:
        if text:
            session.state['search_name'] = text.strip()
        return
    if img:
        session.state[session.current_key] = img
    else:
        session.state[session.current_key] = text


@sv.on_command('添加dlc角色', aliases=('添加DLC角色', '添加角色', '添加女友'))
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
    chara_json = get_json('chara')
    delete_ids = get_json('delete_ids')
    char_id = 0
    for id in delete_ids:
        if int(DLC[choice]['index']) <= int(id) <= int(DLC[choice]['to']):
            char_id = int(id)
            break
    if char_id != 0:
        delete_ids.remove(char_id)
        write_json('delete_ids', delete_ids)
    else:
        count = 0
        for key, values in chara_json.items():
            if int(DLC[choice]['index']) <= int(key) <= int(DLC[choice]['to']):
                count += 1
        char_id = DLC[choice]['index'] + count
    names = [name]
    names.extend(aliases)
    chara_json[char_id] = names
    write_json('chara', chara_json)
    shutil.move(R.img(f'dlc/cache/{icon_pic}').path,
                os.path.join(R.img(f'dlc/icon').path, f'icon_unit_{char_id}61.png'))
    shutil.move(R.img(f'dlc/cache/{full_pic}').path,
                os.path.join(R.img(f'dlc/full').path, f'{char_id}31.png'))
    cfg.refresh_chara()
    duel_chara.roster.update()
    cfg.refresh_config()
    await session.bot.send(session.event, '生成完成，请通过"自定义dlc角色查询+女友名"来查询添加的内容')


@add_chara.args_parser
async def a_p(session: CommandSession):
    text = session.current_arg_text
    img = session.current_arg_images
    if img:
        session.state[session.current_key] = img
    else:
        session.state[session.current_key] = text


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
    cropped = cropped.resize((128, 128), Image.ANTIALIAS)
    re_name = 'icon_' + hash_name.replace('jpg', 'png')
    cropped.save(R.img(f'dlc/cache/{re_name}').path, "PNG")
    return re_name


def trance_2_png(hash_name):
    img = Image.open(R.img(f'dlc/cache/{hash_name}').path)
    re_name = 'full_' + hash_name.replace('jpg', 'png')
    img.save(R.img(f'dlc/cache/{re_name}').path, "PNG")
    return re_name
