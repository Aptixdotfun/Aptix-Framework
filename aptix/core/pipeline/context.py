from dataclasses import dataclass
from Aptixbot.core.config.Aptixbot_config import AptixBotConfig
from Aptixbot.core.star import PluginManager

@dataclass
class PipelineContext:
    Aptixbot_config: AptixBotConfig
    plugin_manager: PluginManager