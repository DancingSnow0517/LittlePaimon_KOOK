from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import LittlePaimon


async def on_startup(bot: 'LittlePaimon'):
    ...
