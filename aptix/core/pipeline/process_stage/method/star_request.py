'''
本地 Agent 模式的 AptixBot 插件调用 Stage
'''
from ...context import PipelineContext
from ..stage import Stage
from typing import Dict, Any, List, AsyncGenerator, Union
from Aptixbot.core.platform.Aptix_message_event import AptixMessageEvent
from Aptixbot.core.message.message_event_result import MessageEventResult
from Aptixbot.core import logger
from Aptixbot.core.star.star_handler import StarHandlerMetadata
from Aptixbot.core.star.star import star_map
import traceback

class StarRequestSubStage(Stage):
    
    async def initialize(self, ctx: PipelineContext) -> None:
        self.curr_provider = ctx.plugin_manager.context.get_using_provider()
        self.prompt_prefix = ctx.Aptixbot_config['provider_settings']['prompt_prefix']
        self.identifier = ctx.Aptixbot_config['provider_settings']['identifier']
        self.ctx = ctx
        
    async def process(self, event: AptixMessageEvent) -> Union[None, AsyncGenerator[None, None]]:
        activated_handlers: List[StarHandlerMetadata] = event.get_extra("activated_handlers")
        handlers_parsed_params: Dict[str, Dict[str, Any]] = event.get_extra("handlers_parsed_params")
        if not handlers_parsed_params:
            handlers_parsed_params = {}
        for handler in activated_handlers:
            params = handlers_parsed_params.get(handler.handler_full_name, {})
            try:
                if handler.handler_module_path not in star_map:
                    # 孤立无援的 star handler 
                    continue
                
                logger.debug(f"执行 Star Handler {handler.handler_full_name}")
                wrapper = self._call_handler(self.ctx, event, handler.handler, **params)
                async for ret in wrapper:
                    yield ret
                event.clear_result() # 清除上一个 handler 的结果
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(f"Star {handler.handler_full_name} handle error: {e}")
                
                if event.is_at_or_wake_command:
                    ret = f":(\n\n在调用插件 {star_map.get(handler.handler_module_path).name} 的处理函数 {handler.handler_name} 时出现异常：{e}"
                    event.set_result(MessageEventResult().message(ret))
                    yield
                    event.clear_result()
                
                event.stop_event()