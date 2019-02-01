import re

import os
import importlib

from inspect import isfunction

register = dict()


def init(package='plugins'):
    global register

    modules = []
    files = os.listdir(package)

    for file in files:
        if not file.startswith("__"):
            name, ext = os.path.splitext(file)
            modules.append("." + name)

    for module in modules:
        module = importlib.import_module(module, package)
        for attr in dir(module):
            if not attr.startswith("__"):
                func = getattr(module, attr)
                if isfunction(func):
                    re_msg = getattr(func, 're_msg', None)
                    if re_msg:
                        register[re_msg] = func


def filter(content):
    cmd_msg = content['message']
    for key in dict(register).keys():
        if re.match(key, cmd_msg):
            func = register.get(key)
            func(content)
