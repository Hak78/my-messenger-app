from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import json

app = FastAPI()

# قائمة لتتبع الاتصالات النشطة للدردشة
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
def read_root():
    return {"status": "My Messenger App Backend is running!"}

# نقطة الاتصال الفوري (WebSocket) للمراسلة
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # تنسيق الرسالة وإرسالها لجميع المتصلين
            message_data = {
                "sender": client_id,
                "message": data
            }
            await manager.broadcast(json.dumps(message_data))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(json.dumps({"sender": "System", "message": f"User {client_id} left the chat."}))
