import paddlehub as hub
import json
import random
from hoshino import Service, priv, R
from nonebot.natural_language import NLPSession
from hoshino.typing import CommandSession
import time
import math
from jieba import posseg
from hoshino.util import request
import os
from pathlib import Path

model = hub.Module(name="plato-mini")


class SpeedList:
    def __init__(self):
        self.maxlen = 1000
        self.list = []

    def push(self, e):
        self.list.append(e)
        if (len(self.list) > self.maxlen):
            self.list.pop(0)

    def get(self):
        return self.list


group_talk_cache = {}
user_talk_cache = {}

sv = Service('对话功能', manage_priv=priv.SUPERUSER, enable_on_default=True, bundle="聊天")

CHAT_PATH = Path(R.get('chat').path)
os.makedirs(CHAT_PATH, exist_ok=True)
KIMO_URL = "https://cdn.jsdelivr.net/gh/Kyomotoi/AnimeThesaurus/data.json"


class Chat(object):
    def __init__(self):
        pass

    @staticmethod
    async def _request(url: str) -> dict:
        res = await request.get(url)
        data = await res.json()
        return data

    @classmethod
    async def _generate_data(cls) -> None:
        file_name = "kimo.json"
        path = CHAT_PATH / file_name
        if not path.is_file():
            data = await cls._request(KIMO_URL)
            with open(path, "w", encoding="utf-8") as w:
                w.write(json.dumps(data, indent=4))

    @classmethod
    async def _load_data(cls) -> dict:
        file_name = "kimo.json"
        path = CHAT_PATH / file_name
        if not path.is_file():
            await cls._generate_data()

        with open(path, "r", encoding="utf-8") as r:
            data = json.loads(r.read())
        return data

    @classmethod
    async def update_data(cls) -> None:
        file_name = "kimo.json"
        path = CHAT_PATH / file_name
        if not path.is_file():
            await cls._generate_data()

        updata_data = await cls._request(KIMO_URL)
        data = json.loads(path.read_bytes())
        for i in updata_data:
            if i not in data:
                data[i] = updata_data[i]

        with open(path, "w", encoding="utf-8") as w:
            w.write(json.dumps(data, indent=4))

    @staticmethod
    def name_is(user_id: str, new_name: str):
        file_name = "users.json"
        path = CHAT_PATH / file_name
        if not path.is_file():
            with open(path, "w", encoding="utf-8") as w:
                w.write(json.dumps({}))

        data = json.loads(path.read_bytes())
        data[user_id] = new_name

        with open(path, "w", encoding="utf-8") as w:
            w.write(json.dumps(data, indent=4))

    @staticmethod
    def load_name(user_id: str) -> str:
        file_name = "users.json"
        path = CHAT_PATH / file_name
        if not path.is_file():
            with open(path, "w", encoding="utf-8") as w:
                w.write(json.dumps({}))
            return "你"

        data = json.loads(path.read_bytes())
        try:
            result = data[user_id]
        except BaseException:
            result = "你"
        return result

    @classmethod
    async def deal(cls, msg: str, user_id: str) -> str:
        keywords = posseg.lcut(msg)
        random.shuffle(keywords)

        data = await cls._load_data()

        repo = str()
        for i in keywords:
            a = i.word
            b = list(a)
            try:
                if b[0] == b[1]:
                    a = b[0]
            except BaseException:
                pass
            if a in data:
                repo = data.get(a, str())

        if not repo:
            temp_data = list(data)
            random.shuffle(temp_data)
            for i in temp_data:
                if i in msg:
                    repo = data.get(i, str())

        a = random.choice(repo) if type(repo) is list else repo
        user_name = cls.load_name(user_id)
        repo = a.replace("你", user_name)
        return repo


# @sv.on_natural_language(only_to_me=False)
# async def group_random(session: NLPSession):
#     ev = session.event
#     bot = session.bot
#     gid = ev.group_id
#     msg = ev['message'].extract_plain_text()
#     if not msg:
#         return
#     if len(msg) > 500:
#         return
#     if not group_talk_cache.get(gid):
#         group_talk_cache[gid] = SpeedList()
#     group_talk_cache[gid].push(msg)
#     rn=random.random()
#     if rn > 0.05:
#         return
#     resp = model.predict([group_talk_cache[gid].get()])[0]
#     await bot.send(ev, resp)

chat = Chat()


@sv.on_command("叫我", aliases=("我是"))
async def my_name_is(session: CommandSession):
    event = session.event
    bot = session.bot
    uid = event.user_id
    new_name = session.get("name", prompt="欧尼酱想让咱如何称呼呢！0w0")
    chat.name_is(uid, new_name)
    repo = random.choice(
        [
            f"好~w 那咱以后就称呼你为{new_name}！",
            f"噢噢噢！原来你叫{new_name}阿~",
            f"好欸！{new_name}ちゃん~~~",
            "很不错的称呼呢w",
        ]
    )
    await bot.send(repo, at_sender=True)


@my_name_is.args_parser
async def _(session: CommandSession):
    text = session.current_arg_text
    img = session.current_arg_images
    if session.is_first_run:
        if text:
            session.state['name'] = text.strip()
        return
    if img:
        session.state[session.current_key] = img
    else:
        session.state[session.current_key] = text


import requests


@sv.on_natural_language(only_to_me=True)
async def only2me(session: NLPSession):
    ev = session.event
    bot = session.bot
    gid = ev.group_id
    uid = ev.user_id
    msg = ev['message'].extract_plain_text()
    if not msg:
        return
    if len(msg) > 500:
        return
    endtime = time.time()
    endtime = math.ceil(endtime)
    guid = gid
    if not user_talk_cache.get(guid):
        user_talk_cache[guid] = {"cache": SpeedList(), "time": endtime}
    # if user_talk_cache[guid]['time'] - endtime > 600:
    #     del user_talk_cache[guid]
    #     user_talk_cache[guid] = {"cache": SpeedList(), "time": endtime}
    # user_talk_cache[guid]["time"] = endtime
    # 随机聊天处理
    user_talk_cache[guid]["cache"].push(msg)
    # 青云客先匹配处理
    resp = str()
    fit = False
    for i in ['天气', '翻译', '怎么', '什么', '歌词', '计算', '等于', '是多少', '归属', '五笔', '拼音', '笑话', '翻译', '成语']:
        if i in msg:
            fit = True
            break
    if fit:
        res = requests.get(f'https://api.qingyunke.com/api.php?key=free&appid=0&msg={msg}')
        data = res.json()
        repo_msg = data.get("content", str())
        repo_msg = repo_msg.replace("{br}", "\n")
        resp = repo_msg.replace("菲菲", "朝日")
    if not resp:
        # 文爱机器人再处理
        if random.randint(1, 5) != 1:
            resp = await chat.deal(msg, uid)
    if not resp:
        resp = model.predict([user_talk_cache[guid]["cache"].get()])[0]
    user_talk_cache[guid]["cache"].push(resp)
    await bot.send(ev, resp)
