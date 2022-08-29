import json
from typing import Union

from khl import Gateway, api


async def update_message(content: Union, msg_id: str, user_id: str, gate: Gateway):
    content = content if isinstance(content, str) else json.dumps(content)
    await gate.exec_req(api.Message.update(msg_id=msg_id, content=content, temp_target_id=user_id))


async def update_private_message(content: Union, msg_id: str, gate: Gateway):
    content = content if isinstance(content, str) else json.dumps(content)
    await gate.exec_req(api.DirectMessage.update(msg_id=msg_id, content=content))
