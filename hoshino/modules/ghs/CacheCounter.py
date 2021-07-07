import os
import sqlite3

from hoshino.config.__bot__ import BASE_DB_PATH

CACHE_DB_PATH = os.path.expanduser(BASE_DB_PATH+'cache.db')

# 记录贵族相关数据

class CacheCounter:
    def __init__(self):
        os.makedirs(os.path.dirname(CACHE_DB_PATH), exist_ok=True)
        self._create_pixivcachetable()

    def _connect(self):
        return sqlite3.connect(CACHE_DB_PATH)

    def _create_pixivcachetable(self):
        try:
            self._connect().execute('''
                    create table IF NOT EXISTS pixivcache
                    (
                        pixiv_id INT not null,
                        "group" INT not null,
                        message VARCHAR(2000) not null,
                        PRIMARY KEY(pixiv_id, "group")
                    );
''')
        except:
            raise Exception('创建p站缓存时发生错误')

    def _get_cache(self, pixiv_id, group):
        try:
            r = self._connect().execute('SELECT message FROM pixivcache WHERE pixiv_id=? AND "group"=?', (pixiv_id, group)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找p站缓存时生错误')

    def _set_cache(self, pixiv_id, group, message):
        with self._connect() as conn:
            conn.execute(
                'INSERT OR REPLACE INTO pixivcache (pixiv_id, "group", message) VALUES (?, ?, ?)',
                (pixiv_id, group, message),
            )