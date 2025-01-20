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
from config_manager import NIRCMD, CHAT_GPT, PATH_TO_VOICE_LINES_FOLDER, translation
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
                                                    text=translation.TG_BOT.MSG_EXPLORER_CURRENT_PATH_AND_PAGE.format(path=path, page=page), reply_markup=markup)

                elif command == 'previous_page':
                    if page != 1:
                        page -= 1

                    path, page, markup = explorer_manager.Explorer().scanning_folders(path, page)

                    edit_msg = self.bot.edit_message_text(chat_id=call.from_user.id, message_id=edit_msg.message_id,
                                                        text=translation.TG_BOT.MSG_EXPLORER_CURRENT_PATH_AND_PAGE.format(path=path, page=page), reply_markup=markup)
                elif command == 'next_page':
                    path, page, markup = explorer_manager.Explorer().scanning_folders(path, page + 1)

                    edit_msg = self.bot.edit_message_text(chat_id=call.from_user.id, message_id=edit_msg.message_id,
                                                        text=translation.TG_BOT.MSG_EXPLORER_CURRENT_PATH_AND_PAGE.format(path=path, page=page), reply_markup=markup)
                elif command == 'back_to_drives':
                    edit_msg = self.bot.edit_message_text(chat_id=call.from_user.id, message_id=edit_msg.message_id, text=translation.TG_BOT.MSG_EXPLORER_ASK_CHOOSE_DRIVE,
                                                        reply_markup=explorer_manager.Explorer().scanning_drives())
                elif command == 'back_explorer':

                    explorer_manager.Explorer().back_path()

                    path, page, markup = explorer_manager.Explorer().scanning_folders(path)

                    edit_msg = self.bot.edit_message_text(chat_id=call.from_user.id, message_id=edit_msg.message_id,
                                                        text=translation.TG_BOT.MSG_EXPLORER_CURRENT_PATH_AND_PAGE.format(path=path, page=page), reply_markup=markup)

                elif command == 'run':
                    subprocess.run(['start', '', path], shell=True)

                elif command == 'download':
                    edit_msg = self.bot.edit_message_text(chat_id=call.from_user.id,
                                                        message_id=call.message.message_id,
                                                        text=translation.TG_BOT.MSG_EXPLORER_DOWNLOAD_FILE)

                    with open(path, 'rb') as file:
                        self.bot.send_document(chat_id=call.from_user.id, document=file)

                    explorer_manager.Explorer().back_path()


                    path, page, markup = explorer_manager.Explorer().scanning_folders(path)

                    edit_msg = self.bot.edit_message_text(chat_id=call.from_user.id, message_id=edit_msg.message_id,
                                                        text=translation.TG_BOT.MSG_EXPLORER_CURRENT_PATH_AND_PAGE.format(path=path, page=page), reply_markup=markup)

                elif command == 'delete':
                    os.remove(path)

                elif os.path.isfile(path + "\\" + str(explorer_manager.Explorer().folders_names.get(command)))\
                        and os.access(path + "\\" + str(explorer_manager.Explorer().folders_names.get(command)), os.X_OK):
                    path = path + "\\" + str(explorer_manager.Explorer().folders_names.get(command))
                    edit_msg = self.bot.edit_message_text(chat_id=call.from_user.id,
                                                        message_id=call.message.message_id,
                                                        text=translation.TG_BOT.MSG_EXPLORER_CURRENT_PATH_AND_ASK_FOR_ACTION.format(path=path),
                                                        reply_markup=explorer_manager.Explorer().script_file_markup)

                else:
                    path, page, markup = explorer_manager.Explorer().scanning_folders(command)

                    edit_msg = self.bot.edit_message_text(chat_id=call.from_user.id,
                                                    message_id=call.message.message_id,
                                                    text=translation.TG_BOT.MSG_EXPLORER_CURRENT_PATH_AND_PAGE.format(path=path, page=page), reply_markup=markup)
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
                        if message.text == translation.TG_BOT.BUTTON_CHATGPT_CLOSE:
                            CHAT_GPT = False
                            keyboard_manager.Keyboard().add_buttons_menu(message.from_user.id)
                            return Thread(target= actions_manager.Actions().del_tg_msg, args=(message,)).start()
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        
                        if actions_manager.Actions().api_key() != '':
                            actions_manager.Actions().chatgpt_text_api(message, text=message.text, msg=None)
                        else:
                            actions_manager.Actions().chatgpt_text(message, text=message.text, msg=None)

                    elif translation.TG_BOT.BUTTON_SCRIPTS == message.text:
                        keyboard_manager.Keyboard().add_buttons_script(message.from_user.id)
                        ui.MainWindow().log_print(translation.LOGS.INFO_SCRIPTS.format(username=message.from_user.username))

                    elif translation.TG_BOT.BUTTON_PC_FOLDERS == message.text:
                        Telegram().bot.send_message(message.from_user.id, translation.TG_BOT.MSG_EXPLORER_ASK_CHOOSE_DRIVE, reply_markup=explorer_manager.Explorer().scanning_drives())
                        ui.MainWindow().log_print(translation.LOGS.INFO_FOLDERS.format(username=message.from_user.username))
                        

                    elif translation.TG_BOT.BUTTON_VOLUME_DOWN == message.text:
                        pyautogui.hotkey('volumedown')
                        ui.MainWindow().log_print(translation.LOGS.INFO_VOLUME_DOWN.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_VOLUME_MUTE == message.text: 
                        pyautogui.hotkey('volumemute')
                        ui.MainWindow().log_print(translation.LOGS.INFO_VOLUME_MUTE.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_VOLUME_UP == message.text:
                        pyautogui.hotkey('volumeup')
                        ui.MainWindow().log_print(translation.LOGS.INFO_VOLUME_UP.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_SOUND_PREV_TRACK == message.text: 
                        pyautogui.hotkey('prevtrack')
                        ui.MainWindow().log_print(translation.LOGS.INFO_SOUND_PREV_TRACK.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_SOUND_PLAY_PAUSE == message.text:
                        pyautogui.hotkey('playpause')
                        
                    elif translation.TG_BOT.BUTTON_VIDEO_PLAY_PAUSE == message.text:
                        pyautogui.hotkey('space')
                        ui.MainWindow().log_print(translation.LOGS.INFO_VIDEO_PLAY_PAUSE.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_SOUND_NEXT_TRACK == message.text:
                        pyautogui.hotkey('nexttrack')
                        ui.MainWindow().log_print(translation.LOGS.INFO_SOUND_NEXT_TRACK.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_VIDEO_GO_BACKWARD == message.text:
                        pyautogui.hotkey('left')
                        ui.MainWindow().log_print(translation.LOGS.INFO_VIDEO_GO_BACKWARD.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_VIDEO_SKIP_FORWARD == message.text:
                        pyautogui.hotkey('right')
                        ui.MainWindow().log_print(translation.LOGS.INFO_VIDEO_SKIP_FORWARD.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_VIDEO_FULLSCREEN == message.text:
                        pyautogui.hotkey('f')
                        ui.MainWindow().log_print(translation.LOGS.INFO_VIDEO_FULLSCREEN.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_PC_LOCK_WORKSTATION == message.text:
                        ctypes.windll.user32.LockWorkStation()
                        ui.MainWindow().log_print(translation.LOGS.INFO_PC_LOCK_WORKSTATION.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_PC_SCREENSHOT == message.text:
                        actions_manager.Actions().screen(message)
                        
                    elif translation.TG_BOT.BUTTON_PC_WEBCAM_SCREENSHOT == message.text:
                        actions_manager.Actions().webcam_screen(message)
                        
                    elif translation.TG_BOT.BUTTON_PC_CLOSE_ACTIVE_WINDOW == message.text:
                        pyautogui.hotkey('alt','f4')
                        ui.MainWindow().log_print(translation.LOGS.INFO_PC_CLOSE_ACTIVE_WINDOW.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_POWER_CONTROL_SLEEP == message.text:
                        subprocess.call('rundll32 powrprof.dll,SetSuspendState 0,1,0')
                        ui.MainWindow().log_print(translation.LOGS.INFO_POWER_CONTROL_SLEEP.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_POWER_CONTROL_REBOOT == message.text:
                        winsound.PlaySound(os.path.join(PATH_TO_VOICE_LINES_FOLDER, "reboot.wav"), winsound.SND_FILENAME)
                        subprocess.call('shutdown -r -t 0')
                        ui.MainWindow().log_print(translation.LOGS.INFO_POWER_CONTROL_REBOOT.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_POWER_CONTROL_SHUT_DOWN == message.text:
                        winsound.PlaySound(os.path.join(PATH_TO_VOICE_LINES_FOLDER, "pcoff.wav"), winsound.SND_FILENAME)
                        subprocess.call('shutdown -s -t 0')
                        ui.MainWindow().log_print(translation.LOGS.INFO_POWER_CONTROL_SHUT_DOWN.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_POWER_CONTROL_HIBERNATE == message.text:
                        subprocess.call('shutdown /h')
                        ui.MainWindow().log_print(translation.LOGS.INFO_POWER_CONTROL_HIBERNATE.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_DOLLAR == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        self.bot.send_message(message.from_user.id, translation.TG_BOT.MSG_DOLLAR.format(value=actions_manager.Actions().currensy_rates()[0]))
                        ui.MainWindow().log_print(translation.LOGS.INFO_DOLLAR.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_EURO == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        self.bot.send_message(message.from_user.id, translation.TG_BOT.MSG_EURO.format(value=actions_manager.Actions().currensy_rates()[1]))
                        ui.MainWindow().log_print(translation.LOGS.INFO_EURO.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_WEATHER == message.text:
                        if actions_manager.Actions().weather() == None:
                            Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                            self.bot.send_message(message.from_user.id, translation.TG_BOT.MSG_WEATHER_ASK_TO_TURN_ON_AND_CITY_ID)
                        else:
                            Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                            self.bot.send_message(message.from_user.id, actions_manager.Actions().weather())
                            ui.MainWindow().log_print(translation.LOGS.INFO_WEATHER.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_BTC == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        self.bot.send_message(message.from_user.id, translation.TG_BOT.MSG_BTC.format(value=actions_manager.Actions().bitcoin_rate()))
                        ui.MainWindow().log_print(translation.LOGS.INFO_BTC.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_DATE == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        current_date = actions_manager.Actions().get_current_date()
                        self.bot.send_message(message.from_user.id, translation.TG_BOT.MSG_DATE.format(weekday=current_date[0], day=current_date[1], month=current_date[2]))
                        ui.MainWindow().log_print(translation.LOGS.INFO_DATE.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_POWER_CONTROL_SHUT_DOWN_TIMER_CANCEL == message.text:
                        subprocess.call('shutdown -a')
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        self.bot.send_message(message.from_user.id, translation.TG_BOT.MSG_POWER_CONTROL_SHUT_DOWN_TIMER_CANCEL)
                        ui.MainWindow().log_print(translation.LOGS.INFO_POWER_CONTROL_SHUT_DOWN_TIMER_CANCEL.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_DEVICE_CONTROL_TURN_OFF_MONITOR == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        self.bot.send_message(message.from_user.id, translation.TG_BOT.MSG_DEVICE_CONTROL_TURN_OFF_MONITOR)
                        subprocess.call(f'{NIRCMD} monitor off')
                        ui.MainWindow().log_print(translation.LOGS.INFO_DEVICE_CONTROL_TURN_OFF_MONITOR.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_PC_CLEAR_RECYCLE_BIN == message.text:
                        subprocess.call(f'{NIRCMD} emptybin')
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        self.bot.send_message(message.from_user.id, translation.TG_BOT.MSG_PC_CLEAR_RECYCLE_BIN)
                        ui.MainWindow().log_print(translation.LOGS.INFO_PC_CLEAR_RECYCLE_BIN.format(username=message.from_user.username))                      

                    elif translation.TG_BOT.BUTTON_BRIGHTNESS_SET_0_PCT == message.text:
                        actions_manager.Actions().set_bright(message, 0)
                        

                    elif translation.TG_BOT.BUTTON_BRIGHTNESS_SET_25_PCT == message.text:
                        actions_manager.Actions().set_bright(message, 25)
                        

                    elif translation.TG_BOT.BUTTON_BRIGHTNESS_SET_50_PCT == message.text:
                        actions_manager.Actions().set_bright(message, 50)
                        

                    elif translation.TG_BOT.BUTTON_BRIGHTNESS_SET_75_PCT == message.text:
                        actions_manager.Actions().set_bright(message, 75)
                        

                    elif translation.TG_BOT.BUTTON_BRIGHTNESS_SET_100_PCT == message.text:
                        actions_manager.Actions().set_bright(message, 100)                      

                    elif translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOVE_UP == message.text:
                        pyautogui.moveRel(0, -25, duration=0)
                        ui.MainWindow().log_print(translation.LOGS.INFO_MOUSE_CONTROL_MOVE_UP.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOVE_DOWN == message.text:
                        pyautogui.moveRel(0, 25, duration=0)
                        ui.MainWindow().log_print(translation.LOGS.INFO_MOUSE_CONTROL_MOVE_DOWN.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOVE_LEFT == message.text:
                        pyautogui.moveRel(-25, 0, duration=0)
                        ui.MainWindow().log_print(translation.LOGS.INFO_MOUSE_CONTROL_MOVE_LEFT.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOVE_RIGHT == message.text:
                        pyautogui.moveRel(25, 0, duration=0)
                        ui.MainWindow().log_print(translation.LOGS.INFO_MOUSE_CONTROL_MOVE_RIGHT.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOUSE1 == message.text:
                        pyautogui.leftClick()
                        ui.MainWindow().log_print(translation.LOGS.INFO_MOUSE_CONTROL_MOUSE1.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOUSE2 == message.text:
                        pyautogui.rightClick()
                        ui.MainWindow().log_print(translation.LOGS.INFO_MOUSE_CONTROL_MOUSE2.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_PC_TASK_MANAGER == message.text:
                        pyautogui.hotkey('CTRL', 'SHIFT', 'ESC')
                        ui.MainWindow().log_print(translation.LOGS.INFO_PC_TASK_MANAGER.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_MEDIA == message.text:
                        keyboard_manager.Keyboard().add_buttons_media(message.from_user.id)
                        ui.MainWindow().log_print(translation.LOGS.INFO_MEDIA.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_PC == message.text:
                        keyboard_manager.Keyboard().add_buttons_control_pc(message.from_user.id)
                        ui.MainWindow().log_print(translation.LOGS.INFO_PC.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_INFO == message.text:
                        keyboard_manager.Keyboard().add_buttons_info(message.from_user.id)
                        ui.MainWindow().log_print(translation.LOGS.INFO_INFORMATION.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_INTERNET == message.text:
                        keyboard_manager.Keyboard().add_buttons_internet(message.from_user.id)
                        ui.MainWindow().log_print(translation.LOGS.INFO_INTERNET.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_PROGRAMS == message.text:
                        keyboard_manager.Keyboard().add_buttons_program(message.from_user.id)
                        ui.MainWindow().log_print(translation.LOGS.INFO_PROGRAMS.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_MENU == message.text:
                        keyboard_manager.Keyboard().add_buttons_menu(message.from_user.id)
                        ui.MainWindow().log_print(translation.LOGS.INFO_MENU.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_VIDEO == message.text:
                        keyboard_manager.Keyboard().add_buttons_video(message.from_user.id)
                        ui.MainWindow().log_print(translation.LOGS.INFO_VIDEO.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_MUSIC == message.text:
                        keyboard_manager.Keyboard().add_buttons_music(message.from_user.id)
                        ui.MainWindow().log_print(translation.LOGS.INFO_MUSIC.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_ADMIN == message.text:
                        keyboard_manager.Keyboard().add_buttons_admin(message.from_user.id)
                        ui.MainWindow().log_print(translation.LOGS.INFO_ADMIN.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_VIDEO_PREV_VIDEO == message.text:
                        pyautogui.hotkey('Shift','P')
                        ui.MainWindow().log_print(translation.LOGS.INFO_VIDEO_PREV_VIDEO.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_VIDEO_NEXT_VIDEO == message.text:
                        pyautogui.hotkey('Shift','N')
                        ui.MainWindow().log_print(translation.LOGS.INFO_VIDEO_NEXT_VIDEO.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_PC_DEVICE_MANAGEMENT == message.text:
                        keyboard_manager.Keyboard().add_buttons_control_devices(message.from_user.id)
                        ui.MainWindow().log_print(translation.LOGS.INFO_PC_DEVICE_MANAGEMENT.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_DEVICE_CONTROL_MOUSE == message.text:
                        keyboard_manager.Keyboard().add_buttons_control_mouse(message.from_user.id)
                        ui.MainWindow().log_print(translation.LOGS.INFO_DEVICE_CONTROL_MOUSE.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_DEVICE_CONTROL_KEYBOARD == message.text:
                        keyboard_manager.Keyboard().add_buttons_control_keyboard(message.from_user.id)
                        ui.MainWindow().log_print(translation.LOGS.INFO_DEVICE_CONTROL_KEYBOARD.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_PC_POWER_MANAGEMENT == message.text:
                        keyboard_manager.Keyboard().add_buttons_control_power(message.from_user.id)
                        ui.MainWindow().log_print(translation.LOGS.INFO_PC_POWER_MANAGEMENT.format(username=message.from_user.username))
                        
                    elif translation.TG_BOT.BUTTON_PC_BRIGHTNESS == message.text:
                        keyboard_manager.Keyboard().add_buttons_brightness(message.from_user.id)
                        ui.MainWindow().log_print(translation.LOGS.INFO_PC_BRIGHTNESS.format(username=message.from_user.username))
                        
                    # elif translation.TG_BOT.BUTTON_PC_TEXT_ALERT == message.text:
                    #     Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                    #     msg = self.bot.send_message(message.from_user.id, 'Какое сообщение вывести на экран?🔈')
                    #     self.bot.register_next_step_handler(msg, actions_manager.Actions().text_on_monitor)

                    elif translation.TG_BOT.BUTTON_VOLUME == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, translation.TG_BOT.MSG_VOLUME_ASK_VOLUME)
                        self.bot.register_next_step_handler(msg, actions_manager.Actions().set_volume)
                                                                                         
                    elif translation.TG_BOT.BUTTON_POWER_CONTROL_SHUT_DOWN_TIMER == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, translation.TG_BOT.MSG_POWER_CONTROL_SHUT_DOWN_TIMER_ASK_TIMER)
                        self.bot.register_next_step_handler(msg, actions_manager.Actions().pc_off_time)
  
                    elif translation.TG_BOT.BUTTON_OPEN_LINK == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, translation.TG_BOT.MSG_OPEN_LINK_ASK_LINK)
                        self.bot.register_next_step_handler(msg, actions_manager.Actions().open_url)
                        
                    elif message.text.split(' ')[0] == translation.TG_BOT.TRIGGER_OPEN:
                        actions_manager.Actions().open_exe(message.text)
                        ui.MainWindow().log_print(translation.LOGS.INFO_TRIGGER_OPEN.format(message_text=message.text, username=message.from_user.username))

                    elif message.text.split(' ')[0] == translation.TG_BOT.TRIGGER_SCRIPT:
                        actions_manager.Actions().do_script(message.text)
                        ui.MainWindow().log_print(translation.LOGS.INFO_TRIGGER_SCRIPT.format(message_text=message.text, username=message.from_user.username))
                        

                    elif translation.TG_BOT.BUTTON_COMMAND_FOR_JARVIS == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, translation.TG_BOT.MSG_JARVIS_ASK_FOR_MESSAGE)
                        self.bot.register_next_step_handler(msg, actions_manager.Actions().text_to_jarvis)                                              

                    elif translation.TG_BOT.BUTTON_ADMIN_CHANGE_PASSWORD == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, translation.TG_BOT.MSG_ADMIN_ASK_NEW_PASSWORD)
                        self.bot.register_next_step_handler(msg, actions_manager.Actions().new_password)
                        
                    
                    elif translation.TG_BOT.BUTTON_ADMIN_CLEAR_TEMP_FOLDER == message.text:
                        Telegram().bot.send_message(message.from_user.id, text= actions_manager.Actions().clean_temp_folder())
                        ui.MainWindow().log_print(translation.LOGS.INFO_ADMIN_CLEAR_TEMP_FOLDER.format(username=message.from_user.username))
                        

                    elif translation.TG_BOT.BUTTON_PC_CHANGE_WALLPAPER == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, translation.TG_BOT.MSG_PC_CHANGE_WALLPAPER_ASK_FOR_WALLPAPER)
                        self.bot.register_next_step_handler(msg, actions_manager.Actions().wallpaper)
                        
                        
                    elif translation.TG_BOT.BUTTON_KEYBOARD_CONTROL_TYPE == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, translation.TG_BOT.MSG_KEYBOARD_CONTROL_TYPE_ASK_FOR_TEXT)
                        self.bot.register_next_step_handler(msg, actions_manager.Actions().write_text)
                        
                    
                    elif translation.TG_BOT.BUTTON_KEYBOARD_CONTROL_PRESS_BUTTON == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, translation.TG_BOT.MSG_KEYBOARD_CONTROL_PRESS_BUTTON_ASK_FOR_BUTTON)
                        self.bot.register_next_step_handler(msg, actions_manager.Actions().press_btn)
                        
                    elif translation.TG_BOT.BUTTON_CHATGPT == message.text:
                        CHAT_GPT = True
                        buttons = ReplyKeyboardMarkup(resize_keyboard=True)
                        buttons.add(translation.TG_BOT.BUTTON_CHATGPT_CLOSE)
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')

                        msg = self.bot.send_message(message.from_user.id, translation.TG_BOT.MSG_CHATGPT_ASK_FOR_MESSAGE, reply_markup=buttons)
                        if actions_manager.Actions().api_key() != '':
                            self.bot.register_next_step_handler(msg, actions_manager.Actions().chatgpt_text_api)
                        else:
                            self.bot.register_next_step_handler(msg, actions_manager.Actions().chatgpt_text)
                        
                    # elif '🧠Сгенерировать фото ChatGPT' == message.text:
                    #     Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                    #     msg = self.bot.send_message(message.from_user.id, 'Опишите ваше фото для ChatGPT, сэр?✍️')
                    #     self.bot.register_next_step_handler(msg, actions_manager.Actions().chatgpt_photo)
                        
                    elif '🎦Запись экрана' == message.text:  # NOTE(danil): disabled, no need to translate
                        Thread(target=actions_manager.Actions().video_record, args=(message,), daemon=True).start()
                        

                    elif translation.TG_BOT.BUTTON_PC_SPEC == message.text:
                        actions_manager.Actions().pc_param(message)
                        
                    
                    elif translation.TG_BOT.BUTTON_SPEEDTEST == message.text:
                        actions_manager.Actions().speed_net(message)
                        
                    
                    elif translation.TG_BOT.BUTTON_MOUSE_CONTROL_MOVE_TO_COORDINATES == message.text:
                        Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                        msg = self.bot.send_message(message.from_user.id, translation.TG_BOT.MSG_MOUSE_CONTROL_MOVE_TO_COORDINATES_ASK_FOR_COORDINATES)
                        self.bot.register_next_step_handler(msg, actions_manager.Actions().move_cursor)
                        

                else: 
                    ui.MainWindow().log_print(translation.LOGS.ERROR_USER_CANT_ACCESS_BOT.format(message_text=message.text, username=message.from_user.username))
                
                if config.getfloat('Settings', 'del_delay') != '':
                    if CHAT_GPT is False:
                        Thread(target= actions_manager.Actions().del_tg_msg, args=(message,)).start()
            
            except Exception as e:
                ui.MainWindow().error_print(e)
                ui.MainWindow().log_print(translation.LOGS.ERROR_COMMAND_FAILED_ASK_CHECK_CONFIG)
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
                    ui.MainWindow().log_print(translation.LOGS.ERROR_JARVIS_VOICE_RECOGNITION_FAILED_NO_TEXT)
                    self.bot.reply_to(message, translation.TG_BOT.MSG_JARVIS_VOICE_RECOGNITION_FAILED_NO_TEXT)
                else:
                    if link != 'False':
                        try:
                            requests.get(link+text)
                            self.bot.reply_to(message, translation.TG_BOT.MSG_JARVIS_PASSED_TO_JARVIS_SUCCESS.format(text=text))
                        except Exception as e:
                            ui.MainWindow().error_print(e)
                            ui.MainWindow()(translation.LOGS.ERROR_JARVIS_LINK_ERROR)
                            Telegram().bot.send_chat_action(message.from_user.id, 'typing')
                            self.bot.send_message(message.from_user.id, text=translation.TG_BOT.MSG_JARVIS_COMMAND_ERROR_CHECK_LINK)
                    else:
                        ui.MainWindow()(translation.LOGS.ERROR_JARVIS_LINK_ERROR)
                        self.bot.send_chat_action(message.from_user.id, 'typing')
                        self.bot.send_message(message.from_user.id, text=translation.TG_BOT.MSG_JARVIS_COMMAND_ERROR_CHECK_LINK)
                try:
                    os.remove(file_name)
                    os.remove(file_name+'.wav')
                except Exception as e:
                    ui.MainWindow().error_print(e)
                    ui.MainWindow().log_print(translation.LOGS.ERROR_JARVIS_VOICE_RECOGNITION_ERROR)
                    pass
            else:
                ui.MainWindow().log_print(translation.LOGS.INFO_JARVIS_DISABLED)
                self.bot.send_chat_action(message.from_user.id, 'typing')
                self.bot.send_message(message.from_user.id, text=translation.TG_BOT.MSG_JARVIS_DISABLED)

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
                    ui.MainWindow().log_print(translation.LOGS.INFO_SENDING_START_MESSAGE_WITH_PHOTO.format(chat_id=chat_id))
        except FileNotFoundError:
            # Если фото не найдено, отправляем текстовое сообщение
            ui.MainWindow().log_print(translation.LOGS.INFO_SENDING_START_MESSAGE_PHOTO_NOT_FOUND)
            for chat_id in chat_ids:
                self.bot.send_chat_action(chat_id, 'typing')
                msg = self.bot.send_message(
                    chat_id=chat_id,
                    text=actions_manager.Actions().create_start_response(),
                    reply_markup=keyboard_manager.Keyboard().add_buttons()
                )
                start_msg_id = msg.id
                ui.MainWindow().log_print(translation.LOGS.INFO_SENDING_START_MESSAGE_ONLY_TEXT.format(chat_id=chat_id))
        except (Exception, telebot.apihelper.ApiException) as e:
            # Обработка ошибок при отправке
            ui.MainWindow().error_print(e)
            ui.MainWindow().log_print(translation.LOGS.ERROR_SENDING_START_MESSAGE_FAILED)
            ui.MainWindow().log_print(translation.LOGS.ERROR_SENDING_START_MESSAGE_CHECK_BOT_TOKEN)
            ui.MainWindow().log_print(translation.LOGS.ERROR_SENDING_START_MESSAGE_CHECK_CHAT_ID)
            ui.MainWindow().log_print(translation.LOGS.ERROR_SENDING_START_MESSAGE_MESSAGE_TO_BOT)
            ui.start_btn.configure(state=ctk.NORMAL)
            utils.autostart_off()
            return

        # Запуск потока для запуска бота
        ui.MainWindow().log_print(translation.LOGS.INFO_SENDING_START_MESSAGE_SUCCESS)
        Thread(target=self.start_bot, args=(), name='Start_bot', daemon=True).start()
    
    def start_bot(self) -> None:
        """Запуск бота."""
        u = ctypes.windll.LoadLibrary("user32.dll")
        pf = getattr(u, "GetKeyboardLayout")
        if hex(pf(0)) == '0x4190419':
            keyboard_layout.change_foreground_window_keyboard_layout(0x04090409)

        while True:
            try:
                ui.MainWindow().log_print(translation.LOGS.INFO_BOT_STARTUP_SUCCESS)
                self.bot.polling(interval=1)
            except telebot.apihelper.ApiException as e:
                ui.MainWindow().error_print(e)
                ui.MainWindow().log_print(translation.LOGS.ERROR_BOT_STARTUP_CHECK_BOT_TOKEN)
                ui.MainWindow().log_print(translation.LOGS.ERROR_BOT_STARTUP_CHECK_CHAT_ID)
                ui.MainWindow().log_print(translation.LOGS.ERROR_BOT_STARTUP_CHECK_MESSAGE_TO_BOT)
                ui.start_btn.configure(state = ctk.NORMAL)
                utils.autostart_off()
                return
            except Exception as e:
                ui.MainWindow().error_print(e)
                ui.MainWindow().log_print(translation.LOGS.ERROR_BOT_STARTUP_RESTART.format(error=e))
                time.sleep(5)
                return self.start_bot()