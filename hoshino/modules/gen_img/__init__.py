from hoshino import Service
from hoshino.typing import CQEvent, MessageSegment
from hoshino.util import pic2b64

from .fkcy import genImage
from io import BytesIO
from os import path

from PIL import Image

from hoshino import Service, aiorequests, R
from hoshino.typing import HoshinoBot, CQEvent
from .rua import generate_gif

sv = Service('图片生成器', help_='''
[5000兆元] (上半句)|(下半句)
[ph] (上半句)|(下半句)
[搓头]@群友
'''.strip(), bundle="图片生成器")


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


sv = Service('Rua')
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
