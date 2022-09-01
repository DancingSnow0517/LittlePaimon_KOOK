from khl_card import CardMessage, Card
from khl_card.modules import ActionGroup, Section, Header, Divider, Context
from khl_card.accessory import Kmarkdown

from .api.panel import ClickablePanel
from .utils.constant import VERSION


class MainPanel(ClickablePanel):

    @staticmethod
    def get_panel() -> CardMessage:
        return CardMessage(
            Card(
                Header('小派蒙的帮助信息'),
                Section(Kmarkdown('命令中的 `[ ]` 不用加进去。')),
                Section(Kmarkdown('例: `[UID]` 只需要将这个替换为你的 `UID`。`[cookie]` 同理')),
                ActionGroup(
                    GachaPanel().get_button()
                ),
                Divider(),
                Context(Kmarkdown(f'当前小派蒙版本: **{VERSION}**'))
            )
        )

    @staticmethod
    def panel_id() -> str:
        return "main_panel"

    @staticmethod
    def name() -> str:
        return "主菜单"


class GachaPanel(ClickablePanel):

    @staticmethod
    def name() -> str:
        return '模拟抽卡'

    @staticmethod
    def get_panel() -> CardMessage:
        return CardMessage(Card(
            Header('模拟抽卡相关的命令'),
            Divider(),
            Section(Kmarkdown('**模拟抽卡**\n用法: 抽[次数]十连[池子]\n例：抽3十连武器 代表抽3个十连武器池')),
            Divider(),
            Section(Kmarkdown('**模拟抽卡记录**\n用法: `!!模拟抽卡记录`')),
            Divider(),
            ActionGroup(
                MainPanel().get_button()
            ),
            Divider(),
            Context(Kmarkdown(f'当前小派蒙版本: **{VERSION}**'))
        ))

    @staticmethod
    def panel_id() -> str:
        return 'gacha_panel'


class TestPanel(ClickablePanel):
    @staticmethod
    def get_panel() -> CardMessage:
        return CardMessage(
            Card(
                ActionGroup(
                    MainPanel().get_button()
                )
            )
        )

    @staticmethod
    def name() -> str:
        pass

    @staticmethod
    def panel_id() -> str:
        pass
