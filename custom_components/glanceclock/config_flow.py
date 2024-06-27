import logging
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_DEVICE
import voluptuous as vol

from bleak import BleakScanner

DOMAIN = "glanceclock"
_LOGGER = logging.getLogger(__name__)

class GlanceClockConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Glance Clock", data=user_input)

        devices = await self.async_get_devices()
        if not devices:
            return self.async_show_form(
                step_id="user",
                errors={"base": "No GlanceClock devices found. Please put it in pairing mode by pushing the power button when device is on."},
                data_schema=vol.Schema({vol.Required(CONF_DEVICE): cv.string}),
                description_placeholders={"device": ""}
            )

        device_list = {device.address: f"{device.name} ({device.address})" for device in devices}
        data_schema = vol.Schema({
            vol.Required(CONF_DEVICE): vol.In(device_list)
        })

        return self.async_show_form(step_id="user", data_schema=data_schema)

    async def async_get_devices(self):
        scanner = BleakScanner()
        devices = await scanner.discover()
        if not devices:
            return None

        glance_devices = [device for device in devices if device.name and "GlanceClock" in device.name]
        return glance_devices
