import configparser
import os
import telebot

from localization.enums import AvailableLanguages
from localization.translation_manager import get_translation, get_language

def create_if_not_exist_config():
    config=configparser.ConfigParser()
    if not os.path.isfile('config.ini'):
        config.add_section('Settings')
        config.set('Settings', 'token', '')
        config.set('Settings', 'chat_id', '')
        config.set('Settings', 'date', 'False')
        config.set('Settings', 'time', 'False')
        config.set('Settings', 'usd', 'False')
        config.set('Settings', 'eur', 'False')
        config.set('Settings', 'btc', 'False')
        config.set('Settings', 'weather', 'False')
        config.set('Settings', 'city_id', ' ')
        config.set('Settings', 'voice_greet', 'False')
        config.set('Settings', 'jarvis', 'False')
        config.set('Settings', 'jarvis_link', ' ')
        config.set('Settings', 'autostart', 'False')
        config.set('Settings', 'gpt_api', ' ')
        config.set('Settings', 'del_delay', '3')
        config.set('Settings', 'photo', f'{os.path.abspath("bin/PC_Started.png")}')
        config.set('Settings', 'language', AvailableLanguages.EN.value)
        with open('config.ini', 'w+', encoding='utf-8') as f:
            config.write(f)

create_if_not_exist_config()

TOKEN_LICENSE= ''

class TelebotPlug():  # NOTE(danil): for testing purposes
    def __init__(self, *args, **kwargs):
        pass
    
    def send_message(self,  *args, **kwargs):
        pass

# TODO(danil): REPLACE WITH PROPER CLASS
telebot_class = TelebotPlug  # TODO(danil): must be telebot.TeleBot

BOT_LICENSE= telebot_class(TOKEN_LICENSE)
BOT_INFO = telebot_class("")

NIRCMD = r'bin\\nircmd.exe'

FLAG = True

CHAT_GPT = False

translation = get_translation()

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

PATH_TO_VOICE_LINES_FOLDER = os.path.join(ROOT_PATH, "bin", "voice_lines", get_language().value)

print(f"Path to voice lines: {PATH_TO_VOICE_LINES_FOLDER}")
