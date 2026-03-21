"""Sensor platform for dnsdist."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfInformation, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DnsdistDataUpdateCoordinator
from .entity import DnsdistMainEntity, DnsdistServerEntity


@dataclass(frozen=True, kw_only=True)
class DnsdistMainSensorDescription(SensorEntityDescription):
    """Description of a main dnsdist sensor."""

    value_fn: Callable[[dict[str, Any]], Any]


@dataclass(frozen=True, kw_only=True)
class DnsdistServerSensorDescription(SensorEntityDescription):
    """Description of a backend dnsdist sensor."""

    value_fn: Callable[[dict[str, Any]], Any]


MAIN_SENSORS: tuple[DnsdistMainSensorDescription, ...] = (
    DnsdistMainSensorDescription(
        key="uptime",
        name="Uptime",
        icon="mdi:clock",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("statistics", {}).get("uptime"),
    ),
    DnsdistMainSensorDescription(
        key="fd_usage",
        name="FD Usage",
        icon="mdi:file-cabinet",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("statistics", {}).get("fd-usage"),
    ),
    DnsdistMainSensorDescription(
        key="memory_usage",
        name="Memory Usage",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class="data_size",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_unit_of_measurement=UnitOfInformation.MEBIBYTES,
        value_fn=lambda data: data.get("statistics", {}).get("real-memory-usage"),
    ),
    DnsdistMainSensorDescription(
        key="queries",
        name="Queries",
        icon="mdi:counter",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("statistics", {}).get("queries"),
    ),
    DnsdistMainSensorDescription(
        key="responses",
        name="Responses",
        icon="mdi:counter",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("statistics", {}).get("responses"),
    ),
    DnsdistMainSensorDescription(
        key="self_answered",
        name="Self Answered",
        icon="mdi:reply",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("statistics", {}).get("self-answered"),
    ),
    DnsdistMainSensorDescription(
        key="cache_hits",
        name="Cache Hits",
        icon="mdi:database-check-outline",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("statistics", {}).get("cache-hits"),
    ),
    DnsdistMainSensorDescription(
        key="cache_misses",
        name="Cache Misses",
        icon="mdi:database-remove-outline",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("statistics", {}).get("cache-misses"),
    ),
)

SERVER_SENSORS: tuple[DnsdistServerSensorDescription, ...] = (
    DnsdistServerSensorDescription(
        key="queries",
        name="Queries",
        icon="mdi:counter",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda server: server.get("queries"),
    ),
    DnsdistServerSensorDescription(
        key="responses",
        name="Responses",
        icon="mdi:counter",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda server: server.get("responses"),
    ),
    DnsdistServerSensorDescription(
        key="latency",
        name="Latency",
        icon="mdi:timer",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        suggested_display_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda server: server.get("latency"),
    ),
    DnsdistServerSensorDescription(
        key="drop_rate",
        name="Drop Rate",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda server: server.get("dropRate"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up dnsdist sensors from a config entry."""
    coordinator: DnsdistDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    known_servers: set[str] = set()

    entities: list[CoordinatorEntity] = [
        DnsdistMainSensor(coordinator, description) for description in MAIN_SENSORS
    ]

    for server_name in sorted(coordinator.server_names):
        known_servers.add(server_name)
        entities.extend(
            DnsdistServerSensor(coordinator, server_name, description)
            for description in SERVER_SENSORS
        )

    async_add_entities(entities)

    @callback
    def _async_add_new_server_entities() -> None:
        nonlocal known_servers
        current = coordinator.server_names
        new_servers = sorted(current - known_servers)
        if not new_servers:
            return

        new_entities: list[DnsdistServerSensor] = []
        for server_name in new_servers:
            new_entities.extend(
                DnsdistServerSensor(coordinator, server_name, description)
                for description in SERVER_SENSORS
            )
        known_servers |= set(new_servers)
        async_add_entities(new_entities)

    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_server_entities))


class DnsdistMainSensor(DnsdistMainEntity, SensorEntity):
    """Main dnsdist sensor."""

    entity_description: DnsdistMainSensorDescription

    def __init__(
        self,
        coordinator: DnsdistDataUpdateCoordinator,
        description: DnsdistMainSensorDescription,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self._entry_id}_main_{description.key}"
        self._attr_name = description.name

    @property
    def native_value(self) -> Any:
        """Return sensor value."""
        return self.entity_description.value_fn(self.coordinator.data or {})


class DnsdistServerSensor(DnsdistServerEntity, SensorEntity):
    """Backend dnsdist sensor."""

    entity_description: DnsdistServerSensorDescription

    def __init__(
        self,
        coordinator: DnsdistDataUpdateCoordinator,
        server_name: str,
        description: DnsdistServerSensorDescription,
    ) -> None:
        """Initialize backend sensor."""
        super().__init__(coordinator, server_name)
        self.entity_description = description
        self._attr_unique_id = (
            f"{self._entry_id}_server_{server_name}_{description.key}"
        )
        self._attr_name = description.name

    @property
    def native_value(self) -> Any:
        """Return sensor value."""
        server = self.server
        if server is None:
            return None
        return self.entity_description.value_fn(server)
