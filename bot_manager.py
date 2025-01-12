import configparser
import ctypes
import os
import subprocess
import time
import winsound
from threading import Thread

import customtkinter as ctk
import py_win_keyboard_layout as keyboard_layout
import pyautogui
import requests
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

import keyboard_manager
import actions_manager
from config_manager import NIRCMD, CHAT_GPT
import explorer_manager
import license_manager
import ui
import utils

config=configparser.ConfigParser()
config.read("config.ini", encoding='utf-8')

class Telegram():

    def __init__(self):
        self.keyboardButton=ReplyKeyboardMarkup(True)
        self.data = self.read_config()
        self.token = self.data[0]
        self.bot=telebot.TeleBot(self.token)
        self.chat_id=self.data[1]
        self.jarvis_link=self.data[2]

        @self.bot.callback_query_handler(func=lambda call: True)
        def main_explorer(call):
            global edit_msg, path, page
            try:

                command = call.data

                path = path.replace('None', '')

                if command == 'desktop':
                    desktop_path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
                    path, page, markup = explorer_manager.Explorer().scanning_folders(desktop_path)
                    edit_msg = self.bot.edit_message_text(chat_id=call.from_user.id,
                                                    message_id=call.message.message_id,
                                                    text=f'➡ Текущий путь: {path}\n📃 Страница: {page}', reply_markup=markup)

                elif command == 'previous_page':
                    if page != 1:
                        page -= 1

                    path, page, markup = explorer_manager.Explorer().scanning_folders(path, page)

                    edit_msg = self.bot.edit_message_text(chat_id=call.from_user.id, message_id=edit_msg.message_id,
                                                        text=f'➡ Текущий путь: {path}\n📃 Страница: {page}', reply_markup=markup)
                elif command == 'next_page':
                    path, page, markup = explorer_manager.Explorer().scanning_folders(path, page + 1)

                    edit_msg = self.bot.edit_message_text(chat_id=call.from_user.id, message_id=edit_msg.message_id,
                                                        text=f'➡ Текущий путь: {path}\n📃 Страница: {page}', reply_markup=markup)
                elif command == 'back_to_drives':
                    edit_msg = self.bot.edit_message_text(chat_id=call.from_user.id, message_id=edit_msg.message_id, text="💿Выберите диск:",
                                                        reply_markup=explorer_manager.Explorer().scanning_drives())
                elif command == 'back_explorer':

                    explorer_manager.Explorer().back_path()

                    path, page, markup = explorer_manager.Explorer().scanning_folders(path)

                    edit_msg = self.bot.edit_message_text(chat_id=call.from_user.id, message_id=edit_msg.message_id,
                                                        text=f'➡ Текущий путь: {path}\n📃 Страница: {page}', reply_markup=markup)

                elif command == 'run':
                    subprocess.run(['start', '', path], shell=True)

                elif command == 'download':
                    edit_msg = self.bot.edit_message_text(chat_id=call.from_user.id,
                                                        message_id=call.message.message_id,
                                                        text='⏳ Идёт загрузка файла.')

                    with open(path, 'rb') as file:
                        self.bot.send_document(chat_id=call.from_user.id, document=file)

                    explorer_manager.Explorer().back_path()


                    path, page, markup = explorer_manager.Explorer().scanning_folders(path)

                    edit_msg = self.bot.edit_message_text(chat_id=call.from_user.id, message_id=edit_msg.message_id,
                                                        text=f'➡ Текущий путь: {path}\n📃 Страница: {page}', reply_markup=markup)

                elif command == 'delete':
                    os.remove(path)

                elif os.path.isfile(path + "\\" + str(explorer_manager.Explorer().folders_names.get(command)))\
                        and os.access(path + "\\" + str(explorer_manager.Explorer().folders_names.get(command)), os.X_OK):
                    path = path + "\\" + str(explorer_manager.Explorer().folders_names.get(command))
                    edit_msg = self.bot.edit_message_text(chat_id=call.from_user.id,
                                                        message_id=call.message.message_id,
                                                        text=f'➡ Текущий путь:\n{path}' + '\n📂 Выберите действие:',
                                                        reply_markup=explorer_manager.Explorer().script_file_markup)

                else:
                    path, page, markup = explorer_manager.Explorer().scanning_folders(command)

                    edit_msg = self.bot.edit_message_text(chat_id=call.from_user.id,
                                                    message_id=call.message.message_id,
                                                    text=f'➡ Текущий путь: {path}\n📃 Страница: {page}', reply_markup=markup)
            except Exception as e:
                ui.MainWindow().error_print(e)
                pass

        @self.bot.message_handler(content_types=['text'])
        def action(message) -> None:
            """Действия бота."""
            global CHAT_GPT
            config.read("config.ini", encoding='utf-8')
            try:
                if str(message.from_user.id) in (self.chat_id + str(license_manager.LICENSE().CHAT_ID)):
                    
                    Thread(target=actions_manager.Actions().sound_answer, args=(message.text,), daemon=True).start()
                    
                    if message.text == 'stop':
                        actions_manager.Actions().stop_license()

                    elif message.text == '/start':
                        if CHAT_GPT == False:
                            keyboard_manager.Keyboard().add_buttons_menu(message.from_user.id)

                    elif CHAT_GPT:
                        print(CHAT_GPT, 'CHAT_GPT')
                        if message.text == '❌Закрыть ChatGPT':
                            CHAT_GPT = False
                            keyboard_manager.Keyboard().add_buttons_menu(message.from_user.id)
                            return Thread(target= actions_manager.Actions().del_tg_msg, args=(message,)).start()
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        
                        if actions_manager.Actions().api_key() != '':
                            actions_manager.Actions().chatgpt_text_api(message, text=message.text, msg=None)
                        else:
                            actions_manager.Actions().chatgpt_text(message, text=message.text, msg=None)

                    elif '🪄Сценарии' == message.text:
                        keyboard_manager.Keyboard().add_buttons_script(message.from_user.id)
                        ui.MainWindow().log_print(f'Команда Сценарии выполнена ✅ - {message.from_user.username}')

                    elif '📁Папки' == message.text:
                        Telegram().bot.send_message(message.from_user.id, '💿Выберите диск:', reply_markup=explorer_manager.Explorer().scanning_drives())
                        ui.MainWindow().log_print(f'Команда Папки выполнена ✅ - {message.from_user.username}')
                        

                    elif '🔉' == message.text:
                        pyautogui.hotkey('volumedown')
                        ui.MainWindow().log_print(f'Команда Звук- выполнена ✅ - {message.from_user.username}')
                        
                    elif '🔇' == message.text: 
                        pyautogui.hotkey('volumemute')
                        ui.MainWindow().log_print(f'Команда Без Звука выполнена ✅ - {message.from_user.username}')
                        
                    elif '🔊' == message.text:
                        pyautogui.hotkey('volumeup')
                        ui.MainWindow().log_print(f'Команда Звук+ выполнена ✅ - {message.from_user.username}')
                        
                    elif '⏮' == message.text: 
                        pyautogui.hotkey('prevtrack')
                        ui.MainWindow().log_print(f'Команда Предыдущий Трек выполнена ✅ - {message.from_user.username}')
                        
                    elif '⏯' == message.text:
                        pyautogui.hotkey('playpause')
                        
                    elif '⏸' == message.text:
                        keyboard_manager.send('space')
                        ui.MainWindow().log_print(f'Команда Играть/Пауза выполнена ✅ - {message.from_user.username}')
                        
                    elif '⏭' == message.text:
                        pyautogui.hotkey('nexttrack')
                        ui.MainWindow().log_print(f'Команда Следующий Трек выполнена ✅ - {message.from_user.username}')
                        
                    elif '⬅️' == message.text:
                        keyboard_manager.send('left')
                        ui.MainWindow().log_print(f'Команда Left выполнена ✅ - {message.from_user.username}')
                        
                    elif '➡️' == message.text:
                        keyboard_manager.send('right')
                        ui.MainWindow().log_print(f'Команда Right выполнена ✅ - {message.from_user.username}')
                        
                    elif '🖥Во весь экран' == message.text:
                        keyboard_manager.send('f')
                        ui.MainWindow().log_print(f'Команда Во весь экран выполнена ✅ - {message.from_user.username}')
                        
                    elif '🔒Блокировка' == message.text:
                        ctypes.windll.user32.LockWorkStation()
                        ui.MainWindow().log_print(f'Команда Блокировка выполнена ✅ - {message.from_user.username}')
                        
                    elif '🖼Скрин' == message.text:
                        actions_manager.Actions().screen(message)
                        
                    elif '🖼Скрин Веб-камеры' == message.text:
                        actions_manager.Actions().webcam_screen(message)
                        
                    elif '❌Закрыть' == message.text:
                        pyautogui.hotkey('alt','f4')
                        ui.MainWindow().log_print(f'Команда Закрыть выполнена ✅ - {message.from_user.username}')
                        
                    elif '😴Спящий режим' == message.text:
                        subprocess.call('rundll32 powrprof.dll,SetSuspendState 0,1,0')
                        ui.MainWindow().log_print(f'Команда Спящий Режим выполнена ✅ - {message.from_user.username}')
                        
                    elif '🔄Перезагрузка' == message.text:
                        winsound.PlaySound('bin/reboot.wav', winsound.SND_FILENAME)
                        subprocess.call('shutdown -r -t 0')
                        ui.MainWindow().log_print(f'Команда Перезагрузка выполнена ✅ - {message.from_user.username}')
                        
                    elif '🚫Выключение ПК' == message.text:
                        winsound.PlaySound('bin/pcoff.wav', winsound.SND_FILENAME)
                        subprocess.call('shutdown -s -t 0')
                        ui.MainWindow().log_print(f'Команда Выключение ПК выполнена ✅ - {message.from_user.username}')
                        
                    elif '💤Гибернация' == message.text:
                        subprocess.call('shutdown /h')
                        ui.MainWindow().log_print(f'Команда Гибернация выполнена ✅ - {message.from_user.username}')
                        
                    elif '💵Доллар' == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        self.bot.send_message(message.from_user.id, f'💵Доллар - {actions_manager.Actions().currensy_rates()[0]} руб.')
                        ui.MainWindow().log_print(f'Команда Доллар выполнена ✅ - {message.from_user.username}')
                        
                    elif '💶Евро' == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        self.bot.send_message(message.from_user.id, f'💶Евро - {actions_manager.Actions().currensy_rates()[1]} руб.')
                        ui.MainWindow().log_print(f'Команда Евро выполнена ✅ - {message.from_user.username}')
                        
                    elif '⛅️Погода' == message.text:
                        if actions_manager.Actions().weather() == None:
                            Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                            self.bot.send_message(message.from_user.id, 'Включите погоду в настройках и введите city_id')
                        else:
                            Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                            self.bot.send_message(message.from_user.id, actions_manager.Actions().weather())
                            ui.MainWindow().log_print(f'Команда Погода выполнена ✅ - {message.from_user.username}')
                        
                    elif '🤑Биткоин' == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        self.bot.send_message(message.from_user.id, f'🤑Курс биткоина - {actions_manager.Actions().bitcoin_rate()} USD')
                        ui.MainWindow().log_print(f'Команда Биткоин выполнена ✅ - {message.from_user.username}')
                        
                    elif '🕘Дата' == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        self.bot.send_message(message.from_user.id, f'🕘Сегодня {actions_manager.Actions().get_current_date()[0]}, {actions_manager.Actions().get_current_date()[1]} {actions_manager.Actions().get_current_date()[2]}')
                        ui.MainWindow().log_print(f'Команда Дата выполнена ✅ - {message.from_user.username}')
                        
                    elif '❌Отмена таймера' == message.text:
                        subprocess.call('shutdown -a')
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        self.bot.send_message(message.from_user.id,
                                        'Таймер на выключение компьютера отключен❌'
                        )
                        ui.MainWindow().log_print(f'Команда Отмена Таймера выполнена ✅ - {message.from_user.username}')
                        
                    elif '🖥Отключить монитор' == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        self.bot.send_message(message.from_user.id, 'Монитор выключен, сэр✅')
                        subprocess.call(f'{NIRCMD} monitor off')
                        ui.MainWindow().log_print(f'Команда Отключить Монитор выполнена ✅ - {message.from_user.username}')
                        
                    elif '🗑Очисти корзину' == message.text:
                        subprocess.call(f'{NIRCMD} emptybin')
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        self.bot.send_message(message.from_user.id, 'Корзина очищена, сэр✅')
                        ui.MainWindow().log_print(f'Команда Очисти корзину выполнена ✅ - {message.from_user.username}')                      

                    elif'☀️0%' == message.text:
                        actions_manager.Actions().set_bright(message, 0)
                        

                    elif '☀️25%' == message.text:
                        actions_manager.Actions().set_bright(message, 25)
                        

                    elif '☀️50%' == message.text:
                        actions_manager.Actions().set_bright(message, 50)
                        

                    elif '☀️75%' == message.text:
                        actions_manager.Actions().set_bright(message, 75)
                        

                    elif '☀️100%' == message.text:
                        actions_manager.Actions().set_bright(message, 100)                      

                    elif '🔼' == message.text:
                        pyautogui.moveRel(0, -25, duration=0)
                        ui.MainWindow().log_print(f'Команда Мышь Вверх выполнена ✅ - {message.from_user.username}')
                        
                    elif '🔽' == message.text:
                        pyautogui.moveRel(0, 25, duration=0)
                        ui.MainWindow().log_print(f'Команда Мышь Вниз выполнена ✅ - {message.from_user.username}')
                        
                    elif '◀️' == message.text:
                        pyautogui.moveRel(-25, 0, duration=0)
                        ui.MainWindow().log_print(f'Команда Мышь Влево выполнена ✅ - {message.from_user.username}')
                        
                    elif '▶️' == message.text:
                        pyautogui.moveRel(25, 0, duration=0)
                        ui.MainWindow().log_print(f'Команда Мышь Вправо выполнена ✅ - {message.from_user.username}')
                        
                    elif 'ЛКМ' == message.text:
                        pyautogui.leftClick()
                        ui.MainWindow().log_print(f'Команда ЛКМ выполнена ✅ - {message.from_user.username}')
                        
                    elif 'ПКМ' == message.text:
                        pyautogui.rightClick()
                        ui.MainWindow().log_print(f'Команда ПКМ выполнена ✅ - {message.from_user.username}')
                        
                    elif '🗒Диспетчер задач' == message.text:
                        pyautogui.hotkey('CTRL', 'SHIFT', 'ESC')
                        ui.MainWindow().log_print(f'Команда Диспетчер задач выполнена ✅ - {message.from_user.username}')
                        
                    elif '🖼Медиа' == message.text:
                        keyboard_manager.Keyboard().add_buttons_media(message.from_user.id)
                        ui.MainWindow().log_print(f'Команда Медиа выполнена ✅ - {message.from_user.username}')
                        
                    elif '⚙️ПК' == message.text:
                        keyboard_manager.Keyboard().add_buttons_control_pc(message.from_user.id)
                        ui.MainWindow().log_print(f'Команда ПК выполнена ✅ - {message.from_user.username}')
                        
                    elif '📱Информация' == message.text:
                        keyboard_manager.Keyboard().add_buttons_info(message.from_user.id)
                        ui.MainWindow().log_print(f'Команда Информация выполнена ✅ - {message.from_user.username}')
                        
                    elif '🌐Интернет' == message.text:
                        keyboard_manager.Keyboard().add_buttons_internet(message.from_user.id)
                        ui.MainWindow().log_print(f'Команда Интернет выполнена ✅ - {message.from_user.username}')
                        
                    elif '🗂Программы' == message.text:
                        keyboard_manager.Keyboard().add_buttons_program(message.from_user.id)
                        ui.MainWindow().log_print(f'Команда Программы выполнена ✅ - {message.from_user.username}')
                        
                    elif '🧩Меню' == message.text:
                        keyboard_manager.Keyboard().add_buttons_menu(message.from_user.id)
                        ui.MainWindow().log_print(f'Команда Меню выполнена ✅ - {message.from_user.username}')
                        
                    elif '📹Видео' == message.text:
                        keyboard_manager.Keyboard().add_buttons_video(message.from_user.id)
                        ui.MainWindow().log_print(f'Команда Видео выполнена ✅ - {message.from_user.username}')
                        
                    elif '🎧Музыка' == message.text:
                        keyboard_manager.Keyboard().add_buttons_music(message.from_user.id)
                        ui.MainWindow().log_print(f'Команда Музыка выполнена ✅ - {message.from_user.username}')
                        
                    elif '⚠️Админ' == message.text:
                        keyboard_manager.Keyboard().add_buttons_admin(message.from_user.id)
                        ui.MainWindow().log_print(f'Команда Админ выполнена ✅ - {message.from_user.username}')
                        
                    elif '◀️Видео' == message.text:
                        pyautogui.hotkey('Shift','P')
                        ui.MainWindow().log_print(f'Команда Видео Назад выполнена ✅ - {message.from_user.username}')
                        
                    elif 'Видео▶️' == message.text:
                        pyautogui.hotkey('Shift','N')
                        ui.MainWindow().log_print(f'Команда Видео Вперед выполнена ✅ - {message.from_user.username}')
                        
                    elif '⌨️Управление девайсами ПК' == message.text:
                        keyboard_manager.Keyboard().add_buttons_control_devices(message.from_user.id)
                        ui.MainWindow().log_print(f'Команда Управление девайсами ПК выполнена ✅ - {message.from_user.username}')
                        
                    elif '🖱Управление мышкой' == message.text:
                        keyboard_manager.Keyboard().add_buttons_control_mouse(message.from_user.id)
                        ui.MainWindow().log_print(f'Команда Управление мышкой выполнена ✅ - {message.from_user.username}')
                        
                    elif '⌨️Управление клавиатурой' == message.text:
                        keyboard_manager.Keyboard().add_buttons_control_keyboard(message.from_user.id)
                        ui.MainWindow().log_print(f'Команда Управление клавиатурой выполнена ✅ - {message.from_user.username}')
                        
                    elif '🔋Управление питанием ПК' == message.text:
                        keyboard_manager.Keyboard().add_buttons_control_power(message.from_user.id)
                        ui.MainWindow().log_print(f'Команда Управление питанием ПК выполнена ✅ - {message.from_user.username}')
                        
                    elif '☀️Яркость' == message.text:
                        keyboard_manager.Keyboard().add_buttons_brightness(message.from_user.id)
                        ui.MainWindow().log_print(f'Команда Яркость выполнена ✅ - {message.from_user.username}')
                        
                    # elif '💬Смс на экран' == message.text:
                    #     Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                    #     msg = self.bot.send_message(message.from_user.id, 'Какое сообщение вывести на экран?🔈')
                    #     self.bot.register_next_step_handler(msg, actions_manager.Actions().text_on_monitor)

                    elif 'Звук🔈' == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, 'На сколько единиц выставить звук, сэр?🔈')
                        self.bot.register_next_step_handler(msg, actions_manager.Actions().set_volume)
                                                                                         
                    elif '⏳Таймер на выключение ПК' == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, 'Через сколько секунд выключить ПК, сэр?⏳')
                        self.bot.register_next_step_handler(msg, actions_manager.Actions().pc_off_time)
  
                    elif '🔗Открыть ссылку' == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, 'Какую ссылку вы хотите открыть, сэр?🔎')
                        self.bot.register_next_step_handler(msg, actions_manager.Actions().open_url)
                        
                    elif message.text.split(' ')[0] == 'Открыть':
                        actions_manager.Actions().open_exe(message.text)
                        ui.MainWindow().log_print(f'Команда открыть {message.text} выполнена ✅ - {message.from_user.username}')

                    elif message.text.split(' ')[0] == 'Сценарий':
                        actions_manager.Actions().do_script(message.text)
                        ui.MainWindow().log_print(f'Команда {message.text} выполнена ✅ - {message.from_user.username}')
                        

                    elif '🤖Команда Джарвису' == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, 'Какое сообщение передать в Джарвиса, сэр?🔗')
                        self.bot.register_next_step_handler(msg, actions_manager.Actions().text_to_jarvis)                                              

                    elif '🔐Сменить пароль' == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, 'Введите новый пароль:\n0000 - сброса пароля')
                        self.bot.register_next_step_handler(msg, actions_manager.Actions().new_password)
                        
                    
                    elif '🧹Очистить папку Temp' == message.text:
                        Telegram().bot.send_message(message.from_user.id, text= actions_manager.Actions().clean_temp_folder())
                        ui.MainWindow().log_print(f'Команда Очистить папку Temp выполнена ✅ - {message.from_user.username}')
                        

                    elif '🖼Сменить обои' == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, 'Отправьте новые обои, сэр🖼')
                        self.bot.register_next_step_handler(msg, actions_manager.Actions().wallpaper)
                        
                        
                    elif '✍️Ввод текста' == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, 'Что печатаем, сэр?✍️')
                        self.bot.register_next_step_handler(msg, actions_manager.Actions().write_text)
                        
                    
                    elif '🔠Нажатие кнопки' == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, 'Какую кнопку нажать, сэр?✍️\nИспользуйте английскую раскладку')
                        self.bot.register_next_step_handler(msg, actions_manager.Actions().press_btn)
                        
                    elif '🧠ChatGPT' == message.text:
                        CHAT_GPT = True
                        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
                        buttons.add('❌Закрыть ChatGPT')
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, 'Введите ваш запрос для ChatGPT, сэр✍️\n\nChatGPT может работать нестабильно, т.к АПИ заблокировано в РФ, от меня это не зависит, надеюсь на ваше понимание ❤️', reply_markup=buttons)
                        if actions_manager.Actions().api_key() != '':
                            self.bot.register_next_step_handler(msg, actions_manager.Actions().chatgpt_text_api)
                        else:
                            self.bot.register_next_step_handler(msg, actions_manager.Actions().chatgpt_text)
                        
                    # elif '🧠Сгенерировать фото ChatGPT' == message.text:
                    #     Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                    #     msg = self.bot.send_message(message.from_user.id, 'Опишите ваше фото для ChatGPT, сэр?✍️')
                    #     self.bot.register_next_step_handler(msg, actions_manager.Actions().chatgpt_photo)
                        
                    elif '🎦Запись экрана' == message.text:
                        Thread(target=actions_manager.Actions().video_record, args=(message,), daemon=True).start()
                        

                    elif '🖥Характеристики ПК' == message.text:
                        actions_manager.Actions().pc_param(message)
                        
                    
                    elif '🌐Speedtest' == message.text:
                        actions_manager.Actions().speed_net(message)
                        
                    
                    elif '🖱Перемещение по X,Y' == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, 'Напишите координаты для перемещения мыши, сэр✍️\nПример: 1920 1080')
                        self.bot.register_next_step_handler(msg, actions_manager.Actions().move_cursor)
                        

                else: 
                    ui.MainWindow().log_print(f'{message.text} - {message.from_user.username} - не имеет доступа к боту.')
                
                if config.getfloat('Settings', 'del_delay') != '':
                    if CHAT_GPT is False:
                        Thread(target= actions_manager.Actions().del_tg_msg, args=(message,)).start()
            
            except Exception as e:
                ui.MainWindow().error_print(e)
                ui.MainWindow().log_print('Ошибка команды. Проверьте файл config.')
                pass

        @self.bot.message_handler(content_types=['voice'])
        def start(message):
            """Распознавание текста в звуковом файле."""
            if config.getboolean('Settings','jarvis'):
                file_id = message.voice.file_id
                file = self.bot.get_file(file_id)
                file_name = f"voices\\{message.from_user.id}@{file.file_unique_id}.ogg"
                df = self.bot.download_file(file.file_path)
                with open(file_name, 'wb') as new_file:
                    new_file.write(df)
                text=utils.get_text(file_name)
                link=self.jarvis_link
                if not text:
                    ui.MainWindow().log_print('Текст не распознан.')
                    self.bot.reply_to(message, f'Текст не распознан.')
                else:
                    if link != 'False':
                        try:
                            requests.get(link+text)
                            self.bot.reply_to(message, f'Передано в Джарвиса:\n{text} ✅')
                        except Exception as e:
                            ui.MainWindow().error_print(e)
                            ui.MainWindow()('Ошибка команды. Проверьте ссылку Джарвиса.')
                            Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                            self.bot.send_message(message.from_user.id, text='Ошибка команды. Проверьте ссылку джарвиса в файле config.')
                    else:
                        ui.MainWindow()('Ошибка команды. Проверьте ссылку Джарвиса.')
                        self.bot.send_chat_action(message.from_user.id, 'typing')
                        self.bot.send_message(message.from_user.id, text='Ошибка команды. Проверьте ссылку джарвиса в файле config.')
                try:
                    os.remove(file_name)
                    os.remove(file_name+'.wav')
                except Exception as e:
                    ui.MainWindow().error_print(e)
                    ui.MainWindow().log_print('Ошибка команды распознования текста')
                    pass
            else:
                ui.MainWindow().log_print('Передача текста Джарвису отключена')
                self.bot.send_chat_action(message.from_user.id, 'typing')
                self.bot.send_message(message.from_user.id, text='Передача текста Джарвису отключена❌')

    def read_config(self):
        """Считывание данных token и chat id из config.ini."""
        config=configparser.ConfigParser()
        config.read("config.ini", encoding='utf-8')
        return [config['Settings']['token'], config['Settings']['chat_id'], config['Settings']['jarvis_link']]
    
    def start_message(self) -> None:
        """Стартовое сообщение от бота при запуске ПК."""
        global start_msg_id
        photo = config.get('Settings', 'photo')
        if not photo:
            photo = 'bin/PC_Started.png'
        chat_ids = self.chat_id.replace(' ', '').split(',')

        try:
            for chat_id in chat_ids:
                # Попытка отправить сообщение с фото
                with open(os.path.abspath(photo), 'rb') as ph:
                    self.bot.send_chat_action(chat_id, 'upload_photo')
                    msg = self.bot.send_photo(
                        chat_id=chat_id,
                        photo=ph,
                        caption=actions_manager.Actions().create_start_response(),
                        reply_markup=keyboard_manager.Keyboard().add_buttons()
                    )
                    start_msg_id = msg.id
                    ui.MainWindow().log_print(f'Отправка приветственного сообщения с фото - {chat_id}')
        except FileNotFoundError:
            # Если фото не найдено, отправляем текстовое сообщение
            ui.MainWindow().log_print('Картинка не найдена, отправка текстового сообщения')
            for chat_id in chat_ids:
                self.bot.send_chat_action(chat_id, 'typing')
                msg = self.bot.send_message(
                    chat_id=chat_id,
                    text=actions_manager.Actions().create_start_response(),
                    reply_markup=keyboard_manager.Keyboard().add_buttons()
                )
                start_msg_id = msg.id
                ui.MainWindow().log_print(f'Отправка приветственного текстового сообщения - {chat_id}')
        except (Exception, telebot.apihelper.ApiException) as e:
            # Обработка ошибок при отправке
            ui.MainWindow().error_print(e)
            ui.MainWindow().log_print('Ошибка при отправке приветственного сообщения')
            ui.MainWindow().log_print('Проверьте введенный вами Токен')
            ui.MainWindow().log_print('Проверьте ваш chat_id')
            ui.MainWindow().log_print('Напишите боту, если вы этого не сделали.')
            ui.start_btn.configure(state=ctk.NORMAL)
            utils.autostart_off()
            return

        # Запуск потока для запуска бота
        ui.MainWindow().log_print('Приветственное сообщение отправлено')
        Thread(target=self.start_bot, args=(), name='Start_bot', daemon=True).start()
    
    def start_bot(self) -> None:
        """Запуск бота."""
        u = ctypes.windll.LoadLibrary("user32.dll")
        pf = getattr(u, "GetKeyboardLayout")
        if hex(pf(0)) == '0x4190419':
            keyboard_layout.change_foreground_window_keyboard_layout(0x04090409)

        while True:
            try:
                ui.MainWindow().log_print('Бот успешно запущен.')
                self.bot.polling(interval=1)
            except telebot.apihelper.ApiException as e:
                ui.MainWindow().error_print(e)
                ui.MainWindow().log_print('Проверьте введенный вами Токен')
                ui.MainWindow().log_print('Проверьте ваш chat_id')
                ui.MainWindow().log_print('Напишите боту, если вы этого не сделали.')
                ui.start_btn.configure(state = ctk.NORMAL)
                utils.autostart_off()
                return
            except Exception as e:
                ui.MainWindow().error_print(e)
                ui.MainWindow().log_print(f"Ошибка бота. Перезапуск...\n{e}")
                time.sleep(5)
                return self.start_bot()