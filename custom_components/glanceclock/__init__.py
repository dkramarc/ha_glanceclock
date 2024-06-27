"""Glance Clock integration."""

from .time_date import update_time_date
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

DOMAIN = "glanceclock"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required("device"): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass, config):
    """Set up the Glance Clock component."""

    device_address = config[DOMAIN]["device"]

    async def handle_update_time(call):
        """Handle the service call to update time."""
        await update_time_date(hass, device_address)

    hass.services.async_register(DOMAIN, "update_time", handle_update_time)

    return True
