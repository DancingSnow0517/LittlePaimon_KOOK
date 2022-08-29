from abc import ABC, abstractmethod
from typing import Union, Dict

from khl_card import CardMessage, ThemeTypes
from khl_card.accessory import Button, PlainText

registered_panel: Dict[str, 'ClickablePanel'] = {}


class BasePanel(ABC):

    @staticmethod
    @abstractmethod
    def get_panel() -> CardMessage:
        ...

    @staticmethod
    @abstractmethod
    def panel_id() -> str:
        ...


class ClickablePanel(BasePanel, ABC):

    def registry(self):
        registered_panel[self.panel_id()] = self

    def get_button(self, theme: Union[str, ThemeTypes] = ThemeTypes.PRIMARY) -> Button:
        return Button(PlainText(self.name()), value=f'open_panel_{self.panel_id()}', click='return-val', theme=theme)

    @staticmethod
    @abstractmethod
    def name() -> str:
        ...
