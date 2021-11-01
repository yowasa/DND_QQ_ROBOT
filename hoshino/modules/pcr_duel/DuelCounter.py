import os
import sqlite3

from hoshino.config.__bot__ import BASE_DB_PATH

DUEL_DB_PATH = os.path.expanduser(BASE_DB_PATH + 'pcr_duel.db')


# 记录贵族相关数据

class DuelCounter:
    def __init__(self):
        os.makedirs(os.path.dirname(DUEL_DB_PATH), exist_ok=True)
        self._create_charatable()
        self._create_uidtable()
        self._create_leveltable()
        self._create_queentable()
        self._create_warehousetable()
        self._create_favortable()
        self._create_gifttable()
        self._create_SWITCH()
        self._create_storetable()
        self._create_fashionbuytable()
        self._create_fashionuptable()
        self._create_pvp_info()

    def _connect(self):
        return sqlite3.connect(DUEL_DB_PATH)

    def _create_pvp_info(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS PVP_INFO
                          (GID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           CIDS TEXT NOT NULL,
                           SKILLS TEXT,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建pvp信息表发生错误')

    def _select_pvp_info(self, gid, uid):
        try:
            r = self._connect().execute(
                f'SELECT CIDS FROM PVP_INFO WHERE GID={gid} AND UID={uid}', ).fetchall()
            if r:
                cids=eval(r[0][0])
                return cids
            else:
                return []
        except:
            raise Exception('查找pvp信息时生错误')
    def _select_pvp_skills(self, gid, uid):
        try:
            r = self._connect().execute(
                f'SELECT SKILLS FROM PVP_INFO WHERE GID={gid} AND UID={uid}', ).fetchall()
            if r:
                cids=eval(r[0][0])
                return cids
            else:
                return []
        except:
            raise Exception('查找pvp信息时生错误')

    def _save_pvp_info(self, gid, uid,cids,skills):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO PVP_INFO (GID, UID, CIDS, SKILLS) VALUES (?, ?, ?, ?)",
                (gid, uid, str(cids),str(skills)),
            )

    def _del_pvp_info(self, gid, uid):
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM PVP_INFO WHERE GID={gid} AND UID={uid} ")

    def _create_storetable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS STORETABLE
                          (GID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           CID           INT    NOT NULL,
                           NUM           INT    NOT NULL,
                           PRIMARY KEY(GID, UID, CID));''')
        except:
            raise Exception('创建商店表发生错误')

    def _create_fashionbuytable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS FASHIONBUY
                          (GID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           CID           INT    NOT NULL,
                           FID           INT    NOT NULL,
                           PRIMARY KEY(GID, UID, FID));''')
        except:
            raise Exception('创建时装表发生错误')

    def _create_fashionuptable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS FASHIONup
                          (GID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           CID           INT    NOT NULL,
                           FID           INT    NOT NULL,
                           PRIMARY KEY(GID, UID, CID));''')
        except:
            raise Exception('创建时装穿戴表发生错误')

    def _create_warehousetable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS WAREHOUSE
                          (GID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           NUM           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建仓库上限表发生错误')

    def _create_charatable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS CHARATABLE
                          (GID             INT    NOT NULL,
                           CID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           PRIMARY KEY(GID, CID));''')
        except:
            raise Exception('创建角色表发生错误')

    def _create_uidtable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS UIDTABLE
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           CID           INT    NOT NULL,
                           NUM           INT    NOT NULL,
                           PRIMARY KEY(GID, UID, CID));''')
        except:
            raise Exception('创建UID表发生错误')

    def _create_leveltable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS LEVELTABLE
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           LEVEL           INT    NOT NULL,
                           
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建UID表发生错误')

    def _get_card_owner(self, gid, cid):
        try:
            r = self._connect().execute("SELECT UID FROM CHARATABLE WHERE GID=? AND CID=?", (gid, cid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找角色归属发生错误')

    def _set_card_owner(self, gid, cid, uid):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO CHARATABLE (GID, CID, UID) VALUES (?, ?, ?)",
                (gid, cid, uid),
            )

    def _delete_card_owner(self, gid, cid):
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM CHARATABLE  WHERE GID=? AND CID=?",
                (gid, cid),
            )

    # 查询已被邀请的女友列表

    def _get_card_list(self, gid):
        with self._connect() as conn:
            r = conn.execute(
                f"SELECT CID FROM CHARATABLE WHERE GID={gid}").fetchall()
            return [c[0] for c in r] if r else {}

    def _get_warehouse(self, gid, uid):
        try:
            r = self._connect().execute("SELECT NUM FROM WAREHOUSE WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找上限发生错误')

    def _add_warehouse(self, gid, uid, increment=1):
        housenum = self._get_warehouse(gid, uid)
        housenum += increment
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO WAREHOUSE (GID, UID, NUM) VALUES (?, ?, ?)",
                (gid, uid, housenum),
            )

    def _get_level(self, gid, uid):
        try:
            r = self._connect().execute("SELECT LEVEL FROM LEVELTABLE WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找等级发生错误')

    def _get_cards(self, gid, uid):
        with self._connect() as conn:
            r = conn.execute(
                "SELECT CID, NUM FROM UIDTABLE WHERE GID=? AND UID=? AND NUM>0", (gid, uid)
            ).fetchall()
        return [c[0] for c in r] if r else {}

    def _get_card_num(self, gid, uid, cid):
        with self._connect() as conn:
            r = conn.execute(
                "SELECT NUM FROM UIDTABLE WHERE GID=? AND UID=? AND CID=?", (gid, uid, cid)
            ).fetchone()
            return r[0] if r else 0

    def _add_card(self, gid, uid, cid, increment=1):
        num = self._get_card_num(gid, uid, cid)
        num += increment
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO UIDTABLE (GID, UID, CID, NUM) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, num),
            )
        if cid != 9999:
            self._set_card_owner(gid, cid, uid)
            self._set_favor(gid, uid, cid, 0)

    def _delete_card(self, gid, uid, cid, increment=1):
        num = self._get_card_num(gid, uid, cid)
        num -= increment
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO UIDTABLE (GID, UID, CID, NUM) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, num),
            )
        self._delete_card_owner(gid, cid)
        self._delete_favor(gid, uid, cid)

    def _add_level(self, gid, uid, increment=1):
        level = self._get_level(gid, uid)
        level += increment
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO LEVELTABLE (GID, UID, LEVEL) VALUES (?, ?, ?)",
                (gid, uid, level),
            )

    def _reduce_level(self, gid, uid, increment=1):
        level = self._get_level(gid, uid)
        level -= increment
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO LEVELTABLE (GID, UID, LEVEL) VALUES (?, ?, ?)",
                (gid, uid, level),
            )

    def _set_level(self, gid, uid, level):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO LEVELTABLE (GID, UID, LEVEL) VALUES (?, ?, ?)",
                (gid, uid, level),
            )

    def _get_level_num(self, gid, level):
        with self._connect() as conn:
            r = conn.execute(
                "SELECT COUNT(UID) FROM LEVELTABLE WHERE GID=? AND LEVEL=? ", (gid, level)
            ).fetchone()
            return r[0] if r else 0
        # 开关部分

    def _create_SWITCH(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS SWITCH
                          (GID             INT    NOT NULL,
                           GC             INT    NULL,
                           QC           INT    NULL,
                           FREE           INT    NULL,
                           SW           INT    NULL,
                           SUO           INT    NULL,
                           PRIMARY KEY(GID));''')
        except:
            raise Exception('创建开关表发生错误')

    def _get_GOLD_CELE(self, gid):
        with self._connect() as conn:
            r = conn.execute("SELECT GC FROM SWITCH WHERE GID=?", (gid,)).fetchone()
            return None if r is None else r[0]

    def _get_SUO_CELE(self, gid):
        with self._connect() as conn:
            r = conn.execute("SELECT SUO FROM SWITCH WHERE GID=?", (gid,)).fetchone()
            return None if r is None else r[0]

    def _get_QC_CELE(self, gid):
        with self._connect() as conn:
            r = conn.execute("SELECT QC FROM SWITCH WHERE GID=?", (gid,)).fetchone()
            return None if r is None else r[0]

    def _get_FREE_CELE(self, gid):
        with self._connect() as conn:
            r = conn.execute("SELECT FREE FROM SWITCH WHERE GID=?", (gid,)).fetchone()
            return None if r is None else r[0]

    def _get_SW_CELE(self, gid):
        with self._connect() as conn:
            r = conn.execute("SELECT SW FROM SWITCH WHERE GID=?", (gid,)).fetchone()
            return None if r is None else r[0]

    def _initialization_CELE(self, gid, GC, QC, SUO, SW, FREE):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO SWITCH (GID, GC, QC, SUO, SW, FREE) VALUES (?, ?, ?, ?, ?, ?)",
                (gid, GC, QC, SUO, SW, FREE),
            )

    # 妻子部分

    def _create_queentable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS QUEENTABLE
                          (GID             INT    NOT NULL,
                           CID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           PRIMARY KEY(GID, CID));''')
        except:
            raise Exception('创建妻子表发生错误')

    def _get_queen_owner(self, gid, cid):
        try:
            r = self._connect().execute("SELECT UID FROM QUEENTABLE WHERE GID=? AND CID=?", (gid, cid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找妻子归属发生错误')

    def _set_queen_owner(self, gid, cid, uid):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO QUEENTABLE (GID, CID, UID) VALUES (?, ?, ?)",
                (gid, cid, uid),
            )

    def _delete_queen_owner(self, gid, cid):
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM QUEENTABLE  WHERE GID=? AND CID=?",
                (gid, cid),
            )

    def _get_queen_list(self, gid):
        with self._connect() as conn:
            r = conn.execute(
                f"SELECT CID FROM QUEENTABLE WHERE GID={gid}").fetchall()
            return [c[0] for c in r] if r else {}

    # 查询某人的妻子，无则返回0
    def _search_queen(self, gid, uid):
        try:
            r = self._connect().execute("SELECT CID FROM QUEENTABLE WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找妻子发生错误')

        # 好感度部分

    def _create_favortable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS FAVORTABLE
                          (
                           GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           CID             INT    NOT NULL,
                           FAVOR           INT    NOT NULL,
                           PRIMARY KEY(GID, UID, CID));''')
        except:
            raise Exception('创建好感表发生错误')

    def _set_favor(self, gid, uid, cid, favor):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO FAVORTABLE (GID, UID, CID, FAVOR) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, favor),
            )

    def _get_favor(self, gid, uid, cid):
        try:
            r = self._connect().execute("SELECT FAVOR FROM FAVORTABLE WHERE GID=? AND UID=? AND CID=?",
                                        (gid, uid, cid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找好感发生错误')

    def _add_favor(self, gid, uid, cid, num):
        favor = self._get_favor(gid, uid, cid)
        if favor == None:
            favor = 0
        favor += num
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO FAVORTABLE (GID, UID, CID, FAVOR) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, favor),
            )

    def _reduce_favor(self, gid, uid, cid, num):
        favor = self._get_favor(gid, uid, cid)
        favor -= num
        favor = max(favor, 0)
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO FAVORTABLE (GID, UID, CID, FAVOR) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, favor),
            )

    def _delete_favor(self, gid, uid, cid):
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM FAVORTABLE  WHERE GID=? AND UID=? AND CID=?",
                (gid, uid, cid),
            )

    # 获取商品信息
    def _get_store(self, gid, uid, cid):
        try:
            r = self._connect().execute("SELECT NUM FROM STORETABLE WHERE GID=? AND UID=? AND CID=?",
                                        (gid, uid, cid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找商店发生错误')

    # 女友上架商城
    def _add_store(self, gid, uid, cid, increment=1):
        scorenum = self._get_store(gid, uid, cid)
        scorenum += increment
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO STORETABLE (GID, UID, CID, NUM) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, scorenum),
            )

    # 下架女友
    def _delete_store(self, gid, uid, cid):
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM STORETABLE  WHERE GID=? AND UID=? AND CID=?",
                (gid, uid, cid),
            )

    # 获取商城列表
    def _get_store_list(self, gid):
        with self._connect() as conn:
            r = conn.execute(
                f"SELECT CID, NUM FROM STORETABLE WHERE GID={gid}").fetchall()
            return [c[0] for c in r] if r else {}

    # 礼物仓库部分

    def _create_gifttable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS GIFTTABLE
                          (
                           GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           GFID             INT    NOT NULL,
                           NUM           INT    NOT NULL,
                           PRIMARY KEY(GID, UID, GFID));''')
        except:
            raise Exception('创建礼物表发生错误')

    def _get_gift_num(self, gid, uid, gfid):
        try:
            r = self._connect().execute("SELECT NUM FROM GIFTTABLE WHERE GID=? AND UID=? AND GFID=?",
                                        (gid, uid, gfid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找礼物发生错误')

    def _add_gift(self, gid, uid, gfid, num=1):
        giftnum = self._get_gift_num(gid, uid, gfid)
        if giftnum == None:
            giftnum = 0
        giftnum += num
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO GIFTTABLE (GID, UID, GFID, NUM) VALUES (?, ?, ?, ?)",
                (gid, uid, gfid, giftnum),
            )

    def _add_fashionbuy(self, gid, uid, cid, fid):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO FASHIONBUY (GID, UID, CID, FID) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, fid),
            )

    def _add_fashionup(self, gid, uid, cid, fid):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO FASHIONUP (GID, UID, CID, FID) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, fid),
            )

    def _get_fashionbuy(self, gid, uid, cid, fid):
        try:
            r = self._connect().execute("SELECT FID FROM FASHIONBUY WHERE GID=? AND UID=? AND CID=? AND FID=?",
                                        (gid, uid, cid, fid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找服装购买信息发生错误')

    def _get_fashionup(self, gid, uid, cid, fid):
        try:
            r = self._connect().execute("SELECT FID FROM FASHIONUP WHERE GID=? AND UID=? AND CID=?",
                                        (gid, uid, cid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找服装穿戴信息发生错误')

    def _delete_fashionup(self, gid, uid, cid):
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM FASHIONUP  WHERE GID=? AND UID=? AND CID=?",
                (gid, uid, cid),
            )

    def _reduce_gift(self, gid, uid, gfid, num=1):
        giftnum = self._get_gift_num(gid, uid, gfid)
        giftnum -= num
        giftnum = max(giftnum, 0)
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO GIFTTABLE (GID, UID, GFID, NUM) VALUES (?, ?, ?, ?)",
                (gid, uid, gfid, giftnum),
            )
