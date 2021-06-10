# 人品处理
import time
import random
from filter import msg_route
from enum import Enum
import os
from PIL import Image, ImageDraw, ImageFont
import json

data = {
    "pcr": "./resources/pcr-fortune",
    "genshin": "./resources/genshin-fortune"
}
env_dist = os.environ
cq_image_file = env_dist.get("cq_image_file")
if not cq_image_file:
    cq_image_file = '/Users/yowasa/workspace/mcl-1.0.5/data/OneBot/image/'


# 今日人品功能 沙雕群友快乐源泉
@msg_route(r'\s*\.jrrp', need_user=True)
def jrrp(content):
    sender = content['sender']
    nickname = sender['nickname']
    user = content.get('sys_user')
    jrrp_date = user.jrrp_date
    date = time.strftime("%Y-%m-%d")
    if not jrrp_date or jrrp_date != date:
        user.jrrp_date = date
        user.jrrp = random.randint(0, 100)
        user.save()
    return f'{nickname} 今天的运势是{user.jrrp}%！！！！！！！！！！'


# 抽签功能
@msg_route(r'\s*\.cq', need_user=True)
def cq(content):
    user = content.get('sys_user')
    msg = content.get('cmd_msg').strip()
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
    name = drawing(model, user.qq_number)
    # 打包成cq码
    return f'[CQ:image,file={name}]'


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


# 画图
def drawing(model, userQQ):
    RESOURCES_BASE_PATH = data[model.value[0]]
    fontPath = {
        "title": f"{RESOURCES_BASE_PATH}/font/Mamelon.otf",
        "text": f"{RESOURCES_BASE_PATH}/font/sakura.ttf",
    }
    imgPath = ""
    if model.value[1] != "default":
        imgPath = f"{RESOURCES_BASE_PATH}/img/frame_{model.value[1]}.jpg"
    else:
        imgPath = randomBasemap(RESOURCES_BASE_PATH)
    img = Image.open(imgPath)
    # Draw title
    draw = ImageDraw.Draw(img)
    text = copywriting(RESOURCES_BASE_PATH)
    title = getTitle(text, RESOURCES_BASE_PATH)
    text = text["content"]
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
    outPath = f'{cq_image_file}cq_{userQQ}.jpg'
    img.save(outPath)
    return f'cq_{userQQ}.jpg'


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
