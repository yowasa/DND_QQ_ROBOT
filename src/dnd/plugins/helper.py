from config import *


def comm_helper():
    msg = ''
    for k, v in COM_HELP.items():
        msg += f'{k}:{v}\n'
    return msg


def helper(content):
    comm = content['message']
    comm = comm.replace('.help ', '')
    result = HELPER.get(comm)
    if result is not None:
        return result
    return '未找到相应的帮助信息'
