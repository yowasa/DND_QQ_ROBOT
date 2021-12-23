import os
import sqlite3
from enum import Enum

from hoshino.config.__bot__ import BASE_DB_PATH

DUEL_DB_PATH = os.path.expanduser(BASE_DB_PATH + 'xiuxian_his.db')


# 用户状态历史储存枚举类
class UserHistory(Enum):
    MAX_LEVEL = [0, "最高境界"]
    MAX_DO = [1, "最多行动次数"]
    RESTART_LINGSHI= [2, "留存灵石"]
    RESTART_ITEM = [3, "留存道具"]
    RESTART_XINFA = [4, "留存心法"]
    RESTART_GONGFA = [5, "留存功法"]
    RESTART_SHENTONG = [6, "留存神通"]
    RESTART_TIANFU = [7, "留存天赋"]
    MAX_HP= [8, "死亡时最高的血量"]
    MAX_MP = [9, "死亡时最高的蓝量"]
    MAX_ACT = [10, "死亡时最高的物理攻击"]
    MAX_ACT2 = [11, "死亡时最高的术法攻击"]
    MAX_DEFEN1 = [12, "死亡时最高的物理防御"]
    MAX_DEFEN2 = [13, "死亡时最高的术法防御"]

# 群组状态历史枚举类
class GroupHistory(Enum):
    OFF_FREE = [1, "定时关闭免费招募庆典标识"]
    WEATHER = [2, "天气"]


class HistoryCounter:
    def __init__(self):
        os.makedirs(os.path.dirname(DUEL_DB_PATH), exist_ok=True)
        self._create_group()
        self._create_user()

    def _connect(self):
        return sqlite3.connect(DUEL_DB_PATH)

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

    # 存储用户信息
    def _save_user_info(self, gid, uid, user_state: UserHistory, flag):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO USER_INFO (GID, UID, BUFF_TYPE, BUFF_INFO) VALUES (?, ?, ?, ?)",
                (gid, uid, user_state.value[0], flag),
            )

    # 获取用户信息
    def _get_user_info(self, gid, uid, user_state: UserHistory):
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

    # 获取用户信息
    def _query_user_info(self, gid, uid):
        try:
            r = self._connect().execute(
                "SELECT BUFF_TYPE,BUFF_INFO FROM USER_INFO WHERE GID=? AND UID=? AND BUFF_INFO>0",
                (gid, uid),
            ).fetchall()
            if not r:
                return []
            return r
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0
        pass

    # 覆盖存储群组状态
    def _save_group_state(self, gid, type: GroupHistory, type_flag):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO GROUP_INFO (GID, INFO_TYPE, INFO_FLAG) VALUES (?, ?, ?)",
                (gid, type.value[0], type_flag),
            )

        # 获取用户信息

    def _get_group_state(self, gid, group_state: GroupHistory):
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
