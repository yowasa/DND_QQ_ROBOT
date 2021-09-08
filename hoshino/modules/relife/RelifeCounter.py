import os
import sqlite3
import json
from hoshino.config.__bot__ import BASE_DB_PATH

CACHE_DB_PATH = os.path.expanduser(BASE_DB_PATH + 'relife.db')


# 记录贵族相关数据
def trance_relifeobj(e):
    return RelifeObj(e)


class RelifeObj():
    def __init__(self, r):
        self.gid = r[0]
        self.uid = r[1]
        self.re_time = r[2]
        self.talent = r[3]
        self.state = r[4]
        self.data = eval(r[5])


class RelifeCounter:
    def __init__(self):
        os.makedirs(os.path.dirname(CACHE_DB_PATH), exist_ok=True)
        self._create_relife_retained()

    def _connect(self):
        return sqlite3.connect(CACHE_DB_PATH)

    def _create_relife_retained(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS RELIFE_RETAINED
                          (GID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           RE_TIME           INT    NOT NULL DEFAULT 0,
                           TALENT           INT     NOT NULL DEFAULT 0,
                           STATE        INT     NOT NULL DEFAULT 0,
                           CONF         TEXT NOT NULL DEFAULT '{}',
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建人生重开表发生错误')

    # 查询重开次数
    def _get_relife_time(self, gid, uid):
        try:
            r = self._connect().execute("SELECT RE_TIME FROM RELIFE_RETAINED WHERE GID=? AND UID=?",
                                        (gid, uid)).fetchone()
            if r is None:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0

    # 查询留存天赋
    def _get_ratain_talent(self, gid, uid):
        try:
            r = self._connect().execute("SELECT TALENT FROM RELIFE_RETAINED WHERE GID=? AND UID=?",
                                        (gid, uid)).fetchone()
            if r is None:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0

    # 获取重开信息
    def _get_relife(self, gid, uid):
        try:
            r = self._connect().execute("SELECT * FROM RELIFE_RETAINED WHERE GID=? AND UID=?",
                                        (gid, uid)).fetchone()
            if r is None:
                with self._connect() as conn:
                    conn.execute(
                        "INSERT OR REPLACE INTO RELIFE_RETAINED (GID, UID) VALUES (?, ?)",
                        (gid, uid),
                    )
                r = self._connect().execute("SELECT * FROM RELIFE_RETAINED WHERE GID=? AND UID=?",
                                            (gid, uid)).fetchone()
            return trance_relifeobj(r)
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0

    # 保存状态
    def _save_relife(self, obj: RelifeObj):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO RELIFE_RETAINED (GID, UID, RE_TIME, TALENT, STATE, CONF) VALUES (?, ?, ?, ?, ?, ?)",
                (obj.gid, obj.uid, obj.re_time, obj.talent, obj.state, str(obj.data)),
            )


