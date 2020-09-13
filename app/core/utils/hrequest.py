import json
from dataclasses import dataclass, field
from enum import Enum, unique
from json import JSONDecodeError
from typing import Optional

import requests

CHROME_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:80.0) Gecko/20100101 Firefox/80.0"


@unique
class HResponseStatus(str, Enum):
    OK = "OK"
    TIMEOUT = "TIMEOUT"
    PROXY_ERROR = "PROXY_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    ERROR = "ERROR"


@dataclass
class HResponse:
    """HTTP Response"""

    status: HResponseStatus
    message: str = ""

    http_code: int = 0
    body: str = ""
    headers: dict = field(default_factory=lambda: {})

    _json_data = None
    _json_parsed = False
    _json_parsed_error = False

    @property
    def json(self) -> dict:
        if not self._json_parsed:
            self._parse_json()
        return self._json_data  # type: ignore

    @property
    def json_parse_error(self) -> bool:
        if not self._json_parsed:
            self._parse_json()
        return self._json_parsed_error

    def _parse_json(self):
        try:
            self._json_data = {}
            self._json_data = json.loads(self.body)
            self._json_parsed_error = False
        except JSONDecodeError:
            self._json_parsed_error = True
        self._json_parsed = True


def hrequest(
    url: str,
    *,
    method="GET",
    proxy: Optional[str] = None,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    timeout=10,
    user_agent: Optional[str] = None,
    json_params=False,
) -> HResponse:
    method = method.upper()
    proxies = {"http": proxy, "https": proxy} if proxy else None
    if not headers:
        headers = {}
    try:
        headers["user-agent"] = user_agent
        if method == "GET":
            r = requests.get(url, proxies=proxies, timeout=timeout, headers=headers, params=params)
        elif method == "POST":
            if json_params:
                r = requests.post(url, proxies=proxies, timeout=timeout, headers=headers, json=params)
            else:
                r = requests.post(url, proxies=proxies, timeout=timeout, headers=headers, data=params)
        elif method == "PUT":
            if json_params:
                r = requests.put(url, proxies=proxies, timeout=timeout, headers=headers, json=params)
            else:
                r = requests.put(url, proxies=proxies, timeout=timeout, headers=headers, data=params)
        elif method == "DELETE":
            if json_params:
                r = requests.delete(url, proxies=proxies, timeout=timeout, headers=headers, json=params)
            else:
                r = requests.delete(url, proxies=proxies, timeout=timeout, headers=headers, data=params)
        else:
            raise ValueError(method)
        return HResponse(HResponseStatus.OK, http_code=r.status_code, body=r.text, headers=dict(r.headers))
    except requests.exceptions.Timeout as e:
        return HResponse(HResponseStatus.TIMEOUT, message=str(e))
    except requests.exceptions.ProxyError:
        return HResponse(HResponseStatus.PROXY_ERROR)
    except requests.exceptions.ConnectionError as e:
        return HResponse(HResponseStatus.CONNECTION_ERROR, message=str(e))
    except Exception as err:
        return HResponse(HResponseStatus.ERROR, message=str(err))
