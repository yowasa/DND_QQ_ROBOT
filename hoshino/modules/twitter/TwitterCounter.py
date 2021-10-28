import os
import sqlite3

from hoshino.config.__bot__ import BASE_DB_PATH

CACHE_DB_PATH = os.path.expanduser(BASE_DB_PATH + 'twitter.db')


class SubInfo():
    def __init__(self, r=None):
        if r:
            self.gid = r[0]
            self.subid = r[1]
            self.mode = r[1]
            self.last_time = r[2]


class TwitterCounter():

    def __init__(self):
        os.makedirs(os.path.dirname(CACHE_DB_PATH), exist_ok=True)
        self._create_subscribe()

    def _connect(self):
        return sqlite3.connect(CACHE_DB_PATH)

    def _create_subscribe(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS TWITTWE_SUB
                          (GID             INT    NOT NULL,
                           SUBID           TEXT    NOT NULL,
                           MODE            INT      NOT NULL,
                           LAST_TIME INT,
                           PRIMARY KEY(GID, SUBID));''')
        except:
            raise Exception('创建B站订阅表发生错误')

    def _get_sub(self, gid, subid):
        try:
            r = self._connect().execute(
                f'SELECT * FROM TWITTWE_SUB WHERE GID={gid} AND SUBID={subid}', ).fetchall()
            if r:
                sub = SubInfo(r=r[0])
                return sub
            else:
                return None
        except:
            raise Exception('查找订阅信息时生错误')

    def _get_sub_list(self, gid):
        try:
            r = self._connect().execute(
                f'SELECT * FROM TWITTWE_SUB WHERE GID={gid}', ).fetchall()
            if r:
                return [SubInfo(r=i) for i in r]
            else:
                return []
        except:
            raise Exception('查找订阅信息时生错误')

    def _get_all_sub(self):
        try:
            r = self._connect().execute(
                f'SELECT * FROM TWITTWE_SUB', ).fetchall()
            if r:
                return [SubInfo(r=i) for i in r]
            else:
                return []
        except:
            raise Exception('查找订阅信息时生错误')

    def _save_sub_info(self, sub: SubInfo):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO TWITTWE_SUB (GID, SUBID,MODE,LAST_TIME) VALUES (?, ?,?, ?)",
                (sub.gid, sub.subid, sub.mode, sub.last_time),
            )

    def _del_sub(self, gid, sub_id):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM TWITTWE_SUB WHERE GID={gid} AND SUBID={sub_id}")
