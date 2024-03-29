"""
nonebot相关配置
"""

# hoshino监听的端口与ip
PORT = 8080
HOST = '127.0.0.1'  # 本地部署使用此条配置（QQ客户端和bot端运行在同一台计算机）
# HOST = '0.0.0.0'      # 开放公网访问使用此条配置（不安全）

DEBUG = False  # 调试模式

WHITE_LIST = []
SUPERUSERS = [2508488843]  # 填写超级用户的QQ号，可填多个用半角逗号","隔开
NICKNAME = '朝日'  # 机器人的昵称。呼叫昵称等同于@bot，可用元组配置多个昵称

COMMAND_START = {''}  # 命令前缀（空字符串匹配任何消息）
COMMAND_SEP = set()  # 命令分隔符（hoshino不需要该特性，保持为set()即可）

# 发送图片的协议
# 可选 http, file, base64
# 当QQ客户端与bot端不在同一台计算机时，可用http协议
RES_PROTOCOL = 'file'
# 资源库文件夹，需可读可写，windows下注意反斜杠转义
RES_DIR = r'~/Documents/content/Resources'
# 使用http协议时需填写，原则上该url应指向RES_DIR目录
RES_URL = 'http://127.0.0.1:5000/static/'

# DB文件存放目录
BASE_DB_PATH = "~/Documents/content/DB/"
# 启用的模块
# 初次尝试部署时请先保持默认
# 如欲启用新模块，请认真阅读部署说明，逐个启用逐个配置
# 切忌一次性开启多个
MODULES_ON = {
    # 'bilibili', # B站相关
    'botmanage',  # 骰娘管理
    # 'bt', # bt搜索
    # 'chat',
    # 'coser',
    # 'dice', #骰子功能
    # 'dnd', #DND跑团
    # 'gen_img',  # 图片生成器
    # 'ghs', #Pixiv功能
    'groupmaster',  # 基础群组功能
    # 'hourcall', # 准点报时
    # 'majsoul', # 雀魂查询
    # 'mikan', #蜜柑番剧订阅
    'pcr_duel', # 贵族决斗
    # 'relife',  # 人生重开模拟器
    # 'saucenao', # 搜图功能
    # 'setu_renew', # 新版色图功能
    # 'telegram',# 电报功能
    # 'touhou_img', #东方人工智能识图
    # 'traceanime', # 搜番功能
    # 'twitter',  # 轮询版转推（old）
    # 'twitter_stream', # 推流版转推（beta）
    # 'updlc', #自定义贵族
    'xiuxian',  # 修仙
    # 'xiuxian_v2',  # 修仙
}
