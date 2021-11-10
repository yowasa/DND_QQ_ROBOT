import aiofiles
import aiohttp
import cv2
import numpy as np
from PIL import Image, ImageFilter
from hoshino import R
from hoshino.typing import CommandSession
from hoshino.util.image_utils import CreateImg, pic2b64
from hoshino.util.message_builder import image
from hoshino.util.utils import is_number
from . import sv

@sv.on_command('修改图片', aliases=('操作图片', '改图'))
async def update_img(session: CommandSession):
    bot = session.bot
    event = session.event
    state = session.state
    method = session.get('method', prompt=f"要使用图片的什么操作呢？{method_str}")
    method_flag = method
    if method_flag not in method_oper:
        del state['method']
        method_flag = session.get('method', prompt=f"操作不正确，请重新输入！{method_str}")
    if method_flag in ["1", "修改尺寸"]:
        x = session.get('x', prompt="请输入宽度")
        if not is_number(str(x)):
            del state['x']
            x = session.get('x', prompt="宽度不正确！请重新输入数字...")
        y = session.get('y', prompt="请输入长度")
        if not is_number(str(y)):
            del state['y']
            y = session.get('y', prompt="长度不正确！请重新输入数字...")

    elif method_flag in ["2", "等比压缩", "3", "旋转图片"]:
        x = session.get('x', prompt="请输入比率/角度")
        if not is_number(str(x)):
            del state['x']
            x = session.get('x', prompt="比率/角度不正确！请重新输入数字...")
        y = ""
    elif method_flag in [
        "4",
        "水平翻转",
        "5",
        "铅笔滤镜",
        "6",
        "模糊效果",
        "7",
        "锐化效果",
        "8",
        "高斯模糊",
        "9",
        "边缘检测",
    ]:
        x = ""
        y = ""
    elif method_flag in ["10", "底色替换"]:
        x = session.get('x', prompt=f"请输原图底色: 红 蓝")
        if x not in ["红色", "蓝色", "红", "蓝"]:
            del state['x']
            x = session.get('x', prompt=f"请输入原图底色红色或者蓝色！")
        y = session.get('y', prompt=f"请输入支持的替换的底色：\n红色 蓝色 白色 绿色")
        if state.get("_current_key") == "y":
            if y not in [
                "红色",
                "白色",
                "蓝色",
                "绿色",
                "黄色",
                "红",
                "白",
                "蓝",
                "绿",
                "黄",
            ]:
                del state['y']
                y = session.get('y', prompt=f"输入错误！请输入支持的替换的底色：\n红色 蓝色 白色 绿色")
    img_list = session.get('img', prompt=f"来图速来！")
    if is_number(x):
        x = float(x)
    if is_number(y):
        y = int(y)
    index = 0
    result = ""
    async with aiohttp.ClientSession() as session:
        for img_url in img_list:
            async with session.get(img_url, timeout=7) as response:
                if response.status == 200:
                    async with aiofiles.open(
                            R.get(f'img/ghs/cache/temp/{event.user_id}_{index}_update.png').path, "wb"
                    ) as f:
                        await f.write(await response.read())
                        index += 1
                else:
                    await bot.finish(event, "获取图片超时了...", at_sender=True)
    if index == 0:
        return
    if method in ["修改尺寸", "1"]:
        for i in range(index):
            img = Image.open(R.get(f'img/ghs/cache/temp/{event.user_id}_{i}_update.png').path)
            img = img.convert("RGB")
            img = img.resize((int(x), int(y)), Image.ANTIALIAS)
            result += image(b64=pic2b64(img))
        await bot.send(event, result, at_sender=True)
        return
    if method in ["等比压缩", "2"]:
        for i in range(index):
            img = Image.open(R.get(f'img/ghs/cache/temp/{event.user_id}_{i}_update.png').path)
            width, height = img.size
            img = img.convert("RGB")
            if width * x < 8000 and height * x < 8000:
                img = img.resize((int(x * width), int(x * height)))
                result += image(b64=pic2b64(img))
            else:
                await bot.send(event, f"不支持图片压缩后宽或高大于8000的存在！！")
                return
    if method in ["旋转图片", "3"]:
        for i in range(index):
            img = Image.open(R.get(f'img/ghs/cache/temp/{event.user_id}_{i}_update.png').path)
            img = img.rotate(x)
            result += image(b64=pic2b64(img))
    if method in ["水平翻转", "4"]:
        for i in range(index):
            img = Image.open(R.get(f'img/ghs/cache/temp/{event.user_id}_{i}_update.png').path)
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
            result += image(b64=pic2b64(img))
    if method in ["铅笔滤镜", "5"]:
        for i in range(index):
            img = Image.open(
                R.get(f'img/ghs/cache/temp/{event.user_id}_{i}_update.png').path
            ).filter(ImageFilter.CONTOUR)
            result += image(b64=pic2b64(img))
    if method in ["模糊效果", "6"]:
        for i in range(index):
            img = Image.open(
                R.get(f'img/ghs/cache/temp/{event.user_id}_{i}_update.png').path
            ).filter(ImageFilter.BLUR)
            result += image(b64=pic2b64(img))
    if method in ["锐化效果", "7"]:
        for i in range(index):
            img = Image.open(
                R.get(f'img/ghs/cache/temp/{event.user_id}_{i}_update.png').path
            ).filter(ImageFilter.EDGE_ENHANCE)
            result += image(b64=pic2b64(img))
    if method in ["高斯模糊", "8"]:
        for i in range(index):
            img = Image.open(
                R.get(f'img/ghs/cache/temp/{event.user_id}_{i}_update.png').path
            ).filter(ImageFilter.GaussianBlur)
            result += image(b64=pic2b64(img))
    if method in ["边缘检测", "9"]:
        for i in range(index):
            img = Image.open(
                R.get(f'img/ghs/cache/temp/{event.user_id}_{i}_update.png').path
            ).filter(ImageFilter.FIND_EDGES)
            result += image(b64=pic2b64(img))
    if method in ["底色替换", "10"]:
        if x in ["蓝色", "蓝"]:
            lower = np.array([90, 70, 70])
            upper = np.array([110, 255, 255])
        if x in ["红色", "红"]:
            lower = np.array([0, 135, 135])
            upper = np.array([180, 245, 230])
        if y in ["蓝色", "蓝"]:
            color = (255, 0, 0)
        if y in ["红色", "红"]:
            color = (0, 0, 255)
        if y in ["白色", "白"]:
            color = (255, 255, 255)
        if y in ["绿色", "绿"]:
            color = (0, 255, 0)
        if y in ["黄色", "黄"]:
            color = (0, 255, 255)
        for k in range(index):

            img = cv2.imread(R.get(f'img/ghs/cache/temp/{event.user_id}_{k}_update.png').path)
            img = cv2.resize(img, None, fx=0.3, fy=0.3)
            rows, cols, channels = img.shape
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, lower, upper)
            # erode = cv2.erode(mask, None, iterations=1)
            dilate = cv2.dilate(mask, None, iterations=1)
            for i in range(rows):
                for j in range(cols):
                    if dilate[i, j] == 255:
                        img[i, j] = color
            cv2.imwrite(R.get(f'img/ghs/cache/temp/{event.user_id}_{k}_update.png').path, img)
        for i in range(index):
            result += image(f"{event.user_id}_{i}_ok_update.png", "temp")
    await bot.send(event, result, at_sender=True)


method_list = [
    "修改尺寸",
    "等比压缩",
    "旋转图片",
    "水平翻转",
    "铅笔滤镜",
    "模糊效果",
    "锐化效果",
    "高斯模糊",
    "边缘检测",
    "底色替换",
]
method_str = ""
method_oper = []
for i in range(len(method_list)):
    method_str += f"\n{i + 1}.{method_list[i]}"
    method_oper.append(method_list[i])
    method_oper.append(str(i + 1))


@update_img.args_parser
async def _(session: CommandSession):
    bot = session.bot
    event = session.event
    if str(session.current_arg) in ["取消", "算了"]:
        await bot.finish(event, "已取消操作..", at_sender=True)
    text = session.current_arg_text
    img = session.current_arg_images
    if img:
        session.state[session.current_key] = img
    else:
        session.state[session.current_key] = text
