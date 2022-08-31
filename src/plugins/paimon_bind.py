from typing import TYPE_CHECKING

from khl import Message
from khl_card import CardMessage, Card
from khl_card.modules import Section, Context, Paragraph
from khl_card.accessory import Kmarkdown, Button, PlainText

from ..utils import requests, database
from ..utils.config import config
from ..utils.genshin_api import get_bind_game_info
from ..utils.message_utils import text_avatar

if TYPE_CHECKING:
    from ..bot import LittlePaimon


async def on_startup(bot: 'LittlePaimon'):
    for _ in range(5):
        try:
            my_ip = await requests.get('https://api.ipify.org/?format=json')
            my_ip = my_ip.json()['ip']
            break
        except:
            continue
    my_ip = '127.0.0.1'

    @bot.my_command('ysb', aliases=['原神绑定', '绑定uid'])
    async def ysb(msg: Message, *cookie: str):
        if len(cookie) == 0:
            cm = CardMessage(Card(
                Section(Kmarkdown('**使用方法：`!!ysb 你的米游社cookie`**')),
                Section(Kmarkdown('也可以使用网页来绑定（如果功能开启了）'),
                        accessory=Button(PlainText('访问'), value=f'http://{my_ip}:{config.web_app_port}',
                                         click='link')),
                Context(Kmarkdown(f'你的用户id：{msg.author.id}'))
            ))
            await msg.reply(cm.build())
        else:
            cookie = ' '.join(cookie)
            if result := await get_bind_game_info(cookie):
                game_name = result['nickname']
                game_uid = result['game_role_id']
                mys_id = result['mys_id']
                if await database.add_cookie(msg.author.id, game_uid, cookie):
                    ret_msg = f'cookie 绑定成功！\n{game_name} - {game_uid}'
                else:
                    ret_msg = f'cookie 绑定失败！\n 可能这个 cookie 的 UID 已经绑定了'
            else:
                ret_msg = '这个cookie**无效**，请确认是否正确\n请重新获取cookie后**刷新**本页面再次绑定'
            await msg.reply(text_avatar(ret_msg, msg.author).build())

    @bot.my_command('ysbc', aliases=['查询ck', '查询绑定', '绑定信息', '校验绑定'])
    async def ysbc(msg: Message):
        cookies = await database.get_cookies(user_id=msg.author.id)
        if len(cookies) != 0:
            l1 = '**序号**'
            l2 = '**UID**'
            l3 = '**状态**'
            for ck in cookies:
                l1 += f'\n{cookies.index(ck) + 1}'
                l2 += f'\n{ck.uid}'
                if await get_bind_game_info(ck.cookie):
                    l3 += '\n有效'
                else:
                    l3 += '\n已失效'
            card = Card(
                Section(Kmarkdown(f'**{msg.author.nickname}** 的绑定情况：')),
                Section(Paragraph(3, [Kmarkdown(l1), Kmarkdown(l2), Kmarkdown(l3)]))
            )
            await msg.reply([card.build()])
        else:
            await msg.reply(text_avatar('当前无绑定信息', msg.author).build())
