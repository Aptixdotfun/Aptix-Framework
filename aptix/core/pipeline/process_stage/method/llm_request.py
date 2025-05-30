'''
本地 Agent 模式的 LLM 调用 Stage
'''
import traceback
import json
from typing import Union, AsyncGenerator
from ...context import PipelineContext
from ..stage import Stage
from Aptixbot.core.platform.Aptix_message_event import AptixMessageEvent
from Aptixbot.core.message.message_event_result import MessageEventResult, ResultContentType
from Aptixbot.core.message.components import Image
from Aptixbot.core import logger
from Aptixbot.core.utils.metrics import Metric
from Aptixbot.core.provider.entites import ProviderRequest, LLMResponse
from Aptixbot.core.star.star_handler import star_handlers_registry, EventType

class LLMRequestSubStage(Stage):
    
    async def initialize(self, ctx: PipelineContext) -> None:
        self.ctx = ctx
        self.bot_wake_prefixs = ctx.Aptixbot_config['wake_prefix'] # list
        self.provider_wake_prefix = ctx.Aptixbot_config['provider_settings']['wake_prefix'] # str
        
        for bwp in self.bot_wake_prefixs:
            if self.provider_wake_prefix.startswith(bwp):
                logger.info(f"识别 LLM 聊天额外唤醒前缀 {self.provider_wake_prefix} 以机器人唤醒前缀 {bwp} 开头，已自动去除。")
                self.provider_wake_prefix = self.provider_wake_prefix[len(bwp):]
                
        self.conv_manager = ctx.plugin_manager.context.conversation_manager
        
    async def process(self, event: AptixMessageEvent, _nested: bool = False) -> Union[None, AsyncGenerator[None, None]]:
        req: ProviderRequest = None
        
        provider = self.ctx.plugin_manager.context.get_using_provider()
        if provider is None:
            return
        
        if event.get_extra("provider_request"):
            req = event.get_extra("provider_request")
            assert isinstance(req, ProviderRequest), "provider_request 必须是 ProviderRequest 类型。"
        else:
            req = ProviderRequest(prompt="", image_urls=[])
            if self.provider_wake_prefix:
                if not event.message_str.startswith(self.provider_wake_prefix):
                    return
            req.prompt = event.message_str[len(self.provider_wake_prefix):]
            req.func_tool = self.ctx.plugin_manager.context.get_llm_tool_manager()
            for comp in event.message_obj.message:
                if isinstance(comp, Image):
                    image_url = comp.url if comp.url else comp.file
                    req.image_urls.append(image_url)
            
            # 获取对话上下文
            conversation_id = await self.conv_manager.get_curr_conversation_id(event.unified_msg_origin)
            if not conversation_id:
                conversation_id = await self.conv_manager.new_conversation(event.unified_msg_origin)
            req.session_id = conversation_id
            conversation = await self.conv_manager.get_conversation(event.unified_msg_origin, conversation_id)
            req.conversation = conversation
            req.contexts = json.loads(conversation.history)

            event.set_extra("provider_request", req)
            
        if not req.prompt and not req.image_urls:
            return
            
        # 执行请求 LLM 前事件。
        # 装饰 system_prompt 等功能
        handlers = star_handlers_registry.get_handlers_by_event_type(EventType.OnLLMRequestEvent)
        for handler in handlers:
            try:
                await handler.handler(event, req)
            except BaseException:
                logger.error(traceback.format_exc())
                
        if isinstance(req.contexts, str):
            req.contexts = json.loads(req.contexts)
        
        try:
            logger.debug(f"提供商请求 Payload: {req}")
            if _nested:
                req.func_tool = None # 暂时不支持递归工具调用
            llm_response = await provider.text_chat(**req.__dict__) # 请求 LLM
            
            # 执行 LLM 响应后的事件。
            handlers = star_handlers_registry.get_handlers_by_event_type(EventType.OnLLMResponseEvent)
            for handler in handlers:
                try:
                    await handler.handler(event, llm_response)
                except BaseException:
                    logger.error(traceback.format_exc())
            
            # 保存到历史记录
            await self._save_to_history(event, req, llm_response)
            
            await Metric.upload(llm_tick=1, model_name=provider.get_model(), provider_type=provider.meta().type)

            if llm_response.role == 'assistant':
                # text completion
                event.set_result(MessageEventResult().message(llm_response.completion_text)
                                 .set_result_content_type(ResultContentType.LLM_RESULT))
            elif llm_response.role == 'err':
                event.set_result(MessageEventResult().message(f"AptixBot 请求失败。\n错误信息: {llm_response.completion_text}"))
            elif llm_response.role == 'tool':
                # function calling
                function_calling_result = {}
                for func_tool_name, func_tool_args in zip(llm_response.tools_call_name, llm_response.tools_call_args):
                    func_tool = req.func_tool.get_func(func_tool_name)
                    logger.info(f"调用工具函数：{func_tool_name}，参数：{func_tool_args}")
                    try:
                        # 尝试调用工具函数
                        wrapper = self._call_handler(self.ctx, event, func_tool.handler, **func_tool_args)
                        async for resp in wrapper:
                            if resp is not None:
                                function_calling_result[func_tool_name] = resp
                            else:
                                yield
                        event.clear_result() # 清除上一个 handler 的结果
                    except BaseException as e:
                        logger.warning(traceback.format_exc())
                        function_calling_result[func_tool_name] = "When calling the function, an error occurred: " + str(e)
                if function_calling_result:
                    # 工具返回 LLM 资源。比如 RAG、网页 得到的相关结果等。
                    # 我们重新执行一遍这个 stage
                    req.func_tool = None # 暂时不支持递归工具调用
                    extra_prompt = "\n\nSystem executed some external tools for this task and here are the results:\n"
                    for tool_name, tool_result in function_calling_result.items():
                        extra_prompt += f"Tool: {tool_name}\nTool Result: {tool_result}\n"
                    req.prompt += extra_prompt
                    async for _ in self.process(event, _nested=True):
                        yield
                else:
                    if llm_response.completion_text:
                        event.set_result(MessageEventResult().message(llm_response.completion_text))

        except BaseException as e:
            logger.error(traceback.format_exc())
            event.set_result(MessageEventResult().message(f"AptixBot 请求失败。\n错误类型: {type(e).__name__}\n错误信息: {str(e)}"))
            return
        
    async def _save_to_history(self, event: AptixMessageEvent, req: ProviderRequest, llm_response: LLMResponse):
        if llm_response.role == "assistant":
            # 文本回复
            contexts = req.contexts
            new_record = {
                "role": "user",
                "content": req.prompt
            }
            contexts.append(new_record)
            contexts.append({
                "role": "assistant",
                "content": llm_response.completion_text
            })
            contexts_to_save = list(filter(lambda item: '_no_save' not in item, contexts))
            await self.conv_manager.update_conversation(
                event.unified_msg_origin, 
                req.session_id, 
                history=contexts_to_save
            )