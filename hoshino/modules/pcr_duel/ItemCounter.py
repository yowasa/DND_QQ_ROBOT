import os
import sqlite3
from datetime import datetime

from hoshino.config.__bot__ import BASE_DB_PATH

DUEL_DB_PATH = os.path.expanduser(BASE_DB_PATH + 'item.db')


class ItemCounter:
    def __init__(self):
        os.makedirs(os.path.dirname(DUEL_DB_PATH), exist_ok=True)
        self._create_item()
        self._create_group()

    def _connect(self):
        return sqlite3.connect(DUEL_DB_PATH)

    def _create_item(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS ITEM
                          (GID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           ITEM_ID           INT    NOT NULL,
                           ITEM_COUNT           INT    NOT NULL,
                           PRIMARY KEY(GID, UID,ITEM_ID));''')
        except:
            raise Exception('创建角道具表发生错误')

    def _create_group(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS GROUP_INFO
                          (GID             INT    NOT NULL,
                           INFO_TYPE           INT    NOT NULL,
                           INFO_FLAG           INT    NOT NULL,
                           PRIMARY KEY(GID, INFO_TYPE));''')
        except:
            raise Exception('创建群状态表发生错误')

    def _save_group_state(self, gid, type, type_flag):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO GROUP_INFO (GID, INFO_TYPE, INFO_FLAG) VALUES (?, ?, ?)",
                (gid, type, type_flag),
            )
    # 0 为梭哈标识 到准点自动关闭
    def _get_sou_state(self):
        try:
            r = self._connect().execute("SELECT GID FROM GROUP_INFO WHERE INFO_TYPE=0 AND INFO_FLAG=1",
                                        ).fetchall()
            if r is None:
                return []
            return r
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return []

    # 获取道具列表
    def _get_item(self, gid, uid):
        try:
            r = self._connect().execute("SELECT ITEM_ID,ITEM_COUNT FROM ITEM WHERE GID=? AND UID=? AND ITEM_COUNT>0",
                                        (gid, uid)).fetchall()
            if r is None:
                return []
            return r
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return []

    # 获取道具数量
    def _get_item_num(self, gid, uid, iid):
        try:
            r = self._connect().execute(
                "SELECT ITEM_COUNT FROM ITEM WHERE GID=? AND UID=? AND ITEM_ID=?",
                (gid, uid, iid)).fetchone()
            if r is None:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))

    # 增加道具
    def _add_item(self, gid, uid, iid, num=1):
        now_num = self._get_item_num(gid, uid, iid)
        now_num = now_num + num
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO ITEM (GID, UID, ITEM_ID, ITEM_COUNT) VALUES (?, ?, ?, ?)",
                (gid, uid, iid, now_num),
            )
            return now_num

