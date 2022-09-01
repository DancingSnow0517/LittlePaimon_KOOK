import json
from typing import Union

from khl import Gateway, api, User, Message
from khl.command import Command
from khl_card import CardMessage, Card, Section, Kmarkdown, Image


async def update_message(content: Union, msg_id: str, user_id: str, gate: Gateway):
    content = content if isinstance(content, str) else json.dumps(content)
    await gate.exec_req(api.Message.update(msg_id=msg_id, content=content, temp_target_id=user_id))


async def update_private_message(content: Union, msg_id: str, gate: Gateway):
    content = content if isinstance(content, str) else json.dumps(content)
    await gate.exec_req(api.DirectMessage.update(msg_id=msg_id, content=content))


def text_avatar(text: str, author: User) -> CardMessage:
    return CardMessage(
        Card(
            Section(Kmarkdown(text), accessory=Image(author.avatar), mode='left')
        )
    )


def on_exception(err_msg: str = '发生了错误，请检查命令是否正确'):
    async def dec(cmd: Command, exc: Exception, msg: Message):
        await msg.reply(err_msg)
    return dec
