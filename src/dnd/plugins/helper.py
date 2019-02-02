from config.help_config import *
from msg import filter


# 查看命令帮助列表
@filter(r'.comm')
def comm_helper(content):
    msg = ''
    for k, v in COM_HELP.items():
        msg += f'{k}:{v}\n'
    return msg


# 查询指定关键词的帮助信息
@filter(r'.help ')
def helper(content):
    comm = content['message']
    comm = comm.replace('.help ', '')
    result = HELPER.get(comm)
    if result is not None:
        return result
    return '未找到相应的帮助信息'
