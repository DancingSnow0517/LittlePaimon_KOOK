import logging

from typing import Optional, List

import aiosqlite

log = logging.getLogger(__name__)


class CookieInfo:
    guild_id: str
    user_id: str
    uid: str
    cookie: str

    def __init__(self, guild_id: str, user_id: str, uid: str, cookie: str) -> None:
        self.guild_id = guild_id
        self.user_id = user_id
        self.uid = uid
        self.cookie = cookie

    def __repr__(self) -> str:
        return f'CookieInfo(guild_id={self.guild_id}, user_id={self.user_id}, uid={self.uid}, cookie={self.cookie})'


async def init():
    """
    初始化数据库数据
    """
    log.info('正在初始化数据库...')

    init_cookie = '''CREATE TABLE if not exists cookie(
    guild_id TEXT,
    user_id TEXT,
    uid TEXT,
    cookie TEXT
    )'''

    async with aiosqlite.connect('little_paimon.db') as db:
        await db.execute(init_cookie)
        await db.commit()

    log.info('数据库初始化完成。')


async def get_cookies(*, guild_id: str = None, user_id: str = None, uid: str = None, cookie: str = None) -> \
        List[CookieInfo]:
    """
    获取数据库的符合条件的 cookie 信息
    :param guild_id: 服务器id
    :param user_id: 用户id
    :param uid: 原神id
    :param cookie: 米游社cookie
    :return: 一个 CookieInfo 的列表
    """
    str_list = []
    if guild_id is not None:
        str_list.append(f"guild_id='{guild_id}'")
    if user_id is not None:
        str_list.append(f"user_id='{user_id}'")
    if uid is not None:
        str_list.append(f"uid='{uid}'")
    if cookie is not None:
        str_list.append(f"cookie='{cookie}'")

    async with aiosqlite.connect('little_paimon.db') as db:
        cur = await db.execute(f'SELECT * FROM cookie {"WHERE" if len(str_list) != 0 else "" + " AND ".join(str_list)}')
        data = await cur.fetchall()
    return [CookieInfo(*info) for info in data]


async def add_cookie(user_id: str, uid: str, cookie: str, guild_id: Optional[str] = None) -> bool:
    """
    往数据库添加cookie
    :param guild_id: 服务器id
    :param user_id: 用户id
    :param uid: 原神id
    :param cookie: 米游社cookie
    :return: bool，表示操作是否成功
    """
    async with aiosqlite.connect('little_paimon.db') as db:
        cur = await db.execute(f"SELECT count(*) FROM cookie WHERE uid={uid}")
        count = (await cur.fetchone())[0]
        if count == 0:
            if guild_id is None:
                await db.execute(f"INSERT INTO cookie (user_id, uid, cookie)"
                                 f"VALUES ('{user_id}', '{uid}', '{cookie}')")
            else:
                await db.execute(f"INSERT INTO cookie (guild_id, user_id, uid, cookie)"
                                 f"VALUES ('{guild_id}', '{user_id}', '{uid}', '{cookie}')")
            await db.commit()
            log.info(f'{user_id} 的 cookie 添加成功')
            return True
        else:
            log.info(f'uid: {uid} 已存在')
            return False


async def remove_cookies(*, guild_id: str = None, user_id: str = None, uid: str = None, cookie: str = None) -> int:
    str_list = []
    if guild_id is not None:
        str_list.append(f"guild_id='{guild_id}'")
    if user_id is not None:
        str_list.append(f"user_id='{user_id}'")
    if uid is not None:
        str_list.append(f"uid='{uid}'")
    if cookie is not None:
        str_list.append(f"cookie='{cookie}'")
    async with aiosqlite.connect('little_paimon.db') as db:
        cur = await db.execute(f"DELETE FROM cookie WHERE {' AND '.join(str_list)}")
        await db.commit()
    log.info(f'删除了 {cur.rowcount} 个cookie')
    return cur.rowcount
