import time
import re
import traceback
from typing import Union, AsyncGenerator
from ..stage import register_stage
from ..context import PipelineContext
from Aptixbot.core.platform.Aptix_message_event import AptixMessageEvent
from Aptixbot.core.platform.message_type import MessageType
from Aptixbot.core import logger
from Aptixbot.core.message.components import Plain, Image, At, Reply, Record
from Aptixbot.core import html_renderer
from Aptixbot.core.star.star_handler import star_handlers_registry, EventType

@register_stage
class ResultDecorateStage:
    async def initialize(self, ctx: PipelineContext):
        self.ctx = ctx
        self.reply_prefix = ctx.Aptixbot_config['platform_settings']['reply_prefix']
        self.reply_with_mention = ctx.Aptixbot_config['platform_settings']['reply_with_mention']
        self.reply_with_quote = ctx.Aptixbot_config['platform_settings']['reply_with_quote']
        self.use_tts = ctx.Aptixbot_config['provider_tts_settings']['enable']
        self.t2i_word_threshold = ctx.Aptixbot_config['t2i_word_threshold']
        try:
            self.t2i_word_threshold = int(self.t2i_word_threshold)
            if self.t2i_word_threshold < 50:
                self.t2i_word_threshold = 50
        except BaseException:
            self.t2i_word_threshold = 150
        
        # 分段回复
        self.enable_segmented_reply = ctx.Aptixbot_config['platform_settings']['segmented_reply']['enable']
        self.only_llm_result = ctx.Aptixbot_config['platform_settings']['segmented_reply']['only_llm_result']
        self.seg_prompt = ctx.Aptixbot_config['platform_settings']['segmented_reply']['seg_prompt']
        self.regex = ctx.Aptixbot_config['platform_settings']['segmented_reply']['regex']

    async def process(self, event: AptixMessageEvent) -> Union[None, AsyncGenerator[None, None]]:
        result = event.get_result()
        if result is None:
            return
        
        handlers = star_handlers_registry.get_handlers_by_event_type(EventType.OnDecoratingResultEvent)
        for handler in handlers:
            # TODO: 如何让这里的 handler 也能使用 LLM 能力。也许需要将 LLMRequestSubStage 提取出来。
            await handler.handler(event)
        
        if len(result.chain) > 0:
            # 回复前缀
            if self.reply_prefix:
                for comp in result.chain:
                    if isinstance(comp, Plain):
                        comp.text = self.reply_prefix + comp.text
                        break
            
             # 分段回复 
            if self.enable_segmented_reply:
                if (self.only_llm_result and result.is_llm_result()) or not self.only_llm_result:
                    new_chain = []
                    for comp in result.chain:
                        if isinstance(comp, Plain):
                            
                            if self.seg_prompt:
                                try:
                                    llm_resp = await self.ctx.plugin_manager.context.get_using_provider().text_chat(
                                        prompt=f"{self.seg_prompt}\n{comp.text}",
                                    )
                                    comp.text = llm_resp.completion_text
                                except BaseException as e:
                                    traceback.print_exc()
                                    logger.warning("使用 LLM 分段回复失败。将不分段回复。： " + str(e))
                                    new_chain.append(comp)
                                    continue
                            
                            split_response = re.findall(self.regex, comp.text)
                            if not split_response:
                                new_chain.append(comp)
                                continue
                            for seg in split_response:
                                if seg:
                                    new_chain.append(Plain(seg))
                        else:
                            # 非 Plain 类型的消息段不分段
                            new_chain.append(comp)
                    result.chain = new_chain
                
            # TTS
            if self.use_tts and result.is_llm_result():
                tts_provider = self.ctx.plugin_manager.context.provider_manager.curr_tts_provider_inst
                new_chain = []
                for comp in result.chain:
                    if isinstance(comp, Plain) and len(comp.text) > 1:
                        try:
                            logger.info("TTS 请求: " + comp.text)
                            audio_path = await tts_provider.get_audio(comp.text)
                            logger.info("TTS 结果: " + audio_path)
                            if audio_path:
                                new_chain.append(Record(file=audio_path, url=audio_path))
                            else:
                                logger.error(f"由于 TTS 音频文件没找到，消息段转语音失败: {comp.text}")
                                new_chain.append(comp)
                        except BaseException:
                            traceback.print_exc()
                            logger.error("TTS 失败，使用文本发送。")
                            new_chain.append(comp)
                    else:
                        new_chain.append(comp)
                result.chain = new_chain
            
            # 文本转图片
            elif (result.use_t2i_ is None and self.ctx.Aptixbot_config['t2i']) or result.use_t2i_:
                plain_str = ""
                for comp in result.chain:
                    if isinstance(comp, Plain):
                        plain_str += "\n\n" + comp.text
                    else:
                        break
                if plain_str and len(plain_str) > self.t2i_word_threshold:
                    render_start = time.time()
                    try:
                        url = await html_renderer.render_t2i(plain_str, return_url=True)
                    except BaseException:
                        logger.error("文本转图片失败，使用文本发送。")
                        return
                    if time.time() - render_start > 3:
                        logger.warning("文本转图片耗时超过了 3 秒，如果觉得很慢可以使用 /t2i 关闭文本转图片模式。")
                    if url:
                        result.chain = [Image.fromURL(url)]
            
            # at 回复
            if self.reply_with_mention and event.get_message_type() != MessageType.FRIEND_MESSAGE:
                result.chain.insert(0, At(qq=event.get_sender_id(), name=event.get_sender_name()))
                if len(result.chain) > 1 and isinstance(result.chain[1], Plain):
                    result.chain[1].text = "\n" + result.chain[1].text
            
            # 引用回复
            if self.reply_with_quote:
                result.chain.insert(0, Reply(id=event.message_obj.message_id))