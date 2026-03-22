import asyncio
from aiocoap import *
from aiocoap.resource import *

import aiosqlite
import sqlite3

from hue_colour import lerp_color_heatmap
from ble import HueBLEClient

class LogResource(Resource):
    
    async def render_put(self, request):
        payload = request.payload.decode('utf-8')
        print(f'[LOG] Received PUT/log request: {payload}')
        return Message(code=PUT, payload='LOGGED'.encode('utf-8'))
    
class RSSIResource(Resource):
    def __init__(self, hue):
        self.rssi = 'NONE'
        self.hue = hue
        super().__init__()
        
    async def render_get(self, request):
        return Message(payload=self.rssi.encode())
    
    async def render_put(self, request):
        old_rssi = self.rssi
        payload = request.payload.decode('utf-8')
        self.rssi = payload
        print(f'Received PUT/RSSI request: {payload}')
        distance = await rssi_to_distance(self.rssi)
        color = await lerp_color_heatmap(distance)
        await self.hue.color(color)
        print(f'Distance: {distance}')
        return Message(code=PUT, payload=f'Previous RSSI: {old_rssi}'.encode('utf-8'))
    
class TimeResource(Resource):
    
    async def render_get(self, request):
        from datetime import datetime
        return Message(payload=datetime.now().strftime('%Y-%m-%d %H:%M:%S').encode())

class LeaderboardResource(Resource):
    
    async def render_get(self, request):
        remote_addr = request.remote
        print(remote_addr)
        print("Debug: Received GET/leaderboard request")
        leaderboard = await top_n_times(10)
        msg = ", ".join(map(str, leaderboard))
        return Message(payload=msg.encode())

class EntryResource(Resource):
    
    async def render_put(self, request):
        payload = request.payload.decode('utf-8')
        print("Debug: Received PUT/entry request")
        print(payload)
        result = await insert_time(payload)
        response = Message(code=PUT, payload=f"{result} PUT request processed for {payload}".encode('utf-8'))
        return response
    
    async def render_post(self, request):
        payload = request.payload.decode('utf-8')
        print("Debug: Received POST/entry request")
        print(payload)
        result = await insert_time(payload)
        response = Message(code=CREATED, payload=f"{result} POST request processed for {payload}".encode('utf-8'))
        return response

class CoAPServer:
    
    def __init__(self):
        self._root = Site()
        self.configure_db()
        self.hue = HueBLEClient()
        self.hue.start()
    
    async def run(self):
        
        self._root.add_resource(['entry'], EntryResource())
        self._root.add_resource(['leaderboard'], LeaderboardResource())
        self._root.add_resource(['log'], LogResource())
        self._root.add_resource(['rssi'], RSSIResource(self.hue))

        context = await Context.create_server_context(self._root, bind=('192.168.1.119', 5683))
        
        await asyncio.get_event_loop().create_future()
    
    def configure_db(self):
        conn = sqlite3.connect('times.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS times (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        print("Created database")

async def insert_time(time_str):
    try:
        float(time_str)
    except ValueError as e:
        print(e)
        return f"ERROR - Received non-float: '{time_str}'"
    async with aiosqlite.connect('times.db') as db:
        await db.execute('''
            INSERT INTO times (time)
            VALUES (?)
        ''', (time_str, ))
        await db.commit()
        return "SUCCESS"

async def top_n_times(n):
    async with aiosqlite.connect('times.db') as db:
        async with db.execute(f'''
            SELECT time FROM times
            ORDER BY CAST(time AS REAL) ASC
            LIMIT {n}
        ''') as cursor:
            top_n = await cursor.fetchall()
            return [time[0] for time in top_n]
    
async def rssi_to_distance(rssi_str, close_threshold=-45, far_threshold=-70):
    
    rssi = float(rssi_str)
    
    if rssi >= close_threshold:
        return 1.0
    elif rssi <= far_threshold:
        return 0.0
    else:
        return 1 - (rssi - close_threshold) / (far_threshold - close_threshold)
    
if __name__ == "__main__":
    coap_server = CoAPServer()
    asyncio.run(coap_server.run())