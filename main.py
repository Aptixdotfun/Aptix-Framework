import os
import asyncio
import sys
import mimetypes
from Aptixbot.dashboard import AptixBotDashBoardLifecycle
from Aptixbot.core import db_helper
from Aptixbot.core import logger, LogManager, LogBroker
from Aptixbot.core.config.default import VERSION
from Aptixbot.core.utils.io import download_dashboard, get_dashboard_version

# add parent path to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ASCII art logo for Aptix Framework
logo_tmpl = r"""
     ___           _______..___________. __     __   __  
    /   \         /       ||           ||  |   |  | |  | 
   /  ^  \       |   (----``---|  |----`|  |   |  | |  | 
  /  /_\  \       \   \        |  |     |  |   |  | |  | 
 /  _____  \  .----)   |       |  |     |  `---'  | |  | 
/__/     \__\ |_______/        |__|      \______/  |__| 
                                                       
"""

def check_env():
    if not (sys.version_info.major == 3 and sys.version_info.minor >= 10):
        logger.error("Please use Python 3.10+ to run this project.")
        exit()
        
    os.makedirs("data/config", exist_ok=True)
    os.makedirs("data/plugins", exist_ok=True)
    os.makedirs("data/temp", exist_ok=True)

    # workaround for issue #181
    mimetypes.add_type("text/javascript", ".js") 
    mimetypes.add_type("text/javascript", ".mjs")
    mimetypes.add_type("application/json", ".json")
    
async def check_dashboard_files():
    '''Download dashboard files'''

    v = await get_dashboard_version()
    if v is not None:
        # has file
        if v == f"v{VERSION}":
            logger.info("Dashboard files are up to date.")
        else:
            logger.warning("Dashboard update detected. Use /dashboard_update command to update.")
        return
    
    logger.info("Starting to download dashboard files... This may be slower during peak hours (evenings). If download fails multiple times, please visit https://github.com/Aptix/AptixBot/releases/latest to download dist.zip, and extract the dist folder to the data directory.")
    
    try:
        await download_dashboard()
    except Exception as e:
        logger.critical(f"Failed to download dashboard files: {e}")
        return

    logger.info("Dashboard download completed successfully.")

if __name__ == "__main__":
    check_env()
    
    # start log broker with secure configuration
    log_broker = LogBroker()
    LogManager.set_queue_handler(logger, log_broker)
    
    # check dashboard files
    asyncio.run(check_dashboard_files())
    
    db = db_helper
    
    # print logo
    logger.info(logo_tmpl)
    
    dashboard_lifecycle = AptixBotDashBoardLifecycle(db, log_broker)
    asyncio.run(dashboard_lifecycle.start())