from typing import TYPE_CHECKING

from khl import Message
from khl_card import CardMessage, Card
from khl_card.accessory import Image
from khl_card.modules import Container

from .draw import draw_gacha_img

if TYPE_CHECKING:
    from ...bot import LittlePaimon


async def on_startup(bot: 'LittlePaimon'):
    @bot.command('sim_gacha', regex=r'^抽(?P<num>\d*)十连(?P<pool>\S*)$')
    async def sim_gacha(msg: Message, num: str, pool):
        num = int(num) if num != '' and num.isdigit() else 1
        if num <= 0 or num > 9:
            await msg.reply('一次性最多抽 9 次十连')
            return
        pool = pool or '角色1'
        result = await draw_gacha_img(msg.author.id, pool, num, msg.author.nickname)
        if isinstance(result, str):
            await msg.reply(result)
            return
        else:
            result_url = []
            for img in result:
                img.save('Temp/gacha.png')
                result_url.append(await bot.client.create_asset('Temp/gacha.png'))

        cm = CardMessage(
            Card(
                Container(*[Image(url) for url in result_url])
            )
        )

        await msg.reply(cm.build())
