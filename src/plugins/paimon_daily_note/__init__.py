import logging
from typing import TYPE_CHECKING

from khl import Message, MessageTypes

from .handle import handle_ssbq
from ...database.models.cookie import PrivateCookie
from ...database.models.player_info import Player

if TYPE_CHECKING:
    from ...bot import LittlePaimon

log = logging.getLogger(__name__)


async def on_startup(bot: 'LittlePaimon'):
    @bot.command_info('查看原神实时便笺(树脂情况)', '!!实时便笺 [UID]')
    @bot.my_command('ssbq', aliases=['实时便笺', '实时便签', '当前树脂'])
    async def ssbq(msg: Message, uid: str = None):
        log.info('原神实时便签: 开始执行查询')
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
            img = await handle_ssbq(Player(user_id=ck.user_id, uid=ck.uid))
            if isinstance(img, str):
                await msg.ctx.channel.send(img)
                return
            img.save('Temp/ssbq.png')
            await msg.ctx.channel.send(await bot.client.create_asset('Temp/ssbq.png'), type=MessageTypes.IMG)
