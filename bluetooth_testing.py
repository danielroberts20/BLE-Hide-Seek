import asyncio
from bleak import BleakClient

# Replace with your actual values
MAC_ADDRESS = "6EC9CE00-8C3F-059E-4F17-641F68AB9A3E"
COLOR_CHAR_UUID = "932C32BD-0005-47A2-835A-A8D455B859DD"

async def set_color(hex_string):
    color_bytes = bytes.fromhex(hex_string)
    async with BleakClient(MAC_ADDRESS) as client:
        await client.connect()
        if await client.is_connected():
            print(f"Connected to {MAC_ADDRESS}")
            await client.write_gatt_char(COLOR_CHAR_UUID, color_bytes, response=True)
            print(f"Sent color: {hex_string}")
        else:
            print("Failed to connect.")

# Example usage
asyncio.run(set_color("3A8FA64A"))  # Replace with your desired color hex
