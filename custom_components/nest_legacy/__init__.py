"""Nest legacy integration."""

import asyncio

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .coordinator import NestConfigEntry, NestCoordinator
from .services import async_setup_services

_PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.CAMERA,
    Platform.CLIMATE,
    Platform.EVENT,
    Platform.FAN,
    Platform.LOCK,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.WATER_HEATER,
]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Nest Legacy integration."""
    async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: NestConfigEntry) -> bool:
    """Set up Nest from a config entry."""
    coordinator = NestCoordinator(hass, entry)

    try:
        await coordinator.async_initialize()
    except ConfigEntryAuthFailed:
        # Re-raise authentication failures to trigger reauth flow
        raise
    except Exception as err:
        # Other startup errors
        raise ConfigEntryNotReady(f"Failed to initialize Nest: {err}") from err

    entry.runtime_data = coordinator

    # Without this, changing an option does nothing until the integration is
    # reloaded or Home Assistant restarts - the options are only read at setup.
    # That is worst for the camera-event option, whose whole point is "I turned
    # it off and the noise stopped": it would look broken on first use.
    entry.async_on_unload(entry.add_update_listener(_async_entry_updated))

    # Start subscribers to get all device data (including from protobuf)
    coordinator.async_start_subscriber()

    # Wait for the first protobuf update to ensure all devices are available
    try:
        await asyncio.wait_for(
            coordinator.first_protobuf_update_received.wait(), timeout=15
        )
    except TimeoutError as err:
        raise ConfigEntryNotReady(
            "Timed out waiting for initial Protobuf data from Nest"
        ) from err

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def _async_entry_updated(hass: HomeAssistant, entry: NestConfigEntry) -> None:
    """Reload the entry when its options change.

    Deliberately scoped to options. Reauth and reconfigure finish with
    ``async_update_reload_and_abort``, which reloads already; reloading again on
    their data write would double the work at the worst possible moment.
    """
    coordinator = getattr(entry, "runtime_data", None)
    if coordinator is not None and coordinator.options_snapshot == dict(entry.options):
        return
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: NestConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator = entry.runtime_data
    coordinator.async_stop_subscriber()
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: NestConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Remove a config entry from a device."""
    return True
