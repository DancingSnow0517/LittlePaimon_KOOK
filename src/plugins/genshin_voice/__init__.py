import datetime
import logging
from typing import TYPE_CHECKING, Dict, List

from khl import Message
from khl_card import CardMessage, Card, Paragraph, Section, Kmarkdown, Header

from .handler import GuessVoiceManager
from .resources import update_voice_resources
from src.utils.path import JSON_DATA
from ...database.models.genshin_voice import GuessVoiceRank
from ...utils.files import load_json

if TYPE_CHECKING:
    from ...bot import LittlePaimon

log = logging.getLogger(__name__)

langs = ['中', '英', '日', '韩']
alias_file = load_json(JSON_DATA / 'alias.json')

chars: Dict[str, List[str]] = {}
aliases: List[str] = []

for char_id in alias_file['角色']:
    chars[alias_file['角色'][char_id][0]] = alias_file['角色'][char_id]
    aliases += alias_file['角色'][char_id]


async def on_startup(bot: 'LittlePaimon'):
    manager = GuessVoiceManager()

    # noinspection PyProtectedMember
    @bot.command('guess', aliases=aliases, prefixes=[''])
    async def guess(msg: Message):
        if game := manager.get(msg.ctx.channel.id):
            content = msg.content
            char = None
            for c in chars:
                if content in chars[c]:
                    char = c
                    break
            if char and char == game.character:
                await GuessVoiceRank.create(user_id=msg.author.id, group_id=msg.ctx.channel.id, answer=char,
                                            guess_time=datetime.datetime.now())
                del manager.gaming[msg.ctx.channel.id]
                if bot.task._scheduler.get_job(f'Guess_voice_{msg.ctx.channel.id}'):
                    bot.task._scheduler.remove_job(f'Guess_voice_{msg.ctx.channel.id}')
                log.info(f'原神猜语音: ➤频道{msg.ctx.channel.id}猜语音游戏结束，答案为{char}，由{msg.author.id}猜对')
                await msg.ctx.channel.send(f'恭喜 (met){msg.author.id}(met) 猜对，正确答案为 {char}')

    @bot.command_info('开始原神猜语音游戏', '!!原神猜语音 [语言]')
    @bot.my_command('guess_voice', aliases=['原神猜语音'])
    async def guess_voice(msg: Message, lang: str = '中'):
        if lang not in langs:
            await msg.reply('不是一个正确的语言。可选语言： 中, 英, 日, 韩')
            return
        # noinspection PyProtectedMember
        result = await manager.start(bot.task._scheduler, msg, 30, lang)
        if isinstance(result, str):
            await msg.reply(result)
        else:
            await msg.ctx.channel.send('即将发送一段语音，将在30秒后公布答案')
            await msg.ctx.channel.send(result.build())

    @bot.command_info('查看近几天的原神猜语音排行榜', '!!猜语音排行榜 [天数]')
    @bot.my_command('voice_rank', aliases=['排行榜', '猜语音排行榜'])
    async def voice_rank(msg: Message, days: int = 7):
        await msg.reply((await get_rank(msg.ctx.channel.id, days)).build())

    @bot.command_info('更新原神语音资源', '!!更新原神语音资源')
    @bot.admin_command('update_voice', aliases=['更新原神语音资源'])
    async def update_voice(msg: Message):
        await msg.ctx.channel.send('开始更新原神语音资源，请稍等...')
        result = await update_voice_resources()
        await msg.ctx.channel.send(result)

    async def get_rank(channel_id: str, days: int = 7):
        records = await GuessVoiceRank.filter(group_id=channel_id,
                                              guess_time__gte=datetime.datetime.now() - datetime.timedelta(days=days))
        l1 = '**排名**'
        l2 = '**用户**'
        l3 = '**次数**'
        rank = {}
        for record in records:
            if record.user_id in rank:
                rank[record.user_id] += 1
            else:
                rank[record.user_id] = 1

        for i, (user_id, count) in enumerate(sorted(rank.items(), key=lambda x: x[1], reverse=True), start=1):
            l1 += f'\n#{i}'
            l2 += f'\n{(await bot.client.fetch_user(user_id)).nickname}'
            l3 += f'\n{count}'

        return CardMessage(Card(
            Header(f'原神猜语音近 {days}天 的排行榜'),
            Section(Paragraph(3, [
                Kmarkdown(l1),
                Kmarkdown(l2),
                Kmarkdown(l3)
            ]))
        ))
