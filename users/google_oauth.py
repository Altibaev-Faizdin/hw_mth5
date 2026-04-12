"""Обмен authorization code на токен и userinfo Google (только стандартная библиотека)."""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'


class GoogleOAuthError(Exception):
    def __init__(self, message: str, *, status: int | None = None):
        self.message = message
        self.status = status
        super().__init__(message)


def _http_json(
    url: str,
    *,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    method: str = 'GET',
) -> dict[str, Any]:
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors='replace')
        try:
            err = json.loads(body)
        except json.JSONDecodeError:
            err = {'error': body}
        msg = err.get('error_description') or err.get('error') or f'HTTP {e.code}'
        raise GoogleOAuthError(str(msg), status=e.code) from e


def exchange_authorization_code(
    code: str,
    redirect_uri: str,
    client_id: str,
    client_secret: str,
) -> dict[str, Any]:
    payload = urllib.parse.urlencode(
        {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }
    ).encode()
    return _http_json(
        GOOGLE_TOKEN_URL,
        data=payload,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        method='POST',
    )


def fetch_userinfo(access_token: str) -> dict[str, Any]:
    return _http_json(
        GOOGLE_USERINFO_URL,
        headers={'Authorization': f'Bearer {access_token}'},
    )
