"""Binary sensor platform for dnsdist."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DnsdistDataUpdateCoordinator
from .entity import DnsdistServerEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up dnsdist binary sensors from a config entry."""
    coordinator: DnsdistDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    known_servers = set(coordinator.server_names)
    async_add_entities(
        [DnsdistServerStateBinarySensor(coordinator, name) for name in sorted(known_servers)]
    )

    @callback
    def _async_add_new_server_entities() -> None:
        nonlocal known_servers
        current = coordinator.server_names
        new_servers = sorted(current - known_servers)
        if not new_servers:
            return

        known_servers |= set(new_servers)
        async_add_entities(
            [DnsdistServerStateBinarySensor(coordinator, name) for name in new_servers]
        )

    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_server_entities))


class DnsdistServerStateBinarySensor(DnsdistServerEntity, BinarySensorEntity):
    """Connectivity state of a dnsdist backend."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self, coordinator: DnsdistDataUpdateCoordinator, server_name: str
    ) -> None:
        """Initialize binary sensor."""
        super().__init__(coordinator, server_name)
        self._attr_unique_id = f"{self._entry_id}_server_{server_name}_state"
        self._attr_name = "State"

    @property
    def is_on(self) -> bool | None:
        """Return true if backend is up."""
        server = self.server
        if server is None:
            return None
        return str(server.get("state", "")).lower() == "up"
