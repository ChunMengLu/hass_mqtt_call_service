"""mqtt call service."""
import asyncio

import json
import logging

import async_timeout
import voluptuous as vol

from homeassistant.config_entries import ConfigEntryState
from homeassistant.components import mqtt
from homeassistant.components.mqtt import DOMAIN, valid_subscribe_topic, mqtt_config_entry_enabled
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

CONF_DOMAIN = "mqtt_call_service"
CONF_SUBSCRIBE_TOPIC = "subscribe_topic"
DATA_MQTT_AVAILABLE = "mqtt_client_available"
AVAILABILITY_TIMEOUT = 30.0

CONFIG_SCHEMA = vol.Schema(
    {
        CONF_DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_SUBSCRIBE_TOPIC): valid_subscribe_topic,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the MQTT eventstream component."""
    # Make sure MQTT integration is enabled and the client is available
    if not await async_wait_for_mqtt_client(hass):
        _LOGGER.error("MQTT integration is not available")
        return False

    conf = config.get(CONF_DOMAIN, {})
    sub_topic = conf.get(CONF_SUBSCRIBE_TOPIC)

    # Process events from a remote server that are received on a queue.
    @callback
    async def _event_receiver(msg):
        """Receive events published by and fire them on this hass instance."""
        event_data = json.loads(msg.payload)

        await hass.services.async_call(
            event_data.get("domain"),
            event_data.get("service"),
            event_data.get("service_data"),
            blocking=True,
        )

    # Only subscribe if you specified a topic.
    if sub_topic:
        await mqtt.async_subscribe(hass, sub_topic, _event_receiver)
    return True

async def async_wait_for_mqtt_client(hass: HomeAssistant) -> bool:
    """Wait for the MQTT client to become available.

    Waits when mqtt set up is in progress,
    It is not needed that the client is connected.
    Returns True if the mqtt client is available.
    Returns False when the client is not available.
    """
    if not mqtt_config_entry_enabled(hass):
        return False

    entry = hass.config_entries.async_entries(DOMAIN)[0]
    if entry.state == ConfigEntryState.LOADED:
        return True

    state_reached_future: asyncio.Future[bool]
    if DATA_MQTT_AVAILABLE not in hass.data:
        hass.data[DATA_MQTT_AVAILABLE] = state_reached_future = asyncio.Future()
    else:
        state_reached_future = hass.data[DATA_MQTT_AVAILABLE]
        if state_reached_future.done():
            return state_reached_future.result()
    try:
        async with async_timeout.timeout(AVAILABILITY_TIMEOUT):
            # Await the client setup or an error state was received
            return await state_reached_future
    except asyncio.TimeoutError:
        return False