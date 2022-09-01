import hashlib
import json
import logging
import random
import re
import string
import time
from typing import Optional

from . import requests

ABYSS_API = 'https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/spiralAbyss'
PLAYER_CARD_API = 'https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/index'
CHARACTER_DETAIL_API = 'https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/character'
CHARACTER_SKILL_API = 'https://api-takumi.mihoyo.com/event/e20200928calculate/v1/sync/avatar/detail'
MONTH_INFO_API = 'https://hk4e-api.mihoyo.com/event/ys_ledger/monthInfo'
DAILY_NOTE_API = 'https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/dailyNote'
GAME_RECORD_API = 'https://api-takumi-record.mihoyo.com/game_record/card/wapi/getGameRecordCard'
SIGN_INFO_API = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/info'
SIGN_REWARD_API = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/home'
SIGN_ACTION_API = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign'

log = logging.getLogger(__name__)


def md5(text: str) -> str:
    """
    md5加密
    :param text: 文本
    :return: md5加密后的文本
    """
    md5_ = hashlib.md5()
    md5_.update(text.encode())
    return md5_.hexdigest()


def random_hex(length: int) -> str:
    """
    生成指定长度的随机字符串
    :param length: 长度
    :return: 随机字符串
    """
    result = hex(random.randint(0, 16 ** length)).replace('0x', '').upper()
    if len(result) < length:
        result = '0' * (length - len(result)) + result
    return result


def random_text(length: int) -> str:
    """
    生成指定长度的随机字符串
    :param length: 长度
    :return: 随机字符串
    """
    return ''.join(random.sample(string.ascii_lowercase + string.digits, length))


def get_ds(q: str = '', b: dict = None, mhy_bbs_sign: bool = False) -> str:
    """
    生成米游社headers的ds_token
    :param q: 查询
    :param b: 请求体
    :param mhy_bbs_sign: 是否为米游社讨论区签到
    :return: ds_token
    """
    br = json.dumps(b) if b else ''
    if mhy_bbs_sign:
        s = 't0qEgfub6cvueAPgR5m9aQWWVciEer7v'
    else:
        s = 'xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs'
    t = str(int(time.time()))
    r = str(random.randint(100000, 200000))
    c = md5(f'salt={s}&t={t}&r={r}&b={br}&q={q}')
    return f'{t},{r},{c}'


def get_old_version_ds(mhy_bbs: bool = False) -> str:
    """
    生成米游社旧版本headers的ds_token
    """
    if mhy_bbs:
        s = 'N50pqm7FSy2AkFz2B3TqtuZMJ5TOl3Ep'
    else:
        s = 'z8DRIUjNDT7IT5IZXvrUAxyupA1peND9'
    t = str(int(time.time()))
    r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c = md5(f"salt={s}&t={t}&r={r}")
    return f"{t},{r},{c}"


def mihoyo_headers(cookie, q='', b=None) -> dict:
    """
    生成米游社headers
    :param cookie: cookie
    :param q: 查询
    :param b: 请求体
    :return: headers
    """
    return {
        'DS': get_ds(q, b),
        'Origin': 'https://webstatic.mihoyo.com',
        'Cookie': cookie,
        'x-rpc-app_version': "2.11.1",
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS '
                      'X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer': 'https://webstatic.mihoyo.com/'
    }


def mihoyo_sign_headers(cookie: str) -> dict:
    """
    生成米游社签到headers
    :param cookie: cookie
    :return: headers
    """
    return {
        'User_Agent': 'Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36 miHoYoBBS/2.35.2',
        'Cookie': cookie,
        'x-rpc-device_id': random_hex(32),
        'Origin': 'https://webstatic.mihoyo.com',
        'X_Requested_With': 'com.mihoyo.hyperion',
        'DS': get_old_version_ds(mhy_bbs=True),
        'x-rpc-client_type': '5',
        'Referer': 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id'
                   '=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon',
        'x-rpc-app_version': '2.35.2'
    }


async def get_bind_game_info(cookie: str) -> Optional[dict]:
    """
    通过cookie，获取米游社绑定的原神游戏信息
    :param cookie: cookie
    :return: 原神信息
    """
    if mys_id := re.search(r'(account_id|ltuid|stuid|login_uid)=(\d*)', cookie):
        mys_id = mys_id.group(2)
        data = (await requests.get(url=GAME_RECORD_API, headers=mihoyo_headers(cookie, f'uid={mys_id}'),
                                   params={'uid': mys_id})).json()
        if data['retcode'] == 0:
            for game_data in data['data']['list']:
                if game_data['game_id'] == 2:
                    game_data['mys_id'] = mys_id
                    return game_data
    return None


async def get_sign_reward_list() -> dict:
    headers = {
        'x-rpc-app_version': '2.11.1',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 ('
                      'KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer': 'https://webstatic.mihoyo.com/'
    }
    resp = await requests.get(url=SIGN_REWARD_API, headers=headers, params={'act_id': 'e202009291139501'})
    data = resp.json()
    log.debug(data)
    return data


async def get_stoken_by_cookie(cookie: str) -> Optional[str]:
    if login_ticket := re.search('login_ticket=([0-9a-zA-Z]+)', cookie):
        bbs_cookie_url = 'https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket?login_ticket={}'
        data = (await requests.get(url=bbs_cookie_url.format(login_ticket[0].split('=')[1]))).json()

        if '成功' in data['data']['msg']:
            stuid = data['data']['cookie_info']['account_id']
            bbs_cookie_url2 = 'https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket={}&token_types=3&uid={}'
            data2 = (await requests.get(url=bbs_cookie_url2.format(login_ticket[0].split('=')[1], stuid))).json()
            return data2['data']['list'][0]['token']
        else:
            return None
    return None


async def get_enka_data(uid):
    try:
        url = f'https://enka.network/u/{uid}/__data.json'
        resp = await requests.get(url=url, headers={'User-Agent': 'LittlePaimon/3.0'}, follow_redirects=True)
        data = resp.json()
        log.debug(data)
        return data
    except Exception:
        url = f'https://enka.microgg.cn/u/{uid}/__data.json'
        resp = await requests.get(url=url, headers={'User-Agent': 'LittlePaimon/3.0'}, follow_redirects=True)
        data = resp.json()
        log.debug(data)
        return data
