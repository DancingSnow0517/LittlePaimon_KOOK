from khl_card import CardMessage, Card, ThemeTypes
from khl_card.accessory import Kmarkdown, Button, PlainText
from khl_card.modules import ActionGroup, Section, Header, Divider, Context, Invite

from .api.panel import ClickablePanel
from .utils.config import config
from .utils.constant import VERSION


class MainPanel(ClickablePanel):

    @staticmethod
    def get_panel() -> CardMessage:
        return CardMessage(
            Card(
                Header('小派蒙的帮助信息'),
                Section(Kmarkdown('命令中的 `[ ]` 不用加进去。')),
                Section(Kmarkdown('例: `[UID]` 只需要将这个替换为你的 `UID`。`[cookie]` 同理')),
                Section(Kmarkdown('可以使用命令 `!!帮助 all` 来查看一图流命令列表')),
                ActionGroup(
                    GenshinInfoPanel().get_button(ThemeTypes.INFO),
                    GachaPanel().get_button(),
                    SignPanel().get_button(),
                    DailyNotePanel().get_button()
                ),
                ActionGroup(
                    GenshinWikiPanel().get_button(),
                    PaimonBindPanel().get_button(),
                    AIVoicePanel().get_button(),
                    AdminPanel().get_button()
                ),
                Divider(),
                Section(Kmarkdown(f'在使用小派蒙的过程中遇到的问题，可以来我的服务器询问')),
                Invite('s69UmB'),
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
            Section(Kmarkdown('**模拟抽卡**\n用法: 抽[次数]十连[池子]\n例：抽3十连武器 代表抽3个十连武器池')),
            Divider(),
            Section(Kmarkdown('**模拟抽卡记录**\n用法: `!!模拟抽卡记录`')),
            Divider(),
            ActionGroup(
                MainPanel().get_button(ThemeTypes.DANGER)
            ),
            Divider(),
            Context(Kmarkdown(f'当前小派蒙版本: **{VERSION}**'))
        ))

    @staticmethod
    def panel_id() -> str:
        return 'gacha_panel'


class SignPanel(ClickablePanel):

    @staticmethod
    def name() -> str:
        return "签到"

    @staticmethod
    def get_panel() -> CardMessage:
        return CardMessage(Card(
            Header('签到相关命令'),
            Section(Kmarkdown('**米游社签到**\n用法: !!米游社签到 [UID]')),
            Divider(),
            Section(Kmarkdown('**米游币获取**\n用法: !!米游币获取 [UID]')),
            Divider(),
            ActionGroup(
                MainPanel().get_button(ThemeTypes.DANGER)
            ),
            Divider(),
            Context(Kmarkdown(f'当前小派蒙版本: **{VERSION}**'))
        ))

    @staticmethod
    def panel_id() -> str:
        return "sign_panel"


class DailyNotePanel(ClickablePanel):
    @staticmethod
    def name() -> str:
        return '实时便笺'

    @staticmethod
    def get_panel() -> CardMessage:
        return CardMessage(Card(
            Header('实时便笺命令'),
            Section(Kmarkdown('**实时便笺**\n用法: !!实时便笺 [UID]')),
            Divider(),
            ActionGroup(
                MainPanel().get_button(ThemeTypes.DANGER)
            ),
            Divider(),
            Context(Kmarkdown(f'当前小派蒙版本: **{VERSION}**'))
        ))

    @staticmethod
    def panel_id() -> str:
        return 'daily_note_panel'


class GenshinInfoPanel(ClickablePanel):
    @staticmethod
    def name() -> str:
        return '原神信息'

    @staticmethod
    def get_panel() -> CardMessage:
        return CardMessage(Card(
            Header('原神信息相关命令'),
            Section(Kmarkdown('**原神卡片**\n用法: !!原神卡片 [UID]')),
            Divider(),
            Section(Kmarkdown('**角色背包**\n用法: !!角色背包 [UID]')),
            Divider(),
            Section(Kmarkdown('**深渊信息**\n用法: !!深渊信息 [1|2] [UID]\n1: 这期深渊 2: 上期深渊')),
            Divider(),
            Section(Kmarkdown('**角色图**\n用法: !!角色图 [角色名]')),
            Divider(),
            Section(Kmarkdown('**角色面板**\n用法: !!角色详情 [角色名]')),
            Divider(),
            Section(Kmarkdown('**每月札记**\n用法: !!每月札记 [月份]')),
            Divider(),
            Section(Kmarkdown('**原神日历**\n用法: !!原神日历')),
            Divider(),
            ActionGroup(
                MainPanel().get_button(ThemeTypes.DANGER)
            ),
            Divider(),
            Context(Kmarkdown(f'当前小派蒙版本: **{VERSION}**'))
        ))

    @staticmethod
    def panel_id() -> str:
        return 'genshin_info_panel'


class GenshinWikiPanel(ClickablePanel):
    @staticmethod
    def name() -> str:
        return 'WIKI'

    @staticmethod
    def get_panel() -> CardMessage:
        return CardMessage(Card(
            Header('WIKI 相关命令'),
            Section(Kmarkdown('**每日材料**\n用法: <今天|周几>材料 例：周三材料')),
            Divider(),
            Section(Kmarkdown('**原魔图鉴**\n用法: <原魔名>原魔图鉴')),
            Divider(),
            Section(Kmarkdown('**武器图鉴**\n用法: <武器名>武器图鉴')),
            Divider(),
            Section(Kmarkdown('**圣遗物图鉴**\n用法: <圣遗物名>圣遗物图鉴')),
            Divider(),
            Section(Kmarkdown('**角色攻略**\n用法: <角色名>角色攻略')),
            Divider(),
            Section(Kmarkdown('**角色材料**\n用法: <角色名>角色材料')),
            Divider(),
            Section(Kmarkdown('**收益曲线**\n用法: <角色名>收益曲线')),
            Divider(),
            Section(Kmarkdown('**参考面板**\n用法: <角色名>参考面板')),
            Divider(),
            ActionGroup(
                MainPanel().get_button(ThemeTypes.DANGER)
            ),
            Divider(),
            Context(Kmarkdown(f'当前小派蒙版本: **{VERSION}**'))
        ))

    @staticmethod
    def panel_id() -> str:
        return 'genshin_wiki_panel'


class PaimonBindPanel(ClickablePanel):

    @staticmethod
    def name() -> str:
        return '原神绑定'

    @staticmethod
    def get_panel() -> CardMessage:
        return CardMessage(Card(
            Header('原神绑定相关命令'),
            Section(Kmarkdown('**原神绑定**\n用法: !!原神绑定 [cookie]')),
            Section(Kmarkdown('也可以使用网页来绑定（如果功能开启了）'),
                    accessory=Button(PlainText('访问'), value=f'http://{config.public_ip}:{config.web_app_port}',
                                     click='link')),
            Divider(),
            Section(Kmarkdown('**查询绑定**\n用法: !!查询绑定')),
            Divider(),
            ActionGroup(
                MainPanel().get_button(ThemeTypes.DANGER)
            ),
            Divider(),
            Context(Kmarkdown(f'当前小派蒙版本: **{VERSION}**'))

        ))

    @staticmethod
    def panel_id() -> str:
        return 'paimon_bind_panel'


class AdminPanel(ClickablePanel):

    @staticmethod
    def name() -> str:
        return '管理员命令'

    @staticmethod
    def get_panel() -> CardMessage:
        return CardMessage(Card(
            Header('管理员命令'),
            Section(Kmarkdown('**校验所有cookie**\n用法: !!校验所有cookie')),
            Divider(),
            Section(Kmarkdown('**添加公共cookie**\n用法: !!添加公共cookie [cookie]')),
            Divider(),
            Section(Kmarkdown('**服务器列表**\n用法: !!服务器列表')),
            Divider(),
            Section(Kmarkdown('**公告**\n用法: !!公告 [公告内容]')),
            Divider(),
            ActionGroup(
                MainPanel().get_button(ThemeTypes.DANGER)
            ),
            Divider(),
            Context(Kmarkdown(f'当前小派蒙版本: **{VERSION}**'))
        ))

    @staticmethod
    def panel_id() -> str:
        return 'admin_panel'


class AIVoicePanel(ClickablePanel):

    @staticmethod
    def name() -> str:
        return 'AI语音'

    @staticmethod
    def get_panel() -> CardMessage:
        return CardMessage(Card(
            Header('AI语音命令'),
            Section(Kmarkdown('**AI语音**\n!!AI语音 [文字] [角色] <noise> <length>\n'
                              '其中 `<>` 中的是可选参数\n'
                              '**参数说明**\n'
                              '**noise**: 可用于控制感情等变化程度。 默认值：**0.667**\n'
                              '**length**: 可用于控制整体语速。 默认值：**1.2**\n'
                              '---\n'
                              '这些参数可以自行组合，找到合适的效果')),
            Divider(),
            ActionGroup(
                MainPanel().get_button(ThemeTypes.DANGER)
            ),
            Divider(),
            Context(Kmarkdown(f'当前小派蒙版本: **{VERSION}**'))
        ))

    @staticmethod
    def panel_id() -> str:
        return 'ai_voice_panel'
