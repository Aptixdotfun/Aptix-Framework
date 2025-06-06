import asyncio
from asyncio import Queue
from Aptixbot.core.pipeline.scheduler import PipelineScheduler
from Aptixbot.core import logger
from .platform import AptixMessageEvent

class EventBus:
    def __init__(self, event_queue: Queue, pipeline_scheduler: PipelineScheduler):
        self.event_queue = event_queue
        self.pipeline_scheduler = pipeline_scheduler

    async def dispatch(self):
        logger.info("事件总线已打开。")
        while True:
            event: AptixMessageEvent = await self.event_queue.get()
            self._print_event(event)
            asyncio.create_task(self.pipeline_scheduler.execute(event))
            
    def _print_event(self, event: AptixMessageEvent):        
        if event.get_sender_name():
            logger.info(f"[{event.get_platform_name()}] {event.get_sender_name()}/{event.get_sender_id()}: {event.get_message_outline()}")
        else:
            logger.info(f"[{event.get_platform_name()}] {event.get_sender_id()}: {event.get_message_outline()}")