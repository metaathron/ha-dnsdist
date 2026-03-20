"""Constants for the dnsdist integration."""

from __future__ import annotations

DOMAIN = "dnsdist"

CONF_API_KEY = "api_key"
CONF_ENDPOINT = "endpoint"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 30

PLATFORMS = ["sensor", "binary_sensor"]

MAIN_DEVICE_ID = "instance"

ATTR_ADDRESS = "address"
ATTR_PROTOCOL = "protocol"
ATTR_SERVER_ID = "id"
ATTR_SERVER_NAME = "name"
