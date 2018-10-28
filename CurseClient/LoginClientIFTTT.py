import redis
import requests
import requests_cache
import traceback
import html
from typing import Optional

from .LoginClient import LoginClient


class LoginClientIFTTT(LoginClient):

    def __init__(self, code: str, redis_store: redis.Redis, key, event):
        # URL needs to set first, because it's used if the constructor errors out.
        self._url = "https://maker.ifttt.com/trigger/{}/with/key/{}".format(event, key)
        super().__init__(code, redis_store)

    def error(self, exception: Optional[BaseException], message: str, *args, **kwargs):
        super().error(exception, message, *args, **kwargs)
        s = 'font-family: monospace; white-space: pre !important;'
        extra = '<h3>Stacktrace</h3>\n' \
                '<p style="{}">{}</p>\n'.format(s, html.escape(str(traceback.format_exc())))
        if args:
            extra += '<h3>Args</h3>\n' \
                     '<p style="{}">{}</p>\n'.format(s, html.escape('\n'.join(args)))
        if kwargs:
            extra += '<h3>KWArgs</h3>\n'
            for k, v in kwargs.items():
                extra += '<h4>{}</h4>\n<p style="{}">{}</p>\n'.format(html.escape(str(k)), s, html.escape(str(v)))

        payload = {
            'value1': html.escape(str(exception)) if exception else 'WARNING',
            'value2': html.escape(str(message)),
            'value3': extra
        }
        with requests_cache.disabled():
            r = requests.post(self._url, json=payload)
            r.raise_for_status()
            print("ITFFF action:", r.status_code, r.text)
