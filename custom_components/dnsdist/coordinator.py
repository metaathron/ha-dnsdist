"""Coordinator for dnsdist."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DnsdistApiClient, DnsdistApiAuthError, DnsdistApiError
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN


class DnsdistDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch dnsdist data periodically."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: DnsdistApiClient,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize coordinator."""
        self.client = client
        self.config_entry = config_entry

        update_interval = timedelta(
            seconds=config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )

        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            return await self.client.async_get_status()
        except DnsdistApiAuthError as err:
            raise UpdateFailed(str(err)) from err
        except DnsdistApiError as err:
            raise UpdateFailed(str(err)) from err

    @property
    def server_names(self) -> set[str]:
        """Return current backend names."""
        servers = self.data.get("servers", []) if self.data else []
        return {
            str(server.get("name", "")).strip()
            for server in servers
            if str(server.get("name", "")).strip()
        }

    def get_server(self, name: str) -> dict[str, Any] | None:
        """Return backend data by name."""
        servers = self.data.get("servers", []) if self.data else []
        for server in servers:
            if str(server.get("name", "")).strip() == name:
                return server
        return None
