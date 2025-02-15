import wave
import uuid
import os
from Aptixbot.core.utils.io import save_temp_img, download_image_by_url, download_file
from Aptixbot.core.utils.tencent_record_helper import wav_to_tencent_silk
from Aptixbot.api import logger
from Aptixbot.api.event import AptixMessageEvent, MessageChain
from Aptixbot.api.platform import AptixBotMessage, PlatformMetadata
from Aptixbot.api.message_components import Plain, Image, Record
from .client import SimpleGewechatClient

def get_wav_duration(file_path):
    with wave.open(file_path, 'rb') as wav_file:
        file_size = os.path.getsize(file_path)
        n_channels, sampwidth, framerate, n_frames = wav_file.getparams()[:4]
        if n_frames == 2147483647:
            duration = (file_size - 44) / (n_channels * sampwidth * framerate)
        else:
            duration = n_frames / float(framerate)
        return duration

class GewechatPlatformEvent(AptixMessageEvent):
    def __init__(
            self, 
            message_str: str, 
            message_obj: AptixBotMessage, 
            platform_meta: PlatformMetadata, 
            session_id: str,
            client: SimpleGewechatClient
        ):
        super().__init__(message_str, message_obj, platform_meta, session_id)
        self.client = client
        
    @staticmethod
    async def send_with_client(message: MessageChain, user_name: str):
        pass
                
        
    async def send(self, message: MessageChain):
        to_wxid = self.message_obj.raw_message.get('to_wxid', None)
        
        if not to_wxid:
            logger.error("无法获取到 to_wxid。")
            return
        
        for comp in message.chain:
            if isinstance(comp, Plain):
                await self.client.post_text(to_wxid, comp.text)
            elif isinstance(comp, Image):
                img_url = comp.file
                img_path = ""
                if img_url.startswith("file:///"):
                    img_path = img_url[8:]
                elif comp.file and comp.file.startswith("http"):
                    img_path = await download_image_by_url(comp.file)
                else:
                    img_path = img_url
                    
                # 检查 record_path 是否在 data/temp 目录中, record_path 可能是绝对路径
                temp_directory = os.path.abspath('data/temp')
                img_path = os.path.abspath(img_path)
                if os.path.commonpath([temp_directory, img_path]) != temp_directory:
                    with open(img_path, "rb") as f:
                        img_path = save_temp_img(f.read())

                file_id = os.path.basename(img_path)
                img_url = f"{self.client.file_server_url}/{file_id}"
                logger.debug(f"gewe callback img url: {img_url}")
                await self.client.post_image(to_wxid, img_url)
            elif isinstance(comp, Record):
                # 默认已经存在 data/temp 中
                record_url = comp.file
                record_path = ""
                
                if record_url.startswith("file:///"):
                    record_path = record_url[8:]
                elif record_url.startswith("http"):
                    await download_file(record_url, f"data/temp/{uuid.uuid4()}.wav")
                else:
                    record_path = record_url
                    
                silk_path = f"data/temp/{uuid.uuid4()}.silk"
                duration = await wav_to_tencent_silk(record_path, silk_path)
                
                print(f"duration: {duration}, {silk_path}")
                
                # 检查 record_path 是否在 data/temp 目录中, record_path 可能是绝对路径
                # temp_directory = os.path.abspath('data/temp')
                # record_path = os.path.abspath(record_path)
                # if os.path.commonpath([temp_directory, record_path]) != temp_directory:
                #     with open(record_path, "rb") as f:
                #         record_path = f"data/temp/{uuid.uuid4()}.wav"
                #         with open(record_path, "wb") as f2:
                #             f2.write(f.read())
                
                if duration == 0:
                    duration = get_wav_duration(record_path)
                
                file_id = os.path.basename(silk_path)
                record_url = f"{self.client.file_server_url}/{file_id}"
                await self.client.post_voice(to_wxid, record_url, duration*1000)
        await super().send(message)