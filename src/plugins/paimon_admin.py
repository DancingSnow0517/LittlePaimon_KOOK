import logging
from typing import TYPE_CHECKING

from khl import Message, ChannelTypes

from ..database.models.cookie import PrivateCookie, PublicCookie
from ..utils.genshin_api import get_bind_game_info

if TYPE_CHECKING:
    from ..bot import LittlePaimon

log = logging.getLogger(__name__)


async def on_startup(bot: 'LittlePaimon'):
    @bot.admin_command('ysbca', aliases=['校验所有ck', '校验所有cookie', '校验所有绑定'])
    async def ysbca(msg: Message):
        log.info('原神Cookie: 开始校验所有cookie情况')
        await msg.ctx.channel.send('开始校验全部cookie，请稍等...')
        private_cookies = await PrivateCookie.all()
        public_cookies = await PublicCookie.all()
        useless_private = []
        useless_public = []
        for cookie in private_cookies:
            if not await get_bind_game_info(cookie.cookie):
                useless_private.append(cookie.uid)
                await cookie.delete()
        for cookie in public_cookies:
            if not await get_bind_game_info(cookie.cookie):
                useless_public.append(str(cookie.id))
                await cookie.delete()
        m = f'当前共 **{len(public_cookies)}** 个公共ck，**{len(private_cookies)}** 个私人ck。\n'
        if useless_public:
            m += '其中失效的公共ck有:' + ' '.join(useless_public) + '\n'
        else:
            m += '公共ck全部有效\n'
        if useless_private:
            m += '其中失效的私人ck有:' + ' '.join(useless_private) + '\n'
        else:
            m += '私人ck全部有效\n'
        await msg.ctx.channel.send(m)

    @bot.admin_command('pck', aliases=['添加公共cookie', '添加pck', '添加公共ck', 'add_pck'])
    async def pck(msg: Message, *cookie: str):
        if len(cookie) == 0:
            await msg.reply(
                '(获取cookie的教程)[docs.qq.com/doc/DQ3JLWk1vQVllZ2Z1]\n获取到后，用[添加公共ck cookie]指令添加')
        else:
            cookie = ' '.join(cookie)
            if await get_bind_game_info(cookie):
                ck = await PublicCookie.create(cookie=cookie)
                log.info(f'原神Cookie: {ck.id} 号公共cookie添加成功')
                await msg.reply(f'成功添加{ck.id}号公共cookie')
            else:
                log.error('原神Cookie: 公共cookie添加失败，cookie已失效')
                await msg.reply('这个cookie无效哦，请确认是否正确')

    @bot.admin_command('guild_list', aliases=['服务器列表'])
    async def guild_list(msg: Message):
        guilds = await bot.client.fetch_guild_list()
        await msg.reply(f'共发现 {len(guilds)} 个服务器')
        for guild in guilds:
            log.info(f'{guild.name} - {guild.id}')

    @bot.admin_command('announcement', aliases=['公告'])
    async def announcement(msg: Message, *content: str):
        content = '\n'.join(content)
        print(content)
        log.info('小派蒙公告: 开始发送...')
        guilds = await bot.client.fetch_guild_list()
        log.info(f'小派蒙公告: 总共发现了 {len(guilds)} 个服务器')
        for guild in guilds:
            if guild.id == msg.ctx.guild.id:
                continue
            log.info(f'小派蒙公告: 正在向 {guild.name} 服务器发送公告')
            channels = await guild.fetch_channel_list()
            for channel in channels:
                if channel.type == ChannelTypes.TEXT:
                    try:
                        log.info(f'小派蒙公告: 尝试向 {guild.name} - {channel.name}/{channel.id} 发送公告')
                        await channel.send(content)
                        log.info('小派蒙公告: 发送成功')
                        break
                    except Exception as e:
                        log.error(f'小派蒙公告: 发送失败: {e}')
                        continue
