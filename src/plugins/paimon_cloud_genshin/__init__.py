import re
import uuid
from typing import TYPE_CHECKING

from khl import Message

from ...database.models.subscription import CloudGenshinSub

if TYPE_CHECKING:
    from ...bot import LittlePaimon

uuid_ = str(uuid.uuid4())


async def on_startup(bot: 'LittlePaimon'):
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
