import datetime
import logging
import random
from typing import Dict, Optional, Union

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from khl import Message, Channel
from khl_card import CardMessage, Card
from khl_card.modules import Audio
from khl_card.accessory import Paragraph, Kmarkdown

from ...database.models.genshin_voice import GenshinVoice, GuessVoiceRank

log = logging.getLogger(__name__)


class GuessVoice:
    game_time: int
    channel_id: str
    language: str
    character: Optional[str]

    def __init__(self, channel_id: str, game_time: int = 30, language: str = '中') -> None:
        self.channel_id = channel_id
        self.game_time = game_time
        self.language = language
        self.character = None


class GuessVoiceManager:
    gaming: Dict[str, GuessVoice]

    def __init__(self) -> None:
        self.gaming = {}

    def add(self, game: GuessVoice):
        self.gaming[game.channel_id] = game

    def get(self, channel_id: str) -> Optional[GuessVoice]:
        if channel_id in self.gaming:
            return self.gaming.get(channel_id)

    def __setitem__(self, channel_id: str, game: GuessVoice):
        if channel_id in self.gaming:
            raise ValueError(f'guess_voice: channel {channel_id} is already running!')
        self.gaming[channel_id] = game

    def __getitem__(self, channel_id: str) -> Optional[GuessVoice]:
        return self.get(channel_id)

    def __iter__(self):
        return iter(self.gaming.items())

    def is_running(self, channel_id: str) -> bool:
        return channel_id in self.gaming

    async def start(self, scheduler: AsyncIOScheduler, msg: Message, game_time: int = 30, language: str = '中') -> \
            Union[str, CardMessage]:
        if self.is_running(msg.ctx.channel.id):
            return '当前已经有一个游戏正在进行中啦！'
        game = GuessVoice(msg.ctx.channel.id, game_time, language)
        self.add(game)
        voice_list = await GenshinVoice.filter(language=game.language)
        if not voice_list:
            return '当前没有语音资源，请先[更新原神语音资源](仅限管理员)'
        voice = random.choice(voice_list)  # type: GenshinVoice
        game.character = voice.character
        if scheduler.get_job(f'Guess_voice_{game.channel_id}'):
            scheduler.remove_job(f'Guess_voice_{game.channel_id}')
        scheduler.add_job(self.end, 'date',
                          run_date=datetime.datetime.now() + datetime.timedelta(seconds=game.game_time),
                          id=f'Guess_voice_{game.channel_id}',
                          misfire_grace_time=10,
                          args=(msg.ctx.channel,),
                          timezone='Asia/Shanghai')
        return CardMessage(Card(Audio(voice.voice_url, '原神猜语音', '')))

    async def end(self, channel: Channel):
        if game := self.get(channel.id):
            answer = game.character
            del self.gaming[channel.id]
            msg = f'还没有人猜中呢，正确答案是：{answer}！'
            try:
                await channel.send(msg)
            except Exception as e:
                log.warning(f'原神猜语音: ➤发送结果时出错 {e}')
            log.info(f'原神猜语音: ➤频道 {channel.id} 猜语音游戏结束, 答案为{answer}，没有人猜对')
