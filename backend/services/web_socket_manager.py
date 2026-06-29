import asyncio
from collections import defaultdict

class ConnectionManager:
    def __init__(self):
        self.connections = defaultdict(list)
        self.lock = asyncio.Lock()

    async def connect(self, meeting_id, ws):
        async with self.lock:
            await ws.accept()
            self.connections[meeting_id].append(ws)

    def disconnect(self, meeting_id, ws):
        if ws in self.connections[meeting_id]:
            self.connections[meeting_id].remove(ws)

    async def send(self, meeting_id, message):
        async with self.lock:
            for ws in list(self.connections[meeting_id]):
                try:
                    await ws.send_json(message)
                except:
                    self.connections[meeting_id].remove(ws)


manager = ConnectionManager()