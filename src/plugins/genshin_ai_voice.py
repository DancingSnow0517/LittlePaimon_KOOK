from pathlib import Path
from typing import TYPE_CHECKING

from khl import Message
from khl_card import Card
from khl_card.modules import Audio

from ..utils import requests
from ..utils.types import CHARACTERS

if TYPE_CHECKING:
    from ..bot import LittlePaimon


async def on_startup(bot: 'LittlePaimon'):
    @bot.command_info('AI生成对应角色语音', '!!AI语音 [文字] [角色]')
    @bot.my_command('tts', aliases=['AI语音'])
    async def tts(msg: Message, text: str, char: str = '派蒙', noise: float = 0.667, noisew: float = 0.8,
                  length: float = 1.2):
        if char not in CHARACTERS:
            await msg.reply('不支持这个角色呢')
        else:
            voice = await get_voice(text, char, noise, noisew, length)
            voice_path = Path() / 'Temp' / 'ai_voice.mp3'
            voice_path.write_bytes(voice)
            url = await bot.client.create_asset(voice_path.__str__())
            await msg.reply([Card(
                Audio(url, title=text, cover='')
            ).build()])


async def get_voice(text: str, char: str, noise: float = 0.667, noisew: float = 0.8, length: float = 1.2,
                    format: str = 'mp3') -> bytes:
    """
    得到 TTS 语音
    :param text: 语音文字
    :param char: 语音使用的角色
    :param noise: 生成时使用的 noise_factor，可用于控制感情等变化程度。
    :param noisew: 生成时使用的 noise_factor_w，可用于控制音素发音长度变化程度。
    :param length: 生成时使用的 length_factor，可用于控制整体语速。
    :param format: 生成语音的格式，必须为mp3或者wav。
    :return: 返回所需语音
    """
    res = await requests.get(
        f'http://233366.proxy.nscc-gz.cn:8888/?text={text}&speaker={char}&noise={noise}&noisew={noisew}&length={length}&format={format}')
    return res.read()
