from __future__ import annotations

import aiohttp
from http import HTTPStatus

from .const import (
    API_CONTRACTS,
    API_DAILY_PRICES,
    API_DASHBOARD,
    API_OTP_GENERATE,
    API_OTP_VERIFY,
    API_TIMEOUT,
)


class SobryAuthError(Exception):
    """Exception raised for authentication errors."""

    pass


class SobryApiClient:
    """HTTP client for the Sobry backend API."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def generate_otp(self, email: str) -> None:
        """Request an OTP code to be sent to the given email."""
        try:
            async with self._session.post(
                API_OTP_GENERATE,
                json={"email": email},
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
            ) as resp:
                if resp.status not in (HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.NO_CONTENT):
                    raise SobryAuthError(f"OTP generation failed: {resp.status}")
        except aiohttp.ClientError as err:
            raise SobryAuthError(f"Connection error: {err}") from err

    async def verify_otp(self, email: str, code: str) -> dict:
        """Verify OTP code and return auth payload with token and customer info."""
        try:
            async with self._session.post(
                API_OTP_VERIFY,
                json={"email": email, "code": code},
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
            ) as resp:
                if resp.status == HTTPStatus.UNAUTHORIZED:
                    raise SobryAuthError("invalid_code")
                if resp.status not in (HTTPStatus.OK, HTTPStatus.CREATED):
                    raise SobryAuthError(f"OTP verification failed: {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise SobryAuthError(f"Connection error: {err}") from err

    async def get_contracts(self, token: str) -> list:
        """Return all contracts associated with the authenticated user."""
        try:
            async with self._session.get(
                API_CONTRACTS,
                headers={"Authorization": f"Bearer {token}"},
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
            ) as resp:
                if resp.status == HTTPStatus.UNAUTHORIZED:
                    raise SobryAuthError("unauthorized")
                if resp.status != HTTPStatus.OK:
                    raise SobryAuthError(f"Contracts fetch failed: {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise SobryAuthError(f"Connection error: {err}") from err

    async def get_dashboard(self, token: str, contract_id: str) -> dict:
        """Return dashboard data for a given contract."""
        try:
            async with self._session.get(
                API_DASHBOARD,
                params={"contractId": contract_id},
                headers={"Authorization": f"Bearer {token}"},
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
            ) as resp:
                if resp.status == HTTPStatus.UNAUTHORIZED:
                    raise SobryAuthError("unauthorized")
                if resp.status != HTTPStatus.OK:
                    raise SobryAuthError(f"Dashboard fetch failed: {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise SobryAuthError(f"Connection error: {err}") from err

    async def get_daily_prices(self, token: str, contract_id: str, day: str) -> list:
        """Return 15-min price slots for a given contract and ISO date (YYYY-MM-DD)."""
        try:
            async with self._session.get(
                API_DAILY_PRICES,
                params={"contractId": contract_id, "taxMode": "ttc", "granularity": "15m", "day": day},
                headers={"Authorization": f"Bearer {token}"},
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
            ) as resp:
                if resp.status == HTTPStatus.UNAUTHORIZED:
                    raise SobryAuthError("unauthorized")
                if resp.status != HTTPStatus.OK:
                    raise SobryAuthError(f"Daily prices fetch failed: {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise SobryAuthError(f"Connection error: {err}") from err
