"""Config flow for dnsdist."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, OptionsFlowWithReload
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DnsdistApiClient, DnsdistApiAuthError, DnsdistApiError
from .const import (
    CONF_API_KEY,
    CONF_ENDPOINT,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


def _normalize_endpoint(endpoint: str) -> str:
    """Normalize endpoint."""
    return endpoint.strip().rstrip("/")


def _entry_matches_endpoint(entry: ConfigEntry, endpoint: str) -> bool:
    """Check if another entry already uses endpoint."""
    return _normalize_endpoint(entry.data[CONF_ENDPOINT]) == _normalize_endpoint(endpoint)


async def _validate_input(hass, data: dict[str, Any]) -> None:
    """Validate user input by calling dnsdist."""
    client = DnsdistApiClient(
        async_get_clientsession(hass),
        _normalize_endpoint(data[CONF_ENDPOINT]),
        data[CONF_API_KEY],
    )
    await client.async_get_status()


class DnsdistConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for dnsdist."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        """Return options flow handler."""
        return DnsdistOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            normalized = {
                CONF_ENDPOINT: _normalize_endpoint(user_input[CONF_ENDPOINT]),
                CONF_API_KEY: user_input[CONF_API_KEY],
            }

            if any(
                _entry_matches_endpoint(entry, normalized[CONF_ENDPOINT])
                for entry in self._async_current_entries()
            ):
                return self.async_abort(reason="already_configured")

            try:
                await _validate_input(self.hass, normalized)
            except DnsdistApiAuthError:
                errors["base"] = "invalid_auth"
            except DnsdistApiError:
                errors["base"] = "cannot_connect"
            else:
                parsed = urlparse(normalized[CONF_ENDPOINT])
                title = parsed.hostname or "dnsdist"
                return self.async_create_entry(title=title, data=normalized)

        return self.async_show_form(
            step_id="user",
            data_schema=_build_config_schema(user_input),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle reconfigure flow."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            normalized = {
                CONF_ENDPOINT: _normalize_endpoint(user_input[CONF_ENDPOINT]),
                CONF_API_KEY: user_input[CONF_API_KEY],
            }

            if any(
                other.entry_id != entry.entry_id
                and _entry_matches_endpoint(other, normalized[CONF_ENDPOINT])
                for other in self._async_current_entries()
            ):
                return self.async_abort(reason="already_configured")

            try:
                await _validate_input(self.hass, normalized)
            except DnsdistApiAuthError:
                errors["base"] = "invalid_auth"
            except DnsdistApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates=normalized,
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_build_config_schema(entry.data),
            errors=errors,
        )


class DnsdistOptionsFlow(OptionsFlowWithReload):
    """dnsdist options flow."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.Coerce(int),
                }
            ),
        )


def _build_config_schema(defaults: dict[str, Any] | None) -> vol.Schema:
    """Build config schema."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_ENDPOINT, default=defaults.get(CONF_ENDPOINT, "")
            ): str,
            vol.Required(
                CONF_API_KEY, default=defaults.get(CONF_API_KEY, "")
            ): str,
        }
    )
