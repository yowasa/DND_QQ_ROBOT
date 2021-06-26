import json
import os
import random
import re
import time
from enum import Enum
from peewee import *

from PIL import Image, ImageDraw, ImageFont

from hoshino import R
from hoshino import Service
from hoshino.config.__bot__ import BASE_DB_PATH
from hoshino.typing import CQEvent, MessageSegment as Seg

sv = Service('骰子', enable_on_default=True, help_=
'''[.r] 掷骰子
[.r 3d12] 掷3次12面骰子
[今日人品] 获取今日人品
[抽签] 抽签看一下运势
''')

DB_PATH = os.path.expanduser(BASE_DB_PATH + "jrrp.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


async def do_dice(bot, ev, num, min_, max_, opr, offset, TIP="的掷骰结果是："):
    if num == 0:
        await bot.send(ev, '咦？我骰子呢？')
        return
    min_, max_ = min(min_, max_), max(min_, max_)
    rolls = list(map(lambda _: random.randint(min_, max_), range(num)))
    sum_ = sum(rolls)
    rolls_str = '+'.join(map(lambda x: str(x), rolls))
    if len(rolls_str) > 100:
        rolls_str = str(sum_)
    res = sum_ + opr * offset
    msg = [
        f'{TIP}\n', str(num) if num > 1 else '', 'D',
        f'{min_}~' if min_ != 1 else '', str(max_),
        (' +-'[opr] + str(offset)) if offset else '',
        '=', rolls_str, (' +-'[opr] + str(offset)) if offset else '',
        f'={res}' if offset or num > 1 else '',
    ]
    msg = ''.join(msg)
    await bot.send(ev, msg, at_sender=True)


@sv.on_rex(
    re.compile(r'^\.r\s*((?P<num>\d{0,2})d((?P<min>\d{1,4})~)?(?P<max>\d{0,4})((?P<opr>[+-])(?P<offset>\d{0,5}))?)?\b',
               re.I))
async def dice(bot, ev):
    num, min_, max_, opr, offset = 1, 1, 100, 1, 0
    match = ev['match']
    if s := match.group('num'):
        num = int(s)
    if s := match.group('min'):
        min_ = int(s)
    if s := match.group('max'):
        max_ = int(s)
    if s := match.group('opr'):
        opr = -1 if s == '-' else 1
    if s := match.group('offset'):
        offset = int(s)
    await do_dice(bot, ev, num, min_, max_, opr, offset)


"""
今日人品功能 沙雕群友快乐源泉
"""


db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class User(BaseModel):
    qq_number = BigIntegerField(index=True, unique=True)
    jrrp = IntegerField(null=True)
    jrrp_date = CharField(null=True)

User.create_table()


@sv.on_prefix(['jrrp', '今日人品'])
async def jrrp(bot, ev: CQEvent):
    user = User.get_or_none(User.qq_number == ev.user_id)
    if not user:
        user = User(qq_number=ev.user_id)
        user.save()

    jrrp_date = user.jrrp_date
    date = time.strftime("%Y-%m-%d")
    if not jrrp_date or jrrp_date != date:
        user.jrrp_date = date
        user.jrrp = random.randint(0, 100)
        user.save()
    await bot.send(ev, f'{Seg.at(ev.user_id)} 今天的运势是{user.jrrp}%！！！！！！！！！！')
    return


"""
抽签功能
"""

data = {
    "pcr": "./resources/pcr-fortune",
    "genshin": "./resources/genshin-fortune"
}
env_dist = os.environ
cq_image_file = env_dist.get("cq_image_file")
if not cq_image_file:
    cq_image_file = 'D:\\workspace\\mcl\\data\\OneBot\\image\\'


# 抽签功能
@sv.on_prefix(['抽签'])
async def cq(bot, ev: CQEvent):
    msg = str(ev.message).strip()
    model = random.choice([FortuneModel.DEFAULT_GEN, FortuneModel.DEFAULT_PCR])
    # gen
    if msg.find("gen") != -1 or msg.find("原神") != -1:
        model = FortuneModel.DEFAULT_GEN
    # pcr
    if msg.find("pcr") != -1 or msg.find("公主") != -1 or msg.find("re") != -1:
        model = FortuneModel.DEFAULT_PCR

    # kure
    if msg.find("可") != -1 or msg.find("哒哒哒") != -1:
        model = FortuneModel.KURE
    # kokusei
    if msg.find("刻晴") != -1:
        model = FortuneModel.KOKUSEI
    # dirukku
    if msg.find("卢") != -1:
        model = FortuneModel.DIRUKKU
    # babara
    if msg.find("芭") != -1 or msg.find("巴") != -1:
        model = FortuneModel.BABARA
    # nana
    if msg.find("七") != -1:
        model = FortuneModel.NANA

    # kkr
    if msg.find("kkr") != -1 or msg.find("妈") != -1:
        model = FortuneModel.M
    # kyaru
    if msg.find("kyaru") != -1 or msg.find("臭鼬") != -1:
        model = FortuneModel.KYARU
        key = "pcr"
    # xcw
    if msg.find("xcw") != -1 or msg.find("炼") != -1:
        model = FortuneModel.XCW

    # 画图
    cq_code = drawing(model, ev.user_id)
    await bot.send(ev, cq_code)
    # 打包成cq码
    return


# pcr枚举类
class FortuneModel(Enum):
    KYARU = ["pcr", 2]

    XCW = ["pcr", 27]

    M = ["pcr", 41]

    KURE = ["genshin", 24]

    KOKUSEI = ["genshin", 23]

    DIRUKKU = ["genshin", 10]

    BABARA = ["genshin", 2]

    NANA = ["genshin", 19]

    DEFAULT_PCR = ["pcr", "default"]

    DEFAULT_GEN = ["genshin", "default"]


def download_chara_icon(id_, star):
    url = f'https://redive.estertion.win/icon/unit/{id_}{star}1.webp'
    save_path = R.img(f'priconne/unit/icon_unit_{id_}{star}1.png').path
    logger.info(f'Downloading chara icon from {url}')
    try:
        rsp = requests.get(url, stream=True, timeout=5)
    except Exception as e:
        logger.error(f'Failed to download {url}. {type(e)}')
        logger.exception(e)
    if 200 == rsp.status_code:
        img = Image.open(BytesIO(rsp.content))
        img.save(save_path)
        logger.info(f'Saved to {save_path}')
    else:
        logger.error(f'Failed to download {url}. HTTP {rsp.status_code}')


# 画图
def drawing(model, userQQ):
    RESOURCES_BASE_PATH = data[model.value[0]]
    fontPath = {
        "title": f"{RESOURCES_BASE_PATH}/font/Mamelon.otf",
        "text": f"{RESOURCES_BASE_PATH}/font/sakura.ttf",
    }
    if model.value[1] != "default":
        imgPath = f"{RESOURCES_BASE_PATH}/img/frame_{model.value[1]}.jpg"
    else:
        imgPath = randomBasemap(RESOURCES_BASE_PATH)

    img = Image.open(imgPath)
    # Draw title
    text = copywriting(RESOURCES_BASE_PATH)
    title = getTitle(text, RESOURCES_BASE_PATH)
    text = text["content"]
    gen_path = hash(imgPath + title + text)
    if R.img(f'chouqian/{gen_path}.jpg').exist:
        return R.img(f'chouqian/{gen_path}.jpg').cqcode

    draw = ImageDraw.Draw(img)
    font_size = 45
    color = "#F5F5F5"
    image_font_center = (140, 99)
    ttfront = ImageFont.truetype(fontPath["title"], font_size)
    font_length = ttfront.getsize(title)
    draw.text(
        (
            image_font_center[0] - font_length[0] / 2,
            image_font_center[1] - font_length[1] / 2,
        ),
        title,
        fill=color,
        font=ttfront,
    )
    # Text rendering
    font_size = 25
    color = "#323232"
    image_font_center = [140, 297]
    ttfront = ImageFont.truetype(fontPath["text"], font_size)
    result = decrement(text)
    for i in range(0, result[0]):
        font_height = len(result[i + 1]) * (font_size + 4)
        textVertical = vertical(result[i + 1])
        x = int(
            image_font_center[0]
            + (result[0] - 2) * font_size / 2
            + (result[0] - 1) * 4
            - i * (font_size + 4)
        )
        y = int(image_font_center[1] - font_height / 2)
        draw.text((x, y), textVertical, fill=color, font=ttfront)
    # Save
    img.save(R.img(f'chouqian/{gen_path}.jpg').path)
    return R.img(f'chouqian/{gen_path}.jpg').cqcode


# 随机找图
def randomBasemap(RESOURCES_BASE_PATH):
    p = f"{RESOURCES_BASE_PATH}/img"
    return p + "/" + random.choice(os.listdir(p))


# 随机找文字
def copywriting(RESOURCES_BASE_PATH):
    p = f"{RESOURCES_BASE_PATH}/fortune/copywriting.json"
    content = readJsonFile(p)
    return random.choice(content["copywriting"])


# 读取json
def readJsonFile(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.loads(f.read())


# 获取title
def getTitle(structure, RESOURCES_BASE_PATH):
    p = f"{RESOURCES_BASE_PATH}/fortune/goodLuck.json"
    content = readJsonFile(p)
    for i in content["types_of"]:
        if i["good-luck"] == structure["good-luck"]:
            return i["name"]


# 行变列
def vertical(str):
    list = []
    for s in str:
        list.append(s)
    return "\n".join(list)


# 根据字的长度决定缩放换行
def decrement(text):
    length = len(text)
    result = []
    cardinality = 9
    if length > 4 * cardinality:
        return [False]
    numberOfSlices = 1
    while length > cardinality:
        numberOfSlices += 1
        length -= cardinality
    result.append(numberOfSlices)
    # Optimize for two columns
    space = " "
    length = len(text)
    if numberOfSlices == 2:
        if length % 2 == 0:
            # even
            fillIn = space * int(9 - length / 2)
            return [
                numberOfSlices,
                text[: int(length / 2)] + fillIn,
                fillIn + text[int(length / 2):],
            ]
        else:
            # odd number
            fillIn = space * int(9 - (length + 1) / 2)
            return [
                numberOfSlices,
                text[: int((length + 1) / 2)] + fillIn,
                fillIn + space + text[int((length + 1) / 2):],
            ]
    for i in range(0, numberOfSlices):
        if i == numberOfSlices - 1 or numberOfSlices == 1:
            result.append(text[i * cardinality:])
        else:
            result.append(text[i * cardinality: (i + 1) * cardinality])
    return result
