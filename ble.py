import asyncio
from bleak import BleakScanner, BleakClient

class HueBLEClient:
    
    def __init__(self):
        return
    
    def start(self):
        print("[BLE] Starting Hue BLE Client")
        return
    
    async def toggle(self):
        # Toggle the light on/off
        print(f"[BLE] Toggling Hue On/Off")
        return
    
    async def brightness(self, t):
        # Ensure t is between 0 and 1
        t = max(0, min(t, 1))
        if t == 0:
            # Set the value to like b'\x01' as it can't be 0
            pass
        
        # Change brightness of light. 01 for min, 1 for max
        print(f"[BLE] Changing Hue Brightness: {t}")
        return
    
    async def color(self, color):
        # Change color of the light. Color will be bytes
        # Expecting color as a tuple of RGB, e.g. (255, 0, 0)
        color_str = ''.join(color)
        color_bytes = bytes.fromhex(color_str)
        await write_to_characteristic(
            _SIDE_LIGHT_MAC,
            _PHILIPS_HUE_LIGHT_CONTROL_SERVICE_UUID,
            _PHILIPS_HUE_COLOR_CHAR_UUID,
            color_bytes
        )
        print(f"[BLE] Changing Hue Colour: {color_bytes}")

_SIDE_LIGHT_MAC = 'D0:A8:D4:6A:04:B3'
_SIDE_LIGHT_ID = '6EC9CE00-8C3F-059E-4F17-641F68AB9A3E'
_PHILIPS_HUE_LIGHT_CONTROL_SERVICE_UUID = '932c32bd-0000-47a2-835a-a8d455b859dd'
_PHILIPS_HUE_ON_OFF_TOGGLE_CHAR_UUID = '932C32BD-0002-47A2-835A-A8D455B859DD'
_PHILIPS_HUE_COLOR_CHAR_UUID = '932C32BD-0005-47A2-835A-A8D455B859DD'

async def write_to_characteristic(address, service_uuid, char_uuid, value):
    async with BleakClient(address, timeout=30) as client:
        if client.is_connected:
            print(f'Connected to {address}')
            await client.write_gatt_char(char_uuid, value, response=True)

async def list_services(address):
    async with BleakClient(address, timeout=30) as client:
        if client.is_connected:
            print(f'Connected to {address}')
            services = client.services
            char = services.get_characteristic(_PHILIPS_HUE_ON_OFF_TOGGLE_CHAR_UUID)
            ar = await client.read_gatt_char(char)
            print(ar)

async def scan():
    
    devices = await BleakScanner.discover()
    for device in devices:
        print(device)
        
#asyncio.run(scan())
#asyncio.run(write_to_characteristic(_SIDE_LIGHT_MAC, _PHILIPS_HUE_LIGHT_CONTROL_SERVICE_UUID, _PHILIPS_HUE_ON_OFF_TOGGLE_CHAR_UUID, b'\x01'))
#asyncio.run(write_to_characteristic(_SIDE_LIGHT_MAC, _PHILIPS_HUE_LIGHT_CONTROL_SERVICE_UUID, _PHILIPS_HUE_COLOR_CHAR_UUID, b'\xAD408335'))
#asyncio.run(list_services(_SIDE_LIGHT_MAC))
#asyncio.run(scan())
asyncio.run(write_to_characteristic(_SIDE_LIGHT_ID, _PHILIPS_HUE_LIGHT_CONTROL_SERVICE_UUID, _PHILIPS_HUE_COLOR_CHAR_UUID, bytes.fromhex('3A8FA64A')))