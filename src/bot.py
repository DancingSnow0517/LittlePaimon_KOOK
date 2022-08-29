import inspect
import re

from khl import Bot, Event, EventTypes, Message, GuildUser, User

from . import panels
from .api.panel import registered_panel, ClickablePanel
from .utils.config import config
from .utils.message_util import update_message, update_private_message


class LittlePaimon(Bot):

    def __init__(self):
        super().__init__(config.token)


def main():
    bot = LittlePaimon()

    @bot.on_startup
    async def onstart_up(_: LittlePaimon):
        for i in inspect.getmembers(
                panels,
                lambda x: issubclass(x, ClickablePanel) if inspect.isclass(x) and x != ClickablePanel else False
        ):
            i[1]().registry()

    @bot.command(name='test')
    async def test(msg: Message):
        await msg.reply(panels.TestPanel.get_panel().build())

    @bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
    async def on_button_click(_: LittlePaimon, event: Event):
        value = event.body['value']
        msg_id = event.body['msg_id']
        user_id = event.body['user_id']
        if 'guild_id' in event.body:
            guild_id = event.body['guild_id']
            user = GuildUser(guild_id=guild_id, _gate_=bot.client.gate, _lazy_loaded_=True, **event.body['user_info'])
        else:
            guild_id = None
            user = User(_gate_=bot.client.gate, _lazy_loaded_=True, **event.body['user_info'])

        match = re.match(r'^open_panel_([a-zA-Z_0-9]+)$', value)
        if match:
            panel_id = match.group(1)
            if panel_id in registered_panel:
                if guild_id is not None:
                    await update_message(registered_panel[panel_id].get_panel().build(), msg_id, user_id,
                                         bot.client.gate)
                else:
                    await update_private_message(registered_panel[panel_id].get_panel().build(), msg_id,
                                                 bot.client.gate)

    bot.run()
