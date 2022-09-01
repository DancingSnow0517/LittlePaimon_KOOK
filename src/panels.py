from khl_card import CardMessage, Card, ActionGroup, Button, PlainText

from .api.panel import ClickablePanel


class MainPanel(ClickablePanel):

    @staticmethod
    def get_panel() -> CardMessage:
        return CardMessage(
            Card(
                ActionGroup(
                    Button(PlainText('paimon_gacha'))
                )
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
        return '抽卡'

    @staticmethod
    def get_panel() -> CardMessage:
        return CardMessage(Card(

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
