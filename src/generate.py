from threading import Lock
from generate_counter import GenerateCounter
from output import Output
from roblox_profile import RobloxProfile
from session import Session
from auth_intent import AuthIntent
from util import Util
from custom_solver import get_token, get_px_cookies
from json import loads, dumps
from base64 import b64encode, b64decode

LOCK = Lock()

def _check_rate_limit(resp):
    if resp.status_code == 429:
        raise ValueError('Rate limited')

class Generate:
    @staticmethod
    def redeem_captcha_v2(session, challenge_id: str) -> tuple:
        Output('CAPTCHA').log('Solving PX captcha')

        px_cookies = get_px_cookies(session)
        if not px_cookies:
            raise ValueError('Failed to solve PX captcha')

        existing = {}
        if session.headers.get('cookie'):
            for pair in session.headers['cookie'].split('; '):
                key = pair.split('=', 1)[0]
                existing[key] = pair

        for k, v in px_cookies.items():
            existing[k] = f'{k}={v}'

        session.headers['cookie'] = '; '.join(existing.values())
        session.headers = Util.sort_dict_order(session.headers)

        Output('CAPTCHA').log(f'Solved PX captcha | {px_cookies.get("_px3", "")[:60]}...')

        session.headers['accept'] = 'application/json'
        resp = session.post('https://apis.roblox.com/v2/captcha', json={'challenge_id': challenge_id})
        _check_rate_limit(resp)

        session.add_cookies(resp)

        if resp.status_code != 200:
            raise ValueError('Rejected by captcha API')

        redemption_token = resp.json().get('redemption_token') or resp.json().get('redemptionToken')
        if not redemption_token:
            raise ValueError('No redemption token returned by captcha API')

        challenge_metadata = dumps({'redemptionToken': redemption_token}, separators=(',', ':'))

        continue_payload = dumps({
            'challengeId': challenge_id,
            'challengeType': 'captchav2',
            'challengeMetadata': challenge_metadata,
        }, separators=(',', ':'))

        resp = session.post('https://apis.roblox.com/challenge/v1/continue', data=continue_payload.encode('utf-8'))
        _check_rate_limit(resp)

        session.add_cookies(resp)

        if resp.status_code != 200:
            raise ValueError('Rejected by continue API')

        data = resp.json()
        raw_metadata = data.get('challengeMetadata')
        new_challenge_id = data.get('challengeId', challenge_id)

        if raw_metadata:
            return new_challenge_id, loads(raw_metadata)

        return new_challenge_id, challenge_metadata

    @staticmethod
    def gen(generate_counter: GenerateCounter) -> None:
        while True:
            try:
                username = RobloxProfile.get_username()
                password = RobloxProfile.get_password()
                birthday = RobloxProfile.get_birth_day()
                gender = RobloxProfile.get_gender()

                Output('INFO').log(f'Generating account {username}')

                session = Session()

                payload = {
                    'username': username,
                    'context': 'Signup',
                    'birthday': birthday,
                }

                resp = session.post('https://auth.roblox.com/v1/usernames/validate', json=payload)
                _check_rate_limit(resp)

                session.add_cookies(resp)

                csrf = resp.headers.get('x-csrf-token')
                if csrf:
                    session.headers = {**session.headers, 'x-csrf-token': csrf}

                while resp.status_code != 200 or resp.json()['code'] != 0:
                    username = RobloxProfile.get_username()
                    payload['username'] = username

                    resp = session.post('https://auth.roblox.com/v1/usernames/validate', json=payload)
                    _check_rate_limit(resp)

                    session.add_cookies(resp)

                    csrf = resp.headers.get('x-csrf-token')
                    if csrf:
                        session.headers = {**session.headers, 'x-csrf-token': csrf}

                resp = session.post('https://auth.roblox.com/v2/passwords/validate', json={'username': username, 'password': password})
                _check_rate_limit(resp)

                session.add_cookies(resp)

                auth_intent = AuthIntent.get_auth_intent(session)

                signup_payload = {
                    'username': username,
                    'password': password,
                    'birthday': birthday,
                    'gender': gender,
                    'isTosAgreementBoxChecked': True,
                    'agreementIds': ['066671de-0a7f-4ea1-b9c4-0e26734c5694', '810ca406-3e52-417d-8bd6-a5ca3c55519d'],
                    'auditSystemContent': {
                        'capturedAuditContent': {
                            'Authentication.SignUp.Label.Birthday': {
                                'translationKey': 'Label.Birthday',
                                'translationNamespace': 'Authentication.SignUp',
                                'translatedSourceString': 'Birthday'
                            },
                            'Authentication.SignUp.Label.Username': {
                                'translationKey': 'Label.Username',
                                'translationNamespace': 'Authentication.SignUp',
                                'translatedSourceString': 'Username'
                            },
                            'Authentication.SignUp.Label.Password': {
                                'translationKey': 'Label.Password',
                                'translationNamespace': 'Authentication.SignUp',
                                'translatedSourceString': 'Password'
                            },
                            'Authentication.SignUp.Label.OptionalGender': {
                                'translationKey': 'Label.OptionalGender',
                                'translationNamespace': 'Authentication.SignUp',
                                'translatedSourceString': 'Gender (optional)'
                            },
                            'Authentication.SignUp.Description.SignUpAgreement.FullCopy': {
                                'translationKey': 'Description.SignUpAgreement.FullCopy',
                                'translationNamespace': 'Authentication.SignUp',
                                'translatedSourceString': 'By clicking Sign Up, you are agreeing to our {termsOfUseLink} (including arbitration) and acknowledge our {privacyPolicyLink}. If you are under 18, you agree that your parent/guardian permits you to create this account and agrees to our Terms of Use.',
                                'parameters': {
                                    'termsOfUseLink': '<a target="_blank" href="https://www.roblox.com/info/terms">Terms of Use</a>', 'privacyPolicyLink': '<a target="_blank" href="https://www.roblox.com/info/privacy">Privacy Policy</a>'
                                }
                            }
                        },
                        'additionalAuditContent': {}
                    },
                    'secureAuthenticationIntent': auth_intent,
                }

                resp = session.post('https://auth.roblox.com/v2/signup', json=signup_payload)
                _check_rate_limit(resp)

                challenge_id = resp.headers.get('rblx-challenge-id')
                challenge_type = resp.headers.get('rblx-challenge-type')

                if not challenge_id:
                    raise ValueError('No challenge returned by signup API')

                if challenge_type == 'captchav2':
                    challenge_id, metadata = Generate.redeem_captcha_v2(session, challenge_id)

                    if isinstance(metadata, str):
                        session.headers = Util.sort_dict_order({
                            **session.headers,
                            'rblx-challenge-id': challenge_id,
                            'rblx-challenge-metadata': b64encode(metadata.encode('utf-8')).decode('utf-8'),
                            'rblx-challenge-type': 'captchav2',
                        })

                        resp = session.post('https://auth.roblox.com/v2/signup', json=signup_payload)
                        if resp.status_code != 200:
                            raise ValueError('Rejected by signup API')

                        session.add_cookies(resp)

                        session.set_page_request_headers()
                        session.get('https://www.roblox.com/home?nu=true')

                        generate_counter.increase_generated()

                        Output('SUCCESS').log(f'Successfully generated account | {username}')

                        account_cookie = resp.cookies['.ROBLOSECURITY']

                        with LOCK:
                            with open('output/accounts.txt', 'a', encoding='utf-8') as file:
                                file.write(f'{username}:{password}:{account_cookie}\n')

                        continue
                else:
                    challenge_metadata_header = resp.headers.get('rblx-challenge-metadata')
                    if not challenge_metadata_header:
                        raise ValueError('No challenge metadata returned by signup API')

                    metadata = loads(b64decode(challenge_metadata_header.encode('utf-8')).decode('utf-8'))

                blob = metadata.get('dataExchangeBlob')
                captcha_id = metadata.get('unifiedCaptchaId')

                if not blob:
                    raise ValueError('No captcha blob returned by challenge API')

                Output('CAPTCHA').log('Solving Arkose captcha')

                solution = get_token(session, blob, session.proxy)
                if solution is None:
                    raise ValueError('Failed to solve Arkose captcha')

                token = solution.split('|')[0]
                token_info = solution.split('pk=A2A14B1D-1AF3-C791-9BBC-EE33CC7A0A6F|')[1].split('|cdn_url=')[0]

                Output('CAPTCHA').log(f'Solved Arkose captcha | {token}|{token_info}')

                challenge_metadata = dumps({
                    'unifiedCaptchaId': captcha_id,
                    'captchaToken': solution,
                    'actionType': 'Signup',
                }, separators=(',', ':'))

                continue_payload = dumps({
                    'challengeId': challenge_id,
                    'challengeType': 'captcha',
                    'challengeMetadata': challenge_metadata,
                }, separators=(',', ':'))

                resp = session.post('https://apis.roblox.com/challenge/v1/continue', data=continue_payload.encode('utf-8'))
                if resp.status_code != 200:
                    raise ValueError('Rejected by continue API')

                session.add_cookies(resp)

                session.headers = Util.sort_dict_order({
                    **session.headers,
                    'rblx-challenge-id': challenge_id,
                    'rblx-challenge-metadata': b64encode(challenge_metadata.encode('utf-8')).decode('utf-8'),
                    'rblx-challenge-type': 'captcha',
                })

                resp = session.post('https://auth.roblox.com/v2/signup', json=signup_payload)
                if resp.status_code != 200:
                    raise ValueError('Rejected by signup API')

                session.add_cookies(resp)

                session.set_page_request_headers()
                session.get('https://www.roblox.com/home?nu=true')

                generate_counter.increase_generated()

                Output('SUCCESS').log(f'Successfully generated account | {username}')

                account_cookie = resp.cookies['.ROBLOSECURITY']

                with LOCK:
                    with open('output/accounts.txt', 'a', encoding='utf-8') as file:
                        file.write(f'{username}:{password}:{account_cookie}\n')

            except Exception as e:
                if 'Failed to perform' in str(e):
                    Output('ERROR').log('Error | Proxy failed to make request')
                else:
                    Output('ERROR').log(f'Error | {str(e)}')