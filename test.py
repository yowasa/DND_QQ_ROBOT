# import os
#
# result=os.system(("python script/call.py"))
#
# print(result)

from telethon import TelegramClient

# Remember to use your own values from my.telegram.org!
api_id = 16572086
api_hash = '8f6e9235e3f4c378fa67643d0bed0098'
client = TelegramClient('anon', api_id, api_hash, proxy=("socks5", '127.0.0.1', '50272'))
with client:
    me = client.get_me()
print(me)
