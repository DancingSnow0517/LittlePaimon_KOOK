import re
import uuid
from typing import TYPE_CHECKING

from khl import Message
from khl_card import CardMessage, Card
from khl_card.modules import Section, Header
from khl_card.accessory import Kmarkdown

from .handle import get_cloud_genshin_info, sign
from ...database.models.subscription import CloudGenshinSub

if TYPE_CHECKING:
    from ...bot import LittlePaimon

uuid_ = str(uuid.uuid4())


async def on_startup(bot: 'LittlePaimon'):
    @bot.command_info('绑定云原神账户token', '!!云原神绑定 [token]')
    @bot.my_command('yys_bind', aliases=['云原神绑定'])
    async def yys_bind(msg: Message, *token: str):
        if len(token) == 0:
            await msg.reply('请给出要绑定的token')
        token = ' '.join(token)
        if match := re.match(r'oi=\d+', token):
            uid = str(match.group()).split('=')[1]
            await CloudGenshinSub.update_or_create(user_id=msg.author.id, uid=uid,
                                                   defaults={'uuid': uuid_, 'token': token})
            await msg.reply(f'米游社账号{uid}云原神token绑定成功，将会每日为你自动领免费时长')
        else:
            await msg.reply('token格式错误哦~请按照[教程](https://blog.ethreal.cn/archives/yysgettoken)所写的方法获取')

    @bot.command_info('进行一次云原神签到', '!!云原神签到 [米游社uid]')
    @bot.my_command('yys_sign', aliases=['云原神签到'])
    async def yys_sign(msg: Message, uid: str = None):
        if uid is None:
            uid_list = await CloudGenshinSub.filter(user_id=msg.author.id)
        else:
            uid_list = await CloudGenshinSub.filter(user_id=msg.author.id, uid=uid)
        if uid_list:
            for uid in uid_list:
                await msg.ctx.channel.send(await sign(uid), temp_target_id=msg.author.id)
        else:
            await msg.reply('没有找到云原神绑定信息')

    @bot.command_info('查看云原神账户信息', '!!云原神信息 [米游社id]')
    @bot.my_command('yys_info', aliases=['云原神信息'])
    async def yys_info(msg: Message, uid: str = None):
        if uid is None:
            if uids := await CloudGenshinSub.filter(user_id=msg.author.id):
                cm = CardMessage(Card(
                    Header('你已绑定的云原神账号有: '),
                    *[Section(Kmarkdown(f'**{uid.uid}**')) for uid in uids]
                ))
                await msg.reply(cm.build())
            else:
                await msg.reply('你还没有绑定云原神账号哦~')
        else:
            await msg.reply(await get_cloud_genshin_info(msg.author.id, uid))

    @bot.command_info('解绑云原神账户', '云原神解绑 [米游社id]')
    @bot.my_command('yys_delete', aliases=['云原神解绑'])
    async def yys_delete(msg: Message, uid: str = None):
        if uid is None:
            if uids := await CloudGenshinSub.filter(user_id=msg.author.id):
                cm = CardMessage(Card(
                    Header('你已绑定的云原神账号有: '),
                    *[Section(Kmarkdown(f'**{uid.uid}**')) for uid in uids]
                ))
                await msg.reply(cm.build())
            else:
                await msg.reply('你还没有绑定云原神账号哦~')
        else:
            if u := await CloudGenshinSub.get_or_none(user_id=msg.author.id, uid=uid):
                await u.delete()
                await msg.reply(f'米游社账号{u.uid}解绑云原神成功')
            else:
                await msg.reply(f'未找到云原神账号 {uid}')
