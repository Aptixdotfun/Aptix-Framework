from .route import Route, Response, RouteContext
from quart import request
from Aptixbot.core.config.default import CONFIG_METADATA_2, DEFAULT_VALUE_MAP
from Aptixbot.core.config.Aptixbot_config import AptixBotConfig
from Aptixbot.core.core_lifecycle import AptixBotCoreLifecycle
from Aptixbot.core.platform.register import platform_registry
from Aptixbot.core.provider.register import provider_registry
from Aptixbot.core.star.star import star_registry
from Aptixbot.core import logger

def try_cast(value: str, type_: str):
    if type_ == "int" and value.isdigit():
        return int(value)
    elif type_ == "float" and isinstance(value, str) \
        and value.replace(".", "", 1).isdigit():
        return float(value)
    elif type_ == "float" and isinstance(value, int):
        return float(value)

def validate_config(data, schema: dict, is_core: bool):
    errors = []
    def validate(data, metadata=schema, path=""):
        for key, meta in metadata.items():
            if key not in data:
                continue
            value = data[key]
            # null 转换
            if value is None:
                data[key] = DEFAULT_VALUE_MAP(meta["type"])
                continue
            # 递归验证
            if meta["type"] == "list" and isinstance(value, list):
                for item in value:
                    validate(item, meta["items"], path=f"{path}{key}.")
            elif meta["type"] == "object" and isinstance(value, dict):
                validate(value, meta["items"], path=f"{path}{key}.")

            if meta["type"] == "int" and not isinstance(value, int):
                casted = try_cast(value, "int")
                if casted is None:
                    errors.append(f"错误的类型 {path}{key}: 期望是 int, 得到了 {type(value).__name__}")
                data[key] = casted
            elif meta["type"] == "float" and not isinstance(value, float):
                casted = try_cast(value, "float")
                if casted is None:
                    errors.append(f"错误的类型 {path}{key}: 期望是 float, 得到了 {type(value).__name__}")
                data[key] = casted
            elif meta["type"] == "bool" and not isinstance(value, bool):
                errors.append(f"错误的类型 {path}{key}: 期望是 bool, 得到了 {type(value).__name__}")
            elif meta["type"] in ["string", "text"] and not isinstance(value, str):
                errors.append(f"错误的类型 {path}{key}: 期望是 string, 得到了 {type(value).__name__}")
            elif meta["type"] == "list" and not isinstance(value, list):
                errors.append(f"错误的类型 {path}{key}: 期望是 list, 得到了 {type(value).__name__}")
            elif meta["type"] == "object" and not isinstance(value, dict):
                errors.append(f"错误的类型 {path}{key}: 期望是 dict, 得到了 {type(value).__name__}")
                validate(value, meta["items"], path=f"{path}{key}.")

    if is_core:
        for key, group in schema.items():
            group_meta = group.get("metadata")
            if not group_meta:
                continue
            logger.info(f"验证配置: 组 {key} ...")
            validate(data, group_meta, path=f"{key}.")
    else:
        validate(data, schema)
    
    return errors

def save_config(post_config: dict, config: AptixBotConfig, is_core: bool = False):
    '''验证并保存配置'''
    errors = None
    try:
        if is_core:
            errors = validate_config(post_config, CONFIG_METADATA_2, is_core)
        else:
            errors = validate_config(post_config, config.schema, is_core)
    except BaseException as e:
        logger.warning(f"验证配置时出现异常: {e}")
    if errors:
        raise ValueError(f"格式校验未通过: {errors}")
    config.save_config(post_config)
    
class ConfigRoute(Route):
    def __init__(self, context: RouteContext, core_lifecycle: AptixBotCoreLifecycle) -> None:
        super().__init__(context)
        self.core_lifecycle = core_lifecycle
        self.routes = {
            '/config/get': ('GET', self.get_configs),
            '/config/Aptixbot/update': ('POST', self.post_Aptixbot_configs),
            '/config/plugin/update': ('POST', self.post_plugin_configs),
        }
        self.register_routes()

    async def get_configs(self):
        # plugin_name 为空时返回 AptixBot 配置
        # 否则返回指定 plugin_name 的插件配置
        plugin_name = request.args.get("plugin_name", None)
        if not plugin_name:
            return Response().ok(await self._get_Aptixbot_config()).__dict__
        return Response().ok(await self._get_plugin_config(plugin_name)).__dict__

    async def post_Aptixbot_configs(self):
        post_configs = await request.json
        try:
            await self._save_Aptixbot_configs(post_configs)
            return Response().ok(None, "保存成功~ 机器人正在重载配置。").__dict__
        except Exception as e:
            logger.error(e)
            return Response().error(str(e)).__dict__
    
    async def post_plugin_configs(self):
        post_configs = await request.json
        plugin_name = request.args.get("plugin_name", "unknown")
        try:
            await self._save_plugin_configs(post_configs, plugin_name)
            return Response().ok(None, f"保存插件 {plugin_name} 成功~ 机器人正在重载配置。").__dict__
        except Exception as e:
            return Response().error(str(e)).__dict__
            
    async def _get_Aptixbot_config(self):
        config = self.config
        
        # 平台适配器的默认配置模板注入
        platform_default_tmpl = CONFIG_METADATA_2['platform_group']['metadata']['platform']['config_template']
        for platform in platform_registry:
            if platform.default_config_tmpl:
                platform_default_tmpl[platform.name] = platform.default_config_tmpl
        
        # 服务提供商的默认配置模板注入
        provider_default_tmpl = CONFIG_METADATA_2['provider_group']['metadata']['provider']['config_template']
        for provider in provider_registry:
            if provider.default_config_tmpl:
                provider_default_tmpl[provider.type] = provider.default_config_tmpl
        
        return {
            "metadata": CONFIG_METADATA_2,
            "config": config
        }

    async def _get_plugin_config(self, plugin_name: str):
        ret = {
            "metadata": None,
            "config": None
        }
        
        for plugin_md in star_registry:
            if plugin_md.name == plugin_name:
                if not plugin_md.config:
                    break
                ret['config'] = plugin_md.config # 这是自定义的 Dict 类（AptixBotConfig）
                ret['metadata'] = {
                    plugin_name: {
                        "description": f"{plugin_name} 配置",
                        "type": "object",
                        "items": plugin_md.config.schema # 初始化时通过 __setattr__ 存入了 schema
                    }
                }
                break
            
        return ret
        
    async def _save_Aptixbot_configs(self, post_configs: dict):
        try:
            save_config(post_configs, self.config, is_core=True)
            self.core_lifecycle.restart()
        except Exception as e:
            raise e
        
    async def _save_plugin_configs(self, post_configs: dict, plugin_name: str):
        md = None
        for plugin_md in star_registry:
            if plugin_md.name == plugin_name:
                md = plugin_md
        
        if not md:
            raise ValueError(f"插件 {plugin_name} 不存在")
        if not md.config:
            raise ValueError(f"插件 {plugin_name} 没有注册配置")
        
        try:
            save_config(post_configs, md.config)
            self.core_lifecycle.restart()
        except Exception as e:
            raise e