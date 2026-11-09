from util import Util
from time import sleep
from curl_cffi import requests

config = Util.get_config()

SOLVER_KEY = config['solverKey']
CHALLENGE_PUBLIC_KEY = 'A2A14B1D-1AF3-C791-9BBC-EE33CC7A0A6F'
MAX_POLL_ATTEMPTS = 120
PX_SITE = 'https://www.roblox.com/CreateAccount'

def get_px_cookies(roblox_session) -> dict | None:
    session = requests.Session()

    payload = {
        'key': SOLVER_KEY,
        'taskType': 'PerimeterXCookies',
        'appId': 'PXbf8PROpW',
        'site': PX_SITE,
        'proxy': roblox_session.proxy,
    }

    response = session.post('https://rosolve.pro/createTask', json=payload, timeout=120).json()

    task_id = response.get('taskId')
    if task_id is None:
        return None

    for _ in range(MAX_POLL_ATTEMPTS):
        sleep(1)

        result = session.post('https://rosolve.pro/taskResult', json={'key': SOLVER_KEY, 'taskId': task_id}).json()

        if result['status'] == 'completed':
            return result['result']['cookies']
        elif result['status'] == 'failed':
            return None

    return None

def get_token(roblox_session, blob: str, proxy: str) -> str | None:
    session = requests.Session()

    payload = {
        'key': SOLVER_KEY,
        'challengeInfo': {
            'publicKey': CHALLENGE_PUBLIC_KEY,
            'site': 'https://www.roblox.com/',
            'surl': 'https://arkoselabs.roblox.com',
            'capiMode': 'inline',
            'styleTheme': 'default',
            'languageEnabled': False,
            'jsfEnabled': False,
            'extraData': {'blob': blob},
            'ancestorOrigins': ['https://www.roblox.com'],
            'treeIndex': [0],
            'treeStructure': '[[]]',
            'locationHref': 'https://www.roblox.com/arkose/iframe',
            'documentReferrer': 'https://www.roblox.com/CreateAccount',
        },
        'browserInfo': {
            'HTTP3': True,
            'Sec-Ch-Ua': roblox_session.headers['sec-ch-ua'],
            'User-Agent': roblox_session.headers['user-agent'],
            'Mobile': False,
        },
        'proxy': proxy,
    }

    response = session.post('https://rosolve.pro/createTask', json=payload, timeout=120).json()

    task_id = response.get('taskId')
    if task_id is None:
        raise ValueError(f'Failed to get taskId, reason: {response.get('error', 'unknown')}')

    for _ in range(MAX_POLL_ATTEMPTS):
        sleep(1)

        result = session.post('https://rosolve.pro/taskResult', json={'key': SOLVER_KEY, 'taskId': task_id}).json()

        if result['status'] == 'completed':
            return result['result']['solution']
        elif result['status'] == 'failed':
            return None

    return None