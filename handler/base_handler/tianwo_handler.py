from robobrowser import RoboBrowser
from filter import msg_route
import json


@msg_route(r'舔我$')
def tianwo_now(content):
    b = RoboBrowser(history=True)
    b.open('https://s.nmsl8.club/getloveword?type=1')
    ls = b.response.text
    a = json.loads(ls)
    return a['content']

@msg_route(r'朋友圈$')
def tianwo_now(content):
    b = RoboBrowser(history=True)
    b.open('https://s.nmsl8.club/getloveword?type=3')
    ls = b.response.text
    a = json.loads(ls)
    return a['content']

@msg_route(r'毒鸡汤$')
def tianwo_now(content):
    b = RoboBrowser(history=True)
    b.open('https://s.nmsl8.club/getloveword?type=4')
    ls = b.response.text
    a = json.loads(ls)
    return a['content']