import random
from hoshino import R, Service, priv, util
import os
from PIL import Image
from hoshino.util.message_builder import image
from hoshino.util.image_utils import pic2b64

sv = Service('简单聊天', visible=False)


@sv.on_fullmatch('沙雕机器人')
async def say_sorry(bot, ev):
    await bot.send(ev, 'ごめんなさい！嘤嘤嘤(〒︿〒)')


@sv.on_fullmatch('老婆', 'waifu', 'laopo', only_to_me=True)
async def chat_waifu(bot, ev):
    path = './resources/img/laopo'
    list = os.listdir(path)  # 列出文件夹下所有的目录与文件
    laopo = random.choice(list)
    path += f"/{laopo}"
    img = Image.open(path)
    result=image(b64=pic2b64(img))
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, result)
    else:
        await bot.send(ev, 'mua~')


@sv.on_fullmatch('老公', only_to_me=True)
async def chat_laogong(bot, ev):
    await bot.send(ev, '你给我滚！', at_sender=True)


@sv.on_fullmatch('mua', only_to_me=True)
async def chat_mua(bot, ev):
    await bot.send(ev, '笨蛋~', at_sender=True)


@sv.on_fullmatch('我好了')
async def nihaole(bot, ev):
    await bot.send(ev, '不许好，憋回去！')
    await util.silence(ev, 30)


@sv.on_keyword('确实', '有一说一', 'u1s1', 'yysy')
async def chat_queshi(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img('确实.jpg').cqcode)


@sv.on_keyword('内鬼')
async def chat_neigui(bot, ctx):
    if random.random() < 0.10:
        await bot.send(ctx, R.img('内鬼.png').cqcode)
