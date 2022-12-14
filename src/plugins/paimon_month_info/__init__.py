import datetime
from typing import TYPE_CHECKING

from khl import Message, MessageTypes

from .handle import handle_myzj
from ...api.interface import CommandGroups
from ...database.models.cookie import PrivateCookie
from ...database.models.player_info import Player

if TYPE_CHECKING:
    from ...bot import LittlePaimon


async def on_startup(bot: 'LittlePaimon'):
    @bot.command_info('查看指定月份的原石、摩拉获取情况', '!!每月札记 [月份]', [CommandGroups.INFO])
    @bot.my_command('myzj', aliases=['札记信息', '每月札记'])
    async def myzj(msg: Message, month: str = None):
        month_now = datetime.datetime.now().month
        if month_now == 1:
            month_list = ['11', '12', '1']
        elif month_now == 2:
            month_list = ['12', '1', '2']
        else:
            month_list = [str(month_now - 2), str(month_now - 1), str(month_now)]
        month = month if month in month_list else month_now
        cookies = await PrivateCookie.filter(user_id=msg.author.id)
        for ck in cookies:
            img = await handle_myzj(Player(user_id=ck.user_id, uid=ck.uid), month)
            if isinstance(img, str):
                await msg.ctx.channel.send(img)
            else:
                img.save('Temp/myzj.png')
                await msg.ctx.channel.send(await bot.client.create_asset('Temp/myzj.png'), type=MessageTypes.IMG)
