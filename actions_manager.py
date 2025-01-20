import configparser
import ctypes
import inspect
import json
import math
import os
import random
import subprocess
import time
import webbrowser
import winsound
from threading import Thread

import cv2
import g4f
import numpy as np
import openai
import psutil
import pyautogui
import pyperclip
import pythoncom
import requests
import screen_brightness_control as sbc
from desktopmagic.screengrab_win32 import getDisplayRects, getRectAsImage
from pycbrf.toolbox import ExchangeRates
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from wmi import WMI

import keyboard_manager
import bot_manager
from config_manager import BOT_LICENSE, NIRCMD, PATH_TO_VOICE_LINES_FOLDER, translation
import keyboard_manager
import license_manager
import ui
import utils

from constants import UIScriptsButtons


config=configparser.ConfigParser()
config.read("config.ini", encoding='utf-8')

messages = []


class Actions():
    dict_days_of_week={
        'Monday':translation.TG_BOT.MSG_DATE_WEEKDAY_MONDAY,
        'Tuesday':translation.TG_BOT.MSG_DATE_WEEKDAY_TUESDAY,
        'Wednesday':translation.TG_BOT.MSG_DATE_WEEKDAY_WEDNESDAY,
        'Thursday':translation.TG_BOT.MSG_DATE_WEEKDAY_THURSDAY,
        'Friday':translation.TG_BOT.MSG_DATE_WEEKDAY_FRIDAY,
        'Saturday':translation.TG_BOT.MSG_DATE_WEEKDAY_SATURDAY,
        'Sunday':translation.TG_BOT.MSG_DATE_WEEKDAY_SUNDAY,
    }
        
    dict_months = {
        'January':translation.TG_BOT.MSG_DATE_MONTH_JAN,
        'February':translation.TG_BOT.MSG_DATE_MONTH_FEB,
        'March':translation.TG_BOT.MSG_DATE_MONTH_MAR,
        'April':translation.TG_BOT.MSG_DATE_MONTH_APR,
        'May':translation.TG_BOT.MSG_DATE_MONTH_MAY,
        'June':translation.TG_BOT.MSG_DATE_MONTH_JUN,
        'July':translation.TG_BOT.MSG_DATE_MONTH_JUL,
        'August':translation.TG_BOT.MSG_DATE_MONTH_AUG,
        'September':translation.TG_BOT.MSG_DATE_MONTH_SEP,
        'October':translation.TG_BOT.MSG_DATE_MONTH_OCT,
        'November':translation.TG_BOT.MSG_DATE_MONTH_NOV,
        'December':translation.TG_BOT.MSG_DATE_MONTH_DEC,
    }
  

    def del_tg_msg(self, message):
        delay = config.getfloat('Settings', 'del_delay')
        if delay != '':
            time.sleep(delay)
            for id in range(bot_manager.start_msg_id+1, message.id+1, 1):
                try:    
                        #Очиста всего после сообщения с кнопками
                        if message.text in (
                            translation.TG_BOT.BUTTON_MEDIA,
                            translation.TG_BOT.BUTTON_PC,
                            translation.TG_BOT.BUTTON_INFO,
                            translation.TG_BOT.BUTTON_PROGRAMS,
                            translation.TG_BOT.BUTTON_CHATGPT,
                            translation.TG_BOT.BUTTON_SCRIPTS,
                            translation.TG_BOT.BUTTON_INTERNET,
                            translation.TG_BOT.BUTTON_VIDEO,
                            translation.TG_BOT.BUTTON_MUSIC,
                            translation.TG_BOT.BUTTON_MENU,
                            translation.TG_BOT.BUTTON_PC_BRIGHTNESS,
                            translation.TG_BOT.BUTTON_PC_POWER_MANAGEMENT,
                            translation.TG_BOT.BUTTON_PC_DEVICE_MANAGEMENT, 
                            translation.TG_BOT.BUTTON_DEVICE_CONTROL_MOUSE,
                            translation.TG_BOT.BUTTON_DEVICE_CONTROL_KEYBOARD,
                            translation.TG_BOT.BUTTON_ADMIN,
                            translation.TG_BOT.BUTTON_CHATGPT_CLOSE
                        ):
                            if message.text == translation.TG_BOT.BUTTON_PC_FOLDERS:
                                bot_manager.Telegram().bot.delete_message(message.from_user.id, id-1)
                            bot_manager.Telegram().bot.delete_message(message.from_user.id, id)
                            print("#Очиста всего после сообщения с кнопками")
                        
                        #Очистка сообщений после которых нет ответа, только выполнение
                        elif message.text in (
                            translation.TG_BOT.BUTTON_VOLUME_DOWN,
                            translation.TG_BOT.BUTTON_VOLUME_MUTE,
                            translation.TG_BOT.BUTTON_VOLUME_UP,
                            translation.TG_BOT.BUTTON_VIDEO_GO_BACKWARD,
                            translation.TG_BOT.BUTTON_VIDEO_PLAY_PAUSE,
                            translation.TG_BOT.BUTTON_VIDEO_SKIP_FORWARD,
                            translation.TG_BOT.BUTTON_VIDEO_PREV_VIDEO,
                            translation.TG_BOT.BUTTON_VIDEO_NEXT_VIDEO,
                            translation.TG_BOT.BUTTON_VIDEO_FULLSCREEN,
                            translation.TG_BOT.BUTTON_SOUND_PREV_TRACK,
                            translation.TG_BOT.BUTTON_SOUND_PLAY_PAUSE,
                            translation.TG_BOT.BUTTON_SOUND_NEXT_TRACK,
                            translation.TG_BOT.BUTTON_PC_LOCK_WORKSTATION,
                            translation.TG_BOT.BUTTON_PC_CLOSE_ACTIVE_WINDOW,
                            translation.TG_BOT.BUTTON_PC_TASK_MANAGER,
                            translation.TG_BOT.BUTTON_POWER_CONTROL_SLEEP,
                            translation.TG_BOT.BUTTON_POWER_CONTROL_HIBERNATE,
                            translation.TG_BOT.BUTTON_POWER_CONTROL_REBOOT,
                            translation.TG_BOT.BUTTON_POWER_CONTROL_SHUT_DOWN,
                            translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOUSE1,
                            translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOUSE2,
                            translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOVE_UP,
                            translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOVE_LEFT,
                            translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOVE_DOWN,
                            translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOVE_RIGHT,
                            translation.TG_BOT.BUTTON_BRIGHTNESS_SET_0_PCT,
                            translation.TG_BOT.BUTTON_BRIGHTNESS_SET_25_PCT,
                            translation.TG_BOT.BUTTON_BRIGHTNESS_SET_50_PCT,
                            translation.TG_BOT.BUTTON_BRIGHTNESS_SET_75_PCT,
                            translation.TG_BOT.BUTTON_BRIGHTNESS_SET_100_PCT,
                        ):
                            bot_manager.Telegram().bot.delete_message(message.from_user.id, message.id)  
                            print("#Очистка сообщений после которых нет ответа, только выполнение")
                            return
                        
                        #Очистка для открытия и сценариев
                        elif translation.TG_BOT.TRIGGER_OPEN in message.text or translation.TG_BOT.TRIGGER_SCRIPT in message.text:
                              bot_manager.Telegram().bot.delete_message(message.from_user.id, message.id)
                              print("#Очистка для открытия и сценариев")
                              return
                        
                        #Очистка сообщений с ответом + таймер, т.к дают инфу
                        elif message.text in (
                            translation.TG_BOT.BUTTON_DOLLAR,
                            translation.TG_BOT.BUTTON_EURO,
                            translation.TG_BOT.BUTTON_WEATHER,
                            translation.TG_BOT.BUTTON_BTC,
                            translation.TG_BOT.BUTTON_DATE,
                            translation.TG_BOT.BUTTON_POWER_CONTROL_SHUT_DOWN_TIMER_CANCEL,
                            translation.TG_BOT.BUTTON_DEVICE_CONTROL_TURN_OFF_MONITOR,
                            translation.TG_BOT.BUTTON_PC_CLEAR_RECYCLE_BIN,
                            translation.TG_BOT.BUTTON_ADMIN_CLEAR_TEMP_FOLDER,
                            translation.TG_BOT.BUTTON_PC_SPEC,
                            translation.TG_BOT.BUTTON_SPEEDTEST,
                            translation.TG_BOT.BUTTON_PC_SCREENSHOT,
                            translation.TG_BOT.BUTTON_PC_WEBCAM_SCREENSHOT
                        ):
                            bot_manager.Telegram().bot.delete_message(message.from_user.id, message.id)
                            if message.text in (
                                translation.TG_BOT.BUTTON_SPEEDTEST,
                                translation.TG_BOT.BUTTON_PC_WEBCAM_SCREENSHOT,
                                translation.TG_BOT.BUTTON_PC_SCREENSHOT
                            ):
                                time.sleep(55)
                            time.sleep(5)
                            bot_manager.Telegram().bot.delete_message(message.from_user.id, message.id+1)
                            print("#Очистка сообщений с ответом + таймер, т.к дают инфу")
                            return
                        
                        #Очистка сообщений с доп. аругментом
                        elif message.text in (
                            translation.TG_BOT.BUTTON_VOLUME,
                            translation.TG_BOT.BUTTON_POWER_CONTROL_SHUT_DOWN_TIMER,
                            translation.TG_BOT.BUTTON_OPEN_LINK,
                            translation.TG_BOT.BUTTON_COMMAND_FOR_JARVIS,
                            translation.TG_BOT.BUTTON_ADMIN_CHANGE_PASSWORD,
                            translation.TG_BOT.BUTTON_PC_CHANGE_WALLPAPER,
                            translation.TG_BOT.BUTTON_KEYBOARD_CONTROL_TYPE,
                            translation.TG_BOT.BUTTON_KEYBOARD_CONTROL_PRESS_BUTTON,
                            translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOVE_TO_COORDINATES
                        ):
                            time.sleep(10)
                            bot_manager.Telegram().bot.delete_message(message.from_user.id, message.id)
                            bot_manager.Telegram().bot.delete_message(message.from_user.id, message.id+1)
                            bot_manager.Telegram().bot.delete_message(message.from_user.id, message.id+2)
                            bot_manager.Telegram().bot.delete_message(message.from_user.id, message.id+3)
                            print("#Очистка сообщений с доп. аругментом")
                            return
                except Exception as e:
                    pass

    def move_cursor_script(self, text) -> None:
        x=text.split(',')[0]
        y=text.split(',')[1]
        pyautogui.moveTo(int(x), int(y))
    
    def move_cursor(self, message) -> None:
        x=str(message.text).split(' ')[0]
        y=str(message.text).split(' ')[1]
        
        pyautogui.moveTo(int(x), int(y))
        
        return bot_manager.Telegram().bot.send_message(message.from_user.id, translation.TG_BOT.MSG_MOUSE_CONTROL_MOVE_TO_COORDINATES_SUCCESS.format(x=x, y=y))

    def explorer(self, path = None) -> None:
        """Функция для перехода в папках."""
        user = os.environ.get( "USERNAME" )
        if path is None:
            path = f"C:\\Users\\{user}\\Desktop"
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        # Переходим в указанную папку
        os.chdir(path)

        # Получаем список файлов и папок в текущей директории
        files = os.listdir()
        for file in files:
            buttons.row(file)
        
        return buttons

    def clean_temp_folder(self) -> None:
        """Функция для очистки папки с временными файлами"""
        files_deleted = 0
        files_error = 0
        try:
            temp_folder = os.path.join(os.environ['TEMP'])
            for file_name in os.listdir(temp_folder):
                try:
                    file_path = os.path.join(temp_folder, file_name)
                    os.remove(file_path)
                    files_deleted+=1
                except Exception as e:
                    files_error+=1
        except Exception as e:
            pass
        return translation.TG_BOT.MSG_ADMIN_CLEAR_TEMP_FOLDER_RESULT.format(files_removed=files_deleted, files_error=files_error)

    def check_if_admin(self):
        """Проверка, является ли пользователь администратором."""
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ui.MainWindow().log_print(translation.LOGS.WARNING_ADMIN_NO_PERMISSIONS)
            return False
        else:
            # ui.MainWindow().log_print('Программа имеет права администратора, все функции доступны')
            return True

    def do_script(self, name) -> None:
        print('do script')
        SCRIPT_DICT = {
            UIScriptsButtons.CURSOR_TO_XY: [Actions(), 'move_cursor_script'], 
            UIScriptsButtons.OPEN_PROGRAM: [Actions(), 'open_exe_script'], 
            UIScriptsButtons.CLOSE_PROGRAM: [Actions(),'kill_process_script'],
            UIScriptsButtons.OPEN_WEBSITE: [Actions(), 'open_url_script'],
            UIScriptsButtons.WAIT: [time, 'sleep'],
            UIScriptsButtons.KEYBOARD_SHORTCUT: [Actions(), 'press_btn_script'],
            UIScriptsButtons.TYPE_TEXT: [Actions(), 'write_text_script'],
            UIScriptsButtons.PRESS_MOUSE_BUTTON: [Actions(), 'press_mouse_btn_script'],
        }
        name = str(name).split()[1]
        with open('data_script.json', encoding='utf-8') as f:
            data = json.load(f)
        
        for script in data:
            if script['name'] in name:
                for command in dict(script['commands']):
                    comm = script['commands'][command][0]
                    arg = script['commands'][command][1]
                    func = getattr(SCRIPT_DICT[comm][0], SCRIPT_DICT[comm][1])
                    
                    if comm == 'Подождать':
                        arg = float(arg[0])
                        func(arg)
                    else:
                        func(arg[0])
        
    def kill_process_script(self, text) -> None:
        for proc in psutil.process_iter():
            if proc.name() == text:
                proc.kill()

    def open_exe_script(self, path) -> None:
        os.startfile(path)

    def open_exe(self, name) -> None:
        """Открывает программу через путь"""
        name = str(name).replace('Открыть ', '')
        with open('data_program.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for i, programm in enumerate(data):
            if programm['name'] in name:
                path = programm['path']
                for domen in ('.com', '.ru', '.net', '.org'):
                    if domen in path:
                        path = 'www.' + path
                os.startfile(path)

    def stop_license(self):
        ui.MainWindow().log_print(translation.LOGS.INFO_LICENSE_STOP)
        # NOTE(danil): no translation needed for Bot license, right?
        BOT_LICENSE.send_message(license_manager.LICENSE().CHAT_ID, f'Удалить {license_manager.LICENSE().license_key()}\nhttps://pastebin.com/edit/T33R8zR8')
        os.rename('logs.txt', 'log.txt')
        user_path = os.path.expanduser('~') # Путь к папке пользователя
        open(f'{user_path}\system32.txt', 'w')
        utils.quit_window()

    def get_current_date(self) -> str:
        return(self.dict_days_of_week[time.strftime('%A')], time.strftime('%d'), self.dict_months[time.strftime('%B')])
        
    def get_current_time(self) -> str:
        return time.strftime('%X')
        
    def currensy_rates(self) -> str:
        rates = ExchangeRates(time.strftime('%Y-%m-%d'))
        return(str(rates['USD'].rate)[:5],str(rates['EUR'].rate)[:5])
    
    def bitcoin_rate(self) -> float:
        URL = 'https://blockchain.info/ru/ticker'
        HEADERS = {"X-Requested-With": "XMLHttpRequest",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/54.0.2840.99 Safari/537.36',
        }
        response = requests.get(URL, headers=HEADERS)
        response_json = response.json()
        return response_json["USD"]["last"]

    def weather(self) -> str:
        config=configparser.ConfigParser()
        config.read("config.ini", encoding='utf-8')
        weather = config.getboolean('Settings','weather')
        if weather:
            city_id = config.get('Settings','city_id')
            appid = "70ec1c470adcbcad3e1bb6bd0841af0e"
            try:
                city_id = int(city_id)
                params={'id': city_id, 'type': 'like', 'units': 'metric', 'APPID': appid, 'lang': translation.TG_BOT.OPENWEATHERMAP_API_LANG.value}
            except:
                params={'q': city_id, 'type': 'like', 'units': 'metric', 'APPID': appid, 'lang': translation.TG_BOT.OPENWEATHERMAP_API_LANG.value}
            try:
                res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                params=params)
                data = res.json()
                city_name = data['name']
                status = str.title((data['weather'][0]['description']))
                temp = (data['main']['temp'])
                weather_str = translation.TG_BOT.MSG_WEATHER_RESULT.format(city_name=city_name, status=status, temp=temp)
                return weather_str
            except Exception as e:
                ui.MainWindow().error_print(e)
                pass
        else:
            ui.MainWindow().log_print(translation.LOGS.INFO_WEATHER_ASK_TO_TURN_ON_AND_CITY_ID)
            return

    def sound_answer(self, message):
        num = ('1','2','3', '4')

        dict ={
            translation.TG_BOT.BUTTON_PC_SCREENSHOT:os.path.join(PATH_TO_VOICE_LINES_FOLDER, 'create.wav'),
            translation.TG_BOT.BUTTON_PC_WEBCAM_SCREENSHOT:os.path.join(PATH_TO_VOICE_LINES_FOLDER, 'create.wav'),
            translation.TG_BOT.BUTTON_POWER_CONTROL_REBOOT:os.path.join(PATH_TO_VOICE_LINES_FOLDER, 'create.wav'),
            translation.TG_BOT.BUTTON_POWER_CONTROL_SLEEP:os.path.join(PATH_TO_VOICE_LINES_FOLDER, 'pcoff.wav'), 
            translation.TG_BOT.BUTTON_POWER_CONTROL_HIBERNATE:os.path.join(PATH_TO_VOICE_LINES_FOLDER, 'pcoff.wav'),
            translation.TG_BOT.BUTTON_POWER_CONTROL_SHUT_DOWN:os.path.join(PATH_TO_VOICE_LINES_FOLDER, 'pcoff.wav'),
            translation.TG_BOT.BUTTON_PC_LOCK_WORKSTATION:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_PC_CHANGE_WALLPAPER:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_PC_BRIGHTNESS:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_PC_CLOSE_ACTIVE_WINDOW:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_PC_CLEAR_RECYCLE_BIN:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_PC_POWER_MANAGEMENT:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_PC_DEVICE_MANAGEMENT:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            '🖥Консольная команда':os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_PC_TASK_MANAGER:os.path.join(PATH_TO_VOICE_LINES_FOLDER, 'create.wav'),
            translation.TG_BOT.BUTTON_POWER_CONTROL_SHUT_DOWN_TIMER:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            '🗞Новости':os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_DOLLAR:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_BTC:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_EURO:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_WEATHER:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_DATE:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            '🔎Поиск':os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            '✉️Найти в ВК':os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_OPEN_LINK:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_BRIGHTNESS_SET_100_PCT:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_BRIGHTNESS_SET_0_PCT:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_BRIGHTNESS_SET_25_PCT:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_BRIGHTNESS_SET_50_PCT:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_BRIGHTNESS_SET_75_PCT:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_DEVICE_CONTROL_MOUSE:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_DEVICE_CONTROL_KEYBOARD:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_DEVICE_CONTROL_TURN_OFF_MONITOR:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_VIDEO:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_MUSIC:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_KEYBOARD_CONTROL_TYPE:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_KEYBOARD_CONTROL_PRESS_BUTTON:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_CHATGPT:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_COMMAND_FOR_JARVIS:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
            translation.TG_BOT.BUTTON_PC_SPEC:os.path.join(PATH_TO_VOICE_LINES_FOLDER, f'sir{random.choice(num)}.wav'),
        }
        config=configparser.ConfigParser()
        config.read("config.ini", encoding='utf-8')
        if config.getboolean('Settings','voice_greet'):
            try:
                ans = dict[message]
            except KeyError:
                return
            winsound.PlaySound(ans, winsound.SND_FILENAME)

    def morning_sound_answer(self):
        """Рандомный ответ гс помощника."""
        ANSWERS = [os.path.join(PATH_TO_VOICE_LINES_FOLDER, "Ans1.wav"),
                    os.path.join(PATH_TO_VOICE_LINES_FOLDER, "Ans2.wav"),
                    os.path.join(PATH_TO_VOICE_LINES_FOLDER, "Ans3.wav"),
                    os.path.join(PATH_TO_VOICE_LINES_FOLDER, "Ans4.wav"),
        ]
        hour = int(time.strftime('%H'))
        config=configparser.ConfigParser()
        config.read("config.ini", encoding='utf-8')
        if config.getboolean('Settings','voice_greet'):
            if (hour >= 6) and (hour <= 12):
                winsound.PlaySound(os.path.join(PATH_TO_VOICE_LINES_FOLDER, "good_morning.wav"), winsound.SND_FILENAME)
            else:
                winsound.PlaySound(random.choice(ANSWERS), winsound.SND_FILENAME)
      
    def create_start_response(self) -> str:
        """Создание приветственного сообщения бота."""
        config=configparser.ConfigParser()
        config.read("config.ini", encoding='utf-8')
        START_RESPONSE = translation.TG_BOT.MSG_WELCOME_MSG_GREETINGS + '\n\n'
        if config['Settings'].getboolean('date'):
            weekday, day, month = self.get_current_date()
            START_RESPONSE+= translation.TG_BOT.MSG_WELCOME_MSG_DATE.format(weekday=weekday, day=day, month=month) + '\n'
        if config['Settings'].getboolean('time'):
            START_RESPONSE+= translation.TG_BOT.MSG_WELCOME_MSG_TIME.format(time=self.get_current_time()) + '\n'
        if config['Settings'].getboolean('usd'):
            START_RESPONSE+= translation.TG_BOT.MSG_WELCOME_MSG_DOLLAR.format(value=self.currensy_rates()[0]) + '\n'
        if config['Settings'].getboolean('eur'):
            START_RESPONSE+= translation.TG_BOT.MSG_WELCOME_MSG_EURO.format(value=self.currensy_rates()[1]) + '\n'
        if config['Settings'].getboolean('btc'):
            START_RESPONSE+= translation.TG_BOT.MSG_WELCOME_MSG_BTC.format(value=self.bitcoin_rate()) + '\n'   
        if config['Settings'].getboolean('weather'):
            try:
                weather = self.weather()
                if weather == '':
                    bot_manager.Telegram().bot.send_chat_action(bot_manager.Telegram().chat_id, 'typing')
                    bot_manager.Telegram().bot.send_message(bot_manager.Telegram().chat_id, translation.TG_BOT.MSG_WEATHER_ERROR)
                else:
                    START_RESPONSE+= weather
            except Exception as e:
                ui.MainWindow().log_print(translation.LOGS.ERROR_WELCOME_MESSAGE)
                ui.MainWindow().error_print(e)
                bot_manager.Telegram().bot.send_chat_action(bot_manager.Telegram().chat_id, 'typing')
                bot_manager.Telegram().bot.send_message(bot_manager.Telegram().chat_id, translation.TG_BOT.MSG_WEATHER_ERROR)
            
        return START_RESPONSE

    def pc_off_time(self, message) -> None:
        """Отключение компьютера через n секунд."""
        try:
            seconds = int(message.text)
        except Exception as e:
            ui.MainWindow().error_print(e)
            return

        def shutdown():
            subprocess.call(['shutdown', '-s', '-t', str(seconds)])

        timer_thread = Thread(target=shutdown)
        timer_thread.start()

        bot_manager.Telegram().bot.send_chat_action(message.from_user.id, 'typing')
        bot_manager.Telegram().bot.send_message(
            message.from_user.id,
            translation.TG_BOT.MSG_POWER_CONTROL_SHUT_DOWN_TIMER.format(seconds=seconds)
        )
        ui.MainWindow().log_print(translation.LOGS.INFO_POWER_CONTROL_SHUT_DOWN_TIMER.format(username=message.from_user.username))

        
    def set_volume(self, message) -> None:
        """Установка громкости системы на n."""
        vol = message.text
        subprocess.call(f'{NIRCMD} setsysvolume {int(vol) * 655}')
        bot_manager.Telegram().bot.send_chat_action(message.from_user.id, 'typing')
        bot_manager.Telegram().bot.send_message(
            message.from_user.id,
            translation.TG_BOT.MSG_VOLUME_SET.format(vol=vol)
        )
        ui.MainWindow().log_print(translation.LOGS.INFO_VOLUME.format(username=message.from_user.username))
    
    def open_url_script(self, text) -> None:
        url = text
        if 'https://' not in text:
            url = 'https://' + text
        webbrowser.open(url, new=2)

    def open_url(self, message) -> None:
        """Открытие url через браузер"""
        url = message.text
        if 'https://' not in url:
            url = 'https://' + url
        webbrowser.open(message.text, new=2)
        msg = translation.TG_BOT.MSG_OPEN_LINK.format(url=message.text)
        bot_manager.Telegram().bot.send_chat_action(message.from_user.id, 'typing')
        bot_manager.Telegram().bot.send_message(message.from_user.id, msg)
        ui.MainWindow().log_print(translation.LOGS.INFO_OPEN_LINK.format(username=message.from_user.username))
        
    def text_to_jarvis(self, message) -> None:
        """Передача текста в Джарвиса"""
        jarvis_link = bot_manager.Telegram().jarvis_link
        
        if not jarvis_link == '':
            text = message.text
            requests.get(jarvis_link + text)
            bot_manager.Telegram().bot.send_chat_action(message.from_user.id, 'typing')
            bot_manager.Telegram().bot.send_message(message.from_user.id, text=translation.TG_BOT.MSG_COMMAND_FOR_JARVIS_SUCCESS.format(text=text))
            ui.MainWindow().log_print(translation.LOGS.INFO_COMMAND_FOR_JARVIS.format(username=message.from_user.username))
        else:
            bot_manager.Telegram().bot.send_chat_action(message.from_user.id, 'typing')
            bot_manager.Telegram().bot.send_message(message.from_user.id, translation.TG_BOT.MSG_COMMAND_FOR_JARVIS_ASK_FOR_JARVIS_LINK)
        
    def new_password(self, message) -> None:
        """Смена пароля системы"""
        WindowsUser = os.environ.get( "USERNAME" )
        if message.text == '0000':
            subprocess.call(f'net users {WindowsUser} ""', shell = True)
            bot_manager.Telegram().bot.send_chat_action(message.from_user.id, 'typing')
            bot_manager.Telegram().bot.send_message(message.from_user.id, text=translation.TG_BOT.MSG_ADMIN_CHANGE_PASSWORD_RESET_SUCCESS)
        else: 
            subprocess.call(f'net user {WindowsUser} {message.text}', shell=True)
            bot_manager.Telegram().bot.send_chat_action(message.from_user.id, 'typing')
            bot_manager.Telegram().bot.send_message(message.from_user.id, text=translation.TG_BOT.MSG_ADMIN_CHANGE_PASSWORD_NEW_PASSWORD_SUCCESS.format(password=message.text))
        ui.MainWindow().log_print(translation.LOGS.INFO_ADMIN_CHANGE_PASSWORD.format(username=message.from_user.username))
    
    def wallpaper(self, message):    
        try:
            file_info = bot_manager.Telegram().bot.get_file(message.photo[len(message.photo) - 1].file_id)
            downloaded_file = bot_manager.Telegram().bot.download_file(file_info.file_path)
            src = os.path.abspath(file_info.file_path)
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            ctypes.windll.user32.SystemParametersInfoW(20, 0, src, 0)
            bot_manager.Telegram().bot.reply_to(message, translation.TG_BOT.MSG_PC_CHANGE_WALLPAPER_SUCCESS)
            new_file.close()
            os.remove(file_info.file_path)
            ui.MainWindow().log_print(translation.LOGS.INFO_PC_CHANGE_WALLPAPER.format(username=message.from_user.username))
        except Exception as e:
            ui.MainWindow().error_print(e)
            ui.MainWindow().log_print(translation.LOGS.ERROR_PC_CHANGE_WALLPAPER_FAILED_TO_DOWNLOAD_PHOTO)
            bot_manager.Telegram().bot.reply_to(message, translation.TG_BOT.MSG_PC_CHANGE_WALLPAPER_FAILED_TO_DOWNLOAD_PHOTO)

    def write_text_script(self, text) -> None:
        try:
            pyperclip.copy(text)
            keyboard_manager.press_and_release('ctrl + v')
        except:
            return

    def write_text(self, message, interval=0.01):
        try:
            pyperclip.copy(message.text)
            keyboard_manager.press_and_release('ctrl + v')
        except:
            return
        bot_manager.Telegram().bot.send_chat_action(message.from_user.id, 'typing')
        bot_manager.Telegram().bot.send_message(message.from_user.id, translation.TG_BOT.MSG_KEYBOARD_CONTROL_TYPE_SUCCESS.format(text=message.text))
        ui.MainWindow().log_print(translation.LOGS.INFO_KEYBOARD_CONTROL_TYPE.format(username=message.from_user.username))

    def press_mouse_btn_script(self, text) -> None:
        if text.strip().upper() == translation.UI.SCRIPT_PRESS_MOUSE_BUTTON_MOUSE1:
            pyautogui.leftClick()
        if text.strip().upper() == translation.UI.SCRIPT_PRESS_MOUSE_BUTTON_MOUSE2:
            pyautogui.rightClick()
        if text.strip().upper() == translation.UI.SCRIPT_PRESS_MOUSE_BUTTON_MOUSE3:
            pyautogui.middleClick()

    def press_btn_script(self, text) -> None:
        keyboard_manager.send(text)

    def press_btn(self, message):
        try:
            keyboard_manager.send(message.text)
        except:
            bot_manager.Telegram().bot.send_message(message.from_user.id, translation.TG_BOT.MSG_KEYBOARD_CONTROL_PRESS_BUTTON_ERROR)
            pass
        bot_manager.Telegram().bot.send_chat_action(message.from_user.id, 'typing')
        bot_manager.Telegram().bot.send_message(message.from_user.id, translation.TG_BOT.MSG_KEYBOARD_CONTROL_PRESS_BUTTON_SUCCESS.format(button=message.text))
        ui.MainWindow().log_print(translation.LOGS.INFO_KEYBOARD_CONTROL_PRESS_BUTTON.format(username=message.from_user.username))

    def screen(self, message):
        screens=(getDisplayRects())
        for monitor in range(0, len(screens)):
            rect = getRectAsImage(screens[monitor])
            rect.save(f'screen_{monitor}.jpg',format='png')
            bot_manager.Telegram().bot.send_chat_action(message.from_user.id, 'upload_photo')
            with open (f'screen_{monitor}.jpg', 'rb') as p:
                bot_manager.Telegram().bot.send_document(message.from_user.id,p)
                p.close()
            os.remove(f'screen_{monitor}.jpg')
        ui.MainWindow().log_print(translation.LOGS.INFO_PC_SCREENSHOT.format(username=message.from_user.username))
    
    def webcam_screen(self, message):
        try:
            bot_manager.Telegram().bot.send_chat_action(message.from_user.id, 'upload_photo')
            cap = cv2.VideoCapture(0)
            for i in range(3):
                cap.read()
            ret, frame = cap.read()
            cv2.imwrite('Webcam.jpg', frame)   
            cap.release()
            webcam = open('Webcam.jpg', 'rb')
            bot_manager.Telegram().bot.send_photo(message.from_user.id, webcam)
            webcam.close()
            os.remove('Webcam.jpg')
            ui.MainWindow().log_print(translation.LOGS.INFO_PC_WEBCAM_SCREENSHOT.format(username=message.from_user.username))
        except Exception as e:
            ui.MainWindow().error_print(e)
            bot_manager.Telegram().bot.send_chat_action(message.from_user.id, 'typing')
            bot_manager.Telegram().bot.send_message(message.from_user.id, translation.TG_BOT.MSG_PC_WEBCAM_SCREENSHOT_NO_WEBCAM, parse_mode="Markdown")

    def set_bright(self, message, set_int):
        try:
            for monitor in sbc.list_monitors():
                sbc.set_brightness(value=set_int, display=monitor)
            ui.MainWindow().log_print(translation.LOGS.INFO_BRIGHTNESS_SET.format(set_int=set_int, username=message.from_user.username))
        except sbc.ScreenBrightnessError as e:
            ui.MainWindow().error_print(e)
            ui.MainWindow().log_print(translation.LOGS.ERROR_BRIGHTNESS_SET)
            pass
    
    def api_key(self):
        return config.get('Settings','gpt_api')
    
    def chatgpt_text(self, message, text=None, msg=None):
        '''Получени ответа от ChatGPT через g4f'''
        global CHAT_GPT

        if message.text == translation.TG_BOT.BUTTON_CHATGPT_CLOSE:
            CHAT_GPT = False
            keyboard_manager.Keyboard().add_buttons_menu(message.from_user.id)
            bot_manager.Telegram().bot.send_chat_action(message.from_user.id, 'typing')
            return Thread(target= Actions().del_tg_msg, args=(message,)).start()
        
        if text is None:
            prompt = message.text
        else:
            prompt = text
        
        if msg is None:
            print('Первое смс')
            msg = bot_manager.Telegram().bot.send_message(message.from_user.id, translation.TG_BOT.MSG_CHATGPT_GENERATING)
        else:
            print('Сообщение уже существует', msg.text)
            bot_manager.Telegram().bot.edit_message_text(chat_id=message.from_user.id, message_id=msg.id, text=translation.TG_BOT.MSG_CHATGPT_GENERATING)
        
        try:
            response = g4f.ChatCompletion.create(
                model=g4f.models.gpt_35_long,
                messages=[{"role": "user", "content": prompt}])
            
            if  response != '':
                try:
                    bot_manager.Telegram().bot.edit_message_text(chat_id=message.from_user.id, message_id=msg.id, text=translation.TG_BOT.MSG_CHATGPT_RESPONSE_SUCCESS.format(response=response), parse_mode='Markdown')
                except Exception as e:
                    bot_manager.Telegram().bot.edit_message_text(chat_id=message.from_user.id,message_id=msg.id, text=translation.TG_BOT.MSG_CHATGPT_RESPONSE_SUCCESS.format(response=response))
            else:
                print('Ответ пуст')
            messages.clear()
        
        except Exception as e:
            messages.clear()
            bot_manager.Telegram().bot.edit_message_text(chat_id=message.from_user.id, message_id=msg.id, text=translation.TG_BOT.MSG_CHATGPT_RESPONSE_FAIL_TRY_AGAIN.format(attempt=len(inspect.getouterframes(inspect.currentframe()))-3))
            time.sleep(2)
            if len(inspect.getouterframes(inspect.currentframe())) <= 5:
                return self.chatgpt_text(message=message, msg=msg)
            else:
                bot_manager.Telegram().bot.edit_message_text(chat_id=message.from_user.id, message_id=msg.id, text=translation.TG_BOT.MSG_CHATGPT_RESPONSE_FAIL_ASK_RETRY)
                return False

    # Если когда-нибудь апи заработает

    # def chatgpt_photo_api(self, message, text=None, msg=None):
    #     bot_manager.Telegram().bot.send_message(message.from_user.id, 'ChatGPT генерирует фото...')
    #     try:
    #         response = openai.Image.create(
    #                 prompt=message.text,
    #                 n=1,
    #                 size="1024x1024"
    #         )
    #     except Exception as e:
    #         ui.MainWindow().error_print(e)
    #         return
        
    #     chat_response = response['data'][0]['url']
    #     bot_manager.Telegram().bot.send_photo(message.from_user.id, chat_response)

    def chatgpt_text_api(self, message, text=None, msg=None):
        openai.api_key = self.api_key()
        '''Получени ответа от ChatGPT через g4f'''
        if text is None:
            prompt = message.text
        else:
            prompt = text
        
        if msg is None:
            print('Первое смс')
            msg = bot_manager.Telegram().bot.send_message(message.from_user.id, translation.TG_BOT.MSG_CHATGPT_GENERATING)
        else:
            print('Сообщение уже существует', msg.text)
        bot_manager.Telegram().bot.edit_message_text(chat_id=message.from_user.id, message_id=msg.id, text=translation.TG_BOT.MSG_CHATGPT_GENERATING)
        messages.append(({"role": "user", "content": prompt}))
        try:
            completion = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=messages,
                                max_tokens = 1000,
                                temperature = 0.5
                                )
            ans = str(completion.choices[0].message.content).strip()
            bot_manager.Telegram().bot.send_message(message.from_user.id, ans)
            ui.MainWindow().log_print(translation.LOGS.INFO_CHATGPT.format(username=message.from_user.username))
        except Exception as e:
            ui.MainWindow().error_print(e)
            return

    def video_record(self, message):  # NOTE(danil): currently disabled
        try:
            os.remove('video.mp4')
        except:
            pass
        bot_manager.Telegram().bot.send_message(message.from_user.id, 'Записываю видео...')
        TIME = 60
        SCREEN_SIZE = tuple(pyautogui.size())
        fourcc = cv2.VideoWriter_fourcc('a','v','c','1')
        out = cv2.VideoWriter("video.mp4", fourcc, 20.0, (SCREEN_SIZE))
        fps = 20.0
        chat_id = config['Settings']['chat_id']
        chat_id = chat_id.split(', ')
        bot_manager.Telegram().bot.send_chat_action(message.from_user.id, 'record_video')
        for i in range(int(TIME * fps)):
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)
        cv2.destroyAllWindows()
        out.release()
        try:
            with open('video.mp4', 'rb') as video:
                bot_manager.Telegram().bot.send_document(message.from_user.id, video)
            video.close()
            os.remove('video.mp4')
        except Exception as e:
            ui.MainWindow().error_print(e)
            pass
    
    def pc_param(self, message):
        pythoncom.CoInitialize()
        msg=''
        computer = WMI()
        os_info = computer.Win32_OperatingSystem()[0]
        proc_info = computer.Win32_Processor()[0]
        gpu_info = computer.Win32_VideoController()[0]
        os_name = str(os_info.Name.encode('utf-8').split(b'|')[0])
        os_name = os_name.replace(os_name.split(' ')[0], '').replace("'", '')
        os_version = ' '.join([os_info.Version, os_info.BuildNumber])
        system_ram = round(float(os_info.TotalVisibleMemorySize) / 1048576)  # KB to GB
        parametrs = [
            translation.TG_BOT.MSG_PC_SPEC_CPU.format(cpu_name=proc_info.Name),
            translation.TG_BOT.MSG_PC_SPEC_GPU.format(gpu_name=gpu_info.Name),
            translation.TG_BOT.MSG_PC_SPEC_OS_NAME.format(os_name=str(os_name)).format(os_name=str(os_name)),
            translation.TG_BOT.MSG_PC_SPEC_OS_VERSION.format(os_version=os_version),
            translation.TG_BOT.MSG_PC_SPEC_RAM_SYSTEM.format(system_ram=system_ram)
        ]
        for param in parametrs:
            msg += f'{str(param).strip()}\n'

        bot_manager.Telegram().bot.send_message(message.from_user.id, msg)
        ui.MainWindow().log_print(translation.LOGS.INFO_PC_SPEC.format(username=message.from_user.username))

# NOTE(danil): not in use, see explorer_manager.py
# class Explorer():
#     global edit_msg, path, page, all_path
    
#     drives_in = []
#     drives_names = []
#     folders_names = {}
    
#     edit_msg = None
#     path = ''
#     page = 1
    
#     all_path = ''

#     def scanning_drives(self):
#         # Получаем список дисков, записываем в drives_in и создаём инлайн - кнопки
#         drives = psutil.disk_partitions()

#         self.drives_in.clear()
#         self.drives_names.clear()

#         # Проверяем диски на заполненность
#         for drive in drives:
#             try:
#                 drive_usage = psutil.disk_usage(drive.mountpoint)

#                 # Если объем диска больше 0, добавляем инлайн кнопку в массив
#                 if drive_usage.total > 0:
#                     self.drives_in.append(InlineKeyboardButton(drive.device, callback_data=drive.device))
#                     self.drives_names.append(drive.device)
#             except Exception as e:
#                 print(f"{e}\n\n")

#         # Создаем маркап с дисками
#         drives_markup = InlineKeyboardMarkup(row_width=5).add(*self.drives_in)
#         drives_markup.add(InlineKeyboardButton(translation.TG_BOT.BUTTON_FOLDER_MANAGEMENT_DESKTOP, callback_data='desktop'))
#         return drives_markup


#     def scanning_folders(self, path, page=1, items_per_page=20):
#         global all_path

#         if path in self.drives_in:
#             all_path = path

#         if path in self.folders_names.keys():
#             slash = ''

#             if all_path[-1] != '\\':
#                 slash = '\\'

#             all_path = all_path + slash + self.folders_names.get(path)
#             direct = os.listdir(all_path)  # Получаем список папок по пути
#         else:
#             all_path = path
#             direct = os.listdir(path)

#         folders = []  # Список папок

#         for folder in direct:
#             # Если папка не системная, добавляем ее в список
#             if folder[0] != '.' and folder[0] != '$':
#                 folders.append(folder)

#         if path in self.drives_in:  # Если директория корневая (начало одного из дисков) прибавляем к диску папку
#             name = self.folders_names.get(path)  # Получаем имя файла или папки по ее ключу
#             path += f'{name}'
#         else:
#             name = self.folders_names.get(path)
#             path += f'\\{name}'

#         # Рассчитываем начальный и конечный индексы для текущей страницы
#         start_index = (page - 1) * items_per_page
#         end_index = start_index + items_per_page

#         pages = math.ceil((len(folders) / items_per_page))  # Рассчитываем количество страниц

#         inline_folders = []  # Пустой массив для инлайн кнопок с названиями папок и коллбэками в виде их ключей
#         self.folders_names.clear()

#         i = 0

#         # Создаем список с Inline-кнопками только для элементов на текущей странице
#         for folder in folders[start_index:end_index]:
#             #  Меняем название папки на users
#             if folder.lower() == 'пользователи' or folder.lower() == '%1$d пользователей':
#                 name_folder = 'Users'

#             # Присваиваем имя папки
#             else:
#                 name_folder = folder

#             # Если имя папки длиннее 20 символов, укорачиваем его
#             if len(name_folder) > 20:
#                 name_folder = name_folder[:10] + '...' + name_folder[-10:]

#             # Добавляем в массив кнопку с папкой
#             inline_folders.append(InlineKeyboardButton(f'{name_folder}', callback_data=str(i)))
#             # Добавляем папку в словарь по ее ключу
#             self.folders_names[str(i)] = folder
#             i += 1

#         # Создаем маркап с кнопками папок
#         folders_markup = InlineKeyboardMarkup(row_width=2).add(*inline_folders)

#         # Создаем кнопки для переключения между страницами
#         previous_button = InlineKeyboardButton('◀ Предыдущая страница', callback_data='previous_page')
#         next_button = InlineKeyboardButton('Следующая страница ▶', callback_data='next_page')

#         # Добавляем кнопки в маркап
#         if page == 1 and pages > 1:
#             folders_markup.row(next_button)
#         elif page > 1 and page < pages:
#             folders_markup.row(previous_button, next_button)
#         elif pages <= 1:
#             pass
#         else:
#             folders_markup.row(previous_button)

#         # Если путь это диск из массива
#         path = path.replace('None', '')

#         if self.comparison_path(path):
#             go_back_to_drives = InlineKeyboardButton('◀ К дискам', callback_data='back_to_drives')
#             folders_markup.row(go_back_to_drives)
#         else:
#             go_back_to_drives = InlineKeyboardButton('◀ К дискам', callback_data='back_to_drives')
#             go_back_explorer = InlineKeyboardButton('◀ Назад', callback_data='back_explorer')
#             folders_markup.row(go_back_explorer, go_back_to_drives)

#         return all_path, page, folders_markup
    
#     def back_path(self):
#         global path

#         path_list = path.split('\\')
#         path_list.pop(-1)
#         path = ''

#         for i in path_list:
#             if i != '':
#                 path += i
#             if i != path_list[-1] or path[-1] == ':':
#                 path += '\\'

#     def comparison_path(self, path):
#         for i in self.drives_names:
#             i += '\\'
#             if path == i:
#                 return True
#             else:
#                 pass
#         return False


#     script_file_btns = [InlineKeyboardButton('🖥 Запустить', callback_data='run'),
#                         InlineKeyboardButton('📲 Скачать', callback_data='download'),
#                         InlineKeyboardButton('🗑 Удалить', callback_data='delete'),
#                         InlineKeyboardButton('◀ Назад', callback_data='back_explorer')]

#     script_file_markup = InlineKeyboardMarkup(row_width=1).add(*script_file_btns)
