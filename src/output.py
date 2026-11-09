from datetime import datetime
from colorama import init, Fore
from threading import Lock

init()

_lock = Lock()

LOG_LEVELS = {
    'INFO': (Fore.LIGHTCYAN_EX, '^'),
    'CAPTCHA': (Fore.LIGHTBLUE_EX, '\U0001f916'),
    'ERROR': (Fore.LIGHTRED_EX, '❌'),
    'SUCCESS': (Fore.LIGHTGREEN_EX, '✅'),
}

class Output:
    def __init__(self, level: str):
        self.level = level

    def log(self, message: str):
        color, icon = LOG_LEVELS[self.level]
        time_now = datetime.now().strftime('%H:%M:%S')
        line = f'{Fore.LIGHTBLACK_EX}[{time_now}]{Fore.RESET} ({color}{icon}{Fore.RESET}){color} {message}'

        with _lock:
            print(line)