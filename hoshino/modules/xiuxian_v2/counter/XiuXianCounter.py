import os
import sqlite3
from enum import Enum

from hoshino.config.__bot__ import BASE_DB_PATH

CACHE_DB_PATH = os.path.expanduser(BASE_DB_PATH + 'xiuxian_v2.db')


# 用户信息
class UserInfo():
    def __init__(self, r=None):
        if r:
            self.uid = r[0]  # qq号
            self.name = r[1]  # 名称
            self.magic_root = r[2]  # 灵根
            self.exp = r[3]  # 经验
            self.grade = r[4]  # 大境界
            self.level = r[5]  # 小境界
            self.local = r[6]  # 所在地点
            self.belong = r[7]  # 门派
            self.arms = r[8]  # 武器
            self.armor = r[9]  # 防具
            self.magic_weapon = r[10]  # 法宝
            self.attr = r[11]  # 属性
            self.ability = r[12]  # 能力
            self.other = r[13]  # 其他


# 用户状态储存枚举类
class UserModel(Enum):
    KILL = [0, "杀人计数器"]
    LINGSHI = [1, "灵石数量"]
    SHANGSHI = [2, "伤势情况"]  # 0 未受伤 1 轻伤 2重伤 3濒死
    STUDY_GONGFA = [3, "正在学习的功法"]  # 功法学习进度
    GONGFA_RATE = [4, "正在学习的功法"]  # 功法学习进度
    XIUYANG_TIME = [5, "修养次数"]  # 修养次数
    ZHUJIDAN = [6, "筑基丹服用标识"]  # 筑基丹服用标识
    JINDANSHA = [7, "杀害金丹的数量"]  # 3次以上方能破丹
    HONGCHEN = [8, "红尘标识"]  # 触发过红尘之绊的标识
    QIUXIAN = [9, "求仙标识"]  # 触发过求仙之绊的标识
    MIJING = [10, "秘境标识"]  # 触发过秘境之绊的标识
    SHENZHOU = [11, "神州标识"]  # 触发过神州之绊的标识
    HUNYUAN = [12, "混元丹服用标识"]  # 混元丹服用标识
    LIANDAN_CD = [13, "炼丹cd"]  # 炼丹cd标识
    LIANDAN_ITEM = [14, "炼丹item"]  # 炼的丹药是什么
    ZUOYOU_XINFA = [15, "左右互博储存的心法"]
    ZUOYOU_GONGFA = [16, "左右互博储存的功法"]
    RANHUN = [17, "燃魂丹服用标识"]
    HUFA_NUM = [18, "护法数量"]
    DUANZAO_CD = [19, "锻造cd"]  # 锻造cd
    DUANZAO_ITEM = [20, "锻造item"]  # 锻造物品
    LIANBAO_ITEM = [21, "炼宝item"]
    LIANBAO_LINGQI = [22, "炼宝灵气"]
    BANGGONG = [23, "帮贡"]
    SUODI = [24, "缩地计数器"]
    MISSION = [25, "接受的任务id"]
    MISSION_COMPLETE = [26, "任务完成标识"]
    YOULI_DAQIAN = [27, "游历大千的地点"]
    YOULI_DAQIAN_COUNT = [28, "游历大千的次数"]
    WUXUE = [29, "武学交流的门派"]
    CHUANSONG = [30, "传送剩余次数"]
    YUANDAN_LIHE = [31, "元旦礼盒"]
    ACT_TIMES = [32, "行动次数"]


# 群组状态储存枚举类
class GroupModel(Enum):
    YUANDAN_BOSS = [0, "元旦限定Boss"]


class XiuXianCounter():

    def __init__(self):
        os.makedirs(os.path.dirname(CACHE_DB_PATH), exist_ok=True)
        self._create_user_table()
        self._create_item()
        self._create_user_model()
        self._create_group_model()
        self._create_trade()

    def _connect(self):
        return sqlite3.connect(CACHE_DB_PATH)

    def _create_user_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS USER_INFO
                          (UID INT    NOT NULL,
                           NAME TEXT NOT NULL,
                           MAGIC_ROOT TEXT NOT NULL,
                           EXP INT NOT NULL DEFAULT 0,
                           GRADE INT NOT NULL DEFAULT 0,
                           LEVEL INT NOT NULL DEFAULT 0,
                           LOCAL TEXT NOT NULL,
                           BELONG TEXT NOT NULL DEFAULT '无',
                           ARMS TEXT NOT NULL DEFAULT '无',
                           ARMOR TEXT NOT NULL DEFAULT '无',
                           MAGIC_WEAPON TEXT NOT NULL DEFAULT '无',
                           ATTR TEXT NOT NULL DEFAULT '{}',
                           ABILITY TEXT NOT NULL DEFAULT '{}',
                           OTHER TEXT NOT NULL DEFAULT '{}',
                           PRIMARY KEY(UID,NAME));''')
        except:
            raise Exception('创建修仙表发生错误')

    # 道具表
    def _create_item(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS ITEM
                              (UID           INT    NOT NULL,
                               ITEM_ID           INT    NOT NULL,
                               ITEM_COUNT           INT    NOT NULL,
                               PRIMARY KEY(UID,ITEM_ID));''')
        except:
            raise Exception('创建角道具表发生错误')

        # 群组状态表

    def _create_group_model(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS GROUP_MODEL
                                  (GID             INT    NOT NULL,
                                   INFO_TYPE           INT    NOT NULL,
                                   INFO_FLAG           INT    NOT NULL,
                                   PRIMARY KEY(GID, INFO_TYPE));''')
        except:
            raise Exception('创建群状态表发生错误')

    # 用户状态表
    def _create_user_model(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS USER_MODEL
                                  (UID           INT    NOT NULL,
                                   BUFF_TYPE           INT    NOT NULL,
                                   BUFF_INFO           INT    NOT NULL,
                                   PRIMARY KEY(GID, UID,BUFF_TYPE));''')
        except:
            raise Exception('创建用户状态表发生错误')

    # 交易表
    def _create_trade(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS TRADE_INFO
                                      (UID           INT    NOT NULL,
                                       ITEM_ID           INT    NOT NULL,
                                       PRICE           INT    NOT NULL,
                                       PRIMARY KEY(UID,ITEM_ID));''')
        except:
            raise Exception('创建交易表发生错误')

    def _get_user(self, uid):
        try:
            r = self._connect().execute(
                f'SELECT * FROM USER_INFO WHERE UID={uid}', ).fetchall()
            if r:
                sub = UserInfo(r=r[0])
                return sub
            else:
                return None
        except:
            raise Exception('查找用户信息时生错误')

    def _get_user_by_name(self, name):
        try:
            r = self._connect().execute(
                f'SELECT * FROM USER_INFO WHERE NAME="{name}"', ).fetchall()
            if r:
                sub = UserInfo(r=r[0])
                return sub
            else:
                return None
        except:
            raise Exception('查找用户信息时生错误')

    def _save_user_info(self, user: UserInfo):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO USER_INFO (UID, NAME, MAGIC_ROOT, EXP, GRADE, LEVEL, LOCAL, BELONG, ARMS, ARMOR, MAGIC_WEAPON, ATTR, ABILITY, OTHER) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (user.uid, user.name, user.magic_root, user.exp, user.grade, user.level, user.local, user.belong,
                 user.arms, user.armor, user.magic_weapon, user.attr, user.ability, user.other),
            )

    def _del_user(self, uid):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM USER_INFO WHERE UID={uid}")

    # 存储用户状态
    def _save_user_model(self, uid, user_state: UserModel, flag):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO USER_MODEL (GID, UID, BUFF_TYPE, BUFF_INFO) VALUES (?, ?, ?, ?)",
                (uid, user_state.value[0], flag),
            )

    # 获取用户信息
    def _get_user_model(self, uid, user_state: UserModel):
        try:
            r = self._connect().execute(
                "SELECT BUFF_INFO FROM USER_MODEL WHERE UID=? AND BUFF_TYPE=? AND BUFF_INFO>0",
                (uid, user_state.value[0]),
            ).fetchone()
            if r is None:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0
        pass

    # 获取用户状态
    def _query_user_model(self, uid):
        try:
            r = self._connect().execute(
                "SELECT BUFF_TYPE,BUFF_INFO FROM USER_MODEL WHERE UID=? AND BUFF_INFO>0",
                (uid),
            ).fetchall()
            if not r:
                return []
            return r
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0
        pass

    # 覆盖存储群组状态
    def _save_group_state(self, gid, type: GroupModel, type_flag):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO GROUP_MODEL (GID, INFO_TYPE, INFO_FLAG) VALUES (?, ?, ?)",
                (gid, type.value[0], type_flag),
            )

    # 获取群组信息
    def _get_group_state(self, gid, group_state: GroupModel):
        try:
            r = self._connect().execute(
                "SELECT INFO_FLAG FROM GROUP_MODEL WHERE GID=? AND INFO_TYPE=? AND INFO_FLAG>0",
                (gid, group_state.value[0]),
            ).fetchone()
            if r is None:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0
        pass

    # 获取道具列表
    def _get_item(self, uid):
        try:
            r = self._connect().execute("SELECT ITEM_ID,ITEM_COUNT FROM ITEM WHERE GID=? AND UID=? AND ITEM_COUNT>0",
                                        (uid)).fetchall()
            if r is None:
                return []
            return r
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return []

    # 获取制定道具数量
    def _get_item_num(self, uid, iid):
        try:
            r = self._connect().execute(
                "SELECT ITEM_COUNT FROM ITEM WHERE UID=? AND ITEM_ID=?",
                (uid, iid)).fetchone()
            if r is None:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))

    # 增加道具
    def _add_item(self, uid, iid, num=1):
        now_num = self._get_item_num(uid, iid)
        now_num = now_num + num
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO ITEM (GID, UID, ITEM_ID, ITEM_COUNT) VALUES (?, ?, ?, ?)",
                (uid, iid, now_num),
            )
            return now_num

    # 获取所有道具数量
    def _count_item_num(self, uid):
        try:
            r = self._connect().execute(
                "SELECT SUM(ITEM_COUNT) FROM ITEM WHERE UID=?",
                (uid)).fetchone()
            if r[0] is None:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))

    # 添加交易信息
    def _save_trade_item(self, uid, itemId, price):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO TRADE_INFO (GID, UID, ITEM_ID, PRICE) VALUES (?, ?, ?, ?)",
                (uid, itemId, price),
            )

    # 获取交易信息
    def _get_trade_item(self, uid):
        try:
            r = self._connect().execute(
                "SELECT * FROM TRADE_INFO WHERE  UID=?",
                (gid, uid)).fetchone()
            if not r:
                return None
            return r
        except Exception as e:
            raise Exception('错误:\n' + str(e))

    # 获取最低价格的三件物品信息
    def _get_low_3_trade_item(self, itemId):
        try:
            r = self._connect().execute(
                "SELECT * FROM TRADE_INFO WHERE ITEM_ID=? ORDER BY PRICE ASC LIMIT 3",
                (itemId)).fetchall()
            if not r:
                return None
            return r
        except Exception as e:
            raise Exception('错误:\n' + str(e))

    # 删除贸易信息
    def _del_trade_info(self, uid):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM TRADE_INFO WHERE UID={uid}")
