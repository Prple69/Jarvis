import configparser
from threading import Thread
import license_manager
import ui
import utils
from config_manager import create_if_not_exist_config

def load_config():
    """Загрузка и возвращение конфигурации из файла."""
    config = configparser.ConfigParser(allow_no_value=True)
    config.read("config.ini", encoding='utf-8')
    return config

def start_app(App, License):
    """Инициализация и запуск приложения."""
    if License.check_license():
        print('Лицензия подтверждена')
        App.menu_buttons()
        config = load_config()
        if config.getboolean('Settings', 'autostart', fallback=False):
            utils.withdraw_window()
            App.start_btn_press()
    else:
        print('Лицензии нет')
        App.no_license_info()

def main():
    """Основная точка входа для приложения."""
    App = ui.MainWindow()
    License = license_manager.LICENSE()
    
    print('Начинаю работу')
    create_if_not_exist_config()
    
    # Запуск приложения и настройка в зависимости от наличия лицензии
    start_app(App, License)

    App.root.protocol('WM_DELETE_WINDOW', utils.withdraw_window)

    # Запуск иконки в фоновом потоке
    Thread(target=utils.start_icon, daemon=True).start()

    App.root.mainloop()

if __name__ == '__main__':
    main()
