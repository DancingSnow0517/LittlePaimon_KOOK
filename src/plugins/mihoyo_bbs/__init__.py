import logging
from pathlib import Path
from typing import TYPE_CHECKING

from khl import Message, MessageTypes

from ...utils.browser import screenshot

if TYPE_CHECKING:
    from ...bot import LittlePaimon

log = logging.getLogger(__name__)

temp_screenshot = Path() / 'Temp' / 'post_screenshot.png'


async def on_startup(bot: 'LittlePaimon'):
    @bot.command('post_screenshot', regex=r'\[.+\]\(((?:https://)?(m\.)?bbs.mihoyo.com/.+/article/\d+)\)')
    async def post_screenshot(msg: Message, url: str, *_):
        log.info(f'米游社: 开始截图帖子 {url}')
        try:
            img = await screenshot(url, elements=['.mhy-article-page__main'], timeout=180000)
        except Exception as e:
            log.info(f'米游社: 帖子 {url}截图失败\n{e}')
            await msg.ctx.channel.send('米游社帖子截图超时失败了~~')
            return

        await msg.ctx.channel.send(await bot.client.create_asset(temp_screenshot), type=MessageTypes.IMG)
