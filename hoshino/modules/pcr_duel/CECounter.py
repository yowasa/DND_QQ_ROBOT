import os
import sqlite3
from datetime import datetime

from hoshino.config.__bot__ import BASE_DB_PATH

DUEL_DB_PATH = os.path.expanduser(BASE_DB_PATH + 'pcr_duel.db')

def get_month_period():
    nowyear = datetime.now().year
    nowmonth = datetime.now().month
    if nowmonth == 1:
        nowyear = nowyear - 1
        nowmonth = 12
    else:
        nowyear = nowyear
        nowmonth = nowmonth - 1
    period = str(nowyear) + str(nowmonth)
    return period

def get_week_period():
    nowyear = datetime.now().year
    zhou=datetime.now().isocalendar()[1]
    period = str(nowyear) + str(zhou)
    return period

class DunInfo():
    def __init__(self, r=None):
        if r:
            self.gid = r[0]
            self.uid = r[1]
            self.cids = eval(r[2])
            self.dun_model = r[3]
            self.left_hp = r[4]
            self.left_sp = r[5]
            self.use_skill = eval(r[6])
            self.now_dun = r[7]
            self.from_dun = r[8]
            self.able_dun = eval(r[9])


class CECounter:
    def __init__(self):
        os.makedirs(os.path.dirname(DUEL_DB_PATH), exist_ok=True)
        self._create_exptable()
        self._create_guajitable()
        self._create_equipment()
        self._create_dun_score()
        self._create_dressequip()
        self._create_rank()
        self._create_bossstate()
        self._create_bossfight()
        self._create_fightcard()
        self._create_bossstate_add()
        self._create_bossfight_add()
        self._create_teamtable()
        self._create_xiuliantable()
        self._create_expnumtable()
        self._create_equipgecha()
        self._create_xingchen()
        self._create_fragment()
        self._create_cardstar()
        self._create_gecha_add()
        self._create_zhuansheng()
        self._create_dun_info()

    def _connect(self):
        return sqlite3.connect(DUEL_DB_PATH)

    def _create_dun_info(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS DUN_INFO
                          (GID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           CIDS TEXT NOT NULL,
                           DUN_MODEL INT,
                           LEFT_HP INT NOT NULL,
                           LEFT_SP INT NOT NULL,
                           USE_SKILL TEXT NOT NULL,
                           NOW_DUN TEXT,
                           FROM_DUN TEXT,
                           ABLE_DUN TEXT NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建副本信息表发生错误')

    def _select_dun_info(self, gid, uid):
        try:
            r = self._connect().execute(
                f'SELECT * FROM DUN_INFO WHERE GID={gid} AND UID={uid}', ).fetchall()
            if r:
                dun=DunInfo(r=r[0])
                return dun
            else:
                return None
        except:
            raise Exception('查找副本信息时生错误')

    def _save_dun_info(self, dun_info: DunInfo):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO DUN_INFO (GID, UID, CIDS, DUN_MODEL, LEFT_HP, LEFT_SP, USE_SKILL, NOW_DUN, FROM_DUN, ABLE_DUN) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (dun_info.gid, dun_info.uid, str(dun_info.cids), dun_info.dun_model, dun_info.left_hp, dun_info.left_sp,
                 str(dun_info.use_skill), dun_info.now_dun, dun_info.from_dun, str(dun_info.able_dun)),
            )

    def _create_exptable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS EXPTABLE
                          (GID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           CID           INT    NOT NULL,
                           LEVEL           INT    NOT NULL,
                           EXP           INT    NOT NULL,
                           PRIMARY KEY(GID, CID));''')
        except:
            raise Exception('创建角色等级经验表发生错误')

    def _create_guajitable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS GUAJITABLE
                          (GID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           CID           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建角色挂机表发生错误')

    def _create_equipment(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS EQUIPMENT
                          (GID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           EID           INT    NOT NULL,
                           NUM           INT    NOT NULL,
                           PRIMARY KEY(GID, UID, EID));''')
        except:
            raise Exception('创建装备表发生错误')

    def _create_dressequip(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS DRESSEQUIP
                          (GID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           CID           INT    NOT NULL,
                           TYPEID           INT    NOT NULL,
                           EID           INT    NOT NULL,
                           PRIMARY KEY(GID, UID, CID, TYPEID));''')
        except:
            raise Exception('创建装备穿戴表发生错误')

    def _create_dun_score(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS DUNSCORE
                          (GID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           NUM           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建副本金币表发生错误')

    # 重置角色等级
    def _set_card_exp(self, gid, uid, cid, level=0, exp=0):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO EXPTABLE (GID, UID, CID, LEVEL, EXP) VALUES (?, ?, ?, ?, ?)",
                (gid, uid, cid, level, exp),
            )

    # 查询角色等级信息
    def _get_card_level(self, gid, uid, cid):
        try:
            r = self._connect().execute("SELECT LEVEL FROM EXPTABLE WHERE GID=? AND UID=? AND CID=?",
                                        (gid, uid, cid)).fetchone()
            if r is None:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0

    # 查询角色经验信息
    def _get_card_exp(self, gid, uid, cid):
        try:
            r = self._connect().execute("SELECT EXP FROM EXPTABLE WHERE GID=? AND UID=? AND CID=?",
                                        (gid, uid, cid)).fetchone()
            if r is None:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0

    # 更新角色等级、经验信息
    def _add_card_exp(self, gid, uid, cid, level, exp):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO EXPTABLE (GID, UID, CID, LEVEL, EXP) VALUES (?, ?, ?, ?, ?)",
                (gid, uid, cid, level, exp),
            )

    # 查询绑定的挂机角色
    def _get_guaji(self, gid, uid):
        try:
            r = self._connect().execute("SELECT CID FROM GUAJITABLE WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0

    # 设定挂机绑定角色
    def _add_guaji(self, gid, uid, cid):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO GUAJITABLE (GID, UID, CID) VALUES (?, ?, ?)",
                (gid, uid, cid),
            )

    # 获取未装备的装备数量
    def _get_equip_num(self, gid, uid, eid):
        try:
            r = self._connect().execute("SELECT NUM FROM EQUIPMENT WHERE GID=? AND UID=? AND EID=?",
                                        (gid, uid, eid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找装备信息发生错误')

    # 装备表数量更新
    def _add_equip(self, gid, uid, eid, shul):
        num = self._get_equip_num(gid, uid, eid)
        if num == None:
            num = 0
        num += shul
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO EQUIPMENT (GID, UID, EID, NUM) VALUES (?, ?, ?, ?)",
                (gid, uid, eid, num),
            )

    # 获取我的装备列表
    def _get_equip_list(self, gid, uid):
        with self._connect() as conn:
            r = conn.execute(
                "SELECT EID as eid, NUM as num FROM EQUIPMENT WHERE GID=? AND UID=? AND NUM>0", (gid, uid)
            ).fetchall()
        return r if r else {}

    # 获取角色穿戴装备列表
    def _get_dress_list(self, gid, uid, cid):
        with self._connect() as conn:
            r = conn.execute(
                "SELECT EID, TYPEID FROM DRESSEQUIP WHERE GID=? AND UID=? AND CID=? AND EID>0", (gid, uid, cid)
            ).fetchall()
        return [c[0] for c in r] if r else []

    # 获取角色穿戴装备列表
    def _get_dress_info(self, gid, uid, cid, typeid):
        try:
            r = self._connect().execute(
                "SELECT EID FROM DRESSEQUIP WHERE GID=? AND UID=? AND CID=? AND TYPEID=? AND EID>0",
                (gid, uid, cid, typeid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找穿戴信息发生错误')

    # 角色装备装备
    def _dress_equip(self, gid, uid, cid, typeid, eid):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO DRESSEQUIP (GID, UID, CID, TYPEID, EID) VALUES (?, ?, ?, ?, ?)",
                (gid, uid, cid, typeid, eid),
            )

    # 副本币查询
    def _get_dunscore(self, gid, uid):
        try:
            r = self._connect().execute("SELECT NUM FROM DUNSCORE WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找副本币信息发生错误')

    # 副本币表数量更新
    def _add_dunscore(self, gid, uid, score):
        num = self._get_dunscore(gid, uid)
        if num == None:
            num = 0
        num += score
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO DUNSCORE (GID, UID, NUM) VALUES (?, ?, ?)",
                (gid, uid, num),
            )

    # RANK部分
    def _create_rank(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS RANKTABLE
                          (
                           GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           CID             INT    NOT NULL,
                           RANK        INT    NOT NULL,
                           PRIMARY KEY(GID, UID, CID));''')
        except:
            raise Exception('创建rank表发生错误')

    def _add_rank(self, gid, uid, cid):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO RANKTABLE (GID, UID, CID, RANK) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, 0),
            )

    def _up_rank(self, gid, uid, cid):
        rank = self._get_rank(gid, uid, cid)
        rank += 1
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO RANKTABLE (GID, UID, CID, RANK) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, rank),
            )

    def _up_rank_num(self, gid, uid, cid, num):
        rank = self._get_rank(gid, uid, cid)
        rank += num
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO RANKTABLE (GID, UID, CID, RANK) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, rank),
            )

    def _get_rank(self, gid, uid, cid):
        try:
            r = self._connect().execute("SELECT RANK FROM RANKTABLE WHERE GID=? AND UID=? AND CID=?",
                                        (gid, uid, cid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找rank发生错误')

    def _get_cards_byrank(self, gid, num):
        with self._connect() as conn:
            r = conn.execute(
                f"SELECT GID,RANK,UID,CID FROM RANKTABLE WHERE GID={gid} ORDER BY RANK desc LIMIT {num}").fetchall()
            return r if r else []

    # 会战部分
    def _create_bossstate(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS BOSSSTATE
                          (
                           GID             INT    NOT NULL,
                           ZHOUMU             INT    NOT NULL,
                           BOSSID             INT    NOT NULL,
                           HP        INT    NOT NULL,
                           PRIMARY KEY(GID));''')
        except:
            raise Exception('创建boss状态表发生错误')

    # 会战部分
    def _create_bossstate_add(self):
        with self._connect() as conn:
            r = conn.execute("select sql from sqlite_master where type='table' and name='BOSSSTATE';").fetchall()
            if 'PERIOD' not in str(r):
                nowyear = datetime.now().year
                nowmonth = datetime.now().month
                period = str(nowyear) + str(nowmonth)
                conn.execute(f"ALTER TABLE BOSSSTATE ADD PERIOD INT DEFAULT {period};").fetchall()

    def _create_bossfight(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS BOSSFIGHT
                          (
                           GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           ZHOUMU             INT    NOT NULL,
                           BOSSID        INT    NOT NULL,
                           NUM        INT    NOT NULL,
                           TYPE        INT    NOT NULL,
                           PRIMARY KEY(GID, UID, ZHOUMU, BOSSID, NUM, TYPE));''')
        except:
            raise Exception('创建伤害表发生错误')

    def _create_bossfight_add(self):
        with self._connect() as conn:
            r = conn.execute("select sql from sqlite_master where type='table' and name='BOSSFIGHT';").fetchall()
            if 'PERIOD' not in str(r):
                period = get_week_period()
                conn.execute(f"ALTER TABLE BOSSFIGHT ADD PERIOD INT DEFAULT {period};").fetchall()

    def _create_fightcard(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS FIGHTCARD
                          (
                           GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           CID             INT    NOT NULL,
                           HITTIME        INT    NOT NULL,
                           HP        INT    NOT NULL,
                           TYPE        INT    NOT NULL,
                           PRIMARY KEY(GID, UID, CID, TYPE));''')
        except:
            raise Exception('创建女友出刀表发生错误')

    # 重置boss状态
    def _set_bossinfo(self, gid):
        nowyear = datetime.now().year
        nowmonth = datetime.now().month
        period = str(nowyear) + str(nowmonth)
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO BOSSSTATE (GID, PERIOD, ZHOUMU, BOSSID, HP) VALUES (?, ?, ?, ?, ?)",
                (gid, period, 1, 1, 0),
            )

    # 获取boss状态
    def _get_bossinfo(self, gid):
        nowyear = datetime.now().year
        nowmonth = datetime.now().month
        period = str(nowyear) + str(nowmonth)
        with self._connect() as conn:
            r = conn.execute(
                f"SELECT ZHOUMU,BOSSID,HP FROM BOSSSTATE WHERE GID={gid} AND PERIOD={period}").fetchall()
            if r:
                return r[0]
            else:
                self._set_bossinfo(gid)
                return [1, 1, 0]

    # 保存boss状态
    def _up_bossinfo(self, gid, zhoumu, bossid, hp):
        nowyear = datetime.now().year
        nowmonth = datetime.now().month
        period = str(nowyear) + str(nowmonth)
        with self._connect() as conn:
            conn.execute(
                f"UPDATE BOSSSTATE SET ZHOUMU={zhoumu},BOSSID={bossid},HP={hp} WHERE GID={gid} AND PERIOD={period}"
            )

    # 记录出刀情况
    def _add_cardfight(self, gid, uid, cid, hittime, hp, shijieflag):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO FIGHTCARD (GID, UID, CID, HITTIME, HP, TYPE) VALUES (?, ?, ?, ?, ?, ?)",
                (gid, uid, cid, hittime, hp, shijieflag),
            )

    def _get_shuchu_pm(self, gid, shijieflag):
        period = get_week_period()
        with self._connect() as conn:
            r = conn.execute(
                f"SELECT UID,SUM(NUM) FROM BOSSFIGHT WHERE GID={gid} AND TYPE={shijieflag} AND PERIOD={period} GROUP BY UID ORDER BY SUM(NUM) DESC").fetchall()
            return r if r else 0

    def _get_shuchu_pmq(self, period=0):
        per = get_week_period()
        if period == 0:
            period = per
        with self._connect() as conn:
            r = conn.execute(
                f"SELECT GID,UID,ZHOUMU,BOSSID,SUM(NUM) AS NUM,TYPE FROM BOSSFIGHT WHERE PERIOD={period} GROUP BY GID,TYPE,UID,ZHOUMU,BOSSID").fetchall()
            return r if r else 0

    # 获取boss伤害数据
    def _get_shuchulist(self, gid, zhoumu, bossid, shijieflag):
        period = get_week_period()
        with self._connect() as conn:
            if shijieflag == 1:
                r = conn.execute(
                    f"SELECT GID,UID,NUM FROM BOSSFIGHT WHERE ZHOUMU={zhoumu} AND BOSSID={bossid} AND TYPE={shijieflag} AND PERIOD={period} ORDER BY NUM DESC").fetchall()
            else:
                r = conn.execute(
                    f"SELECT GID,UID,NUM FROM BOSSFIGHT WHERE ZHOUMU={zhoumu} AND BOSSID={bossid} AND GID={gid} AND TYPE={shijieflag} AND PERIOD={period} ORDER BY NUM DESC").fetchall()
            return r if r else 0

    # 记录出刀伤害
    def _add_bossfight(self, gid, uid, zhoumu, bossid, num, shijieflag):
        period = get_week_period()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO BOSSFIGHT (GID, UID, ZHOUMU, BOSSID, NUM, TYPE, PERIOD) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (gid, uid, zhoumu, bossid, num, shijieflag, period),
            )

    # 获取女友是否出过刀，或者是否处于补时刀
    def _get_cardfightinfo(self, gid, uid, cid, fighttime, shijieflag):
        with self._connect() as conn:
            r = conn.execute(
                f"SELECT CID,HP FROM FIGHTCARD WHERE GID={gid} AND UID={uid} AND CID={cid} AND TYPE={shijieflag} AND HITTIME={fighttime}").fetchall()
            return r[0] if r else [0, 0]

        # 获取女友是否出过刀，或者是否处于补时刀

    def _del_cardfightinfo(self, gid, uid, cid, fighttime, shijieflag):
        result = self._get_cardfightinfo(gid, uid, cid, fighttime, shijieflag)
        if result[0] > 0:
            with self._connect() as conn:
                conn.execute(
                    f"DELETE FROM FIGHTCARD WHERE GID={gid} AND UID={uid} AND CID={cid} AND TYPE={shijieflag} AND HITTIME={fighttime}"
                )

    # 获取补时刀女友
    def _get_cardbushi(self, gid, uid, fighttime, shijieflag):
        with self._connect() as conn:
            r = conn.execute(
                f"SELECT CID,HP FROM FIGHTCARD WHERE GID={gid} AND UID={uid} AND TYPE={shijieflag} AND HITTIME={fighttime} AND HP>0").fetchall()
            return r if r else 0

    # 创建编组表
    def _create_teamtable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS TEAMTABLE
                          (
                           GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           CID             INT    NOT NULL,
                           NAME        VARCHAR(20)    NOT NULL,
                           PRIMARY KEY(GID, UID, CID, NAME));''')
        except:
            raise Exception('创建队伍表发生错误')

    def _add_team(self, gid, uid, cid, name):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO TEAMTABLE (GID, UID, CID, NAME) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, name),
            )

    def _delete_team(self, gid, uid, name):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM TEAMTABLE WHERE GID={gid} AND UID={uid} AND NAME = '{name}'").fetchall()

    def _get_teamlist(self, gid, uid, name):
        with self._connect() as conn:
            r = conn.execute(
                f"SELECT CID FROM TEAMTABLE WHERE GID={gid} AND UID={uid} AND NAME = '{name}'").fetchall()
            return r if r else 0

    def _get_teamnum(self, gid, uid):
        with self._connect() as conn:
            r = conn.execute(
                f"SELECT count(NAME) AS NUM FROM (SELECT distinct GID,UID,NAME FROM TEAMTABLE WHERE GID={gid} AND UID={uid} GROUP BY NAME) A").fetchall()
            return r[0][0] if r else 0

    def _get_teamname(self, gid, uid):
        with self._connect() as conn:
            r = conn.execute(
                f"SELECT NAME FROM TEAMTABLE WHERE GID={gid} AND UID={uid} GROUP BY NAME").fetchall()
            return r if r else 0

    # 创建机修炼表
    def _create_xiuliantable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS XIULIAN
                          (
                           GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           CID             INT    NOT NULL,
                           XLTIME        INT    NOT NULL,
                           PRIMARY KEY(GID, UID, CID));''')
        except:
            raise Exception('创建挂机修炼表发生错误')

    def _get_xiulian(self, gid, uid):
        with self._connect() as conn:
            r = conn.execute(
                f"SELECT CID,XLTIME FROM XIULIAN WHERE GID={gid} AND UID={uid}").fetchall()
            return r[0] if r else [0, 0]

    def _add_xiulian(self, gid, uid, cid, xltime):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO XIULIAN (GID, UID, CID, XLTIME) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, xltime),
            )

    def _delete_xiulian(self, gid, uid):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM XIULIAN WHERE GID={gid} AND UID={uid}").fetchall()

    # 创建经验池表
    def _create_expnumtable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS EXPNUM
                          (
                           GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           NUM        INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建经验池表发生错误')

    def _get_exp_chizi(self, gid, uid):
        try:
            r = self._connect().execute("SELECT NUM FROM EXPNUM WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            if r is None:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0

    def _add_exp_chizi(self, gid, uid, num):
        now_exp = self._get_exp_chizi(gid, uid)
        now_exp = now_exp + num
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO EXPNUM (GID, UID, NUM) VALUES (?, ?, ?)",
                (gid, uid, now_exp),
            )

    # 创建抽卡保底表
    def _create_equipgecha(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS EQUIPGECHA
                          (
                           GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           XNUM        INT    NOT NULL,
                           DNUM        INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建抽卡保底表发生错误')

    # 会战部分
    def _create_gecha_add(self):
        with self._connect() as conn:
            r = conn.execute("select sql from sqlite_master where type='table' and name='EQUIPGECHA';").fetchall()
            if 'UNUM' not in str(r):
                nowyear = datetime.now().year
                nowmonth = datetime.now().month
                period = str(nowyear) + str(nowmonth)
                conn.execute(f"ALTER TABLE EQUIPGECHA ADD UNUM INT DEFAULT 0;").fetchall()

    def _get_gecha_num(self, gid, uid):
        with self._connect() as conn:
            r = conn.execute(
                f"SELECT XNUM,DNUM,UNUM FROM EQUIPGECHA WHERE GID={gid} AND UID={uid}").fetchall()
            return r[0] if r else [0, 0, 0]

    def _add_gecha_num(self, gid, uid, xnum, dnum, unum):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO EQUIPGECHA (GID, UID, XNUM, DNUM, UNUM) VALUES (?, ?, ?, ?, ?)",
                (gid, uid, xnum, dnum, unum),
            )

    # 创建抽卡获得星尘表
    def _create_xingchen(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS XINGCHEN
                          (
                           GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           NUM        INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建抽卡星尘表发生错误')

    def _get_xingchen_num(self, gid, uid):
        try:
            r = self._connect().execute("SELECT NUM FROM XINGCHEN WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            if r is None:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0

    def _add_xingchen_num(self, gid, uid, num):
        now_num = self._get_xingchen_num(gid, uid)
        now_num = now_num + num
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO XINGCHEN (GID, UID, NUM) VALUES (?, ?, ?)",
                (gid, uid, now_num),
            )
            return now_num

    # 创建角色碎片表
    def _create_fragment(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS FRAGMENT
                          (
                           GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           CID        INT    NOT NULL,
                           NUM        INT    NOT NULL,
                           PRIMARY KEY(GID, UID, CID));''')
        except:
            raise Exception('创建角色碎片表发生错误')

    # 创建角色星级表
    def _create_cardstar(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS CARDSTAR
                          (
                           GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           CID        INT    NOT NULL,
                           NUM        INT    NOT NULL,
                           PRIMARY KEY(GID, UID, CID));''')
        except:
            raise Exception('创建角色星级表发生错误')

    # 获取角色碎片数量
    def _get_fragment_num(self, gid, uid, cid):
        try:
            r = self._connect().execute("SELECT NUM FROM FRAGMENT WHERE GID=? AND UID=? AND CID=?",
                                        (gid, uid, cid)).fetchone()
            if r is None:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0

    # 添加/删除角色碎片
    def _add_fragment_num(self, gid, uid, cid, num):
        now_num = self._get_fragment_num(gid, uid, cid)
        now_num = now_num + num
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO FRAGMENT (GID, UID, CID, NUM) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, now_num),
            )
            return now_num

    # 获取角色星级
    def _get_cardstar(self, gid, uid, cid):
        try:
            r = self._connect().execute("SELECT NUM FROM CARDSTAR WHERE GID=? AND UID=? AND CID=?",
                                        (gid, uid, cid)).fetchone()
            if r is None:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0

    # 角色升星
    def _add_cardstar(self, gid, uid, cid):
        now_num = self._get_cardstar(gid, uid, cid)
        now_num = now_num + 1
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO CARDSTAR (GID, UID, CID, NUM) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, now_num),
            )
            return now_num

    # 获取我的角色碎片列表
    def _get_fragment_list(self, gid, uid):
        with self._connect() as conn:
            r = conn.execute(
                "SELECT CID,NUM FROM FRAGMENT WHERE GID=? AND UID=? AND NUM>0 ORDER BY CID", (gid, uid)
            ).fetchall()
        return r if r else {}

    # 创建角色转生表
    def _create_zhuansheng(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS ZHUANSHENG
                          (
                           GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           CID        INT    NOT NULL,
                           NUM        INT    NOT NULL,
                           PRIMARY KEY(GID, UID, CID));''')
        except:
            raise Exception('创建角色转生表发生错误')

    # 获取角色转生等级（等级上限提升次数)
    def _get_zhuansheng(self, gid, uid, cid):
        try:
            r = self._connect().execute("SELECT NUM FROM ZHUANSHENG WHERE GID=? AND UID=? AND CID=?",
                                        (gid, uid, cid)).fetchone()
            if r is None:
                return 0
            return r[0]
        except Exception as e:
            raise Exception('错误:\n' + str(e))
            return 0

    # 角色转生
    def _add_zhuansheng(self, gid, uid, cid):
        now_num = self._get_zhuansheng(gid, uid, cid)
        now_num = now_num + 1
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO ZHUANSHENG (GID, UID, CID, NUM) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, now_num),
            )
            return now_num
