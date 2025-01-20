import datetime as dt
import hashlib

import pythoncom
import requests
from wmi import WMI

import ui

from config_manager import translation


info = []


class LICENSE():
    """Класс лицензии."""
    def __init__(self) -> None:
        self.CHAT_ID=5232307589
        self.LICENSE_URL='https://pastebin.com/raw/4vBGLZ8C'

    def license_key(self) -> str:
        """Генерация хвида."""
        try:
            pythoncom.CoInitialize()
        except:
            pass
        key = WMI().Win32_ComputerSystemProduct()[0].UUID
        key = hashlib.sha256(key.encode()).hexdigest()
        return str(key[:32])
    
    def check_license(self) -> bool:
        """Checks for the presence of the license on the pastebin page."""
        return True  # TODO(danil): DELETE
        key = self.license_key()
        try:
            tone = requests.get(self.LICENSE_URL).text.split('\n')
            for line in tone:
                line = line.strip()
                try:
                    hwid = line.split(' ')[1]
                    print(hwid, key)
                except IndexError:
                    continue
                if hwid == key:
                    info.append(line.split(' ')[3])
                    date = line.split(' ')[4].strip()
                    if date == 'lt':
                        title = translation.UI.TITLE_LICENSE_UNLIMITED
                    else:
                        today = dt.datetime.now()
                        date_time_obj = dt.datetime.strptime(date, '%d.%m.%Y')
                        delta_days = (date_time_obj - today).days
                        if delta_days < 0:
                            return False
                        else:
                            title = translation.UI.TITLE_LICENSE_LIMITED.format(days=delta_days+1)
                    ui.MainWindow().root.title(title)
                    return True
            return False
        except Exception as e:
            print(e)
            return False

print(LICENSE().check_license())