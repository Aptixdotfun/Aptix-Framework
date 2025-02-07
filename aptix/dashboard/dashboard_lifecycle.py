import asyncio
import traceback
from Aptixbot.core import logger
from Aptixbot.core.core_lifecycle import AptixBotCoreLifecycle
from .server import AptixBotDashboard
from Aptixbot.core.db import BaseDatabase
from Aptixbot.core import LogBroker
class AptixBotDashBoardLifecycle:
    def __init__(self, db: BaseDatabase, log_broker: LogBroker):
        self.db = db
        self.logger = logger
        self.log_broker = log_broker
        self.dashboard_server = None
        
    async def start(self):
        core_lifecycle = AptixBotCoreLifecycle(self.log_broker, self.db)
        
        core_task = []
        try:
            await core_lifecycle.initialize()
            core_task = core_lifecycle.start()
        except Exception as e:
            logger.critical(f"初始化 AptixBot 失败：{e} !!!!!!!")
            logger.critical(f"初始化 AptixBot 失败：{e} !!!!!!!")
            logger.critical(f"初始化 AptixBot 失败：{e} !!!!!!!")
        
        self.dashboard_server = AptixBotDashboard(core_lifecycle, self.db)
        task = asyncio.gather(core_task, self.dashboard_server.run())
        
        try:
            await task
        except asyncio.CancelledError:
            logger.info("🌈 正在关闭 AptixBot...")
            await core_lifecycle.stop()