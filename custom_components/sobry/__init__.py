from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SobryApiClient
from .const import CONF_TOKEN, DOMAIN
from .coordinator import SobryContractCoordinator

PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sobry from a config entry.

    Creates one coordinator per contract, performs the initial price fetch,
    then forwards setup to the sensor platform.
    """
    hass.data.setdefault(DOMAIN, {})

    # Initialize the API Client
    client = SobryApiClient(async_get_clientsession(hass))

    # Fetch contracts
    contracts = await client.get_contracts(entry.data[CONF_TOKEN])

    coordinators = []
    for contract in contracts:
        dashboard = await client.get_dashboard(entry.data[CONF_TOKEN], contract["id"])
        contract["meter"] = dashboard.get("meter", {})
        contract["consumption"] = dashboard.get("consumption", {})
        coordinator = SobryContractCoordinator(hass, entry, client, entry.data[CONF_TOKEN], contract)
        await coordinator.async_setup()
        coordinators.append(coordinator)

    hass.data[DOMAIN][entry.entry_id] = {
        **entry.data,
        "contracts": contracts,
        "coordinators": coordinators,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and clean up its data."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded
