import configparser
import json
import random

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

import actions_manager
import bot_manager

config=configparser.ConfigParser()
config.read("config.ini", encoding='utf-8')

class Keyboard():
    """Кнопки"""

    BUTTONS_MENU = [
        ('🖼Медиа','⚙️ПК', '📱Информация',),
        ('🗂Программы','🧠ChatGPT', '🪄Сценарии',),
        ('🌐Интернет',),
    ]
    BUTTONS_VIDEO = [
        ('Звук🔈',),
        ('🔉', '🔇', '🔊'),
        ('⬅️','⏸','➡️',),
        ('◀️Видео', 'Видео▶️',),
        ('🖥Во весь экран',),
        ('🔗Открыть ссылку',),
        ('🧩Меню', '🖼Медиа',),
    ]
    BUTTONS_MUSIC = [
        ('Звук🔈',),
        ('🔉', '🔇', '🔊'),
        ('⏮', '⏯', '⏭'),
        ('🧩Меню', '🖼Медиа',),
    ]
    BUTTONS_MEDIA = [
        ('📹Видео',),
        ('🎧Музыка',),
        ('🧩Меню',),
    ]
    BUTTONS_CONTROL_PC = [
            ('🖥Характеристики ПК', '📁Папки'),
            ('🔒Блокировка', '☀️Яркость', '❌Закрыть',),
            ('🖼Сменить обои','💬Смс на экран', '🗑Очисти корзину',),
            ('🖼Скрин Веб-камеры', '🖼Скрин',),
            ('🔋Управление питанием ПК','⌨️Управление девайсами ПК',),
            ('🗒Диспетчер задач',),
            ('🧩Меню',),
    ]
    BUTTONS_CONTROL_POWER =[
        ('😴Спящий режим', '💤Гибернация','🔄Перезагрузка',),
        ('🚫Выключение ПК',),
        ('⏳Таймер на выключение ПК',),
        ('❌Отмена таймера',),
        ('🧩Меню','⚙️ПК',),
    ]
    BUTTONS_CONTROL_DEVICES = [
        ('🖱Управление мышкой',),
        ('⌨️Управление клавиатурой',),
        ('🖥Отключить монитор',),
        ('🧩Меню','⚙️ПК',),
    ]
    BUTTONS_CONTROL_MOUSE = [
        ('ЛКМ','ПКМ',),
        ('🔼',),
        ('◀️','🔽','▶️',),
        ('🖱Перемещение по X,Y',),
        ('🧩Меню','⌨️Управление девайсами ПК',),
    ]
    BUTTONS_INFO = [
            ('💵Доллар','🤑Биткоин','💶Евро',),
            ('⛅️Погода','🕘Дата',),
            ('🧩Меню',),
    ]
    BUTTONS_INTERNET = [
            ('🌐Speedtest',),
            ('🔗Открыть ссылку',),
            ('🧩Меню',),
    ]
    BUTTONS_CONTROL_BRIGHTNESS = [
        ( '☀️100%',),
        ('☀️25%', '☀️50%', '☀️75%',),
        ('☀️0%',),
        ('🧩Меню','⚙️ПК',),
    ]
    BUTTONS_CONTROL_KEYBOARD = [
        ('✍️Ввод текста',),
        ('🔠Нажатие кнопки',),
        ('🧩Меню','⌨️Управление девайсами ПК',),
    ]

    BUTTONS_ADMIN = [
        ('🔐Сменить пароль',),
        ('🧹Очистить папку Temp',),
        ('🧩Меню',),
    ]

    def add_buttons(self) -> ReplyKeyboardMarkup:
        """Добавление основных кнопок."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button_row in Keyboard().BUTTONS_MENU:
            buttons.row(*button_row)
            
        if actions_manager.Actions().check_if_admin():
            buttons.row('⚠️Админ')

        if config.getboolean('Settings', 'jarvis'):
            buttons.row('🤖Команда Джарвису')

        return buttons
    
    def add_buttons_admin(self, chat_id) -> None:
        """Добавлене кнопок админа."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_ADMIN:
            menu = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                        '⚠️Админ',
                        reply_markup=menu) 

    def add_buttons_music(self, chat_id) -> None:
        """Добавлене кнопок управления музыкой."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_MUSIC:
            menu = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                        '🎧Музыка',
                        reply_markup=menu)            
    
    def add_buttons_video(self, chat_id) -> None:
        """Добавление видео кнопок."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_VIDEO:
            menu = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                        '📹Видео',
                        reply_markup=menu)

    def add_buttons_menu(self, chat_id) -> ReplyKeyboardMarkup:
        """Добавление основных кнопок."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button_row in Keyboard().BUTTONS_MENU:
            buttons.row(*button_row)
            
        if actions_manager.Actions().check_if_admin():
            buttons.row('⚠️Админ')

        if config.getboolean('Settings', 'jarvis'):
            buttons.row('🤖Команда Джарвису')

        bot_manager.Telegram().bot.send_message(chat_id, 
                            '🧩Меню',
                            reply_markup=buttons
        )

    def add_buttons_media(self, chat_id) -> None:
        """Медиа меню."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_MEDIA:
            menu_media = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id,
                            '🖼Медиа',
                            reply_markup=menu_media)
        
    def add_buttons_control_pc(self, chat_id) -> None:
        """Меню управления ПК."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_CONTROL_PC:
            menu_pc = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            '⚙️Управление ПК',
                            reply_markup=menu_pc)

    def add_buttons_control_power(self, chat_id) -> None:
        """Меню управления питанием ПК."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_CONTROL_POWER:
            menu_pc = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            '🔋Управление питанием ПК',
                            reply_markup=menu_pc)

    def add_buttons_control_devices(self, chat_id) -> None:
        """Меню управления девайсами."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_CONTROL_DEVICES:
            menu_pc = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            '⌨️Управление девайсами ПК',
                            reply_markup=menu_pc)

    def add_buttons_control_mouse(self, chat_id) -> None:
        """Меню управления мышью."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_CONTROL_MOUSE:
            menu_pc = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            '🖱Управление мышкой',
                            reply_markup=menu_pc)
    
    def add_buttons_control_keyboard(self, chat_id) -> None:
        """Меню управления клавиатурой."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_CONTROL_KEYBOARD:
            menu_pc = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            '⌨️Управление клавиатурой',
                            reply_markup=menu_pc)
        
    def add_buttons_info(self, chat_id) -> None:
        """Информационное меню."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_INFO:
            menu_info = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            '📱Информация',
                            reply_markup=menu_info)
        
    def add_buttons_internet(self, chat_id) -> None:
        """Интернет меню."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_INTERNET:
            menu_info = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            '🌐Интернет',
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
            btn = f'Сценарий {script["name"]} {random.choice(emoji)}'
            if len(row_button) < 3:
                row_button.append(btn)
            else:
                BUTTONS.append(row_button)
                row_button = []
                row_button.append(btn)
        BUTTONS.append(row_button)
        
        for button in BUTTONS:
            menu_info = buttons.row(*button)
        
        menu_info = buttons.row('🧩Меню')
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            '🪄Сценарии',
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
            btn = f'Открыть {programm[1]["name"]} {random.choice(emoji)}'
            if len(row_button) < 3:
                row_button.append(btn)
            else:
                BUTTONS.append(row_button)
                row_button = []
                row_button.append(btn)
        BUTTONS.append(row_button)
        
        for button in BUTTONS:
            menu_info = buttons.row(*button)
        
        menu_info = buttons.row('🧩Меню')
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            '🗂Программы',
                            reply_markup=menu_info)
    
    def add_buttons_brightness(self, chat_id) -> None:
        """Меню яркости."""
        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
        
        for button in Keyboard().BUTTONS_CONTROL_BRIGHTNESS:
            menu_info = buttons.row(*button)
        
        bot_manager.Telegram().bot.send_message(chat_id, 
                            '☀️Яркость',
                            reply_markup=menu_info)