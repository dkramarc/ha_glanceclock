import asyncio
from datetime import datetime
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak

async def update_time_date(hass, address):
    bluetooth = hass.components.bluetooth
    service_info: BluetoothServiceInfoBleak = bluetooth.async_get_service_info(address)
    if service_info:
        client = service_info.client
        now = datetime.now()
        data = now.strftime("%Y%m%d%H%M%S").encode()
        await client.write_gatt_char("UUID", data)
    else:
        raise Exception("Unable to find Bluetooth device")
