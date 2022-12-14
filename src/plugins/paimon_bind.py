import datetime
import logging
from typing import TYPE_CHECKING

from khl import Message
from khl.command.exception import Exceptions
from khl_card import CardMessage, Card
from khl_card.accessory import Kmarkdown, Button, PlainText, Paragraph
from khl_card.modules import Section, Context

from ..api.interface import CommandGroups
from ..database.models.cookie import LastQuery, PrivateCookie
from ..utils.config import config
from ..utils.genshin_api import get_bind_game_info, get_stoken_by_cookie
from ..utils.message_util import text_avatar, on_exception

if TYPE_CHECKING:
    from ..bot import LittlePaimon

log = logging.getLogger(__name__)


async def on_startup(bot: 'LittlePaimon'):

    @bot.command_info('绑定原神 **uid** 和 **cookie**', '!!原神绑定 [cookie]', [CommandGroups.BIND])
    @bot.my_command('ysb', aliases=['原神绑定', '绑定uid'])
    async def ysb(msg: Message, *cookie: str):
        if len(cookie) == 0:
            cm = CardMessage(Card(
                Section(Kmarkdown('**使用方法：`!!ysb 你的米游社cookie`**')),
                Section(Kmarkdown('也可以使用网页来绑定（如果功能开启了）'),
                        accessory=Button(PlainText('访问'), value=f'{config.public_ip}', click='link')),
                Context(Kmarkdown(f'你的用户id：{msg.author.id}'))
            ))
            await msg.reply(cm.build())
        else:
            cookie = ' '.join(cookie)
            if result := await get_bind_game_info(cookie):
                game_name = result['nickname']
                game_uid = result['game_role_id']
                mys_id = result['mys_id']
                await LastQuery.update_or_create(user_id=msg.author.id,
                                                 defaults={'uid': game_uid, 'last_time': datetime.datetime.now()})
                if 'login_ticket' in cookie and (stoken := await get_stoken_by_cookie(cookie)):
                    await PrivateCookie.update_or_create(user_id=msg.author.id, uid=game_uid, mys_id=mys_id,
                                                         defaults={'cookie': cookie,
                                                                   'stoken': f'stuid={mys_id};stoken={stoken};'})
                    ret_msg = f'**{game_name}** 成功绑定cookie ** {game_uid}'
                else:
                    await PrivateCookie.update_or_create(user_id=msg.author.id, uid=game_uid, mys_id=mys_id,
                                                         defaults={'cookie': cookie})
                    ret_msg = f'**{game_name}** 成功绑定cookie ** {game_uid}\n但是cookie中没有login_ticket，米游币相关功能无法使用哦'
            else:
                ret_msg = '这个cookie无效哦，请确认是否正确\n [cookie获取方法](docs.qq.com/doc/DQ3JLWk1vQVllZ2Z1)'
            await msg.reply(text_avatar(ret_msg, msg.author).build())

    @bot.command_info('查询已绑定的原神cookie情况', '!!查询绑定', [CommandGroups.BIND])
    @bot.my_command('ysbc', aliases=['查询ck', '查询绑定', '绑定信息', '校验绑定'])
    async def ysbc(msg: Message):
        log.info(f'开始校验 {msg.author.id} 的绑定情况')
        ck = await PrivateCookie.filter(user_id=msg.author.id)
        uid = await LastQuery.get_or_none(user_id=msg.author.id)
        if ck:
            l1 = '**序号**'
            l2 = '**UID**'
            l3 = '**状态**'
            for ck_ in ck:
                l1 += f'\n{ck.index(ck_) + 1}'
                l2 += f'\n{ck_.uid}'
                if await get_bind_game_info(ck_.cookie):
                    l3 += f'\n有效'
                else:
                    l3 += f'\n已失效'
                    await ck_.delete()
                    log.info(f'➤用户 {msg.author.id}, UID {ck_.uid} 的cookie已失效')
            card = Card(
                Section(Kmarkdown(f'**{msg.author.nickname}** 的绑定情况：')),
                Section(Paragraph(3, [Kmarkdown(l1), Kmarkdown(l2), Kmarkdown(l3)]))
            )
            await msg.reply([card.build()])
        elif uid:
            await msg.reply(f'{msg.author.id}当前已绑定uid{uid.uid}，但未绑定cookie')
        else:
            await msg.reply(f'{msg.author.id}当前无绑定信息')

    ysbc.on_exception(Exceptions.Handler.ArgLenNotMatched)(on_exception())

    @bot.command_info('删除你绑定的 **所有** cookie', '!!删除cookie', [CommandGroups.BIND])
    @bot.my_command('delete_ck', aliases=['删除cookie'])
    async def delete_ck(msg: Message):
        await PrivateCookie.filter(user_id=msg.author.id).delete()
        await msg.reply('已清除你号下绑定的cookie')

    delete_ck.on_exception(Exceptions.Handler.ArgLenNotMatched)(on_exception())
