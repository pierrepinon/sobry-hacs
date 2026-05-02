from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
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
    async_add_entities(
        entity
        for coord in coordinators
        for entity in (
            SobryCurrentPriceSensor(coord),
            SobrySubscribedPowerSensor(coord),
            SobryMonthlyEnergySensor(coord),
            SobryMonthlyPriceSensor(coord),
        )
    )


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

    def _next_24h_slots(self) -> list[dict]:
        """Return slots covering the next 24 hours, ordered chronologically."""
        cache = self.coordinator.data
        if not cache:
            return []
        now = dt_util.now()
        current_ts = int(now.replace(minute=(now.minute // 15) * 15, second=0, microsecond=0).timestamp())
        cutoff = current_ts + 86400
        return [
            {"timestamp": ts, "price": slot.get("price")}
            for ts, slot in sorted(cache.items())
            if current_ts <= ts < cutoff
        ]


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
            "prices": self._next_24h_slots(),
        }


class SobryMonthlyEnergySensor(_SobryBaseSensor):
    """Monthly energy consumption for a Sobry contract."""

    _attr_native_unit_of_measurement = "kWh"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_icon = "mdi:lightning-bolt"

    def __init__(self, coordinator: SobryContractCoordinator) -> None:
        super().__init__(coordinator)
        contract = coordinator.contract
        self._attr_unique_id = f"{contract['id']}_monthly_energy"
        self._attr_name = "Consommation Mensuelle"

    @property
    def native_value(self) -> float | None:
        return self.coordinator.contract.get("consumption", {}).get("energy")


class SobryMonthlyPriceSensor(_SobryBaseSensor):
    """Monthly electricity cost for a Sobry contract."""

    _attr_native_unit_of_measurement = "EUR"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_suggested_display_precision = 2
    _attr_icon = "mdi:currency-eur"

    def __init__(self, coordinator: SobryContractCoordinator) -> None:
        super().__init__(coordinator)
        contract = coordinator.contract
        self._attr_unique_id = f"{contract['id']}_monthly_price"
        self._attr_name = "Coût Mensuel"

    @property
    def native_value(self) -> float | None:
        return self.coordinator.contract.get("consumption", {}).get("price")


class SobrySubscribedPowerSensor(_SobryBaseSensor):
    """Contracted maximum power for a Sobry contract (diagnostic)."""

    _attr_native_unit_of_measurement = "kVA"
    _attr_icon = "mdi:lightning-bolt"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: SobryContractCoordinator) -> None:
        super().__init__(coordinator)
        contract = coordinator.contract
        self._attr_unique_id = f"{contract['id']}_subscribed_power"
        self._attr_name = "Puissance Souscrite"

    @property
    def native_value(self) -> int | None:
        return self.coordinator.contract.get("meter", {}).get("subscribedPower")


def _current_slot(cache: dict[int, dict]) -> dict | None:
    """Return the slot whose 15-min window contains the current time, or None."""
    now = dt_util.now()
    # Floor to the nearest 15-min boundary to match slot keys in the cache.
    ts = int(now.replace(minute=(now.minute // 15) * 15, second=0, microsecond=0).timestamp())
    return cache.get(ts)

