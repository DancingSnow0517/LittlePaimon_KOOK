from khl import User
from khl_card import CardMessage, Card, Section, Kmarkdown, Image


def text_avatar(text: str, author: User) -> CardMessage:
    return CardMessage(
        Card(
            Section(Kmarkdown(text), accessory=Image(author.avatar), mode='left')
        )
    )
