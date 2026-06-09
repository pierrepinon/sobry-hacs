from __future__ import annotations

import logging
from datetime import date, datetime, time, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import SobryApiClient, SobryAuthError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Only keep today and tomorrow in the cache.
# Past days are useless: sensors only display slots for the current day.
_CACHE_MAX_DAYS = 2


class SobryContractCoordinator(DataUpdateCoordinator[dict[int, dict]]):
    """Price data coordinator for a single Sobry electricity contract."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: SobryApiClient, token: str, contract: dict) -> None:
        super().__init__(hass, _LOGGER, name=f"{DOMAIN}_{contract['id']}")
        self._entry = entry
        self._client = client
        self._token = token
        self.contract = contract
        self._price_cache: dict[int, dict] = {}
        self._last_cache_purge = date.today()

    # ------------------------------------------------------------------
    # DataUpdateCoordinator interface
    # ------------------------------------------------------------------

    async def _async_update_data(self) -> dict[int, dict]:
        """Load today's prices if not cached, then return the full cache."""
        today = date.today().isoformat()
        if self._is_stale(today):
            try:
                slots = await self._client.get_daily_prices(self._token, self.contract["id"], today)
                self._set_cache(today, slots)
            except SobryAuthError as err:
                raise UpdateFailed(str(err)) from err

        # Clean up cache once per day to avoid unnecessary overhead
        if date.today() != self._last_cache_purge:
            self._purge_old_cache()
            self._last_cache_purge = date.today()

        return self._price_cache

    async def async_setup(self) -> None:
        """Perform the initial data fetch and register time triggers."""
        await self.async_refresh()

        # Pre-fetch tomorrow if HA starts after 14:00
        if dt_util.now().hour >= 14:
            await self._fetch_tomorrow()

        # Refresh sensors at each 15-min slot boundary
        self._entry.async_on_unload(
            async_track_time_change(
                self.hass, self._handle_slot_boundary, minute=[0, 15, 30, 45], second=0,
            )
        )

        # 14:00: pre-fetch tomorrow's prices
        self._entry.async_on_unload(
            async_track_time_change(
                self.hass, self._handle_fetch_tomorrow, hour=14, minute=0, second=0
            )
        )

    # ------------------------------------------------------------------
    # Time-triggered callbacks
    # ------------------------------------------------------------------

    async def _handle_slot_boundary(self, _) -> None:
        """Trigger a coordinator refresh at each 15-min slot boundary."""
        await self.async_refresh()

    @callback
    def _handle_fetch_tomorrow(self, _) -> None:
        """Trigger a pre-fetch of tomorrow's prices at 14:00."""
        self.hass.async_create_task(self._fetch_tomorrow())

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _fetch_tomorrow(self) -> None:
        """Fetch and cache tomorrow's price slots."""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        if not self._is_stale(tomorrow):
            return
        try:
            slots = await self._client.get_daily_prices(self._token, self.contract["id"], tomorrow)
            self._set_cache(tomorrow, slots)
        except SobryAuthError:
            _LOGGER.warning("Failed to pre-fetch prices for %s", tomorrow)

    @staticmethod
    def _day_ts(day: str, slot_time: str) -> int:
        """Return the Unix timestamp for a given ISO date and HH:MM slot time."""
        hour: int = int(slot_time.split(':')[0])
        minute: int = int(slot_time.split(':')[1])
        return int(datetime.combine(date.fromisoformat(day), time(hour, minute)).timestamp())

    def _is_stale(self, day: str) -> bool:
        """Return True if the cache has no entry for the midnight slot of day."""
        return SobryContractCoordinator._day_ts(day, "00:00") not in self._price_cache

    def _set_cache(self, day: str, slots: list) -> None:
        """Store each slot keyed by its start timestamp."""
        for slot in slots:
            self._price_cache[SobryContractCoordinator._day_ts(day, slot["time"])] = slot

    def _purge_old_cache(self) -> None:
        """Remove cache entries older than _CACHE_MAX_DAYS days."""
        cutoff = SobryContractCoordinator._day_ts(
            (date.today() - timedelta(days=_CACHE_MAX_DAYS - 1)).isoformat(), "00:00"
        )
        for ts in [ts for ts in self._price_cache if ts < cutoff]:
            del self._price_cache[ts]
