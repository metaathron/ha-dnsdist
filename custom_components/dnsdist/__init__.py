"""The dnsdist integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .api import DnsdistApiClient
from .const import CONF_API_KEY, CONF_ENDPOINT, CONF_VERIFY_SSL, DOMAIN, PLATFORMS
from .coordinator import DnsdistDataUpdateCoordinator


type DnsdistConfigEntry = ConfigEntry


async def async_setup_entry(hass: HomeAssistant, entry: DnsdistConfigEntry) -> bool:
    """Set up dnsdist from a config entry."""
    client = DnsdistApiClient(
        async_get_clientsession(hass),
        entry.data[CONF_ENDPOINT],
        entry.data[CONF_API_KEY],
        entry.data.get(CONF_VERIFY_SSL, True),
    )
    coordinator = DnsdistDataUpdateCoordinator(hass, client, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    known_servers = set(coordinator.server_names)

    @callback
    def _remove_missing_servers() -> None:
        nonlocal known_servers
        current_servers = set(coordinator.server_names)
        removed_servers = known_servers - current_servers
        if not removed_servers:
            known_servers = current_servers
            return

        entity_registry = er.async_get(hass)
        device_registry = dr.async_get(hass)

        for server_name in removed_servers:
            prefix = f"{entry.entry_id}_server_{server_name}_"
            for entity_entry in er.async_entries_for_config_entry(entity_registry, entry.entry_id):
                if entity_entry.unique_id.startswith(prefix):
                    entity_registry.async_remove(entity_entry.entity_id)

            device_id = device_registry.async_get_device(
                identifiers={(DOMAIN, f"{entry.entry_id}_server_{server_name}")}
            )
            if device_id is not None:
                device_registry.async_remove_device(device_id.id)

        known_servers = current_servers

    entry.async_on_unload(coordinator.async_add_listener(_remove_missing_servers))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DnsdistConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: DnsdistConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
