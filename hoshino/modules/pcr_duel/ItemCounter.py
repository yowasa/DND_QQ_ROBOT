import os
import sqlite3
from datetime import datetime
from enum import Enum

from hoshino.config.__bot__ import BASE_DB_PATH

DUEL_DB_PATH = os.path.expanduser(BASE_DB_PATH + 'item.db')


# 用户状态储存枚举类 100-200被领地建筑占据，不要插入
class UserModel(Enum):
    BATTLE = [0, "战斗力BUFF，数字是{num}%增加计算"]
    FENSHOU = [1, "分手次数计数器"]
    FENJIE = [2, "分解装备次数计数器"]
    CHOU = [3, "抽取装备次数计数器"]
    WIN = [4, "决斗胜利计数器"]
    LOSE = [5, "决斗失败计数器"]
    YUE_FAILE = [6, "约会失败计数器"]
    EQUIP_UP = [7, "贤者之石计数器"]
    YONGHENG = [8, "是否已经获取过永恒爱恋"]
    MANOR_BEGIN = [9, "是否已经开启了领地"]
    ZHI_AN = [10, "领地治安"]
    GENGDI = [11, "耕地占比"]
    BUILD_CD = [12, "建筑CD"]
    BUILD_BUFFER = [13, "正在建造的建筑"]
    MANOR_POLICY = [14, "领地政策"]
    TAX_RATIO = [15, "领地税率"]
    ITEM_BUY_TIME = [16, "购买道具次数"]
    TECHNOLOGY_BUFFER = [17, "正在研发的科技"]
    TECHNOLOGY_CD = [18, "研发CD"]


# 群组状态储存枚举类
class GroupModel(Enum):
    OFF_SUO = [0, "定时关闭梭哈庆典标识"]
    OFF_FREE = [1, "定时关闭免费招募庆典标识"]


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
    def _save_group_state(self, gid, type, type_flag):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO GROUP_INFO (GID, INFO_TYPE, INFO_FLAG) VALUES (?, ?, ?)",
                (gid, type, type_flag),
            )

    # 获取有梭哈庆典自动关闭标识的群
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
