import asyncio
from bleak import BleakClient
from datetime import datetime

async def update_time_date(address):
    async with BleakClient(address) as client:
        now = datetime.now()
        # Replace the UUID and command with the correct ones for the Glance Clock
        await client.write_gatt_char("UUID", now.strftime("%Y%m%d%H%M%S").encode())
