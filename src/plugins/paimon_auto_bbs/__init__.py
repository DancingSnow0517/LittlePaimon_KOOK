import logging
from typing import TYPE_CHECKING

from khl import Message

from .coin_handle import mhy_bbs_coin
from .sign_handle import mhy_bbs_sign, init_reward_list
from ...database.models.cookie import PrivateCookie

if TYPE_CHECKING:
    from ...bot import LittlePaimon

log = logging.getLogger(__name__)

signing_list = []
coin_getting_list = []


async def on_startup(bot: 'LittlePaimon'):
    await init_reward_list()

    @bot.command_info('执行米游社签到操作', '!!米游社签到 [UID]')
    @bot.my_command('sign', aliases=['mys签到', '米游社签到', 'mys自动签到', '米游社自动签到'])
    async def sign(msg: Message, uid: str = None):
        if uid is None:
            cookies = await PrivateCookie.filter(user_id=msg.author.id)
            if len(cookies) == 0:
                await msg.reply('你还没有绑定 cookie')
                return
        else:
            cookies = await PrivateCookie.filter(uid=uid)
            if len(cookies) == 0:
                await msg.reply(f'数据库没有查询到 uid 的信息')
                return
            for ck in cookies:
                if ck.user_id != msg.author.id:
                    await msg.reply(f'UID: {ck.uid} 不属于你')
                    cookies.remove(ck)
        await msg.ctx.channel.send('米游社原神签到不维护，不保证成功！')
        for ck in cookies:
            if f'{ck.user_id}-{ck.uid}' in signing_list:
                await msg.reply('你已经在执行签到任务中，请勿重复发送')
            else:
                await msg.reply(f'开始为UID **{ck.uid}** 执行米游社签到，请稍等...')
                log.info(f'米游社原神签到: user_id: {ck.user_id} uid: {ck.uid} 执行签到')
                signing_list.append(f'{ck.user_id}-{ck.uid}')
                _, result = await mhy_bbs_sign(ck.user_id, ck.uid)
                signing_list.remove(f'{ck.user_id}-{ck.uid}')
                await msg.reply(result)

    @bot.command_info('执行米游币任务操作', '!!米游币获取 [UID]')
    @bot.my_command('get_coin', aliases=['myb获取', '米游币获取', 'myb自动获取', '米游币自动获取', '米游币任务'])
    async def get_coin(msg: Message, uid: str = None):
        if uid is None:
            cookies = await PrivateCookie.filter(user_id=msg.author.id)
            if len(cookies) == 0:
                await msg.reply('你还没有绑定 cookie')
                return
        else:
            cookies = await PrivateCookie.filter(uid=uid)
            if len(cookies) == 0:
                await msg.reply(f'数据库没有查询到 uid 的信息')
                return
            for ck in cookies:
                if ck.user_id != msg.author.id:
                    await msg.reply(f'UID: {ck.uid} 不属于你')
                    cookies.remove(ck)
        for ck in cookies:
            if f'{ck.user_id}-{ck.uid}' in coin_getting_list:
                await msg.reply('你已经在执行米游币获取任务中，请勿重复发送')
            else:
                await msg.reply(f'开始为UID **{ck.uid}** 执行米游币获取，请稍等...')
                log.info(f'米游币自动获取: user_id: {ck.user_id} uid: {ck.uid} 执行签到')
                coin_getting_list.append(f'{ck.user_id}-{ck.uid}')
                result = await mhy_bbs_coin(ck.user_id, ck.uid)
                coin_getting_list.remove(f'{ck.user_id}-{ck.uid}')
                await msg.reply(result)
