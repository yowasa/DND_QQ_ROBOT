import os
import sqlite3
from enum import Enum

from hoshino.config.__bot__ import BASE_DB_PATH

DUEL_DB_PATH = os.path.expanduser(BASE_DB_PATH + 'xiuxian_item.db')


# 用户状态储存枚举类 100-200被城市建筑占据，不要插入
class UserModel(Enum):
    KILL = [0, "杀人计数器"]
    LINGSHI = [1, "灵石数量"]



# 群组状态储存枚举类
class GroupModel(Enum):
    OFF_FREE = [1, "定时关闭免费招募庆典标识"]
    WEATHER = [2, "天气"]


class ItemCounter:
    def __init__(self):
        os.makedirs(os.path.dirname(DUEL_DB_PATH), exist_ok=True)
        self._create_item()
        self._create_group()
        self._create_user()

    def _connect(self):
        return sqlite3.connect(DUEL_DB_PATH)

    # 道具表
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

    # 群组状态表
    def _create_group(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS GROUP_INFO
                          (GID             INT    NOT NULL,
                           INFO_TYPE           INT    NOT NULL,
                           INFO_FLAG           INT    NOT NULL,
                           PRIMARY KEY(GID, INFO_TYPE));''')
        except:
            raise Exception('创建群状态表发生错误')

    # 用户状态表
    def _create_user(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS USER_INFO
                          (GID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           BUFF_TYPE           INT    NOT NULL,
                           BUFF_INFO           INT    NOT NULL,
                           PRIMARY KEY(GID, UID,BUFF_TYPE));''')
        except:
            raise Exception('创建用户状态表发生错误')

    # 覆盖存储用户状态
    def _save_user_state(self, gid, uid, type, type_flag):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO USER_INFO (GID, UID, BUFF_TYPE, BUFF_INFO) VALUES (?, ?, ?, ?)",
                (gid, uid, type, type_flag),
            )

    # 存储用户信息
    def _save_user_info(self, gid, uid, user_state: UserModel, flag):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO USER_INFO (GID, UID, BUFF_TYPE, BUFF_INFO) VALUES (?, ?, ?, ?)",
                (gid, uid, user_state.value[0], flag),
            )

    # 获取用户信息
    def _get_user_info(self, gid, uid, user_state: UserModel):
        try:
            r = self._connect().execute(
                "SELECT BUFF_INFO FROM USER_INFO WHERE GID=? AND UID=? AND BUFF_TYPE=? AND BUFF_INFO>0",
                (gid, uid, user_state.value[0]),
            ).fetchone()
            if r is None:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0
        pass

    # 获取建筑信息
    def _get_build_info(self, gid, uid):
        try:
            r = self._connect().execute(
                "SELECT BUFF_TYPE,BUFF_INFO FROM USER_INFO WHERE GID=? AND UID=? AND BUFF_TYPE>100 AND BUFF_TYPE<200 AND BUFF_INFO>0",
                (gid, uid),
            ).fetchall()
            if r is None:
                return []
            return r
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return []

    # 获取建筑信息
    def _get_user_state(self, gid, uid, buff):
        try:
            r = self._connect().execute(
                "SELECT BUFF_INFO FROM USER_INFO WHERE GID=? AND UID=? AND BUFF_TYPE=? AND BUFF_INFO>0",
                (gid, uid, buff),
            ).fetchone()
            if not r:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0

    # 获取用户战斗buff状态
    def _get_buff_state(self, gid, uid):
        try:
            r = self._connect().execute(
                "SELECT BUFF_INFO FROM USER_INFO WHERE GID=? AND UID=? AND BUFF_TYPE=0 AND BUFF_INFO>0",
                (gid, uid),
            ).fetchone()
            if r is None:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0

    # 覆盖存储群组状态
    def _save_group_state(self, gid, type:GroupModel, type_flag):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO GROUP_INFO (GID, INFO_TYPE, INFO_FLAG) VALUES (?, ?, ?)",
                (gid, type.value[0], type_flag),
            )

        # 获取用户信息

    def _get_group_state(self, gid, group_state: GroupModel):
        try:
            r = self._connect().execute(
                "SELECT INFO_FLAG FROM GROUP_INFO WHERE GID=? AND INFO_TYPE=? AND INFO_FLAG>0",
                (gid, group_state.value[0]),
            ).fetchone()
            if r is None:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0
        pass

    # 获取超再生恢复
    def _get_all_user_recover(self):
        try:
            r = self._connect().execute("SELECT GID,UID,BUFF_INFO FROM USER_INFO WHERE BUFF_TYPE=23 AND BUFF_INFO>0",
                                        ).fetchall()
            if r is None:
                return []
            return r
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return []

    # 获取蓬莱恢复
    def _get_all_user_penglai(self):
        try:
            r = self._connect().execute(
                "SELECT GID,UID FROM USER_INFO WHERE BUFF_TYPE=25 AND BUFF_INFO=1",
            ).fetchall()
            if r is None:
                return []
            return r
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return []

    # 获取有免费招募自动关闭标识的群
    def _get_free_state(self):
        try:
            r = self._connect().execute("SELECT GID FROM GROUP_INFO WHERE INFO_TYPE=1 AND INFO_FLAG=1",
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
    # 获取道具数量
    def _count_item_num(self, gid, uid):
        try:
            r = self._connect().execute(
                "SELECT SUM(ITEM_COUNT) FROM ITEM WHERE GID=? AND UID=?",
                (gid, uid)).fetchone()
            if r[0] is None:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))