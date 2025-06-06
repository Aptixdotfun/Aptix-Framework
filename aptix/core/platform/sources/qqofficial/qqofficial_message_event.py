import botpy
import botpy.message
import botpy.types
import botpy.types.message
from Aptixbot.core.utils.io import file_to_base64, download_image_by_url
from Aptixbot.api.event import AptixMessageEvent, MessageChain
from Aptixbot.api.platform import AptixBotMessage, PlatformMetadata
from Aptixbot.api.message_components import Plain, Image, Reply
from botpy import Client
from botpy.http import Route


class QQOfficialMessageEvent(AptixMessageEvent):
    def __init__(self, message_str: str, message_obj: AptixBotMessage, platform_meta: PlatformMetadata, session_id: str, bot: Client):
        super().__init__(message_str, message_obj, platform_meta, session_id)
        self.bot = bot
        self.send_buffer = None
        
    async def send(self, message: MessageChain):
        if not self.send_buffer:
            self.send_buffer = message
        else:
            self.send_buffer.chain.extend(message.chain)

    async def _post_send(self):
        '''QQ 官方 API 仅支持回复一次'''
        source = self.message_obj.raw_message
        assert isinstance(source, (botpy.message.Message, botpy.message.GroupMessage, botpy.message.DirectMessage, botpy.message.C2CMessage))
        
        plain_text, image_base64, image_path = await QQOfficialMessageEvent._parse_to_qqofficial(self.send_buffer)
        
        ref = None
        for i in self.send_buffer.chain:
            if isinstance(i, Reply):
                try:
                    ref = self.message_obj.raw_message.message_reference
                    ref = botpy.types.message.Reference(
                        message_id=ref.message_id,
                        ignore_get_message_error=False
                    )
                except BaseException as _:
                    pass
                break
        
        payload = {
            'content': plain_text,
            'msg_id': self.message_obj.message_id,
        }
        
        match type(source):
            case botpy.message.GroupMessage:
                if ref:
                    payload['message_reference'] = ref
                if image_base64:
                    media = await self.upload_group_and_c2c_image(image_base64, 1, group_openid=source.group_openid)
                    payload['media'] = media
                    payload['msg_type'] = 7
                await self.bot.api.post_group_message(group_openid=source.group_openid, **payload)
            case botpy.message.C2CMessage:
                if ref:
                    payload['message_reference'] = ref
                if image_base64:
                    media = await self.upload_group_and_c2c_image(image_base64, 1, openid=source.author.user_openid)
                    payload['media'] = media
                    payload['msg_type'] = 7
                await self.bot.api.post_c2c_message(openid=source.author.user_openid, **payload)
            case botpy.message.Message:
                if ref:
                    payload['message_reference'] = ref
                if image_path:
                    payload['file_image'] = image_path
                await self.bot.api.post_message(channel_id=source.channel_id, **payload)
            case botpy.message.DirectMessage:
                if ref:
                    payload['message_reference'] = ref
                if image_path:
                    payload['file_image'] = image_path
                await self.bot.api.post_dms(guild_id=source.guild_id, **payload)

        await super().send(self.send_buffer)
        
        self.send_buffer = None
            
    async def upload_group_and_c2c_image(self, image_base64: str, file_type: int, **kwargs) -> botpy.types.message.Media:
        payload = {
            'file_data': image_base64,
            'file_type': file_type,
            "srv_send_msg": False
        }
        if 'openid' in kwargs:
            payload['openid'] = kwargs['openid']
            route = Route("POST", "/v2/users/{openid}/files", openid=kwargs['openid'])
            return await self.bot.api._http.request(route, json=payload)
        elif 'group_openid' in kwargs:
            payload['group_openid'] = kwargs['group_openid']
            route = Route("POST", "/v2/groups/{group_openid}/files", group_openid=kwargs['group_openid'])
            return await self.bot.api._http.request(route, json=payload)
            
    @staticmethod
    async def _parse_to_qqofficial(message: MessageChain):
        plain_text = ""
        image_base64 = None  # only one img supported
        image_file_path = None
        for i in message.chain:
            if isinstance(i, Plain):
                plain_text += i.text
            elif isinstance(i, Image) and not image_base64:
                if i.file and i.file.startswith("file:///"):
                    image_base64 = file_to_base64(i.file[8:]).replace("base64://", "")
                    image_file_path = i.file[8:]
                elif i.file and i.file.startswith("http"):
                    image_file_path = await download_image_by_url(i.file)
                    image_base64 = file_to_base64(image_file_path).replace("base64://", "")
                else:
                    image_base64 = file_to_base64(i.file).replace("base64://", "")
                    image_file_path = i.file
        return plain_text, image_base64, image_file_path