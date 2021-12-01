import os
import sqlite3

from hoshino.config.__bot__ import BASE_DB_PATH

CACHE_DB_PATH = os.path.expanduser(BASE_DB_PATH + 'xiuxian.db')


class UserInfo():
    def __init__(self, r=None):
        if r:
            self.gid = r[0]  # 群号
            self.uid = r[1]  # qq号
            self.name = r[2]  # 名称
            self.linggen = r[3]  # 灵根
            self.exp = r[4]  # 经验
            self.level = r[5]  # 境界
            self.belong = r[6]  # 门派
            self.map = r[7]  # 地图
            self.gongfa = r[8]  # 修炼功法
            self.fabao = r[9]  # 法宝
            self.wuqi = r[10]  # 武器
            self.wuxing = r[11]  # 悟性
            self.lingli = r[12]  # 灵力
            self.daohang = r[13]  # 道行
            self.act = r[14]  # 攻击力
            self.defen = r[15]  # 物理防御
            self.defen2 = r[16]  # 魔法防御
            self.hp = r[17]  # 血量
            self.mp = r[18]  # 蓝量
            self.skill = r[19]  # 战斗熟练度（0-100提升战斗力）
            self.tizhi = r[20]  # 体质
            self.act2 = r[21]  # 魔法攻击力
            self.gongfa2 = r[22]  # 战斗功法
            self.gongfa3 = r[23]  # 辅助功法


class XiuxianCounter():

    def __init__(self):
        os.makedirs(os.path.dirname(CACHE_DB_PATH), exist_ok=True)
        self._create_user_table()

    def _connect(self):
        return sqlite3.connect(CACHE_DB_PATH)

    def _create_user_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS USER_INFO
                          (GID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           USER_NAME TEXT NOT NULL,
                           LING_GEN TEXT NOT NULL,
                           EXP INT NOT NULL DEFAULT 0,
                           LEVEL INT NOT NULL DEFAULT 0,
                            BELONG TEXT NOT NULL DEFAULT '散修',
                            MAP TEXT NOT NULL DEFAULT '新手村',
                            GONGFA TEXT NOT NULL DEFAULT '无',
                            FABAO TEXT NOT NULL DEFAULT '无',
                            WUQI TEXT NOT NULL DEFAULT '赤手空拳',
                            WUXING INT NOT NULL DEFAULT 0,
                            LINGLI INT NOT NULL DEFAULT 0,
                            DAOHANG INT NOT NULL DEFAULT 0,
                            ACT INT NOT NULL DEFAULT 0,
                            DEFEN INT NOT NULL DEFAULT 0,
                            DEFEN2 INT NOT NULL DEFAULT 0,
                            HP INT NOT NULL DEFAULT 0,
                            MP INT NOT NULL DEFAULT 0,
                            SKILL INT NOT NULL DEFAULT 0,
                            TIZHI INT NOT NULL DEFAULT 0,
                            ACT2 INT NOT NULL DEFAULT 0,
                            GONGFA2 TEXT NOT NULL DEFAULT '无',
                            GONGFA3 TEXT NOT NULL DEFAULT '无',
                           PRIMARY KEY(GID, UID,USER_NAME));''')
        except:
            raise Exception('创建修仙表发生错误')

    def _get_user(self, gid, uid):
        try:
            r = self._connect().execute(
                f'SELECT * FROM USER_INFO WHERE GID={gid} AND UID={uid}', ).fetchall()
            if r:
                sub = UserInfo(r=r[0])
                return sub
            else:
                return None
        except:
            raise Exception('查找用户信息时生错误')

    def _get_user_by_name(self, gid, name):
        try:
            r = self._connect().execute(
                f'SELECT * FROM USER_INFO WHERE GID={gid} AND USER_NAME="{name}"', ).fetchall()
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
                "INSERT OR REPLACE INTO USER_INFO (GID, UID, USER_NAME, LING_GEN, EXP, LEVEL, BELONG, MAP, GONGFA, FABAO, WUQI, WUXING, LINGLI, DAOHANG, ACT, DEFEN, DEFEN2, HP, MP, SKILL, TIZHI, ACT2, GONGFA2, GONGFA3) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (user.gid, user.uid, user.name, user.linggen, user.exp, user.level, user.belong, user.map, user.gongfa,
                 user.fabao, user.wuqi, user.wuxing, user.lingli, user.daohang, user.act, user.defen, user.defen2,
                 user.hp, user.mp, user.skill, user.tizhi, user.act2, user.gongfa2, user.gongfa3),
            )

    def _del_user(self, gid, uid):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM USER_INFO WHERE GID={gid} AND UID={uid}")
