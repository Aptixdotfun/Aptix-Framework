
import re
from . import HandlerFilter
from Aptixbot.core.platform.Aptix_message_event import AptixMessageEvent
from Aptixbot.core.config import AptixBotConfig

# 正则表达式过滤器不会受到 wake_prefix 的制约。
class RegexFilter(HandlerFilter):
    '''正则表达式过滤器'''
    def __init__(self, regex: str):
        self.regex_str = regex
        self.regex = re.compile(regex)
        
    def filter(self, event: AptixMessageEvent, cfg: AptixBotConfig) -> bool:
        return bool(self.regex.match(event.get_message_str().strip()))