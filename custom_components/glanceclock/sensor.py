import logging
from datetime import timedelta
import async_timeout
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import Throttle
from bleak import BleakClient, BleakError

DOMAIN = "glanceclock"
SCAN_INTERVAL = timedelta(minutes=1)
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    device_address = config_entry.data["device"]
    coordinator = GlanceClockDataUpdateCoordinator(hass, device_address)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([GlanceClockSensor(coordinator)], True)

class GlanceClockDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, device_address: str):
        self.device_address = device_address
        self.client = BleakClient(device_address)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(10):
                await self.client.connect()
                _LOGGER.info(f"Connected to GlanceClock at {self.device_address}")
                data = await self._get_glanceclock_time()
                await self.client.disconnect()
                return data
        except BleakError as e:
            _LOGGER.error(f"Error updating GlanceClock sensor: {e}")
            raise UpdateFailed(f"Failed to update data: {e}")
        except Exception as e:
            _LOGGER.error(f"Unexpected error: {e}")
            raise UpdateFailed(f"Unexpected error: {e}")

    async def _get_glanceclock_time(self):
        try:
            _LOGGER.info(f"Reading time from GlanceClock at {self.device_address}")
            # Assuming we need to read a specific characteristic for time
            TIME_CHARACTERISTIC_UUID = "5075fb2e-1e0e-11e7-93ae-92361f002671"
            data = await self.client.read_gatt_char(TIME_CHARACTERISTIC_UUID)
            _LOGGER.info(f"Received time data: {data}")
            return data.decode("utf-8")
        except Exception as e:
            _LOGGER.error(f"Failed to get time from GlanceClock: {e}")
            raise

class GlanceClockSensor(Entity):
    def __init__(self, coordinator: GlanceClockDataUpdateCoordinator):
        self.coordinator = coordinator

    @property
    def name(self):
        return "Glance Clock"

    @property
    def state(self):
        return self.coordinator.data

    @property
    def unique_id(self):
        return self.coordinator.device_address

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

    async def async_update(self):
        await self.coordinator.async_request_refresh()
