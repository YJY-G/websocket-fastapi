from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends,Request
from fastapi.templating import Jinja2Templates
from starlette import status
from models import User,ChatMessage
from database import get_db  
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from .user import SECRET_KEY, ALGORITHM
from jose import JWTError, jwt

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)
class ConnectionManager:  
    def __init__(self):  
        self.active_connections: dict[int, WebSocket] = {}  

    async def connect(self, websocket: WebSocket, user: User):  
        await websocket.accept()  
        self.active_connections[user.id] = websocket  

    def disconnect(self, user_id: int):  
        del self.active_connections[user_id]  

    async def send_personal_message(self, message: str, user_id: int):  
        if websocket := self.active_connections.get(user_id):  
            await websocket.send_text(message)  

    async def broadcast(self, message: str):  
        for connection in self.active_connections.values():  
            await connection.send_text(message)  

manager = ConnectionManager()  

@router.websocket("/ws")  
async def websocket_endpoint(  
    websocket: WebSocket,  
    token: str,  
    db: Session = Depends(get_db)  
):  
    try:  
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  
        username = payload.get("sub")  
        user = db.query(User).filter(User.username == username).first()  
        if not user:  
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)  
            return  
            
        await manager.connect(websocket, user)
        try:
            await manager.broadcast(f"{user.username} connect to the chat")
            while True:  
                data = await websocket.receive_text()  
                message = ChatMessage(  
                    content=data,  
                    sender_id=user.id,  
                    timestamp=datetime.now(timezone.utc)
                )  
                db.add(message)  
                db.commit()  
                await manager.broadcast(  
                    f"{user.username} ({user.user_type}): {data}"  
                )  
        except WebSocketDisconnect:  
            manager.disconnect(user.id)  
            await manager.broadcast(f"{user.username} left the chat")  
    except JWTError:  
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

@router.get("/")  
async def redirect_chatroom(request: Request):  
    return templates.TemplateResponse("chatroom.html", {"request": request})