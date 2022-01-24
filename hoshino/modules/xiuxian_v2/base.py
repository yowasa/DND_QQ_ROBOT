from hoshino import Service, priv
from hoshino.typing import CQEvent
from hoshino.util.utils import get_message_at, get_message_text
sv = Service('修仙v2', manage_priv=priv.SUPERUSER, enable_on_default=False, visible=True, bundle='修仙', help_=
'''[#修仙手册] 查询修仙帮助
''')