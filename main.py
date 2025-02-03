from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from routers import websocket, user
import models
from fastapi.staticfiles import StaticFiles
from database import engine

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")  


app.include_router(websocket.router)
app.include_router(user.router)

@app.get("/")  
async def home():  
    return templates.TemplateResponse("index.html", {"request": {}})  

@app.get("/chatroom")  
async def chatroom():  
    return templates.TemplateResponse("chatroom.html", {"request": {}}) 




