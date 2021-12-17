from hoshino import Service, priv
from hoshino.typing import CQEvent
sv = Service('修仙', manage_priv=priv.SUPERUSER, enable_on_default=False, visible=True, bundle='修仙', help_=
'''[#修仙手册] 查询修仙帮助
''')