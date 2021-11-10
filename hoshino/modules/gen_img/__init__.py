import hashlib
import os
from io import BytesIO
from os import path
import re
import requests
from PIL import Image
from hoshino.typing import CommandSession
from .miragetank import mt_make
from hoshino import Service, aiorequests, R
from hoshino.typing import HoshinoBot, CQEvent
from hoshino.typing import MessageSegment
from hoshino.util import pic2b64
from .fkcy import genImage
from .rua import generate_gif
from .luxunshuo import luxunshuo
from hoshino.util.utils import get_user_avatar,get_message_at,get_message_text
from hoshino.util.image_utils import CreateImg
from hoshino.util.message_builder import image
import random

sv = Service('图片生成器', help_='''
[5kcy] (上半句)|(下半句)
[ph] (上半句)|(下半句)
[rua]@群友
[mt] 生成幻影坦克
[改图]
[鲁迅说]{内容}
[我有个朋友说] {内容} @朋友
'''.strip(), bundle="图片生成器")


def requests_download_url(url, path):
    hash_name = md5(url) + '.jpg'
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        open(os.path.join(path, hash_name), 'wb').write(r.content)
    return hash_name


def md5(str):
    m = hashlib.md5()
    m.update(str.encode("utf8"))
    print(m.hexdigest())
    return m.hexdigest()


@sv.on_prefix(('5000兆元', '5000兆円', '5kcy'))
async def gen_5000_pic(bot, ev: CQEvent):
    uid = ev.user_id
    gid = ev.group_id
    mid = ev.message_id
    try:
        keyword = ev.message.extract_plain_text().strip()
        if not keyword:
            await bot.send(ev, '请提供要生成的句子！')
            return
        if '｜' in keyword:
            keyword = keyword.replace('｜', '|')
        upper = keyword.split("|")[0]
        downer = keyword.split("|")[1]
        img = genImage(word_a=upper, word_b=downer)
        img = str(MessageSegment.image(pic2b64(img)))
        await bot.send(ev, img)
    except OSError:
        await bot.send(ev, '生成失败……请检查字体文件设置是否正确')
    except:
        await bot.send(ev, '生成失败……请检查命令格式是否正确')


data_dir = path.join(path.dirname(__file__), 'data')


@sv.on_prefix(('rua', '挫', '挫头', '搓', '搓头'))
async def creep(bot: HoshinoBot, ev: CQEvent):
    if ev.message[0].type == 'at':
        creep_id = int(ev.message[0].data['qq'])
    else:
        return

    url = f'http://q1.qlogo.cn/g?b=qq&nk={creep_id}&s=160'
    resp = await aiorequests.get(url)
    resp_cont = await resp.content
    avatar = Image.open(BytesIO(resp_cont))
    img = generate_gif(data_dir, avatar)
    await bot.send(ev, img)


from .ph_logo import combine_img


@sv.on_prefix('ph')
async def gen_ph_pic(bot, ev: CQEvent):
    keyword = ev.message.extract_plain_text().strip()
    if not keyword:
        await bot.send(ev, '请提供要生成的句子！')
        return
    if '｜' in keyword:
        keyword = keyword.replace('｜', '|')
    upper = keyword.split("|")[0]
    downer = keyword.split("|")[1]
    combine_img(left_text=upper, right_text=downer, font_size=50, out_put_path=R.img('ph.png').path)
    await bot.send(ev, R.img('ph.png').cqcode)


os.makedirs(R.img('gen').path, exist_ok=True)
os.makedirs(R.img('gen/result').path, exist_ok=True)

import uuid


@sv.on_command("mt")
async def mt(session: CommandSession):
    bot = session.bot
    ev = session.event
    img_1 = session.get('img_1', prompt='输入上层图片')
    if type(img_1) == list:
        img_1 = img_1[0]
    img_2 = session.get('img_2', prompt='输入下层图片')
    if type(img_2) == list:
        img_2 = img_2[0]
    img_1_name = requests_download_url(img_1, R.img('gen').path)
    img_2_name = requests_download_url(img_2, R.img('gen').path)
    reslt_name = str(uuid.uuid1()) + '.png'
    mt_make(R.img(f'gen/{img_1_name}').path, R.img(f'gen/{img_2_name}').path, R.img(f'gen/result/{reslt_name}').path)
    await bot.send(ev, R.img(f'gen/result/{reslt_name}').cqcode)


@mt.args_parser
async def _(session: CommandSession):
    text = session.current_arg_text
    img = session.current_arg_images
    if img:
        session.state[session.current_key] = img
    else:
        session.state[session.current_key] = text

@sv.on_prefix(('鲁迅说'))
async def luxun(bot: HoshinoBot, ev: CQEvent):
    text = ev.message.extract_plain_text().strip()
    result = luxunshuo(text)
    await bot.send(ev, result)

@sv.on_rex('^我.*?朋友.*?(想问问|说|让我问问|想问|让我问|想知道|让我帮他问问|让我帮他问|让我帮忙问|让我帮忙问问|问).*')
async def pengyou_say(bot: HoshinoBot, ev: CQEvent):
    qq=get_message_at(ev)
    msg = get_message_text(ev)
    if not qq:
        qq = random.choice(
            [
                x["user_id"]
                for x in await bot.get_group_member_list(
                    self_id=ev.self_id, group_id=ev.group_id
                )
            ]
        )
        user_name = "朋友"
    else:
        qq = qq[0]
        at_user = await bot.get_group_member_info(group_id=ev.group_id, user_id=qq)
        user_name = at_user["card"] if at_user["card"] else at_user["nickname"]
    msg = re.search(
        r"^我.*?朋友.*?(想问问|说|让我问问|想问|让我问|想知道|让我帮他问问|让我帮他问|让我帮忙问|让我帮忙问问|问)(.*)", msg
    )
    msg = msg.group(2)
    if not msg:
        msg = "都不知道问什么"
    msg = msg.replace("他", "我").replace("她", "我").replace("它", "我")
    x=get_user_avatar(qq)
    url = f'http://q1.qlogo.cn/g?b=qq&nk={qq}&s=160'
    resp = await aiorequests.get(url)
    resp_cont = await resp.content
    if x:
        ava = CreateImg(200, 100, background=BytesIO(resp_cont))
    else:
        ava = CreateImg(200, 100, color=(0, 0, 0))
    ava.circle()
    text = CreateImg(300, 30, font_size=30)
    text.text((0, 0), user_name)
    A = CreateImg(700, 150, font_size=25, color="white")
    A.paste(ava, (30, 25), True)
    A.paste(text, (150, 38))
    A.text((150, 85), msg, (125, 125, 125))

    await bot.send(ev, image(b64=A.pic2bs4()))