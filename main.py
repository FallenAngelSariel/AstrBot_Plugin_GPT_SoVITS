from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult, CommandResult, MessageChain
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.all import *

from .GPT_SoVITS import GPTSOVITS_apiv2
import os
import re


@register("TTS", "AstralGuardian", "TTS Through GPT-SoVITS", "1.0.0", "")
class MyPlugin(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config
        self.GPT_SoVITS_filepath = config.get("GPT_SoVITS_filepath", "")
        self.GPT_Path = config.get("GPT_Path", "")
        logger.info(self.GPT_Path)
        self.Sovits_Path = config.get("Sovits_Path", "")
        self.text_lang = config.get("text_lang", "")
        self.ref_audio_path = config.get("ref_audio_path", "")
        self.prompt_text = config.get("prompt_text", "")
        self.prompt_lang = config.get("prompt_lang", "")

        if not self.GPT_SoVITS_filepath and not self.GPT_Path and not self.Sovits_Path \
           and not self.text_lang and not self.ref_audio_path and not self.prompt_text and not self.prompt_lang :
            logger.error("input config first")
            self.config_flag = False
        else:
            self.api = GPTSOVITS_apiv2()
            self.api.Open_GPTSOVITS_apiv2(self.GPT_SoVITS_filepath)
            self.api.GPTSOVITS_SetModel(self.GPT_Path, self.Sovits_Path)
            self.config_flag = True
    
    @filter.on_decorating_result()
    @filter.command("h")
    async def on_decorating_result(self, event:AstrMessageEvent):
        # get and process bot message
        result = event.get_result()
        self.text = result.get_plain_text()
        cleaned_text = self.remove_complex_emoticons(self.text)
        # tts, send voice
        if self.config_flag:
            if not cleaned_text.strip():
                cleaned_text = "字符串是空的哦"
            audio_output_path = self.api.tts(cleaned_text,self.text_lang,self.ref_audio_path,self.prompt_text,self.prompt_lang)
            voice = MessageChain()
            voice.chain.append(Record(audio_output_path))
            await event.send(voice)
        
    def remove_complex_emoticons(self,text):
        pattern = r"""
                [a-zA-Z]                
                |                       
                \([^()]+\)              
                |                       
                [^\u4e00-\u9fff，。？！、]  
        """
        regex = re.compile(pattern, re.VERBOSE)
        cleaned_text = regex.sub('', text)
        return cleaned_text
    









