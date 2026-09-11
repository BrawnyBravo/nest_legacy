"""Tests for the option that stops camera event polling.

The five ``enable_protobuf_*`` options only choose which API a device type
arrives on. None of them stops ``_async_poll_camera_events``, which runs for
every online, streaming camera on the account for as long as the integration is
loaded. These tests pin the behaviour of the option that does stop it, and that
it is opt-out so nobody's cameras go quiet on upgrade.
"""

from unittest.mock import AsyncMock, patch

from custom_components.nest_legacy.const import CONF_ENABLE_CAMERA_EVENTS
import pytest

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from . import setup_integration

from pytest_homeassistant_custom_component.common import MockConfigEntry


@pytest.fixture
def platforms() -> list[Platform]:
    """No platforms needed; these tests only observe the background task."""
    return []


async def _poll_started(
    hass: HomeAssistant, entry: MockConfigEntry, options: dict | None
) -> bool:
    """Set the integration up with ``options`` and report whether polling began."""
    if options is not None:
        hass.config_entries.async_update_entry(entry, options=options)
    with patch(
        "custom_components.nest_legacy.coordinator.NestCoordinator"
        "._async_poll_camera_events",
        new_callable=AsyncMock,
    ) as poll:
        await setup_integration(hass, entry)
        await hass.async_block_till_done()
        return poll.called


async def test_camera_events_polled_by_default(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_nest_client: AsyncMock,
) -> None:
    """With no option set the poll still runs, so upgrades change nothing."""
    assert await _poll_started(hass, mock_config_entry, None) is True


async def test_camera_events_polled_when_enabled(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_nest_client: AsyncMock,
) -> None:
    """Explicitly enabling it polls, same as the default."""
    assert (
        await _poll_started(
            hass, mock_config_entry, {CONF_ENABLE_CAMERA_EVENTS: True}
        )
        is True
    )


async def test_camera_events_not_polled_when_disabled(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_nest_client: AsyncMock,
) -> None:
    """The point of the option: disabling it starts no poll at all.

    This is the assertion that matters. A test that only checked the option
    round-tripped through the config entry would pass while the poll kept
    running.
    """
    assert (
        await _poll_started(
            hass, mock_config_entry, {CONF_ENABLE_CAMERA_EVENTS: False}
        )
        is False
    )


async def test_disabling_camera_events_leaves_other_updates_running(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_nest_client: AsyncMock,
) -> None:
    """Turning camera events off must not take the device updates with it.

    Thermostats and temperature sensors are why this install exists; they arrive
    over the subscribe/observe channels, which are started by the same method.
    """
    hass.config_entries.async_update_entry(
        mock_config_entry, options={CONF_ENABLE_CAMERA_EVENTS: False}
    )
    with (
        patch(
            "custom_components.nest_legacy.coordinator.NestCoordinator"
            "._async_poll_camera_events",
            new_callable=AsyncMock,
        ) as poll,
        patch(
            "custom_components.nest_legacy.coordinator.NestCoordinator"
            "._async_subscribe_for_updates",
            new_callable=AsyncMock,
        ) as subscribe,
        patch(
            "custom_components.nest_legacy.coordinator.NestCoordinator"
            "._async_observe_for_updates",
            new_callable=AsyncMock,
        ) as observe,
    ):
        await setup_integration(hass, mock_config_entry)
        await hass.async_block_till_done()

    assert poll.called is False
    assert subscribe.called is True
    assert observe.called is True
