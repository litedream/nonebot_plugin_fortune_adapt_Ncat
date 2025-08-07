from typing import override

from ncatbot.core import BaseMessage, GroupMessage, MessageChain
from ncatbot.utils import get_log

from module.Handler.message import messageHandler
from . import nonebot_plugin_fortune
from ncatbot.plugin.base_plugin import BasePlugin

logger = get_log()

class FortunePlugin(BasePlugin):
    name = "fortune"
    version = "0.0.1"

    @override
    async def on_load(self):
        await nonebot_plugin_fortune.fortune_check(self.data.get("config", {}))
        self.add_scheduled_task(interval="00:00", job_func=nonebot_plugin_fortune.cleanOutPics, name="cleanOutPics")

@messageHandler.on_message(r"^/(今日运势|抽签|运势)$")
async def userCommand(msg: BaseMessage):
    if isinstance(msg, GroupMessage):
        resp = await nonebot_plugin_fortune.generalDivine(msg.raw_message, str(msg.group_id), str(msg.user_id))
        if isinstance(resp, str):
            await msg.reply(resp)
        elif isinstance(resp, MessageChain):
            await msg.api.post_group_msg(msg.group_id, rtf=resp)
        return
    logger.warn("非群聊消息，无法使用今日运势功能")