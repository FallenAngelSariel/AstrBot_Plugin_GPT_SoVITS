#  .\.venv_GPT-SoVITS\Scripts\activate
# cd E:\SpeechSynthesis

# coding=utf-8

import requests
import os
import psutil
import time
from astrbot.api import logger

class GPTSOVITS_apiv2:
    def __init__(self):
        main_dir = os.path.dirname(os.path.abspath(__file__))
        self.voicepath = os.path.join(main_dir, r"Voice")

#        self.text_lang = "zh"
#        self.ref_audio_path = os.path.join(main_dir, r"references\【激动】为你献上！让世界热闹起来吧！.wav")
        self.aux_ref_audio_paths = []  # may be some errors directly use, be careful of url
#        self.prompt_text = "为你献上！让世界热闹起来吧！"
#        self.prompt_lang = "zh"
        # available choice
        self.top_k = 5
        self.top_p = 1
        self.temperature = 1.3
        self.Text_Split_Method = "cut1"
        self.speed_factor = 1.0
        self.streaming_mode = False
        self.seed = -1
        self.parallel_infer = True
        self.repetition_penalty = 2

        self.counter = 0

    def is_GPTSOVITS_apiv2_running(self, program_name, script_name):
        for process in psutil.process_iter(['pid', 'name','cmdline']):
            try:
                if process.info['name'] == program_name and script_name in process.info['cmdline']:
                    return True
            except(psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return False

    def Open_GPTSOVITS_apiv2(self, GPT_SoVITS_filepath):
        if not self.is_GPTSOVITS_apiv2_running("python.exe", "api_v2.py"):
            os.system(f'start cmd /k "cd {GPT_SoVITS_filepath} && .\\runtime\\python.exe api_v2.py"')
            time.sleep(1)
            if self.is_GPTSOVITS_apiv2_running("python.exe", "api_v2.py"):
                logger.debug("successfully open GPT-SOVITS api_v2")
                time.sleep(15)
                return
            logger.error("fail to open GPT-SOVITS api_v2")
        else:
            logger.debug("has already opened GPT-SOVITS api_v2")

    def GPTSOVITS_SetModel(self, GPT_Path, Sovits_Path):
        url_SetModel_gpt = f"http://127.0.0.1:9880/set_gpt_weights?weights_path={GPT_Path}"
        res = requests.get(url_SetModel_gpt)
        if res.status_code == 200:
            logger.debug("Successfully set gpt")
        elif res.status_code == 400:
            logger.error("fail to set gpt")
        url_SetModel_Sovit = f"http://127.0.0.1:9880/set_sovits_weights?weights_path={Sovits_Path}"
        res = requests.get(url_SetModel_Sovit)
        if res.status_code == 200:
            logger.debug("Successfully set sovit")
        elif res.status_code == 400:
            logger.error("fail to set sovit")

    def get_voivce_path(self):
        if not os.path.exists(self.voicepath):
             os.makedirs(self.voicepath)
        return self.voicepath

    def get_voice_output_path(self,text):
        self.voice_output_path = os.path.join(self.get_voivce_path(), f"voice{text}.wav")
        return self.voice_output_path


    def tts(self,text, text_lang, ref_audio_path, prompt_text, prompt_lang):
        url = f"http://127.0.0.1:9880/tts?text={text}&text_lang={text_lang}\
&ref_audio_path={ref_audio_path}&prompt_lang={prompt_lang}&prompt_text={prompt_text}\
&aux_ref_audio_paths={self.aux_ref_audio_paths}&text_split_method={self.Text_Split_Method}\
&temperature={self.temperature}&top_k={self.top_k}&top_p={self.top_p}&speed_factor={self.speed_factor}\
&streaming_mode={self.streaming_mode}&seed={self.seed}&repetition_penalty={self.repetition_penalty}\
&batch_size=1&parallel_infer={self.parallel_infer}&media_type=wav"
        try:
            res = requests.get(url)
            res.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            if res.status_code == 400:
                logger.error("http error 400: %s :(", http_err)
                logger.error(f"{res.content}")
            else:
                logger.error("http error: %s", http_err)
        except requests.exceptions.RequestException as err:
            logger.error("%s",err)
        else:
            if self.counter >= 20:
                self.counter = 0
            self.counter = self.counter + 1
            with open(self.get_voice_output_path(str(self.counter)), 'wb') as file:
                file.write(res.content)
                logger.debug("sucess converting to speech :)")
            return self.get_voice_output_path(str(self.counter))

    

            
