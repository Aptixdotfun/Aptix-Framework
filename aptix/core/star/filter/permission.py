import enum
from . import HandlerFilter
from Aptixbot.core.platform.Aptix_message_event import AptixMessageEvent
from Aptixbot.core.config import AptixBotConfig

class PermissionType(enum.Flag):
    '''权限类型。当选择 MEMBER，ADMIN 也可以通过。
    '''
    ADMIN = enum.auto()
    MEMBER = enum.auto()

class PermissionTypeFilter(HandlerFilter):
    def __init__(self, permission_type: PermissionType, raise_error: bool = True):
        self.permission_type = permission_type
        self.raise_error = raise_error
        
    def filter(self, event: AptixMessageEvent, cfg: AptixBotConfig) -> bool:
        '''过滤器
        '''
        if self.permission_type == PermissionType.ADMIN:
            if not event.is_admin():
                # event.stop_event()
                # raise ValueError(f"您 (ID: {event.get_sender_id()}) 没有权限操作管理员指令。")
                return False

        return True
