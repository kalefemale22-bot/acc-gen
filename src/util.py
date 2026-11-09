from string import digits, ascii_letters
from random import choice, randint
from json import load
from secrets import token_hex

with open('input/proxies.txt', 'r', encoding='utf-8') as file:
    proxies = file.readlines()

with open('input/config.json', 'r', encoding='utf-8') as file:
    config = load(file)

HEADER_KEY_ORDER = [
    'content-length',
    'sec-ch-ua-platform',
    'x-csrf-token',
    'sec-ch-ua',
    'sec-ch-ua-mobile',
    'traceparent',
    'accept',
    'content-type',
    'user-agent',
    'origin',
    'sec-fetch-site',
    'sec-fetch-mode',
    'sec-fetch-dest',
    'referer',
    'accept-encoding',
    'accept-language',
    'cookie',
    'priority',
]

class Util:
    @staticmethod
    def get_random_proxy() -> str:
        return choice(proxies).strip('\n')

    @staticmethod
    def get_config() -> dict:
        return config

    @staticmethod
    def get_random_string() -> str:
        return ''.join(choice(ascii_letters + digits) for _ in range(randint(12, 20)))

    @staticmethod
    def sort_dict_order(input_dict: dict) -> dict:
        ordered = {key: input_dict[key] for key in HEADER_KEY_ORDER if key in input_dict}

        for key, value in input_dict.items():
            if key not in ordered:
                ordered[key] = value

        return ordered

    @staticmethod
    def generate_traceparent():
        trace_id = token_hex(16)
        span_id = token_hex(8)

        return f'00-{trace_id}-{span_id}-00'