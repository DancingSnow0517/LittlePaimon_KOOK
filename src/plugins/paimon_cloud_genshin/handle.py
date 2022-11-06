from .api import get_info, check_token, get_notification
from ...database.models.subscription import CloudGenshinSub


async def get_cloud_genshin_info(user_id: str, uid: str):
    if not (info := await CloudGenshinSub.get_or_none(user_id=user_id, uid=uid)):
        return f'你的UID{uid}还没有绑定云原神账户哦~请使用[云原神绑定]命令绑定账户'
    result = await get_info(info.uuid, info.token)
    if result['retcode'] != 0:
        return '你的云原神token已失效，请重新绑定'
    coins = result['data']['coin']['coin_num']
    free_time = result['data']['free_time']['free_time']
    card = result['data']['play_card']['short_msg']
    return f'======== UID: {uid} ========\n' \
           f'剩余米云币: {coins}\n' \
           f'剩余免费时间: {free_time}分钟\n' \
           f'畅玩卡状态: {card}'


async def sign(uid: CloudGenshinSub):
    if await check_token(uid.uuid, uid.token):
        info = await get_info(uid.uuid, uid.token)
        if info['data']['free_time']['free_time'] == 600:
            msg = '云原神签到失败，免费时长已达上限'
        else:
            s = await get_notification(uid.uuid, uid.token)
            msg = '云原神签到成功' if s['data']['list'] else '云原神今日已签到'
    else:
        msg = f'UID{uid.uid}云原神token已失效，请重新绑定'
    return msg
