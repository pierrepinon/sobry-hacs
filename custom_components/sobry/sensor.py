from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import APP_URL, DOMAIN
from .coordinator import SobryContractCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Create one sensor per Sobry contract and register them with HA."""
    coordinators: list[SobryContractCoordinator] = hass.data[DOMAIN][entry.entry_id]["coordinators"]
    async_add_entities(SobryCurrentPriceSensor(coord) for coord in coordinators)


class _SobryBaseSensor(CoordinatorEntity[SobryContractCoordinator], SensorEntity):
    """Base sensor: binds a HA entity to one Sobry contract coordinator."""

    def __init__(self, coordinator: SobryContractCoordinator) -> None:
        super().__init__(coordinator)
        contract = coordinator.contract
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, contract["id"])},
            name=f"Contrat {contract['ref']}",
            manufacturer="Sobry",
            model=f"Linky {contract['pdl']}",
            configuration_url=APP_URL,
        )

    def _today_cache(self) -> dict[int, dict]:
        """Return only today's slots from the coordinator cache (keyed by Unix timestamp)."""
        cache = self.coordinator.data
        if not cache:
            return {}
        now = dt_util.now()
        day_start = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
        return {ts: slot for ts, slot in cache.items() if day_start <= ts < day_start + 86400}


class SobryCurrentPriceSensor(_SobryBaseSensor):
    """Current electricity price for a Sobry contract, updated every 15 min.

    State   : price in EUR/kWh for the ongoing 15-min slot.
    Attributes:
      color        — tariff tier identifier (e.g. "green", "red")
      color_label  — human-readable tier label (e.g. "Off-peak", "Peak")
    """

    _attr_native_unit_of_measurement = "EUR/kWh"
    _attr_suggested_display_precision = 4
    _attr_icon = "mdi:meter-electric"

    def __init__(self, coordinator: SobryContractCoordinator) -> None:
        super().__init__(coordinator)
        contract = coordinator.contract
        self._attr_unique_id = f"{contract['id']}_current_price"
        self._attr_name = "Prix Actuel"

    @property
    def native_value(self) -> float | None:
        slot = _current_slot(self._today_cache())
        return slot.get("price") if slot else None

    @property
    def extra_state_attributes(self) -> dict | None:
        slot = _current_slot(self._today_cache())
        if slot is None:
            return None
        return {
            "color": slot.get("color"),
            "color_label": slot.get("colorLabel"),
        }


def _current_slot(cache: dict[int, dict]) -> dict | None:
    """Return the slot whose 15-min window contains the current time, or None."""
    now = dt_util.now()
    # Floor to the nearest 15-min boundary to match slot keys in the cache.
    ts = int(now.replace(minute=(now.minute // 15) * 15, second=0, microsecond=0).timestamp())
    return cache.get(ts)

