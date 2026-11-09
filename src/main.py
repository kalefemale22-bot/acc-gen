import ctypes
from time import gmtime, strftime, sleep
from threading import Thread
from generate_counter import generate_counter
from generate import Generate
from util import Util

config = Util.get_config()

THREAD_AMOUNT = config['threads']

def cpm_checker() -> None:
    elapsed = 0
    cpm_time = 0

    while True:
        generated = generate_counter.get_generated()
        cpm = round((60 / cpm_time) * generated) if cpm_time != 0 else 0

        ctypes.windll.kernel32.SetConsoleTitleW(f'Elapsed: {strftime('%H:%M:%S', gmtime(elapsed))} | CPM: {cpm}')

        if generated != 0:
            cpm_time += 1

        elapsed += 1

        sleep(1)

def main() -> None:
    for _ in range(THREAD_AMOUNT):
        Thread(target=Generate.gen, args=(generate_counter,), daemon=True).start()

    cpm_checker()

if __name__ == '__main__':
    main()