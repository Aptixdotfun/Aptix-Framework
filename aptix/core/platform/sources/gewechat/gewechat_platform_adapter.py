import sys
import asyncio
import os

from Aptixbot.api.platform import Platform, AptixBotMessage, MessageType, PlatformMetadata
from Aptixbot.api.event import MessageChain
from Aptixbot.api import logger
from Aptixbot.core.platform.Aptix_message_event import MessageSesion
from ...register import register_platform_adapter
from .gewechat_event import GewechatPlatformEvent
from .client import SimpleGewechatClient
from Aptixbot.core.message.components import Plain

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override
            

@register_platform_adapter("gewechat", "基于 gewechat 的 Wechat 适配器")
class GewechatPlatformAdapter(Platform):

    def __init__(self, platform_config: dict, platform_settings: dict, event_queue: asyncio.Queue) -> None:
        super().__init__(event_queue)
        self.config = platform_config
        self.settingss = platform_settings
        self.test_mode = os.environ.get('TEST_MODE', 'off') == 'on'
        self.client = None
    
    @override
    async def send_by_session(self, session: MessageSesion, message_chain: MessageChain):
        to_wxid = session.session_id
        if "_" in to_wxid:
            # 群聊，开启了独立会话
            _, to_wxid = to_wxid.split("_")
        
        if not to_wxid:
            logger.error("无法获取到 to_wxid。")
            return
        
        for comp in message_chain.chain:
            if isinstance(comp, Plain):
                await self.client.post_text(to_wxid, comp.text)

        await super().send_by_session(session, message_chain)
    
    @override
    def meta(self) -> PlatformMetadata:
        return PlatformMetadata(
            "gewechat",
            "基于 gewechat 的 Wechat 适配器",
        )

    @override
    def run(self):
        self.client = SimpleGewechatClient(
            self.config['base_url'],
            self.config['nickname'],
            self.config['host'],
            self.config['port'],
            self._event_queue,
        )
        
        async def on_event_received(abm: AptixBotMessage):
            await self.handle_msg(abm)
            
        self.client.on_event_received = on_event_received
        
        return self._run()
    
    async def logout(self):
        await self.client.logout()
    
    async def _run(self):
        await self.client.login()
        
        await self.client.start_polling()
        
    
    async def handle_msg(self, message: AptixBotMessage):
        if message.type == MessageType.GROUP_MESSAGE:
            if self.settingss['unique_session']:
                message.session_id = message.sender.user_id + "_" + message.group_id
        
        message_event = GewechatPlatformEvent(
            message_str=message.message_str,
            message_obj=message,
            platform_meta=self.meta(),
            session_id=message.session_id,
            client=self.client
        )
        
        self.commit_event(message_event)