from curl_cffi import Session as CurlSession, Response
from util import Util

SEC_CH_UA = '"Not:A-Brand";v="8", "Chromium";v="156", "Google Chrome";v="156"'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36'

class Session:
    def __init__(self):
        self.proxy = Util.get_random_proxy()
        self._session = CurlSession(
            impersonate='chrome',
            discard_cookies=True,
            default_headers=0,
            proxy=self.proxy,
            verify=False
        )

        self.headers = Util.sort_dict_order({
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://www.roblox.com',
            'priority': 'u=1, i',
            'sec-ch-ua': SEC_CH_UA,
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'traceparent': Util.generate_traceparent(),
            'user-agent': USER_AGENT
        })

    @property
    def headers(self):
        return self._session.headers

    @headers.setter
    def headers(self, value):
        self._session.headers = value

    def get(self, url, **kwargs):
        return self._session.get(url, **kwargs)

    def post(self, url, **kwargs):
        return self._session.post(url, **kwargs)

    def add_cookies(self, response: Response):
        if response.cookies:
            existing = {}

            if self.headers.get('cookie'):
                for pair in self.headers['cookie'].split('; '):
                    key = pair.split('=', 1)[0]
                    existing[key] = pair

            for cookie in response.headers.get_list('set-cookie'):
                pair = cookie.split(';')[0]
                key = pair.split('=', 1)[0]
                existing[key] = pair

            self.headers['cookie'] = '; '.join(existing.values())
            self.headers = Util.sort_dict_order(self.headers)