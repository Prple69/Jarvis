import os
from PIL import Image
from pystray import Icon
from pystray import MenuItem as item
import customtkinter as ctk
from win32com.client import Dispatch
import ui
import speech_recognition as sr
import configparser

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
        with open('config.ini', 'w+', encoding='utf-8') as f:
            config.write(f)

def quit_window():
    ui.MainWindow().root.destroy()
    os.system('taskkill /im "Pc Control.exe"')
 
def show_window():
    ui.MainWindow().root.after(0, ui.MainWindow().root.deiconify)
    with open('logs.txt', 'r', encoding='utf-8') as logs_txt:
        if os.stat("logs.txt").st_size != 0:
            ui.logs_lbl.configure(state = ctk.NORMAL)
            ui.logs_lbl.delete(0.0, ctk.END)
            ui.logs_lbl.insert(ctk.INSERT, logs_txt.read())
            ui.logs_lbl.configure(state = ctk.DISABLED)
    logs_txt.close()
 
def withdraw_window():
    ui.MainWindow().root.withdraw()

def start_icon():
    image = Image.open(os.path.abspath(r'bin/icon.ico'), 'r')
    menu=(item('Показать', show_window), item('Закрыть', quit_window))
    icon = Icon('Pc Control', image, menu=menu)
    icon.run()

def get_text(filepath):
    # filepath: voices\\filename.ogg
    try:
        args = ['bin/ffmpeg.exe','-i', filepath, f'{filepath}.wav']
        # process = subprocess.check_output(args)
        r = sr.Recognizer()
        harvard = sr.AudioFile(filepath+'.wav')
        with harvard as source:
            audio = r.record(source)
        return(r.recognize_google(audio,language='ru_RU')) # тут можешь поменять язык распознавания, если уберешь то англ
    except Exception as e:
        ui.MainWindow().error_print(e)
        pass

def autostart_off():
    Thisfile = os.path.abspath('PC Control.exe') # Полный путь к файлу, включая название и расширение
    Thisfile_name = os.path.basename(Thisfile) # Название файла без пути
    user_path = os.path.expanduser('~') # Путь к папке пользователя
    try:
        os.remove(f"{user_path}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\{Thisfile_name.replace('exe','lnk')}")
    except FileNotFoundError as e:
        ui.MainWindow().error_print(e)
        pass

def autostart():
    Thisfile = os.path.abspath('PC Control.exe') # Полный путь к файлу, включая название и расширение
    Thisfile_name = os.path.basename(Thisfile) # Название файла без пути
    user_path = os.path.expanduser('~') # Путь к папке пользователя

    if not os.path.exists(f"{user_path}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\{Thisfile_name}"):
        path = os.path.join(f"{user_path}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\", Thisfile_name.replace('exe','lnk'))
        target = Thisfile
        wDir = Thisfile.replace(Thisfile_name,'')
        icon = Thisfile
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon
        shortcut.save()