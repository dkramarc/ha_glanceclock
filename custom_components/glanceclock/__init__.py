"""Glance Clock integration."""

import asyncio
from datetime import datetime
from bleak import BleakClient
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

DOMAIN = "glanceclock"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required("ble_address"): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass, config):
    """Set up the Glance Clock component."""

    ble_address = config[DOMAIN]["ble_address"]

    async def handle_update_time(call):
        """Handle the service call to update time."""
        await update_time_date(ble_address)

    async def handle_pair_device(call):
        """Handle the service call to pair the device."""
        await pair_device(ble_address)

    hass.services.async_register(DOMAIN, "update_time", handle_update_time)
    hass.services.async_register(DOMAIN, "pair_device", handle_pair_device)

    return True

async def update_time_date(address):
    async with BleakClient(address) as client:
        now = datetime.now()
        # Replace the UUID with the correct one for the Glance Clock
        await client.write_gatt_char("UUID", now.strftime("%Y%m%d%H%M%S").encode())

async def pair_device(address):
    async with BleakClient(address) as client:
        # Replace this with the actual pairing logic
        await client.connect()
        # Assume some characteristic UUID and pairing logic here
        PAIRING_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"
        await client.write_gatt_char(PAIRING_UUID, bytearray([0x01]))
        await asyncio.sleep(1)  # Wait for pairing to complete
