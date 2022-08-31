import inspect
import logging
import re
from threading import Thread

from gevent import pywsgi
from khl import Bot, Event, EventTypes, Message, GuildUser, User

from . import panels
from .api.panel import registered_panel, ClickablePanel
from .utils import database
from .utils.config import config
from .utils.message_util import update_message, update_private_message
from .webapp import app

log = logging.getLogger(__name__)


class WebappThread(Thread):
    server: pywsgi.WSGIServer = None

    def run(self) -> None:
        super().run()
        log.info('正在启动web服务...')
        self.server = pywsgi.WSGIServer((config.web_app_address, config.web_app_port), app, log=None)
        self.server.serve_forever()

    def stop(self):
        if self.server:
            self.server.stop()


class LittlePaimon(Bot):

    def __init__(self):
        super().__init__(config.token)


def main():
    bot = LittlePaimon()

    webapp_thread = WebappThread()

    @bot.on_startup
    async def onstart_up(_: LittlePaimon):
        if config.enable_web_app:
            webapp_thread.start()
        database.init()
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
    webapp_thread.stop()
