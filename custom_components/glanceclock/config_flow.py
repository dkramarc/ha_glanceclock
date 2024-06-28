import logging
import asyncio
import subprocess
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_DEVICE
import voluptuous as vol

from bleak import BleakClient, BleakScanner, BleakError

DOMAIN = "glanceclock"
_LOGGER = logging.getLogger(__name__)

class GlanceClockConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            _LOGGER.info(f"Selected device address: {user_input[CONF_DEVICE]}")
            pairing_result = await self.async_pair_device(user_input[CONF_DEVICE])
            if pairing_result is not None:
                return pairing_result

            return self.async_create_entry(title="Glance Clock", data=user_input)

        devices = await self.async_get_devices()
        if not devices:
            _LOGGER.error("No GlanceClock devices found.")
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

        _LOGGER.info(f"Found GlanceClock devices: {device_list}")
        return self.async_show_form(step_id="user", data_schema=data_schema)

    async def async_get_devices(self):
        _LOGGER.info("Starting Bluetooth scan for GlanceClock devices")
        scanner = BleakScanner()
        devices = await scanner.discover()
        _LOGGER.info(f"Found devices: {devices}")

        if not devices:
            return None

        glance_devices = [device for device in devices if device.name and "GlanceClock" in device.name]
        _LOGGER.info(f"Filtered GlanceClock devices: {glance_devices}")
        return glance_devices

    async def async_pair_device(self, device_address):
        _LOGGER.info(f"Initializing BleakClient for address: {device_address}")
        client = BleakClient(
            address_or_ble_device=device_address,
            timeout=10.0,
            adapter="hci0",
        )

        try:
            await self._connect_with_retries(client)
            await self.pair_with_bluetoothctl(device_address)
            _LOGGER.info(f"Successfully paired with GlanceClock at {device_address}")
        except Exception as e:
            _LOGGER.error(f"Unexpected error while pairing with GlanceClock at {device_address}: {e}", exc_info=True)
            return self.async_show_form(
                step_id="user",
                errors={"base": "pairing_failed"},
                data_schema=vol.Schema({vol.Required(CONF_DEVICE): device_address}),
            )

    async def _connect_with_retries(self, client, retries=3, timeout=10):
        for attempt in range(retries):
            try:
                device_address = getattr(client, 'address_or_ble_device', 'Unknown address')
                _LOGGER.info(f"Attempting to connect to GlanceClock at {device_address}, attempt {attempt + 1} of {retries}")
                async with asyncio.timeout(timeout):
                    await client.connect()
                    _LOGGER.info(f"Successfully connected to GlanceClock at {device_address}")
                    return
            except (BleakError, asyncio.TimeoutError) as e:
                _LOGGER.error(f"Error during connection attempt {attempt + 1} of {retries}: {e}", exc_info=True)
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    raise
            except Exception as e:
                _LOGGER.error(f"Unexpected error during connection attempt {attempt + 1} of {retries}: {e}", exc_info=True)
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    raise

    async def pair_with_bluetoothctl(self, device_address):
        _LOGGER.info(f"Attempting to pair with device at address: {device_address} using bluetoothctl")
        try:
            result = subprocess.run(["bluetoothctl", "pair", device_address], check=True, capture_output=True, text=True)
            _LOGGER.info(f"Pairing output: {result.stdout}")
            result = subprocess.run(["bluetoothctl", "trust", device_address], check=True, capture_output=True, text=True)
            _LOGGER.info(f"Trust output: {result.stdout}")
            result = subprocess.run(["bluetoothctl", "connect", device_address], check=True, capture_output=True, text=True)
            _LOGGER.info(f"Connect output: {result.stdout}")
            _LOGGER.info(f"Successfully paired with device at address: {device_address}")
        except subprocess.CalledProcessError as e:
            _LOGGER.error(f"Failed to pair with device: {e.stderr}")
            raise
