from robobrowser import RoboBrowser
from filter import msg_route
import json


@msg_route(r'嘴臭一下$')
def zuichou_now(content):
    b = RoboBrowser(history=True)
    b.open('https://s.nmsl8.club/getloveword?type=2')
    ls = b.response.text
    a = json.loads(ls)
    return a['content']