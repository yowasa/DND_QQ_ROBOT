import re

cmd_msg='2 2'
msg_m=re.compile(r'[1-4]').findall(cmd_msg)
print(len(msg_m))
print(msg_m[0])
print(msg_m[1])


