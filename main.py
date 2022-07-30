from unittest import skip
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# setup fastapi
app_fastapi = FastAPI()
# setup socketio
sio = socketio.AsyncServer(
  async_mode='asgi',
  cors_allowed_origins='*',
  logger=False,
  engineio_logger=False
  )

app_socketio = socketio.ASGIApp(
  socketio_server=sio,
  other_asgi_app=app_fastapi,
  socketio_path='/socket.io/'
  )
#app_socketio = socketio.ASGIApp(sio, other_asgi_app=app_fastapi)
#app_socketio.mount_to("/ws", app_fastapi)

origins = ["*"]

app_fastapi.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app_fastapi.get("/")
async def index():
    """fastapiのAPI実装(socketioに関係ない)
    """
    return {"result": "Index"}


@app_fastapi.get("/ping/{sid}")
async def ping(sid: str):
    """指定されたsidにemitするエンドポイント
    """
    sio.start_background_task(
        sio.emit,
        "ping", {"message": "ping from server"}, room=sid)
    return {"result": "OK"}


@sio.event
async def connect(sid, environ):

    print('connect ', sid)
    print("yaa")
    sio.emit('MY_EVENT', {'data': 'foobar'})


@sio.event
async def disconnect(sid):
    print('disconnect ', sid)

@sio.on('getRoomMessage')
async def getRoomMessage(sid, message):
    print(message)
    await sio.emit('MY_EVENT', {'data': 'foobar'}, room="room1", skip_sid=sid)

@sio.on("getMessage")
async def getMessage(sid, message):
    print(message)
    await sio.emit("RECEIVE",{"data":"single"}, skip_sid=sid)

@sio.on("JOIN_ROOM")
async def join_room(sid):
    sio.enter_room(sid, 'room1')

@sio.on("LEAVE_ROOM")
async def leave_room(sid):
    print("sid:" + sid + "が退出しました")
    sio.leave_room(sid, "room1")
