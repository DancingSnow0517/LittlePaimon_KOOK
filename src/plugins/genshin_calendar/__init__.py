from pathlib import Path
from typing import TYPE_CHECKING

from khl import Message, MessageTypes

from .generate import generate_day_schedule

if TYPE_CHECKING:
    from ...bot import LittlePaimon


async def on_startup(bot: 'LittlePaimon'):
    @bot.my_command('calendar', aliases=['原神日程', '活动日历', '原神日历'])
    async def calendar(msg: Message):
        im = await generate_day_schedule('cn')
        (Path() / 'Temp' / 'calendar.png').write_bytes(im)
        await msg.reply(await bot.client.create_asset('Temp/calendar.png'), type=MessageTypes.IMG)
