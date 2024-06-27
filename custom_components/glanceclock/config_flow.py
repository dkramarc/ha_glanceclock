import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.bluetooth import async_discovered_service_info
from homeassistant.core import callback
import logging
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class GlanceClockConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Glance Clock."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            device_info = user_input["device"]
            mac_address, device_name = device_info.split(" - ", 1)
            return self.async_create_entry(title=device_name, data={"ble_address": mac_address})

        devices = await self.async_get_devices()

        if not devices:
            return self.async_abort(reason="no_devices_found")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("device"): vol.In(devices),
            }),
        )

    @callback
    async def async_get_devices(self):
        """Get the list of available Bluetooth devices."""
        devices = async_discovered_service_info(self.hass)
        device_list = {
            f"{device.address} - {device.name}": f"{device.address} - {device.name}"
            for device in devices
            if device.name and device.name.startswith("GlanceClock")  # Filter devices with name starting with "GlanceClock"
        }

        # Correct logging method
        for device in devices:
            if device.name and device.name.startswith("GlanceClock"):
                _LOGGER.info(f"Found device: {device.address} - {device.name}")

        return device_list
