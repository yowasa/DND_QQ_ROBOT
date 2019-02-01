from config.help_config import *
from msg import filter


def comm_helper():
    msg = ''
    for k, v in COM_HELP.items():
        msg += f'{k}:{v}\n'
    return msg


@filter(r'.help ')
def helper(content):
    helper.msg='aaa'
    comm = content['message']
    comm = comm.replace('.help ', '')
    result = HELPER.get(comm)
    if result is not None:
        return result
    return '未找到相应的帮助信息'


print(helper.re_msg)

# for name in helper.__dir__():
#     print(name,str(getattr(helper,name,None)))
