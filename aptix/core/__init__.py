import os
import asyncio
from .log import LogManager, LogBroker
from Aptixbot.core.utils.t2i.renderer import HtmlRenderer
from Aptixbot.core.utils.shared_preferences import SharedPreferences
from Aptixbot.core.utils.pip_installer import PipInstaller
from Aptixbot.core.db.sqlite import SQLiteDatabase
from Aptixbot.core.config.default import DB_PATH
from Aptixbot.core.config import AptixBotConfig

os.makedirs("data", exist_ok=True)

Aptixbot_config = AptixBotConfig()
t2i_base_url = Aptixbot_config.get('t2i_endpoint', 'https://t2i.Aptix.top/text2img')
html_renderer = HtmlRenderer(t2i_base_url)
logger = LogManager.GetLogger(log_name='Aptixbot')

if os.environ.get('TESTING', ""):
    logger.setLevel('DEBUG')
    
db_helper = SQLiteDatabase(DB_PATH)
sp = SharedPreferences() # 简单的偏好设置存储
pip_installer = PipInstaller(Aptixbot_config.get('pip_install_arg', ''))
web_chat_queue = asyncio.Queue(maxsize=32)
web_chat_back_queue = asyncio.Queue(maxsize=32)
WEBUI_SK = "Advanced_System_for_Text_Response_and_Bot_Operations_Tool"
