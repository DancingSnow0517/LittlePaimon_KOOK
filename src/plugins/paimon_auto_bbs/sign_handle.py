import asyncio
import datetime
import logging
import random
from typing import Tuple

from .draw import SignResult
from ...database.models.cookie import LastQuery
from ...utils.genshin_api import get_mihoyo_private_data, get_sign_reward_list

log = logging.getLogger(__name__)

sign_reward_list: dict = {}


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
        log.info(f'米游社原神签到: ➤ 用户 {user_id} UID {uid}, 未绑定私人cookie')
        return SignResult.FAIL, sign_info
    elif sign_info['data']['is_sign']:
        signed_days = sign_info['data']['total_sign_day'] - 1
        log.info(f'米游社原神签到: ➤ 用户 {user_id} UID {uid}, 今天已经签过了')
        return SignResult.DONE, f'UID{uid}今天已经签过了，获得的奖励为\n{sign_reward_list[signed_days]["name"]}*{sign_reward_list[signed_days]["cnt"]}'
    for i in range(6):
        sign_data = await get_mihoyo_private_data(uid, user_id, 'sign_action')
        if isinstance(sign_data, str):
            log.info(f'米游社原神签到: ➤ 用户 {user_id} UID {uid}, 获取数据失败, {sign_data}')
            return SignResult.FAIL, f'{uid}签到失败，{sign_data}'
        elif sign_data['retcode'] == -5003:
            signed_days = sign_info['data']['total_sign_day'] - 1
            log.info(f'米游社原神签到: ➤ 用户 {user_id} UID {uid}, 今天已经签过了')
            return SignResult.DONE, f'UID{uid}今天已经签过了，获得的奖励为\n{sign_reward_list[signed_days]["name"]}*{sign_reward_list[signed_days]["cnt"]}'
        elif sign_data['retcode'] != 0:
            log.info(
                f'米游社原神签到: ➤ 用户 {user_id}, UID {uid}, 获取数据失败，code为 {sign_data["retcode"]}， msg为 {sign_data["message"]}')
            return SignResult.FAIL, f'{uid}获取数据失败，签到失败，msg为{sign_data["message"]}\n'
        else:
            if sign_data['data']['success'] == 0:
                log.info(f'米游社原神签到: ➤ 用户 {user_id} UID {uid}, 签到成功')
                signed_days = sign_info['data']['total_sign_day']
                return SignResult.SUCCESS, f'签到成功，获得的奖励为\n{sign_reward_list[signed_days]["name"]}*{sign_reward_list[signed_days]["cnt"]}'
            else:
                log.warning(f'米游社原神签到: ➤ 用户 {user_id} UID {uid} 出现验证码，重试第 {i} 次')
                await asyncio.sleep(random.randint(10, 15))
    log.error(f'米游社原神签到: ➤ 用户 {user_id} UID {uid}, 尝试6次签到失败，无法绕过验证码')
    return SignResult.FAIL, f'{uid}签到失败，无法绕过验证码'


async def init_reward_list():
    global sign_reward_list
    sign_reward_list = await get_sign_reward_list()
    sign_reward_list = sign_reward_list['data']['awards']
