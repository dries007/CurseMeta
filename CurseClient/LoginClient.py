import datetime
import json
from typing import Optional

import redis
import requests
import requests_cache


_URL_BASE = 'https://logins-v1.curseapp.net/login/'
_REDIS_KEY_SESSION = 'CurseClientLogin-session'
_REDIS_KEY_LOCK = 'CurseClientLogin-lock'
_REDIS_KEY_LAST_RENEW = 'CurseClientLogin-lastRenew'
MAX_ADDONS_PER_REQUEST = 16000


def _post_json_retry(url, data=None, headers=None, timeout=10, attempts=5):
    while attempts > 0:
        try:
            with requests_cache.disabled():
                r = requests.post(url, json=data, timeout=timeout, headers=headers)
            r.raise_for_status()
            return r.json()
        except ConnectionError or requests.RequestException:
            attempts -= 1
            if attempts == 0:
                raise


class LoginClient(object):
    """
    This class handles Curse/Twitch api login information.
    It uses redis to make sure there is only _one_ session open.
    It locks (via redis) for the required operations, so it should be safe on a multi process setup.
    """
    def __init__(self, code: str, redis_store: redis.Redis):
        self._session = None
        self._redis = redis_store
        if self._redis:
            self._redisLock = self._redis.lock(_REDIS_KEY_LOCK, timeout=60)
            with self._redisLock:
                try:
                    self._lastRenew = self._redis[_REDIS_KEY_LAST_RENEW]
                    self._session = json.loads(self._redis[_REDIS_KEY_SESSION])
                except json.JSONDecodeError as e:
                    # get here instead of [] to not raise keyerror.
                    self.error(e, "Redis session invalid json.", self._redis.get(_REDIS_KEY_SESSION))
                    self._redis.delete(_REDIS_KEY_SESSION, _REDIS_KEY_LAST_RENEW)
                except KeyError:
                    self._redis.delete(_REDIS_KEY_SESSION, _REDIS_KEY_LAST_RENEW)
                if not self._session_valid():
                    self._lastRenew = self._login(code)
                    self._redis[_REDIS_KEY_LAST_RENEW] = self._lastRenew
                    self._redis[_REDIS_KEY_SESSION] = json.dumps(self._session)
        else:
            print("!!DANGER!! Running without redis is unsupported. Curse login information cannot be shared.")
            self._login(code)
        self.renew_session()

    def __repr__(self):
        return "<CurseClient.LoginClient Redis={} Session={}>".format(self._redis, self._session)

    def _login(self, code):
        """
        Lock must be already acquired if redis is used!
        This can only be used once per code, and codes cannot be acquired automatically.
        This means that everything possible should be done to avoid the token expiring.
        """
        output = None
        try:
            data = {
                "ClientID": "jf3xu125ejjjt5cl4osdjci6oz6p93r",
                "Code": code,
                "RedirectUri": "https://web.curseapp.net/laguna/passport-callback.html",
                "State": ""
            }
            output = _post_json_retry(_URL_BASE + "twitch-oauth", data=data)
            self._session = output["Session"]
            if not self._session_valid():
                print(self._session)
                raise RuntimeError("Returned session not valid.")
            if output["Status"] != 0:
                # Warning
                self.error(None, "Login Status != 0", code=code, output=output)
        except BaseException as e:
            # This is *bad*
            self.error(e, "Error logging in.", code=code, output=output)
            raise
        print("Curse Login successful. Code now used!")
        return int(output["Timestamp"] / 1000)

    # noinspection PyMethodMayBeStatic
    def error(self, exception: Optional[BaseException], message: str, *args, **kwargs):
        """
        Should tell sysop about warning (if exception None) or error.
        """
        print(exception, message, "Extra data:", repr(args), repr(kwargs))

    def _session_valid(self) -> bool:
        """
        False if session is invalid. (Either None, missing keys or expired)
        """
        if self._session is None:
            return False
        for key in ["Token", "Expires", "RenewAfter"]:
            if key not in self._session:
                return False
        return datetime.datetime.fromtimestamp(self._session["Expires"] / 1000) > datetime.datetime.now()

    def _session_should_renew(self, check_redis) -> bool:
        """
        Should only be called if a valid session is stored.
        True if a renew should be tried.
        """
        if check_redis and self._redis:
            with self._redisLock:
                try:
                    if self._lastRenew != self._redis[_REDIS_KEY_LAST_RENEW]:
                        return True
                except KeyError:
                    self._redis.delete(_REDIS_KEY_SESSION, _REDIS_KEY_LAST_RENEW)
                    return True
        return datetime.datetime.fromtimestamp(self._session["RenewAfter"] / 1000) < datetime.datetime.now()

    def renew_session(self):
        """
        This function checks if the session is still valid.
        If not, raise a RuntimeError
        :return: True if the session was renewed
        """
        if not self._session_valid() or self._session_should_renew(True):
            if self._redis:
                with self._redisLock:
                    old_last_renew = self._lastRenew
                    old_session = self._session
                    # Try loading (maybe updated) redis session data.
                    try:
                        self._lastRenew = self._redis[_REDIS_KEY_LAST_RENEW]
                        self._session = json.loads(self._redis[_REDIS_KEY_SESSION])
                    except json.JSONDecodeError as e:
                        # get here instead of [] to not raise keyerror.
                        self.error(e, "Redis session invalid json.", self._redis.get(_REDIS_KEY_SESSION))
                        self._redis.delete(_REDIS_KEY_SESSION, _REDIS_KEY_LAST_RENEW)
                    except KeyError:
                        self._redis.delete(_REDIS_KEY_SESSION, _REDIS_KEY_LAST_RENEW)
                    if not self._session_valid():
                        # Session was either invalid before or became invalid thanks to redis. Restore.
                        self._lastRenew = old_last_renew
                        self._session = old_session
                        if not self._session_valid():
                            # This is *bad*
                            self.error(None, "Session became invalid.", session=self._session)
                            raise RuntimeError("Session became invalid.")
                    # Now we've loaded the session data from redis, someone else might have already renewed it.
                    if self._session_should_renew(False):
                        try:
                            data = _post_json_retry(_URL_BASE + "renew", headers=self.get_headers(True))
                            print("Curse Login renewed.")
                            self._lastRenew = int(datetime.datetime.now().timestamp())
                            self._session.update(data)
                            self._redis.set(_REDIS_KEY_LAST_RENEW, self._lastRenew)
                            self._redis.set(_REDIS_KEY_SESSION, json.dumps(self._session))
                        except BaseException as e:
                            # This is *bad*
                            self.error(e, "Error renewing session. Keeping old.", data=data, session=self._session)
            else:
                data = None
                try:
                    data = _post_json_retry(_URL_BASE + "renew", headers=self.get_headers(True))
                    print("Curse Login renewed.")
                    self._session.update(data)
                except BaseException as e:
                    # This is *bad*
                    self.error(e, "Error renewing session. Keeping old.", data=data, session=self._session)
            return True
        return False

    def get_token(self, __is_renewing=False):
        """
        Returns our current token. May be renewed first if required.
        :param __is_renewing: Must be false unless called from self.renew_session
        """
        if not __is_renewing:
            self.renew_session()
        return self._session['Token']

    def get_headers(self, __is_renewing=False):
        """
        Returns the header(s) required for authentication to the API.
        :param __is_renewing: Must be false unless called from self.renew_session
        """
        return {'AuthenticationToken': self.get_token()}
