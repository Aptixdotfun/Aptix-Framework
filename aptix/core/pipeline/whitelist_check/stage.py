from ..stage import Stage, register_stage
from ..context import PipelineContext
from typing import AsyncGenerator, Union
from Aptixbot.core.platform.Aptix_message_event import AptixMessageEvent
from Aptixbot.core.platform.message_type import MessageType
from Aptixbot.core import logger

@register_stage
class WhitelistCheckStage(Stage):
    '''检查是否在群聊/私聊白名单
    '''
    async def initialize(self, ctx: PipelineContext) -> None:
        self.enable_whitelist_check = ctx.Aptixbot_config['platform_settings']['enable_id_white_list']
        self.whitelist = ctx.Aptixbot_config['platform_settings']['id_whitelist']
        self.wl_ignore_admin_on_group = ctx.Aptixbot_config['platform_settings']['wl_ignore_admin_on_group']
        self.wl_ignore_admin_on_friend = ctx.Aptixbot_config['platform_settings']['wl_ignore_admin_on_friend']    
        self.wl_log = ctx.Aptixbot_config['platform_settings']['id_whitelist_log']
        
    async def process(self, event: AptixMessageEvent) -> Union[None, AsyncGenerator[None, None]]:
        if not self.enable_whitelist_check:
            # 白名单检查未启用
            return
        
        if len(self.whitelist) == 0:
            # 白名单为空，不检查
            return
        
        if event.get_platform_name() == 'webchat':
            # WebChat 豁免
            return
        
        # 检查是否在白名单
        if self.wl_ignore_admin_on_group:
            if event.role == 'admin' and event.get_message_type() == MessageType.GROUP_MESSAGE:
                return
        if self.wl_ignore_admin_on_friend:
            if event.role == 'admin' and event.get_message_type() == MessageType.FRIEND_MESSAGE:
                return
        if event.unified_msg_origin not in self.whitelist:
            if self.wl_log:
                logger.info(f"会话 ID {event.unified_msg_origin} 不在会话白名单中，已终止事件传播。请在配置文件中添加该会话 ID 到白名单。")
            event.stop_event()