import asyncio
import datetime
import json
import logging
import random
from typing import Tuple, Dict, Any, Union, Optional

from .draw import SignResult
from ...database.models.cookie import LastQuery, PrivateCookie
from ...utils import requests
from ...utils.genshin_api import get_mihoyo_private_data, get_sign_reward_list, mihoyo_sign_headers, check_retcode

log = logging.getLogger(__name__)

SIGN_ACTION_API = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign'
GEETEST_HEADER = {"Accept": "*/*",
                  "X-Requested-With": "com.mihoyo.hyperion",
                  "User-Agent": 'Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, '
                                'like Gecko) '
                                'Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36 miHoYoBBS/2.35.2',
                  "Referer": "https://webstatic.mihoyo.com/",
                  "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
                  }

sign_reward_list: dict = {}


async def pass_geetest(data: Dict[str, Any]):
    if data is not None:
        url = f'https://api.geetest.com/ajax.php?gt={data["gt"]}&challenge={data["challenge"]}&lang=zh-cn&pt=3&client_type=web_mobile'
        resp = await requests.get(url, headers=GEETEST_HEADER)
        if resp.status_code == 200:
            resp_data = json.loads(resp.text.replace('(', '').replace(')', ''))
            if 'success' in resp_data['status'] and 'success' in resp_data['data']['result']:
                return resp_data['data']['validate']
    return None


async def sign_action(user_id: str, uid: str, validate: Optional[dict] = None, last_data: Optional[dict] = None) -> \
        Union[dict, str]:
    server_id = 'cn_qd01' if uid[0] == '5' else 'cn_gf01'
    cookie_info = await PrivateCookie.get_or_none(user_id=user_id, uid=uid)
    if last_data and validate:
        extra_headers = {
            'x-rpc-challenge': last_data['data']['challenge'],
            'x-rpc-validate': validate,
            'x-rpc-seccode': f'{validate}|jordan'
        }
    else:
        extra_headers = None
    resp = await requests.post(SIGN_ACTION_API, headers=mihoyo_sign_headers(cookie_info.cookie, extra_headers),
                               json={
                                   'act_id': 'e202009291139501',
                                   'uid': uid,
                                   'region': server_id
                               })
    data = resp.json()
    if await check_retcode(data, cookie_info, 'private', user_id, uid):
        return data
    else:
        return f'你的UID{uid}的cookie疑似失效了'


async def mhy_bbs_sign(user_id: str, uid: str) -> Tuple[SignResult, str]:
    """
    执行米游社原神签到，返回签到成功天数或失败原因
    :param user_id: 用户id
    :param uid: 原神uid
    :return: 签到成功天数或失败原因
    """
    await LastQuery.update_or_create(user_id=user_id,
                                     defaults={'uid': uid, 'last_time': datetime.datetime.now()})
    sign_info = await get_mihoyo_private_data(uid, user_id, 'sign_info')
    if isinstance(sign_info, str):
        log.info(f'米游社原神签到: ➤ 用户 {user_id} UID {uid}, 未绑定私人cookie或已失效')
        return SignResult.FAIL, sign_info
    elif sign_info['data']['is_sign']:
        signed_days = sign_info['data']['total_sign_day'] - 1
        log.info(f'米游社原神签到: ➤ 用户 {user_id} UID {uid}, 今天已经签过了')
        if sign_reward_list:
            return SignResult.DONE, f'UID{uid}今天已经签过了，获得的奖励为\n{sign_reward_list[signed_days]["name"]}*{sign_reward_list[signed_days]["cnt"]}'
        else:
            return SignResult.DONE, f'UID{uid}今天已经签过了'
        validate = None
        sign_data = None
        for i in range(3):
            sign_data = await sign_action(user_id, uid, validate, sign_data)
            validate = await pass_geetest(sign_data['data'])
        if isinstance(sign_data, str):
            log.info(f'米游社原神签到: ➤ 用户 {user_id} UID {uid}, 获取数据失败, {sign_data}')
            return SignResult.FAIL, f'{uid}签到失败，{sign_data}'
        elif sign_data['retcode'] == -5003:
            signed_days = sign_info['data']['total_sign_day'] - 1
            log.info(f'米游社原神签到: ➤ 用户 {user_id} UID {uid}, 今天已经签过了')
            if sign_reward_list:
                return SignResult.DONE, f'UID{uid}今天已经签过了，获得的奖励为\n{sign_reward_list[signed_days]["name"]}*{sign_reward_list[signed_days]["cnt"]}'
            else:
                return SignResult.DONE, f'UID{uid}今天已经签过了'
        elif sign_data['retcode'] != 0:
            log.info(
                f'米游社原神签到: ➤ 用户 {user_id}, UID {uid}, 获取数据失败，code为 {sign_data["retcode"]}， msg为 {sign_data["message"]}')
            return SignResult.FAIL, f'{uid}获取数据失败，签到失败，msg为{sign_data["message"]}\n'
        else:
            if sign_data['data']['success'] == 0:
                log.info(f'米游社原神签到: ➤ 用户 {user_id} UID {uid}, 签到成功')
                signed_days = sign_info['data']['total_sign_day']
                if sign_reward_list:
                    return SignResult.SUCCESS, f'签到成功，获得的奖励为\n{sign_reward_list[signed_days]["name"]}*{sign_reward_list[signed_days]["cnt"]}'
                else:
                    return SignResult.SUCCESS, '签到成功'
            else:
                wait_time = random.randint(90, 120)
                log.info(f'米游社原神签到: ➤ 用户 {user_id} UID {uid}, 出现验证码，等待{wait_time}秒后进行第{i + 1}次尝试绕过')
                await asyncio.sleep(wait_time)
            log.info('米游社原神签到', '➤', {'用户': user_id, 'UID': uid}, '尝试3次签到失败，无法绕过验证码', False)
    log.error(f'米游社原神签到: ➤ 用户 {user_id} UID {uid}, 尝试3次签到失败，无法绕过验证码')
    return SignResult.FAIL, f'{uid}签到失败，无法绕过验证码'


async def init_reward_list():
    global sign_reward_list
    try:
        sign_reward_list = await get_sign_reward_list()
        sign_reward_list = sign_reward_list['data']['awards']
    except Exception:
        log.error('米游社原神签到: 初始化签到奖励列表失败')
