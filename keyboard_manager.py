import configparser
import json
import random

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

import actions_manager
import bot_manager

from config_manager import translation

config=configparser.ConfigParser()
config.read("config.ini", encoding='utf-8')


class Keyboard():
    """Кнопки"""

    BUTTONS_MENU = [
        (translation.TG_BOT.BUTTON_MEDIA,translation.TG_BOT.BUTTON_PC, translation.TG_BOT.BUTTON_INFO,),
        (translation.TG_BOT.BUTTON_PROGRAMS,translation.TG_BOT.BUTTON_CHATGPT, translation.TG_BOT.BUTTON_SCRIPTS,),
        (translation.TG_BOT.BUTTON_INTERNET,),
    ]
    BUTTONS_VIDEO = [
        (translation.TG_BOT.BUTTON_VOLUME,),
        (translation.TG_BOT.BUTTON_VOLUME_DOWN, translation.TG_BOT.BUTTON_VOLUME_MUTE, translation.TG_BOT.BUTTON_VOLUME_UP),
        (translation.TG_BOT.BUTTON_VIDEO_GO_BACKWARD,translation.TG_BOT.BUTTON_VIDEO_PLAY_PAUSE,translation.TG_BOT.BUTTON_VIDEO_SKIP_FORWARD,),
        (translation.TG_BOT.BUTTON_VIDEO_PREV_VIDEO, translation.TG_BOT.BUTTON_VIDEO_NEXT_VIDEO,),
        (translation.TG_BOT.BUTTON_VIDEO_FULLSCREEN,),
        (translation.TG_BOT.BUTTON_OPEN_LINK,),
        (translation.TG_BOT.BUTTON_MENU, translation.TG_BOT.BUTTON_MEDIA,),
    ]
    BUTTONS_MUSIC = [
        (translation.TG_BOT.BUTTON_VOLUME,),
        (translation.TG_BOT.BUTTON_VOLUME_DOWN, translation.TG_BOT.BUTTON_VOLUME_MUTE, translation.TG_BOT.BUTTON_VOLUME_UP),
        (translation.TG_BOT.BUTTON_SOUND_PREV_TRACK, translation.TG_BOT.BUTTON_SOUND_PLAY_PAUSE, translation.TG_BOT.BUTTON_SOUND_NEXT_TRACK),
        (translation.TG_BOT.BUTTON_MENU, translation.TG_BOT.BUTTON_MEDIA,),
    ]
    BUTTONS_MEDIA = [
        (translation.TG_BOT.BUTTON_VIDEO,),
        (translation.TG_BOT.BUTTON_MUSIC,),
        (translation.TG_BOT.BUTTON_MENU,),
    ]
    BUTTONS_CONTROL_PC = [
        (translation.TG_BOT.BUTTON_PC_SPEC, translation.TG_BOT.BUTTON_PC_FOLDERS),
        (translation.TG_BOT.BUTTON_PC_LOCK_WORKSTATION, translation.TG_BOT.BUTTON_PC_BRIGHTNESS, translation.TG_BOT.BUTTON_PC_CLOSE_ACTIVE_WINDOW,),
        (translation.TG_BOT.BUTTON_PC_CHANGE_WALLPAPER,translation.TG_BOT.BUTTON_PC_TEXT_ALERT, translation.TG_BOT.BUTTON_PC_CLEAR_RECYCLE_BIN,),
        (translation.TG_BOT.BUTTON_PC_WEBCAM_SCREENSHOT, translation.TG_BOT.BUTTON_PC_SCREENSHOT,),
        (translation.TG_BOT.BUTTON_PC_POWER_MANAGEMENT,translation.TG_BOT.BUTTON_PC_DEVICE_MANAGEMENT,),
        (translation.TG_BOT.BUTTON_PC_TASK_MANAGER,),
        (translation.TG_BOT.BUTTON_MENU,),
    ]
    BUTTONS_CONTROL_POWER =[
        (translation.TG_BOT.BUTTON_POWER_CONTROL_SLEEP, translation.TG_BOT.BUTTON_POWER_CONTROL_HIBERNATE,translation.TG_BOT.BUTTON_POWER_CONTROL_REBOOT,),
        (translation.TG_BOT.BUTTON_POWER_CONTROL_SHUT_DOWN,),
        (translation.TG_BOT.BUTTON_POWER_CONTROL_SHUT_DOWN_TIMER,),
        (translation.TG_BOT.BUTTON_POWER_CONTROL_SHUT_DOWN_TIMER_CANCEL,),
        (translation.TG_BOT.BUTTON_MENU,translation.TG_BOT.BUTTON_PC,),
    ]
    BUTTONS_CONTROL_DEVICES = [
        (translation.TG_BOT.BUTTON_DEVICE_CONTROL_MOUSE,),
        (translation.TG_BOT.BUTTON_DEVICE_CONTROL_KEYBOARD,),
        (translation.TG_BOT.BUTTON_DEVICE_CONTROL_TURN_OFF_MONITOR,),
        (translation.TG_BOT.BUTTON_MENU,translation.TG_BOT.BUTTON_PC,),
    ]
    BUTTONS_CONTROL_MOUSE = [
        (translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOUSE1,translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOUSE2,),
        (translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOVE_UP,),
        (translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOVE_LEFT,translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOVE_DOWN,translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOVE_RIGHT,),
        (translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOVE_TO_COORDINATES,),
        (translation.TG_BOT.BUTTON_MENU,translation.TG_BOT.BUTTON_PC_DEVICE_MANAGEMENT,),
    ]
    BUTTONS_INFO = [
        (translation.TG_BOT.BUTTON_DOLLAR,translation.TG_BOT.BUTTON_BTC,translation.TG_BOT.BUTTON_EURO,),
        (translation.TG_BOT.BUTTON_WEATHER,translation.TG_BOT.BUTTON_DATE,),
        (translation.TG_BOT.BUTTON_MENU,),
    ]
    BUTTONS_INTERNET = [
        (translation.TG_BOT.BUTTON_SPEEDTEST,),
        (translation.TG_BOT.BUTTON_OPEN_LINK,),
        (translation.TG_BOT.BUTTON_MENU,),
    ]
    BUTTONS_CONTROL_BRIGHTNESS = [
        (translation.TG_BOT.BUTTON_BRIGHTNESS_SET_100_PCT,),
        (translation.TG_BOT.BUTTON_BRIGHTNESS_SET_25_PCT, translation.TG_BOT.BUTTON_BRIGHTNESS_SET_50_PCT, translation.TG_BOT.BUTTON_BRIGHTNESS_SET_75_PCT,),
        (translation.TG_BOT.BUTTON_BRIGHTNESS_SET_0_PCT,),
        (translation.TG_BOT.BUTTON_MENU,translation.TG_BOT.BUTTON_PC,),
    ]
    BUTTONS_CONTROL_KEYBOARD = [
        (translation.TG_BOT.BUTTON_KEYBOARD_CONTROL_TYPE,),
        (translation.TG_BOT.BUTTON_KEYBOARD_CONTROL_PRESS_BUTTON,),
        (translation.TG_BOT.BUTTON_MENU,translation.TG_BOT.BUTTON_PC_DEVICE_MANAGEMENT,),
    ]

    BUTTONS_ADMIN = [
        (translation.TG_BOT.BUTTON_ADMIN_CHANGE_PASSWORD,),
        (translation.TG_BOT.BUTTON_ADMIN_CLEAR_TEMP_FOLDER,),
        (translation.TG_BOT.BUTTON_MENU,),
    ]

    def add_buttons(self) -> ReplyKeyboardMarkup:
        """Добавление основных кнопок."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button_row in Keyboard().BUTTONS_MENU:
            buttons.row(*button_row)
            
        if actions_manager.Actions().check_if_admin():
            buttons.row(translation.TG_BOT.BUTTON_ADMIN)

        if config.getboolean('Settings', 'jarvis'):
            buttons.row(translation.TG_BOT.BUTTON_COMMAND_FOR_JARVIS)

        return buttons
    
    def add_buttons_admin(self, chat_id) -> None:
        """Добавлене кнопок админа."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_ADMIN:
            menu = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                        translation.TG_BOT.MSG_ADMIN,
                        reply_markup=menu) 

    def add_buttons_music(self, chat_id) -> None:
        """Добавлене кнопок управления музыкой."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_MUSIC:
            menu = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                        translation.TG_BOT.BUTTON_MUSIC,
                        reply_markup=menu)            
    
    def add_buttons_video(self, chat_id) -> None:
        """Добавление видео кнопок."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_VIDEO:
            menu = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                        translation.TG_BOT.BUTTON_VIDEO,
                        reply_markup=menu)

    def add_buttons_menu(self, chat_id) -> ReplyKeyboardMarkup:
        """Добавление основных кнопок."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button_row in Keyboard().BUTTONS_MENU:
            buttons.row(*button_row)
            
        if actions_manager.Actions().check_if_admin():
            buttons.row(translation.TG_BOT.BUTTON_ADMIN)

        if config.getboolean('Settings', 'jarvis'):
            buttons.row(translation.TG_BOT.BUTTON_COMMAND_FOR_JARVIS)

        bot_manager.Telegram().bot.send_message(chat_id, 
                            translation.TG_BOT.BUTTON_MENU,
                            reply_markup=buttons
        )

    def add_buttons_media(self, chat_id) -> None:
        """Медиа меню."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_MEDIA:
            menu_media = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id,
                            translation.TG_BOT.BUTTON_MEDIA,
                            reply_markup=menu_media)
        
    def add_buttons_control_pc(self, chat_id) -> None:
        """Меню управления ПК."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_CONTROL_PC:
            menu_pc = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            translation.TG_BOT.MSG_PC,
                            reply_markup=menu_pc)

    def add_buttons_control_power(self, chat_id) -> None:
        """Меню управления питанием ПК."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_CONTROL_POWER:
            menu_pc = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            translation.TG_BOT.BUTTON_PC_POWER_MANAGEMENT,
                            reply_markup=menu_pc)

    def add_buttons_control_devices(self, chat_id) -> None:
        """Меню управления девайсами."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_CONTROL_DEVICES:
            menu_pc = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            translation.TG_BOT.BUTTON_PC_DEVICE_MANAGEMENT,
                            reply_markup=menu_pc)

    def add_buttons_control_mouse(self, chat_id) -> None:
        """Меню управления мышью."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_CONTROL_MOUSE:
            menu_pc = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            translation.TG_BOT.BUTTON_DEVICE_CONTROL_MOUSE,
                            reply_markup=menu_pc)
    
    def add_buttons_control_keyboard(self, chat_id) -> None:
        """Меню управления клавиатурой."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_CONTROL_KEYBOARD:
            menu_pc = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            translation.TG_BOT.BUTTON_DEVICE_CONTROL_KEYBOARD,
                            reply_markup=menu_pc)
        
    def add_buttons_info(self, chat_id) -> None:
        """Информационное меню."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_INFO:
            menu_info = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            translation.TG_BOT.BUTTON_INFO,
                            reply_markup=menu_info)
        
    def add_buttons_internet(self, chat_id) -> None:
        """Интернет меню."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_INTERNET:
            menu_info = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            translation.TG_BOT.BUTTON_INTERNET,
                            reply_markup=menu_info)
    
    def add_buttons_script(self, chat_id) -> None:
        """Меню программ."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        emoji = ['❤️','🧡','💛','💚','💙','💜']
        row_button = []
        BUTTONS = []
        
        with open('data_script.json', encoding='utf-8') as f:
            data = json.load(f)
        
        for script in data:
            btn = translation.TG_BOT.BUTTON_SCRIPT_OPEN.format(script_name=script["name"], emoji=random.choice(emoji))
            if len(row_button) < 3:
                row_button.append(btn)
            else:
                BUTTONS.append(row_button)
                row_button = []
                row_button.append(btn)
        BUTTONS.append(row_button)
        
        for button in BUTTONS:
            menu_info = buttons.row(*button)
        
        menu_info = buttons.row(translation.TG_BOT.BUTTON_MENU)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            translation.TG_BOT.BUTTON_SCRIPTS,
                            reply_markup=menu_info)

    def add_buttons_program(self, chat_id) -> None:
        """Меню программ."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        emoji = ['❤️','🧡','💛','💚','💙','💜']
        row_button = []
        BUTTONS = []
        
        with open('data_program.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for programm in enumerate(data):
            btn = translation.TG_BOT.BUTTON_PROGRAM_OPEN.format(program_name=programm[1]["name"], emoji=random.choice(emoji))
            if len(row_button) < 3:
                row_button.append(btn)
            else:
                BUTTONS.append(row_button)
                row_button = []
                row_button.append(btn)
        BUTTONS.append(row_button)
        
        for button in BUTTONS:
            menu_info = buttons.row(*button)
        
        menu_info = buttons.row(translation.TG_BOT.BUTTON_MENU)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            translation.TG_BOT.BUTTON_PROGRAMS,
                            reply_markup=menu_info)
    
    def add_buttons_brightness(self, chat_id) -> None:
        """Меню яркости."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_CONTROL_BRIGHTNESS:
            menu_info = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            translation.TG_BOT.BUTTON_PC_BRIGHTNESS,
                            reply_markup=menu_info)