"""Shared entity classes for dnsdist."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_ADDRESS,
    ATTR_PROTOCOL,
    ATTR_SERVER_ID,
    ATTR_SERVER_NAME,
    DOMAIN,
    MAIN_DEVICE_ID,
)
from .coordinator import DnsdistDataUpdateCoordinator


class DnsdistBaseEntity(CoordinatorEntity[DnsdistDataUpdateCoordinator]):
    """Base entity for dnsdist."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: DnsdistDataUpdateCoordinator) -> None:
        """Initialize base entity."""
        super().__init__(coordinator)
        self._entry_id = coordinator.config_entry.entry_id


class DnsdistMainEntity(DnsdistBaseEntity):
    """Base entity for main dnsdist device."""

    @property
    def device_info(self) -> DeviceInfo:
        """Return main dnsdist device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry_id}_{MAIN_DEVICE_ID}")},
            name="DNSdist Server",
            manufacturer="PowerDNS",
            model="dnsdist",
            sw_version=self.coordinator.data.get("version") if self.coordinator.data else None,
        )


class DnsdistServerEntity(DnsdistBaseEntity):
    """Base entity for dnsdist backend server."""

    def __init__(self, coordinator: DnsdistDataUpdateCoordinator, server_name: str) -> None:
        """Initialize backend entity."""
        super().__init__(coordinator)
        self.server_name = server_name

    @property
    def server(self) -> dict | None:
        """Return server payload."""
        return self.coordinator.get_server(self.server_name)

    @property
    def device_info(self) -> DeviceInfo:
        """Return backend device info."""
        server = self.server or {}
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry_id}_server_{self.server_name}")},
            name=f"DNSdist {self.server_name}",
            manufacturer="PowerDNS",
            model="dnsdist backend",
            sw_version=self.coordinator.data.get("version") if self.coordinator.data else None,
            via_device=(DOMAIN, f"{self._entry_id}_{MAIN_DEVICE_ID}"),
        )

    @property
    def extra_state_attributes(self) -> dict[str, str | int] | None:
        """Return backend attributes common for this device."""
        server = self.server
        if server is None:
            return None

        return {
            ATTR_ADDRESS: server.get("address"),
            ATTR_PROTOCOL: server.get("protocol"),
            ATTR_SERVER_ID: server.get("id"),
            ATTR_SERVER_NAME: server.get("name"),
        }
