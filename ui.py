import configparser
import json
import os
import time
import webbrowser
from functools import lru_cache
from threading import Thread
from tkinter import PhotoImage

import customtkinter as ctk
import requests
from PIL import Image
from screeninfo import get_monitors

import actions_manager
import bot_manager
from config_manager import BOT_INFO, BOT_LICENSE, translation
import license_manager
import main
from constants import UIScriptsButtons
import utils


VALUES_TO_LABELS = {
    translation.UI.SCRIPT_NAME_CURSOR_TO_COORDINATES: UIScriptsButtons.CURSOR_TO_XY, 
    translation.UI.SCRIPT_NAME_LAUNCH_PROGRAM: UIScriptsButtons.OPEN_PROGRAM, 
    translation.UI.SCRIPT_NAME_CLOSE_PROGRAM: UIScriptsButtons.CLOSE_PROGRAM,
    translation.UI.SCRIPT_NAME_OPEN_WEBSITE: UIScriptsButtons.OPEN_WEBSITE,
    translation.UI.SCRIPT_NAME_WAIT: UIScriptsButtons.WAIT,
    translation.UI.SCRIPT_NAME_KEYBOARD_SHORTCUT: UIScriptsButtons.KEYBOARD_SHORTCUT,
    translation.UI.SCRIPT_NAME_TYPE_TEXT: UIScriptsButtons.TYPE_TEXT,
    translation.UI.SCRIPT_NAME_PRESS_MOUSE_BUTTON: UIScriptsButtons.PRESS_MOUSE_BUTTON,
}

class MainWindow():
    """Класс дизайна."""
    ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    root = ctk.CTk()
    root.geometry('550x320')
    root.title(translation.UI.TITLE)
    root.resizable(False, False)
    bg = '#18191d'
    fg = '#2b2b2b'
    root.config(bg=bg)
    root.iconbitmap(default=os.path.abspath(r'bin/image.ico'))
    icon = PhotoImage(file=os.path.abspath(r'bin/image.png'))
    root.iconphoto(False, icon)

    def _onKeyRelease(event) -> None:
        """Бинд на работу русских символов для вставки, копирования, выделения."""
        ctrl  = (event.state & 0x4) != 0
        if event.keycode==88 and  ctrl and event.keysym.lower() != "x": 
            event.widget.event_generate("<<Cut>>")
        if event.keycode==67 and  ctrl and event.keysym.lower() != "c":
            event.widget.event_generate("<<Copy>>")
        if event.keycode==86 and  ctrl and event.keysym.lower() != "v": 
            event.widget.event_generate("<<Paste>>")
        if event.keycode==65 and  ctrl and event.keysym.lower() != "a":
            event.widget.event_generate("<<SelectAll>>")
    
    root.bind_all("<Key>", _onKeyRelease, "+")
    
    def logs_page(self) -> None:
        """Формирование страницы дизайна - Логи."""
        self.delete_pages()

        global logs_lbl, FLAG
        FLAG = True

        logs_page = ctk.CTkFrame(main_frame, bg_color='white')
		
        logs_lbl = ctk.CTkTextbox(logs_page, 
                                width=410, 
                                height=300, 
                                corner_radius=5, 
                                bg_color=self.bg, 
                                fg_color=self.fg, 
                                text_color='#b6b0b0', 
                                wrap='none', 
                                activate_scrollbars=True,
                                state = ctk.DISABLED
        )
        logs_lbl.pack()
        if start_btn._state == 'normal':
            logs_lbl.configure(state = ctk.NORMAL)
            logs_lbl.insert(ctk.INSERT, MainWindow().print_update())
            logs_lbl.configure(state = ctk.DISABLED)
        else:
            with open('logs.txt', 'r', encoding='utf-8') as logs_txt:
                logs_lbl.configure(state = ctk.NORMAL)
                logs_lbl.insert(ctk.INSERT, logs_txt.read())
                logs_lbl.configure(state = ctk.DISABLED)
            logs_txt.close()
        logs_page.pack()
    
    @staticmethod
    @lru_cache()
    def print_update() -> None:
        """Выводит логи о последнем обновлении."""
        url = 'https://pastebin.com/raw/gSEefmw2'
        tone=requests.get(url).text
        update = tone.split('Update')[1].strip()
        return update
    
    def error_print(self, text:str) -> None:
        """Записывает лог об ошибке в error.txt."""
        log = time.strftime('[%H:%M] ') + str(text)
        with open('error.txt', 'a', encoding='utf-8') as error:
            error.write(f'{log}\n')
        error.close()

    def log_print(self, text:str) -> None:
        """Пишет лог в TextBox."""
        global FLAG
        if 'prpleprog' in text:
            return
        log = time.strftime('[%H:%M] ') + text
        if FLAG:
            try:
                logs_lbl.configure(state = ctk.NORMAL)
                logs_lbl.insert(ctk.INSERT, f'{log}\n')
                logs_lbl.configure(state = ctk.DISABLED)
            except:
                pass
        with open('logs.txt', 'a', encoding='utf-8') as logs_txt:
            logs_txt.write(f'{log}\n')
        logs_txt.close()

    def bot_page(self) -> None:
        """Формирование страницы - Бот."""
        self.delete_pages()
        global token_entry, chat_id_entry, FLAG
        FLAG = False
        # Страница настроек.
        bot_page = ctk.CTkFrame(main_frame)
        bot_page.configure(width=410, height=250, corner_radius=5, fg_color=self.fg)
        bot_page.pack_propagate(False)
        bot_page.pack()
        # Строка - Введите токен бота.
        token_lbl = ctk.CTkLabel(bot_page, text=translation.UI.INPUT_BOT_TOKEN, font=('Bold',18))
        token_lbl.pack()
        token_lbl.place(x=10, y=5)
        # Ввод токена бота.
        token_entry = ctk.CTkEntry(bot_page, placeholder_text='123456789:AdhyUIklmnBvsrqwTyuJjgd', width=390)
        token_entry.pack()
        token_entry.place(x=10, y=33)
        token_entry.bind('<KeyRelease>', self.save_data_bot)
        # Строка - Введите чат айди.
        city_id_lbl = ctk.CTkLabel(bot_page, text=translation.UI.INPUT_CHAT_ID, font=('Bold',18))
        city_id_lbl.pack()
        city_id_lbl.place(x=10, y=76)
        # Ввод чат айди.
        chat_id_entry = ctk.CTkEntry(bot_page, placeholder_text='9790583040, 32165446, 5445764767', width=390)
        chat_id_entry.pack()
        chat_id_entry.place(x=10, y=104)
        chat_id_entry.bind('<KeyRelease>', self.save_data_bot)
		
        config=configparser.ConfigParser()
        config.read("config.ini", encoding='utf-8')
        token=config['Settings']['token']
        chat_id=config['Settings']['chat_id']
		
        if token !='':
            token_entry.insert(ctk.INSERT, token)
        if chat_id !='':
            chat_id_entry.insert(ctk.INSERT, chat_id)
    
    def script_page(self) -> None:
        """Формирование страницы - Сценарии."""
        global script_page, FLAG
        self.delete_pages()
        FLAG = False

        # NOTE(danil): keys - for developers, values for user (to keep the same format for each language)

        LABELS_TO_VALUES = {
            UIScriptsButtons.CURSOR_TO_XY: translation.UI.SCRIPT_NAME_CURSOR_TO_COORDINATES, 
            UIScriptsButtons.OPEN_PROGRAM: translation.UI.SCRIPT_NAME_LAUNCH_PROGRAM, 
            UIScriptsButtons.CLOSE_PROGRAM: translation.UI.SCRIPT_NAME_CLOSE_PROGRAM,
            UIScriptsButtons.OPEN_WEBSITE: translation.UI.SCRIPT_NAME_OPEN_WEBSITE,
            UIScriptsButtons.WAIT: translation.UI.SCRIPT_NAME_WAIT,
            UIScriptsButtons.KEYBOARD_SHORTCUT: translation.UI.SCRIPT_NAME_KEYBOARD_SHORTCUT,
            UIScriptsButtons.TYPE_TEXT: translation.UI.SCRIPT_NAME_TYPE_TEXT,
            UIScriptsButtons.PRESS_MOUSE_BUTTON: translation.UI.SCRIPT_NAME_PRESS_MOUSE_BUTTON,
        }
        
        ARGS_DICT = {
            UIScriptsButtons.CURSOR_TO_XY: translation.UI.SCRIPT_PLACEHOLDER_CURSOR_TO_COORDINATES,
            UIScriptsButtons.OPEN_PROGRAM: translation.UI.SCRIPT_PLACEHOLDER_LAUNCH_PROGRAM,
            UIScriptsButtons.CLOSE_PROGRAM: translation.UI.SCRIPT_PLACEHOLDER_CLOSE_PROGRAM,
            UIScriptsButtons.OPEN_WEBSITE: translation.UI.SCRIPT_PLACEHOLDER_OPEN_WEBSITE,
            UIScriptsButtons.WAIT: translation.UI.SCRIPT_PLACEHOLDER_WAIT,
            UIScriptsButtons.KEYBOARD_SHORTCUT: translation.UI.SCRIPT_PLACEHOLDER_KEYBOARD_SHORTCUT,
            UIScriptsButtons.TYPE_TEXT: translation.UI.SCRIPT_PLACEHOLDER_TYPE_TEXT,
            UIScriptsButtons.PRESS_MOUSE_BUTTON: f"{translation.UI.SCRIPT_PRESS_MOUSE_BUTTON_MOUSE1}, {translation.UI.SCRIPT_PRESS_MOUSE_BUTTON_MOUSE2}, {translation.UI.SCRIPT_PRESS_MOUSE_BUTTON_MOUSE3}"
        }
        
        script_page = ctk.CTkScrollableFrame(main_frame, orientation = 'vertical')
        script_page.configure(width=410, height=250, corner_radius=5, fg_color=self.fg)
        script_page.pack_propagate(False)
        script_page.pack()

        entry_list = []
        
        def load_data() -> None:
            """Загружает имена и кнопки сценариев в дизайн."""
            #Если нет файла json создает его и добавляет туда []
            if not(os.path.exists('data_script.json')):
                data=[]
                with open("data_script.json", "w", encoding='utf-8') as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)
            
            # Открывает и читает файл json
            with open('data_script.json', encoding='utf-8') as f:
                data = json.load(f)

            #Если json не пуст, то заполняет строки - имена, кнопки
            if len(data) != 0:
                for index, programm in enumerate(data):
                    row = index
                    
                    edit_photo = ctk.CTkImage(Image.open('bin/edit.png'), size=(15,15))
                    edit_button = ctk.CTkButton(script_page, width=15, height=15, image=edit_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, text='')
                    edit_button.configure(command=lambda id=programm['id']: load_editor(id))
                    edit_button.grid(row=row, column=0, pady=5, sticky = 'ns', padx=(15, 5))
                    
                    prog_name_lbl = ctk.CTkLabel(script_page, width=255, text=programm['name'], font=('Bold', 20), text_color='white')
                    prog_name_lbl.grid(row=row, column=1, pady=5, sticky = 'ns')

                    delete_photo = ctk.CTkImage(Image.open('bin/minus.png'), size=(15,15))
                    delete_button = ctk.CTkButton(script_page, width=15, height=15, image=delete_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, text='')
                    delete_button.grid(row=row, column=2, pady=5, padx=(5, 15), sticky = 'ns')
                    delete_button.configure(command=lambda index=programm['id'], edit_btn=edit_button, name=prog_name_lbl, del_btn=delete_button: delete_script(index, edit_btn, name, del_btn))
                    
                    #Добавляю имена, строки и их айди по строчно в словарь, дабы правильно удалять их
                    entry_dict = {
                        'edit': edit_photo,
                        'prog': prog_name_lbl,
                        'index': programm['id']
                    }

                    entry_list.append(entry_dict)
            else:
                row=0
            
            #Кнопка - добавление строк
            add_photo = ctk.CTkImage(Image.open('bin/plus.png'), size=(30,30))
            add_button = ctk.CTkButton(script_page, width=390, height=0, text=translation.UI.BUTTON_NEW_SCRIPT, font=('Bold', 18), image=add_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, command= lambda: load_editor(id=None))
            add_button.grid(row=row+1, columnspan=3, pady = (0,0), sticky='nsew')
        
        def show_cord(path, args_list, id) -> None:
            def click(evt):
                root.destroy()
                path.delete(0, 'end')
                path.insert(ctk.INSERT, f'{evt.x},{evt.y}')
                save_script(args_list, id, False)
                
            def show_coord(evt):
                coord.pack()
                coord.configure(text = f'{evt.x, evt.y}')
                coord.place(x=evt.x, y = evt.y+50)
                return

            root = ctk.CTk()

            root.attributes('-topmost', True)
            root.attributes('-alpha', 0.5)
            root.overrideredirect(True)
            
            width = sum(monitor.width for monitor in get_monitors())
            height = sum(monitor.height for monitor in get_monitors())
            x = min(monitor.x for monitor in get_monitors())
            y = min(monitor.y for monitor in get_monitors())
            root.geometry(f'{width}x{height}+{x}+{y}')
            
            canvas = ctk.CTkCanvas(root, width=width, height=height, bg='grey')
            coord = ctk.CTkLabel(canvas, text ='0,0', text_color='white', font=('Bold',20))
            canvas.bind('<Button-1>', click)
            canvas.bind('<Motion>', show_coord)
            canvas.pack()

            root.mainloop()

        def select_file_script(path, args_list, id) -> None:
            filetypes = (
                ('All files', '*.*'),
                ('Text files', '*.txt'),
                ('Exe files', '*.exe')
            )

            filename = ctk.filedialog.askopenfilename(
                title=translation.UI.CHOOSE_FILE,
                initialdir= os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') ,
                filetypes=filetypes)
            path.delete(0, 'end')
            path.insert(ctk.INSERT, filename)
            save_script(args_list, id, False)

        def load_editor(id = None) -> None: # Должен получать id сценария и подгружать всю инфу
            """Загрузка данных сценария через id."""
            self.delete_pages()
            args_list = []
            global prog_name_entry

            menu_frame = ctk.CTkFrame(main_frame, width=0, height=0)
            menu_frame.grid(row=0, column=0, sticky='nw')
            
            editor_page = ctk.CTkScrollableFrame(main_frame, orientation = 'vertical')
            editor_page.configure(width=400, height=206, corner_radius=5, fg_color=self.fg)
            editor_page.grid(row=1, column=0, sticky='nw')
            editor_page.rowconfigure(index=tuple(range(100)),weight=6)
            
            #Ввод имени сценария
            prog_name_entry = ctk.CTkEntry(menu_frame, width=150, placeholder_text=translation.UI.SCRIPT_PLACEHOLDER_TITLE)
            prog_name_entry.grid(row=0, column=0, pady=3, padx=(3,3))
            
            #Выбор функции
            variable = ctk.StringVar()
            variable.set(translation.UI.ACTION)
            choose_act_tab = ctk.CTkOptionMenu(menu_frame, variable=variable, width=150, font=(None, 12), values=list(VALUES_TO_LABELS.keys()))
            choose_act_tab.grid(row=0, column=1, pady=3, padx=(3,3))
            
            #Кнопка назад - вовзращает к списку сценариев
            back_photo = ctk.CTkImage(Image.open('bin/back.png'), size=(20,20))
            back_button = ctk.CTkButton(menu_frame, width=0, height=0, image=back_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, text='', command= lambda: MainWindow().indicate(script_btn_indicate, MainWindow().script_page))
            back_button.grid(row=0, column=3, pady=3, padx=(5,3), sticky = 'w')
            
            #Читаю json файл для дальнейшей загрузки виджетов
            with open('data_script.json', encoding='utf-8') as f:
                data = json.load(f)
            
            index = 0
            
            if id is not None:                          #Если такой id есть в json
                for i, script in enumerate(data):   
                    if script['id'] == id:              #Сравниваю id, дабы получить инфу из нужного блока json
                        prog_name_entry.insert(ctk.INSERT, script['name'])
                        if len(script['commands']) !=0:
                            for idx, func in enumerate(dict(script['commands'])):
                                editor_page.rowconfigure(index=index, weight=5)
                                name = script['commands'][func][0]  # NOTE(danil): name should be one of UIScriptsButtons values
                                args = script['commands'][func][1]
                                
                                arrow_up_photo = ctk.CTkImage(Image.open('bin/arrow_up.png'), size=(15,15))
                                arrow_down_photo = ctk.CTkImage(Image.open('bin/arrow_down.png'), size=(15,15))
                                arrow_up_btn = ctk.CTkButton(editor_page, width=0, height=0, image=arrow_up_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, text='', textvariable='up')
                                arrow_down_btn = ctk.CTkButton(editor_page, width=0, height=0, image=arrow_down_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, text='', textvariable='down')
                                arg_lbl = ctk.CTkLabel(editor_page, text=LABELS_TO_VALUES[name])
                                arg_entry = ctk.CTkEntry(editor_page, placeholder_text=ARGS_DICT[name])
                                select_photo = ctk.CTkImage(Image.open('bin/select.png'), size=(15,15))
                                select_button = ctk.CTkButton(editor_page, width=0, height=0, image=select_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, text='')
                                delete_photo = ctk.CTkImage(Image.open('bin/minus.png'), size=(15,15))
                                delete_button = ctk.CTkButton(editor_page, width=0, height=0, image=delete_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, text='', textvariable=index)
                                
                                if idx == 0:
                                    if len(script['commands']) != 1:
                                        arrow_down_btn.grid(row=index, column=1, padx=(0,5), sticky='w')
                                        arg_lbl.grid(row=index, column=2, pady=5, padx=(3, 3))
                                        arg_entry.insert(ctk.INSERT, args)
                                        arg_entry.grid(row=index, column=3, pady=5, padx=(3,6))
                                        if name in (UIScriptsButtons.CURSOR_TO_XY, UIScriptsButtons.OPEN_PROGRAM):
                                            select_button.grid(row=index, column=4, pady=5)
                                            if name == UIScriptsButtons.OPEN_PROGRAM:
                                                select_button.configure(command = lambda arg_entry=arg_entry: select_file_script(arg_entry, args_list, id))
                                            elif name == UIScriptsButtons.CURSOR_TO_XY:
                                                select_button.configure(command = lambda arg_entry=arg_entry: show_cord(arg_entry, args_list, id))
                                        delete_button.grid(row=index, column=5, padx=(3,0))
                                        delete_button.configure(command= lambda 
                                                                arg_lbl=arg_lbl, 
                                                                del_btn=delete_button: 
                                                                delete_func(args_list=args_list, arg_lbl=arg_lbl, del_btn=del_btn))
                                        
                                        arrow_down_photo.configure(command=lambda id=id, index=index,  arrow_down_btn=arrow_down_btn:
                                                                swap_func(
                                                                    id=id,
                                                                    row=index,
                                                                    btn=arrow_down_btn))
                                        arg_entry.bind('<KeyRelease>', command= lambda save: save_script(args_list, id, False))

                                    else:
                                        arg_lbl.grid(row=index, column=2, pady=5, padx=(3, 3))
                                        arg_entry.insert(ctk.INSERT, args)
                                        arg_entry.grid(row=index, column=3, pady=5, padx=(3,6))
                                        if name in (UIScriptsButtons.CURSOR_TO_XY, UIScriptsButtons.OPEN_PROGRAM):
                                            select_button.grid(row=index, column=4, pady=5)
                                            if name == UIScriptsButtons.OPEN_PROGRAM:
                                                select_button.configure(command = lambda arg_entry=arg_entry: select_file_script(arg_entry, args_list, id))
                                            elif name == UIScriptsButtons.CURSOR_TO_XY:
                                                select_button.configure(command = lambda arg_entry=arg_entry: show_cord(arg_entry, args_list, id))
                                        delete_button.grid(row=index, column=5, padx=(3,0))
                                        delete_button.configure(command= lambda 
                                                                arg_lbl=arg_lbl, 
                                                                del_btn=delete_button: 
                                                                delete_func(args_list=args_list, arg_lbl=arg_lbl, del_btn=del_btn))
                                        arg_entry.bind('<KeyRelease>', command= lambda save: save_script(args_list, id, False))
                                elif idx == len(script['commands']) - 1:
                                    arrow_up_btn.grid(row=index, column=0, padx=(0,5), sticky='w')
                                    arg_lbl.grid(row=index, column=2, pady=5, padx=(3, 3))
                                    arg_entry.insert(ctk.INSERT, args)
                                    arg_entry.grid(row=index, column=3, pady=5, padx=(3,6))
                                    if name in (UIScriptsButtons.CURSOR_TO_XY, UIScriptsButtons.OPEN_PROGRAM):
                                        select_button.grid(row=index, column=4, pady=5)
                                        if name == UIScriptsButtons.OPEN_PROGRAM:
                                            select_button.configure(command = lambda arg_entry=arg_entry: select_file_script(arg_entry, args_list, id))
                                        elif name == UIScriptsButtons.CURSOR_TO_XY:
                                            select_button.configure(command = lambda arg_entry=arg_entry: show_cord(arg_entry, args_list, id))
                                    delete_button.grid(row=index, column=5, padx=(3,0))
                                    delete_button.configure(command= lambda 
                                                            arg_lbl=arg_lbl, 
                                                            del_btn=delete_button: 
                                                            delete_func(args_list=args_list, arg_lbl=arg_lbl, del_btn=del_btn))
                                    
                                    arrow_up_btn.configure(command=lambda id=id, index=index, arrow_up_btn=arrow_up_btn:
                                                        swap_func(
                                                        id=id,
                                                        row=index,
                                                        btn=arrow_up_btn))
                                    arg_entry.bind('<KeyRelease>', command= lambda save: save_script(args_list, id, False))

                                else:
                                    arrow_up_btn.grid(row=index, column=0, padx=(0,5), sticky='w')
                                    arrow_down_btn.grid(row=index, column=1, padx=(0,5), sticky='w')
                                    arg_lbl.grid(row=index, column=2, pady=5, padx=(3, 3))
                                    arg_entry.insert(ctk.INSERT, args)
                                    arg_entry.grid(row=index, column=3, pady=5, padx=(3,6))
                                    if name in (UIScriptsButtons.CURSOR_TO_XY, UIScriptsButtons.OPEN_PROGRAM):
                                        select_button.grid(row=index, column=4, pady=5)
                                        if name == UIScriptsButtons.OPEN_PROGRAM:
                                            select_button.configure(command = lambda arg_entry=arg_entry: select_file_script(arg_entry, args_list, id))
                                        elif name == UIScriptsButtons.CURSOR_TO_XY:
                                            select_button.configure(command = lambda arg_entry=arg_entry: show_cord(arg_entry, args_list, id))
                                    delete_button.grid(row=index, column=5, padx=(3,0))
                                    delete_button.configure(command= lambda 
                                                            arg_lbl=arg_lbl, 
                                                            del_btn=delete_button: 
                                                            delete_func(args_list=args_list, arg_lbl = arg_lbl, del_btn=del_btn))
                                    arg_entry.bind('<KeyRelease>', command= lambda save: save_script(args_list, id, False))
                                
                                arrow_up_btn.configure(command=lambda id=id, index=index, arrow_up_btn=arrow_up_btn:
                                                        swap_func(
                                                        id=id,
                                                        row=index,
                                                        btn=arrow_up_btn))
                                
                                arrow_down_btn.configure(command=lambda id=id, index=index, arrow_down_btn=arrow_down_btn:
                                                        swap_func(
                                                        id=id,
                                                        row=index,
                                                        btn=arrow_down_btn))
                                arg_dict = {
                                    'arg_lbl': arg_lbl,
                                    'arg_entry': arg_entry,
                                    'index': index,
                                    'id': id,
                                    'del': delete_button,
                                    'sel': select_button,
                                    }
                                args_list.append(arg_dict)
                                
                                index+=1
                            
                            #Бинд на сохранение при вводе имени сценария
                            prog_name_entry.bind('<KeyRelease>', command= lambda save: save_script(args_list, id, False))
                            arg_entry.bind('<KeyRelease>', command= lambda save: save_script(args_list, id, False))
                            back_button.bind('<KeyRelease>', command= lambda save: save_script(args_list, id, True))
                            
                            #Обновляю значени для кнопки
                            choose_act_tab.configure(command= lambda add: add_arg_entry(
                                                                args_list=args_list,
                                                                choose_act_tab=choose_act_tab,
                                                                editor_page=editor_page,
                                                                id=id,
                                                                argument_label=arg_lbl,
                                                                argument_entry=arg_entry,
                                                                sel_btn=select_button,
                                                                del_btn=delete_button,
                                                                up_btn=arrow_up_btn,
                                                                down_btn=arrow_down_btn))
                        else:
                            prog_name_entry.bind('<KeyRelease>', command= lambda save: save_script(args_list, id, False))
                            back_button.bind('<KeyRelease>', command= lambda save: save_script(args_list, id, True))
                            choose_act_tab.configure(command= lambda add: add_arg_entry(
                                    args_list=args_list,
                                    choose_act_tab=choose_act_tab,
                                    editor_page=editor_page,
                                    id=id,
                                    argument_label=None,
                                    argument_entry=None,
                                    sel_btn=None,
                                    del_btn=None,
                                    up_btn=None,
                                    down_btn=None))
            else:
                print('Создание нового сценария')
                with open('data_script.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    id = len(data)
                #Бинд на сохранение при вводе имени сценария
                prog_name_entry.bind('<KeyRelease>', command= lambda save: save_script(args_list, id, False))
                save_script(args_list, id, False)
                choose_act_tab.configure(command= lambda add: add_arg_entry(
                                                    args_list=args_list,
                                                    choose_act_tab=choose_act_tab,
                                                    editor_page=editor_page,
                                                    id=id,
                                                    argument_label=None,
                                                    argument_entry=None,
                                                    sel_btn=None,
                                                    del_btn=None,
                                                    up_btn=None,
                                                    down_btn=None))

        def delete_func(args_list, arg_lbl=None, del_btn=None):
            for index, dict in enumerate(args_list):
                if arg_lbl == dict['arg_lbl']:
                    id = dict['id']                 #ID скрипта в json
                    index = dict['index']           #Номер функции в скрипте
                    del args_list[index]
            
            with open('data_script.json', 'r+', encoding='utf-8') as f:
                data = json.load(f)
                del data[id]['commands'][f'act_{del_btn._textvariable}']
            with open("data_script.json", "w", encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            
            save_script(args_list, id, False, None)
            load_editor(id)        

        def delete_script(index, edit_btn, name, del_btn) -> None:
            """Удаление сценария полностью."""
            for dict in entry_list:
                if dict['edit'] == edit_btn:
                    entry_list.pop(entry_list.index(dict))

            edit_btn.destroy()
            name.destroy()
            del_btn.destroy()

            #Удаляю весь блок json по его id
            filepath = 'data_script.json'
            with open(filepath, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                for i, script in enumerate(data):
                    if script['id'] == index:
                        del data[i]
                        break
            with open("data_script.json", "w", encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            
        def add_arg_entry(args_list, choose_act_tab, editor_page, id, argument_label=None, argument_entry=None, sel_btn=None, del_btn=None, up_btn=None, down_btn=None) -> None:
            """Добавление строк для новый функций в редакторе."""
            if id is None:
                with open('data_script.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    id = len(data)
            
            try:
                row = len(args_list)
            except Exception:
                row = 0
            
            #Значки для кнопок
            arrow_up_photo = ctk.CTkImage(Image.open('bin/arrow_up.png'), size=(15,15))
            arrow_down_photo = ctk.CTkImage(Image.open('bin/arrow_down.png'), size=(15,15))
            delete_photo = ctk.CTkImage(Image.open('bin/minus.png'), size=(15,15))
            select_photo = ctk.CTkImage(Image.open('bin/select.png'), size=(15,15))   

            if row == 1:
                print('Добавляем новую строку с кнопкой вверх')
                new_1_arrow_down_btn= ctk.CTkButton(editor_page, width=0, height=0, image=arrow_down_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, text='', textvariable='down')
                new_1_arrow_down_btn.grid(row=row, column=1, padx=(0,5), sticky='w')
                argument_label.grid(row=row, column=2, padx=(0,5), sticky='w')
                argument_entry.grid(row=row, column=3, padx=(0,5), sticky='w')
                if argument_label._text in (UIScriptsButtons.CURSOR_TO_XY, UIScriptsButtons.OPEN_PROGRAM):
                    sel_btn.grid(row=row, column=4)
                    if argument_label._text == UIScriptsButtons.OPEN_PROGRAM:
                        sel_btn.configure(command = lambda arg_entry=argument_entry: select_file_script(arg_entry, args_list, id))
                    elif argument_label._text == UIScriptsButtons.CURSOR_TO_XY:
                        sel_btn.configure(command = lambda arg_entry=argument_entry: show_cord(arg_entry, args_list, id))
                del_btn.grid(row=row, column=5)
                del_btn.configure(command=lambda:
                                  delete_func(args_list=args_list, 
                                              arg_lbl=argument_label, 
                                              del_btn=del_btn))

                new_1_arrow_down_btn.configure(command=lambda:
                                    swap_func(
                                            id=id,
                                            row=row,
                                            btn=new_1_arrow_down_btn))
            
            #Добавялем к верхней строке кнопку вниз и перемещаем остальные виджеты (Кнопка вниз и вверх)
            if row >= 2:
                print('Добавляем к верхней строке кнопку вниз и новую строку с кнопкой вверх')
                new_2_arrow_down_btn= ctk.CTkButton(editor_page, width=0, height=0, image=arrow_down_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, text='', textvariable='down')
                up_btn.grid(row=row, column=0, padx=(0,5), sticky='w')
                new_2_arrow_down_btn.grid(row=row, column=1, padx=(0,5), sticky='w')
                argument_label.grid(row=row, column=2, padx=(3,3), sticky='w')
                argument_entry.grid(row=row, column=3, padx=(3,6), pady=(3,6), sticky='w')
                if argument_label._text in (UIScriptsButtons.CURSOR_TO_XY, UIScriptsButtons.OPEN_PROGRAM):
                    sel_btn.grid(row=row, column=4, pady=5)
                    if argument_label._text == UIScriptsButtons.OPEN_PROGRAM:
                        sel_btn.configure(command = lambda arg_entry=argument_entry: select_file_script(arg_entry, args_list, id))
                    elif argument_label._text == UIScriptsButtons.CURSOR_TO_XY:
                        sel_btn.configure(command = lambda arg_entry=argument_entry: show_cord(arg_entry, args_list, id))
                del_btn.grid(row=row, column=5, padx=(3,0))
                del_btn.configure(command=lambda:
                                  delete_func(args_list=args_list, 
                                              arg_lbl=argument_label,  
                                              del_btn=del_btn))
                up_btn.configure(command=lambda:
                                    swap_func(
                                            id=id,
                                            row=row,
                                            btn=up_btn))
                
                new_2_arrow_down_btn.configure(command=lambda:
                                    swap_func(
                                            id=id,
                                            row=row,
                                            btn=new_2_arrow_down_btn))
                argument_entry.bind('<KeyRelease>', command= lambda save: save_script(args_list, id, False))
            # Виджеты для новой строки
            new_arg_lbl = ctk.CTkLabel(editor_page, text=choose_act_tab.get())
            new_arg_entry = ctk.CTkEntry(editor_page, placeholder_text=ARGS_DICT[VALUES_TO_LABELS[choose_act_tab.get()]])

            new_arrow_up_btn = ctk.CTkButton(editor_page, width=0, height=0, image=arrow_up_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, text='', textvariable='up')
            new_delete_button = ctk.CTkButton(editor_page, width=0, height=0, image=delete_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, text='', textvariable=row)
            new_select_button = ctk.CTkButton(editor_page, width=0, height=0, image=select_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, text='')
            row+=1

            #Добавялем нижнюю строку с кнопкой верх, только если row != 1(0, т.к переносим строку, по факту первая строка)
            if row !=1:
                new_arrow_up_btn.grid(row=row, column=0, padx=(0,5), sticky='w')
            else:
                new_arrow_up_btn = None
            new_arg_lbl.grid(row=row, column=2, padx=(0, 5), pady=(3,3))
            new_arg_entry.grid(row=row, column=3, padx=(0,5))
            if choose_act_tab.get() in (UIScriptsButtons.CURSOR_TO_XY, UIScriptsButtons.OPEN_PROGRAM):
                new_select_button.grid(row=row, column=4)
                if choose_act_tab.get() == UIScriptsButtons.OPEN_PROGRAM:
                    new_select_button.configure(command = lambda arg_entry=new_arg_entry: select_file_script(arg_entry, args_list, id))
                elif choose_act_tab.get() == UIScriptsButtons.CURSOR_TO_XY:
                    new_select_button.configure(command = lambda arg_entry=new_arg_entry: show_cord(arg_entry, args_list, id))
            
            new_delete_button.grid(row=row, column=5)
            new_delete_button.configure(command=lambda 
                                        arg_lbl=new_arg_lbl,
                                        del_btn=new_delete_button:
                                        delete_func(args_list=args_list, arg_lbl=arg_lbl, del_btn=del_btn))
            
            if new_arrow_up_btn is not None:
                new_arrow_up_btn.configure(command=lambda:
                                    swap_func(
                                            id=id,
                                            row=row,
                                            btn=new_arrow_up_btn))

            new_arg_entry.bind('<KeyRelease>', command= lambda save: save_script(args_list, id, False))
            arg_dict = {
                'arg_lbl': new_arg_lbl,
                'arg_entry': new_arg_entry,
                'index': row-1,
                'id':id,
                'del': new_delete_button,
                'sel': new_select_button
                }
                               
            args_list.append(arg_dict)
            
            choose_act_tab.configure(command= lambda create: add_arg_entry(
                                                                args_list=args_list,
                                                                choose_act_tab=choose_act_tab,
                                                                editor_page=editor_page,
                                                                id=id,
                                                                argument_label=new_arg_lbl,
                                                                argument_entry=new_arg_entry,
                                                                sel_btn=new_select_button,
                                                                del_btn=new_delete_button, 
                                                                up_btn=new_arrow_up_btn,
                                                                down_btn=None))
            save_script(args_list, id, False)
            load_editor(id)

        def swap_func(id, row, btn) -> None:                  
            #Меняю значения в json
            with open('data_script.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            # Меняем местами словари
            for i, script in enumerate(data):
                if script['id'] == id:
                    if btn._textvariable == 'up':
                        data[i]['commands'][f'act_{row}'], data[i]['commands'][f'act_{row-1}'] = data[i]['commands'][f'act_{row-1}'], data[i]['commands'][f'act_{row}']
                    else:
                        data[i]['commands'][f'act_{row}'], data[i]['commands'][f'act_{row+1}'] = data[i]['commands'][f'act_{row+1}'], data[i]['commands'][f'act_{row}']

            with open("data_script.json", 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            file.close()
            
            load_editor(id)

        def save_script(args_list, id, close, event=None) -> None:
            """Сохраняет имена и аргументы сценариев."""
            
            #Получение индекса для id блока в json и проверка, есть ли такой сценарий в базе
            with open("data_script.json", 'r+', encoding='utf-8') as file:
                data = json.load(file)
                index = len(data)
                for script in data:
                    if script['id'] == id:
                        index = id

            file.close()
            
            #Фомирование list команд
            commands = {}
            for idx, dict in enumerate(args_list):
                if dict['id'] == id:
                    try:
                        func = dict['arg_lbl']._text
                        arg = dict['arg_entry'].get()
                        if arg == '':
                            arg = 'None'
                        commands[f'act_{idx}'] = [VALUES_TO_LABELS[func], [arg]]
                    except Exception as e:
                        print(e)
                        pass
            name = prog_name_entry.get()
            if name == '':
                name = translation.UI.SCRIPT_DEFALUT_NAME_PREFIX + f'_{len(data)}'
            
            data = ({"id":index, "name": name, "commands": commands})
            
            #Замена функций уже в существующем сценарии или добавление нового
            with open("data_script.json", 'r', encoding='utf-8') as file:
                all_data = json.load(file)
                flag = True
                for index, script in enumerate(all_data):
                    if script['id'] == id:
                        flag = False
                        all_data[index] = data
                if flag:
                    all_data.append(data)
            file.close()
            
            #Сохранение сценария
            with open("data_script.json", 'w', encoding='utf-8') as file:
                json.dump(all_data, file, indent=4, ensure_ascii=False)
            file.close()
            
            if close:    
                MainWindow().indicate(script_btn_indicate, MainWindow().script_page)

        load_data()
    
    def programm_page(self) -> None:
        """Формирование страницы - Программы."""
        global programm_page, FLAG
        self.delete_pages()
        FLAG = False

        programm_page = ctk.CTkScrollableFrame(main_frame, orientation = 'vertical')
        programm_page.configure(width=410, height=250, corner_radius=5, fg_color=self.fg)
        programm_page.pack_propagate(False)
        programm_page.pack()

        entry_list = []

        def load_data() -> None:
            """Загружает имена и пути программ в дизайн."""
            if not(os.path.exists('data_program.json')):
                data=[]
                with open("data_program.json", "w", encoding='utf-8') as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)

            with open('data_program.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                if len(data) == 0:
                    row=0

            for i, programm in enumerate(data):
                row = i
                #Строка - имя
                name_entry = ctk.CTkEntry(programm_page, width=155, placeholder_text=translation.UI.PROGRAM_PLACEHOLDER_TITLE)
                name_entry.grid(row=row, column=0, pady=5)
                name_entry.insert(ctk.INSERT, programm['name'])
                
                #Строка - путь к файлу
                path_entry = ctk.CTkEntry(programm_page, width=155, placeholder_text=translation.UI.PROGRAM_PLACEHOLDER_PATH)
                path_entry.grid(row=row, column=1, pady=5)
                path_entry.insert(ctk.INSERT, programm['path'])
                
                #Кнопка - удаление строк
                delete_photo = ctk.CTkImage(Image.open('bin/minus.png'), size=(15,15))
                delete_button = ctk.CTkButton(programm_page, width=15, height=15, image=delete_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, text='')
                delete_button.grid(row=row, column=2, pady=5)
                
                #Кнопка - выбор файла
                select_photo = ctk.CTkImage(Image.open('bin/select.png'), size=(15,15))
                select_button = ctk.CTkButton(programm_page, width=15, height=15, image=select_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, text='')
                select_button.grid(row=row, column=3, pady=5)
                
                delete_button.configure(command=lambda i=programm['id'], name=name_entry, path=path_entry, select=select_button, del_btn=delete_button: delete_program(i, name, path, select, del_btn))
                select_button.configure(command = lambda name = name_entry, path=path_entry, fd = select_button: select_file(name, path))
                
                entry_dict = {
                    'name': name_entry,
                    'path': path_entry,
                    'index': programm['id']
                }

                entry_list.append(entry_dict)

                name_entry.bind('<KeyRelease>', lambda save: save_data(self= self, entry_list=entry_list))
                path_entry.bind('<KeyRelease>', lambda save: save_data(self= self, entry_list=entry_list))

            #Кнопка - добавление строк
            add_photo = ctk.CTkImage(Image.open('bin/plus.png'), size=(30,30))
            add_button = ctk.CTkButton(programm_page, width=390, height=0, text=translation.UI.PROGRAM_BUTTON_NEW_COMMAND, font=('Bold', 18), image=add_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg)
            add_button.configure(command= lambda: add_program(add_button, row))
            add_button.grid(row=row+1, columnspan=4, sticky='nsew')
            add_button.bind('<ButtonRelease-1>', lambda save: save_data(self= self, entry_list=entry_list))
        
        def add_program(btn, row) -> None:
            """Добавляет строки для ввода имени и пути к программе."""
            btn.destroy()
            row+=1                              #Увеличиваю row для переноса виджетов на следующую строку
            filepath = 'data_program.json'
            with open(filepath, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                try:
                    index = data[-1]['id'] + 1
                except Exception:
                    index = 0

            name_entry = ctk.CTkEntry(programm_page, width=155, placeholder_text=translation.UI.PROGRAM_PLACEHOLDER_TITLE)
            name_entry.grid(row=row, column=0, pady=5)

            path_entry = ctk.CTkEntry(programm_page, width=155, placeholder_text=translation.UI.PROGRAM_PLACEHOLDER_PATH)
            path_entry.grid(row=row, column=1, pady=5)
            
            entry_dict = {
                'name': name_entry,
                'path': path_entry,
                'index': index
            }

            entry_list.append(entry_dict)


            select_photo = ctk.CTkImage(Image.open('bin/select.png'), size=(15,15))
            select_button = ctk.CTkButton(programm_page, width=15, height=15, image=select_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, text='')
            select_button.configure(command = lambda name=name_entry, path=path_entry, fd = select_button: select_file(name, path))
            select_button.grid(row=row, column=3, pady=5)

            delete_photo = ctk.CTkImage(Image.open('bin/minus.png'), size=(15,15))
            delete_button = ctk.CTkButton(programm_page, width=15, height=15, image=delete_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, text='')
            delete_button.configure(command=lambda i=index, f1=name_entry, f2=path_entry, f3=select_button, fd=delete_button: delete_program(i, f1, f2, f3, fd)) #Фикс row, не совпадают индексы
            delete_button.grid(row=row, column=2, pady=5)
            
            add_photo = ctk.CTkImage(Image.open('bin/plus.png'), size=(30,30))
            add_button = ctk.CTkButton(programm_page, width=390, height=0, text=translation.UI.PROGRAM_BUTTON_NEW_COMMAND, font=('Bold', 18), image=add_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg)
            add_button.grid(row=row+1, columnspan=4, sticky='nsew')
            add_button.configure(command= lambda: add_program(add_button, row))
            
            name_entry.bind('<KeyRelease>', lambda save: save_data(self=self, entry_list=entry_list))
            path_entry.bind('<KeyRelease>', lambda save: save_data(self=self, entry_list=entry_list))
            delete_button.bind('<ButtonRelease-1>', lambda save: save_data(self=self, entry_list=entry_list))

            save_data(self, entry_list)
            

        def delete_program(index, name, path, select, del_btn):

            for dict in entry_list:
                if dict['name'] == name:
                    entry_list.pop(entry_list.index(dict))

            name.destroy()
            path.destroy()
            select.destroy()
            del_btn.destroy()

            filepath = 'data_program.json'
            with open(filepath, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                for i, programm in enumerate(data):
                    if programm['id'] == index:
                        del data[i]
                        break
            with open("data_program.json", "w", encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        def save_data(self, entry_list) -> None:
            """Сохраняет имена и пути программ."""
            data=[]
            
            if len(entry_list) == 0:
                return

            for dict in entry_list:
                try:
                    name = dict['name'].get()
                    path = dict['path'].get()
                    if name == '' or path == '':
                        data.append({"id":dict["index"], "name": "", "path": ""})
                    else:
                        data.append({"id":dict["index"], "name": name, "path": path})
                    with open("data_program.json", "w", encoding='utf-8') as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)
                
                except Exception as e: 
                    pass
        
        def select_file(name, path):
            filetypes = (
                ('All files', '*.*'),
                ('Text files', '*.txt'),
                ('Exe files', '*.exe')
            )

            filename = ctk.filedialog.askopenfilename(
                title=translation.UI.CHOOSE_FILE,
                initialdir= os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') ,
                filetypes=filetypes)
            path.delete(0, 'end')
            path.insert(ctk.INSERT, filename)
            filename = filename.split('/')[-1]
            name.delete(0, 'end')
            name.insert(ctk.INSERT, str(filename)[:-4])
        
            save_data(self=self, entry_list=entry_list)
    
        load_data()
    
    def settings_page(self) -> None:
        """Формирование страницы - Настройки."""
        global settings_page, FLAG
        
        self.delete_pages()
        FLAG = False

        #Рамка
        settings_page = ctk.CTkScrollableFrame(main_frame)
        settings_page.configure(width=410, height=250, corner_radius=5, fg_color=self.fg)
        settings_page.pack_propagate(False)
        settings_page.pack()

        # Свитчи
        global switch_date, switch_time, switch_usd, switch_eur, switch_btc, switch_weather, switch_voice_greet, switch_jarvis_link, city_id_entry, jarvis_link_entry, switch_autostart, gpt_api_entry, del_delay_entry, del_delay, select_photo_entry

        # Первый столбец
        switch_date = ctk.CTkSwitch(settings_page, text=translation.UI.SETTINGS_NAME_DATE)
        switch_time = ctk.CTkSwitch(settings_page, text=translation.UI.SETTINGS_NAME_TIME)
        switch_usd = ctk.CTkSwitch(settings_page, text=translation.UI.SETTINGS_NAME_DOLLAR)
        switch_eur = ctk.CTkSwitch(settings_page, text=translation.UI.SETTINGS_NAME_EURO)
        switch_btc = ctk.CTkSwitch(settings_page, text=translation.UI.SETTINGS_NAME_BTC)
        switch_voice_greet = ctk.CTkSwitch(settings_page, text=translation.UI.SETTINGS_NAME_VOICE_LINES)
        switch_autostart = ctk.CTkSwitch(settings_page, text=translation.UI.SETTINGS_NAME_AUTOSTART)
        del_delay_lbl = ctk.CTkLabel(settings_page, text=translation.UI.SETTINGS_NAME_MESSAGE_AUTODELETE, font=('Bold', 18))
        del_delay_entry = ctk.CTkEntry(settings_page, placeholder_text=translation.UI.SETTINGS_PLACEHOLDER_MESSAGE_AUTODELETE, width=125)
        select_photo_image = ctk.CTkImage(Image.open('bin/select.png'), size=(15,15))
        select_photo_lbl = ctk.CTkLabel(settings_page, text=translation.UI.SETTINGS_NAME_GREETING_IMAGE, font=('Bold', 18))
        select_photo_entry = ctk.CTkEntry(settings_page, placeholder_text=translation.UI.SETTINGS_PLACEHOLDER_GREETING_IMAGE, width=185)
        select_photo_btn = ctk.CTkButton(settings_page, width=15, height=15, image=select_photo_image, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, text='')
        
        switch_date.grid(row=0, column=0, sticky='nsew', padx = 5, pady=5)
        switch_time.grid(row=1, column=0, sticky='nsew', padx = 5, pady=5)
        switch_usd.grid(row=2, column=0, sticky='nsew', padx = 5, pady=5)
        switch_eur.grid(row=3, column=0, sticky='nsew', padx = 5, pady=5)
        switch_btc.grid(row=4, column=0, sticky='nsew', padx = 5, pady=5)
        switch_voice_greet.grid(row=5, column=0, sticky='nsew', padx = 5, pady=5)
        switch_autostart.grid(row=6, column=0, sticky='nsew', padx = 5, pady=5)
        del_delay_lbl.grid(row=7, column=0, sticky='w', padx = 5, pady=(30, 0))
        del_delay_entry.grid(row=8, column=0, sticky='w', padx = 5, pady=(2,15))
        select_photo_lbl.grid(row=9, column=0, sticky='w', padx = 5, pady=(2,5))
        select_photo_entry.grid(row=10, column=0, sticky='w', padx = 5, pady=(2,5))
        select_photo_btn.grid(row=10, column=1, sticky='w', padx = 5, pady=(2,5))


        #Второй столбец
        help_photo= ctk.CTkImage(Image.open('bin/help.png'), size=(15,15))
        switch_weather = ctk.CTkSwitch(settings_page, text=translation.UI.SETTINGS_NAME_WEATHER, command = lambda: MainWindow().show_entry(), variable=ctk.BooleanVar())
        switch_jarvis_link = ctk.CTkSwitch(settings_page, text=translation.UI.SETTINGS_NAME_JARVIS, command = lambda: MainWindow().show_entry(), variable=ctk.BooleanVar())
        help_weather_btn = ctk.CTkButton(settings_page, width=0, height=0, text='', image=help_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, command=lambda: webbrowser.open_new('https://telegra.ph/Nastrojka-Pc-Control-03-22-2'))
        help_jar_btn = ctk.CTkButton(settings_page, width=0, height=0, text='', image=help_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, command=lambda: webbrowser.open_new('https://t.me/c/1627334371/47'))
        help_gpt_btn = ctk.CTkButton(settings_page, width=0, height=0, text='', image=help_photo, bg_color=self.fg, fg_color=self.fg, hover_color=self.bg, command=lambda: webbrowser.open_new('https://platform.openai.com/account/api-keys'))

        switch_weather.grid(row=0, column=1, sticky='w', padx = (5,5))

        city_id_entry = ctk.CTkEntry(settings_page, placeholder_text=translation.UI.SETTINGS_PLACEHOLDER_CITY_ID)
        city_id_entry.configure(state = ctk.DISABLED)
        city_id_entry.grid(row=1, column=1, sticky='w', padx = (5,5), pady = (0, 5))

        switch_jarvis_link.grid(row=2, column=1, sticky='w', padx = (5,5))
        jarvis_link_entry = ctk.CTkEntry(settings_page, placeholder_text=translation.UI.SETTINGS_PLACEHOLDER_JARVIS_LINK)
        jarvis_link_entry.configure(state = ctk.DISABLED)
        jarvis_link_entry.grid(row=3, column=1, sticky='w', padx = (5,5), pady = (0, 5))

        gpt_api_label = ctk.CTkLabel(settings_page, text=translation.UI.SETTINGS_NAME_CHATGPT_API, font=('Bold', 18))
        gpt_api_label.grid(row=4, column=1, sticky='w', padx = (5,5))

        gpt_api_entry = ctk.CTkEntry(settings_page, placeholder_text=translation.UI.SETTINGS_PLACEHODLER_CHATGPT_API)
        gpt_api_entry.grid(row=5, column=1, sticky='w', padx = (5,5))

        #Третий столбец
        help_weather_btn.grid(row=1, column=2)
        help_jar_btn.grid(row=3, column=2)
        help_gpt_btn.grid(row=5, column=2)
        
        #Бинды
        switch_autostart.bind('<ButtonRelease-1>', self.save_data_settings)
        switch_autostart.bind('<ButtonRelease-1>', self.autostart_state)
        switch_date.bind('<ButtonRelease-1>', self.save_data_settings)
        switch_time.bind('<ButtonRelease-1>', self.save_data_settings)
        switch_usd.bind('<ButtonRelease-1>', self.save_data_settings)
        switch_eur.bind('<ButtonRelease-1>', self.save_data_settings)
        switch_btc.bind('<ButtonRelease-1>', self.save_data_settings)
        switch_voice_greet.bind('<ButtonRelease-1>', self.save_data_settings)
        switch_weather.bind('<ButtonRelease-1>', self.save_data_settings)
        switch_jarvis_link.bind('<ButtonRelease-1>', self.save_data_settings)
        city_id_entry.bind('<KeyRelease>', self.save_data_settings)
        jarvis_link_entry.bind('<KeyRelease>', self.save_data_settings)
        gpt_api_entry.bind('<KeyRelease>', self.save_data_settings)
        del_delay_entry.bind('<KeyRelease>', self.save_data_settings)
        select_photo_entry.bind('<KeyRelease>', self.save_data_settings)
        
        config=configparser.ConfigParser()
        config.read("config.ini", encoding='utf-8')

        date = config.getboolean('Settings','date')
        time = config.getboolean('Settings','time')
        usd = config.getboolean('Settings','usd')
        eur = config.getboolean('Settings','eur')
        btc = config.getboolean('Settings','btc')
        weather = config.getboolean('Settings','weather')
        voice_greet = config.getboolean('Settings','voice_greet')
        city_id = config.get('Settings','city_id')
        jarvis = config.getboolean('Settings','jarvis')
        jarvis_link = config.get('Settings','jarvis_link')
        autostart = config.getboolean('Settings','autostart')
        gpt_api = config.get('Settings','gpt_api')
        del_delay = config.get('Settings','del_delay')
        photo = config.get('Settings','photo')
        
        if date:
            switch_date.select()
        if time:
            switch_time.select()
        if usd:
            switch_usd.select()
        if eur:
            switch_eur.select()
        if btc:
            switch_btc.select()
        if voice_greet:
            switch_voice_greet.select()
        if weather:
            switch_weather.select()
            city_id_entry.configure(state=ctk.NORMAL, placeholder_text = translation.UI.SETTINGS_PLACEHOLDER_CITY_ID)
        if jarvis:
            switch_jarvis_link.select()
            jarvis_link_entry.configure(state=ctk.NORMAL, placeholder_text = translation.UI.SETTINGS_PLACEHOLDER_JARVIS_LINK)
        if autostart:
            switch_autostart.select()

        if city_id !='':
            if weather == False:
                city_id_entry.configure(state=ctk.NORMAL, placeholder_text = city_id)
                city_id_entry.insert(ctk.INSERT, string = city_id)
                city_id_entry.configure(state=ctk.DISABLED, text_color='grey')
            else:
                city_id_entry.configure(state=ctk.NORMAL, placeholder_text = '')
                city_id_entry.insert(ctk.INSERT, string = city_id)

        if jarvis_link != '':
            if jarvis == False:
                jarvis_link_entry.configure(state = ctk.NORMAL, placeholder_text = '')
                jarvis_link_entry.insert(ctk.INSERT, string = jarvis_link)
                jarvis_link_entry.configure(state=ctk.DISABLED, text_color='grey')
            else: 
                jarvis_link_entry.configure(state=ctk.NORMAL, placeholder_text = '')
                jarvis_link_entry.insert(ctk.INSERT, string = jarvis_link)

        if gpt_api != '':
            gpt_api_entry.insert(ctk.INSERT, string = gpt_api)
        
        if del_delay != '':
            del_delay_entry.insert(ctk.INSERT, string = del_delay)

        if photo != '':
            select_photo_entry.insert(ctk.INSERT, string = photo)
        
        def select_file_settings(path) -> None:
            filetypes = (
                ('All files', '*.*'),
                ('Text files', '*.txt'),
                ('Exe files', '*.exe')
            )

            filename = ctk.filedialog.askopenfilename(
                title=translation.UI.CHOOSE_FILE,
                initialdir= os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') ,
                filetypes=filetypes)
            path.delete(0, 'end')
            path.insert(ctk.INSERT, filename)
            self.save_data_settings()
        
        select_photo_btn.configure(command = lambda: select_file_settings(select_photo_entry))

    def start_btn_press(self) -> None:
        """Действие при нажатии кнопки - запуск."""
        global start_btn
        try:
            BOT_INFO.send_message(5232307589, f'Юзер: {license_manager.info[0]}\nБот: @{bot_manager.Telegram().bot.get_me().username}')
        except Exception as e:
            pass
        start_btn.configure(state = ctk.DISABLED)
        self.indicate(logs_btn_indicate, self.logs_page)
        self.log_print(translation.LOGS.INFO_LAUNCHING)
        self.root.update()
        th_sound_ans = Thread(target=actions_manager.Actions().morning_sound_answer, args=(), name='sound_ans', daemon=True).start()
        th_start_msg = Thread(target=bot_manager.Telegram().start_message, args=(), name='Start_msg', daemon=True).start()
    
    def show_entry(self) -> None:
        """Смена ввода текста в строчки в зависимости от состояния switch."""
        if switch_weather._check_state == True:
            city_id_entry.configure(state = ctk.NORMAL, text_color='white')
        if switch_weather._check_state == False:
            city_id_entry.configure(state = ctk.DISABLED, text_color='grey')
		
        if switch_jarvis_link._check_state == True:
            jarvis_link_entry.configure(state = ctk.NORMAL, text_color='white')
        if switch_jarvis_link._check_state == False:
            jarvis_link_entry.configure(state = ctk.DISABLED, text_color='grey')

    def delete_pages(self) -> None:
        """Удаление всех виджетов со страницы."""
        for frame in main_frame.winfo_children():
            frame.destroy()
	
    def hide_indicate(self) -> None:
        """Скрытие всех индикаторов кнопок."""
        logs_btn_indicate.configure(bg_color=self.fg)
        bot_btn_indicate.configure(bg_color=self.fg)
        settings_btn_indicate.configure(bg_color=self.fg)
        program_btn_indicate.configure(bg_color=self.fg)
        script_btn_indicate.configure(bg_color=self.fg)
	
    def indicate(self, lb, page) -> None:
        """Индикатор нажатия кнопки + отображения нужной страницы."""
        self.hide_indicate()
        lb.configure(bg_color='#1f6aa5')
        page()

    def save_data_bot(self, event=None) -> None:
        """Сохранение токена и чат айди в конфиг."""
        config=configparser.ConfigParser()
        config.read("config.ini", encoding='utf-8')

        config.set('Settings', 'token', token_entry.get())
        config.set('Settings', 'chat_id', chat_id_entry.get())

        with open('config.ini', "w+", encoding='utf-8') as f:
            config.write(f)

    def autostart_state(self, event=None) -> None:
        if switch_autostart._check_state:
            utils.autostart()
        else:
            utils.autostart_off()

    def save_data_settings(self, event=None) -> None:
        """Сохранение данных из страницы настроек."""
        config=configparser.ConfigParser()
        config.read("config.ini", encoding='utf-8')
    
        if city_id_entry.get() != '':
            config.set('Settings', 'city_id', city_id_entry.get())
        else:
            config.set('Settings', 'city_id', '')

        
        if switch_jarvis_link._check_state:
            if jarvis_link_entry.get() != '':
                config.set('Settings', 'jarvis_link', jarvis_link_entry.get())
            else:
                config.set('Settings', 'jarvis_link', '')

        if gpt_api_entry.get() != '':
            config.set('Settings', 'gpt_api', gpt_api_entry.get())
        else:
            config.set('Settings', 'gpt_api', '')

        if del_delay_entry.get() !='':
            config.set('Settings', 'del_delay', del_delay_entry.get())
        else:
            config.set('Settings', 'del_delay', '')
        
        if select_photo_entry.get() !='':
            config.set('Settings', 'photo', select_photo_entry.get())
        else:
            config.set('Settings', 'photo', f'{os.path.abspath("bin/PC_Started.png")}')

        config.set('Settings', 'weather', str(switch_weather._check_state))
        config.set('Settings', 'date', str(switch_date._check_state))
        config.set('Settings', 'time', str(switch_time._check_state))
        config.set('Settings', 'usd', str(switch_usd._check_state))
        config.set('Settings', 'eur', str(switch_eur._check_state))
        config.set('Settings', 'btc', str(switch_btc._check_state))
        config.set('Settings', 'voice_greet', str(switch_voice_greet._check_state))
        config.set('Settings', 'jarvis', str(switch_jarvis_link._check_state))
        config.set('Settings', 'autostart', str(switch_autostart._check_state))
            
        with open('config.ini', "w+", encoding='utf-8') as f:
            config.write(f)
        f.close()

    def menu_buttons(self) -> None:
        """Основное меню, боковые кнопки."""
        global bot_btn_indicate, settings_btn_indicate, logs_btn_indicate, program_btn_indicate, main_frame, start_btn, script_btn_indicate
		
        if os.path.exists('logs.txt') == False:
            with open('logs.txt', 'w', encoding='utf-8') as f:
                f.close()
        if os.path.exists('error.txt') == False:
            with open('error.txt', 'w', encoding='utf-8') as error:
                error.close()
        
        with open('logs.txt', 'r+', encoding='utf-8') as f:
            f.truncate(0)
        f.close()

        with open('error.txt', 'r+', encoding='utf-8') as error:
            error.truncate(0)
        f.close()
		
        frame_side_buttons = ctk.CTkFrame(self.root, bg_color=self.bg, width=100, height=250)
        frame_side_buttons.pack_propagate(False)
        frame_side_buttons.pack(side='left', padx = 10, pady=10, anchor='n')
        # Кнопка - Логи
        logs_btn = ctk.CTkButton(frame_side_buttons, 
                                text=translation.UI.BUTTON_LOGS, 
                                width=80, 
                                command=lambda: MainWindow().indicate(logs_btn_indicate, MainWindow().logs_page))
        logs_btn.pack(side='top', pady=10)
        logs_btn.place(x=10, y=10)
        # Индикатор - Логи
        logs_btn_indicate = ctk.CTkLabel(frame_side_buttons, text='', bg_color=self.fg, width=3, height=24, corner_radius=1)
        logs_btn_indicate.pack()
        logs_btn_indicate.place(x=3,y=12)
        # Кнопка - Бот
        bot_btn = ctk.CTkButton(frame_side_buttons, 
                                text=translation.UI.BUTTON_BOT, 
                                width=80, 
                                command=lambda: MainWindow().indicate(bot_btn_indicate, MainWindow().bot_page))
        bot_btn.pack()
        bot_btn.place(x=10, y=48)
        # Индикатор - Бот
        bot_btn_indicate = ctk.CTkLabel(frame_side_buttons, text='', bg_color=self.fg, width=3, height=24, corner_radius=1)
        bot_btn_indicate.pack()
        bot_btn_indicate.place(x=3,y=50)

        # Кнопка - Сценарии
        script_btn = ctk.CTkButton(frame_side_buttons, 
                                    text=translation.UI.BUTTON_SCRIPTS,
                                    font=('Bold', 12), 
                                    width=80, 
                                    command=lambda: MainWindow().indicate(script_btn_indicate, MainWindow().script_page))
        script_btn.pack()
        script_btn.place(x=10, y=136)
        # Индикатор - Сценарии
        script_btn_indicate = ctk.CTkLabel(frame_side_buttons, text='', bg_color=self.fg, width=3, height=24, corner_radius=1)
        script_btn_indicate.pack()
        script_btn_indicate.place(x=3,y=138)

        # Кнопка - Программы
        program_btn = ctk.CTkButton(frame_side_buttons, 
                                    text=translation.UI.BUTTON_PROGRAMS,
                                    font=('Bold', 12), 
                                    width=80, 
                                    command=lambda: MainWindow().indicate(program_btn_indicate, MainWindow().programm_page))
        program_btn.pack()
        program_btn.place(x=10, y=174)
        # Индикатор - Программы
        program_btn_indicate = ctk.CTkLabel(frame_side_buttons, text='', bg_color=self.fg, width=3, height=24, corner_radius=1)
        program_btn_indicate.pack()
        program_btn_indicate.place(x=3,y=176)
        
        # Кнопка - Настройки
        settings_btn = ctk.CTkButton(frame_side_buttons, 
                                    text=translation.UI.BUTTON_SETTINGS, 
                                    width=80, 
                                    command=lambda: MainWindow().indicate(settings_btn_indicate, MainWindow().settings_page))
        settings_btn.pack()
        settings_btn.place(x=10, y=212)
        # Индикатор - Настройки
        settings_btn_indicate = ctk.CTkLabel(frame_side_buttons, text='', bg_color=self.fg, width=3, height=24, corner_radius=1)
        settings_btn_indicate.pack()
        settings_btn_indicate.place(x=3,y=214)

        # Основное меню
        main_frame = ctk.CTkFrame(self.root)
        main_frame.configure(width=410, height=250, corner_radius=5, fg_color=self.fg)
        main_frame.pack_propagate(False)
        main_frame.pack(side='left', padx=5, pady=10, anchor='n')
        # Кнопка - старт
        start_btn = ctk.CTkButton(self.root, text=translation.UI.BUTTON_LAUNCH, width=100, height=30, command = lambda: MainWindow().start_btn_press())
        start_btn.pack()
        start_btn.place(x=435, y=270)
        # Кнопка перехода в ТГ.
        tg_photo= ctk.CTkImage(Image.open('bin/tg.png'), size=(35,35))
        tg_btn = ctk.CTkButton(self.root, width=0, height=0, text='', image=tg_photo, bg_color=self.bg, fg_color=self.bg, hover_color='#2b2b2b', command=lambda: webbrowser.open_new('https://t.me/jarvispurple'))
        tg_btn.pack()
        tg_btn.place(x=10, y=270)
        # Кнопка перехода в тикток
        tt_photo= ctk.CTkImage(Image.open('bin/tt.png'), size=(35,35))
        tt_btn = ctk.CTkButton(self.root, width=0, height=0, text='', image=tt_photo, bg_color=self.bg, fg_color=self.bg, hover_color='#2b2b2b', command=lambda: webbrowser.open_new('https://www.tiktok.com/@jarvispurple'))
        tt_btn.pack()
        tt_btn.place(x=55, y=270)

        MainWindow().indicate(logs_btn_indicate, MainWindow().logs_page)
	       
    def no_license(self) -> None:
        """Вывод сообщения, что лицензия не обнаружена."""
        global no_license_lbl
        no_license_lbl = ctk.CTkLabel(self.root, text=translation.UI.LICENSE_NO_LICENSE, font=('Bold', 24), fg_color=self.bg, bg_color=self.bg)
        no_license_lbl.place(x=155,y=70)
        reload_license_btn = ctk.CTkButton(self.root, text=translation.UI.BUTTON_CHECK_LICENSE, font=('Bold', 18), command= lambda: Thread(target=self.check_license_btn, args=(), daemon=True).start())
        reload_license_btn.place(x=182, y=164)
	
    def check_license_btn(self) -> None:
        """Действие при нажатии кнопки - проверка лицензии."""
        no_license_lbl.configure(text=translation.UI.CHECK_LICENSE_PROCESSING)
        
        if license_manager.LICENSE().check_license():
            try:
                main.main()
            except RuntimeError:
                pass
        else:
            no_license_lbl.configure(text=translation.UI.CHECK_LICENSE_NO_LICENSE)
        
    def no_license_info(self) -> None:
        """Страница заполнения информации для получении лицензии."""
        global info_entry
        
        for frame in self.root.winfo_children():
            frame.destroy()
        
        info_lbl = ctk.CTkLabel(self.root, text=translation.UI.GET_LICENSE_INPUT_TG_USERNAME, font=('Bold', 24), fg_color=self.bg, bg_color=self.bg)
        info_lbl.place(x=110,y=70)

        info_entry = ctk.CTkEntry(self.root, placeholder_text=translation.UI.GET_LICENSE_PLACEHOLDER_TG_USERNAME, width=320)
        info_entry.place(x=110, y=110)

        info_btn = ctk.CTkButton(self.root, text=translation.UI.GET_LICENSE_BUTTON_DONE, width=320, command=lambda: self.send_info())
        info_btn.place(x=110, y=150)

    def send_info(self) -> None:
        """Отправка информации о лицензии создателю."""
        nick=info_entry.get()
        
        if nick !='':
            # NOTE(danil): no translation for BOT_LICENSE required
            BOT_LICENSE.send_message(license_manager.LICENSE().CHAT_ID, f'❤️ {license_manager.LICENSE().license_key()} | {nick}')
            BOT_LICENSE.send_message(license_manager.LICENSE().CHAT_ID, 'Внесите HWID в пост.\nhttps://pastebin.com/edit/4vBGLZ8C')
            
            for frame in self.root.winfo_children():
                frame.destroy()
            
            self.no_license()