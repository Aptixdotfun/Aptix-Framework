import abc
from Aptixbot.core.platform.message_type import MessageType
from Aptixbot.core.platform.Aptix_message_event import AptixMessageEvent
from Aptixbot.core.config import AptixBotConfig

class HandlerFilter(abc.ABC):
    @abc.abstractmethod
    def filter(self, event: AptixMessageEvent, cfg: AptixBotConfig) -> bool:
        '''是否应当被过滤'''
        raise NotImplementedError
