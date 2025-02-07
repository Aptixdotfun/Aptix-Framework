import enum
from . import HandlerFilter
from Aptixbot.core.platform.Aptix_message_event import AptixMessageEvent
from Aptixbot.core.config import AptixBotConfig
from typing import Union

class PlatformAdapterType(enum.Flag):
    AIOCQHTTP = enum.auto()
    QQOFFICIAL = enum.auto()
    VCHAT = enum.auto()
    GEWECHAT = enum.auto()
    ALL = AIOCQHTTP | QQOFFICIAL | VCHAT | GEWECHAT
    
ADAPTER_NAME_2_TYPE = {
    "aiocqhttp": PlatformAdapterType.AIOCQHTTP,
    "qq_official": PlatformAdapterType.QQOFFICIAL,
    "vchat": PlatformAdapterType.VCHAT,
    "gewechat": PlatformAdapterType.GEWECHAT
}

class PlatformAdapterTypeFilter(HandlerFilter):
    def __init__(self, platform_adapter_type_or_str: Union[PlatformAdapterType, str]):
        self.type_or_str = platform_adapter_type_or_str
        
    def filter(self, event: AptixMessageEvent, cfg: AptixBotConfig) -> bool:
        adapter_name = event.get_platform_name()
        if adapter_name in ADAPTER_NAME_2_TYPE:
            return ADAPTER_NAME_2_TYPE[adapter_name] & self.type_or_str
        return False