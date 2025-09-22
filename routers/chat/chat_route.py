from datetime import datetime
from celery.result import AsyncResult as CeleryAsyncResult
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from langchain_core.messages import HumanMessage

from core.agent.chat_banner.banner_from_chat import ChatAgentWorker
from core.tasks.long_running_tasks import long_running_task
from config.celery_worker_config import celery_app
from core.utils.logger import Logger
from models.message_model import Message
from repository.chat_message_repository import (
    add_message,
    get_chat_history,
    create_chat_room as create_room,
)

router = APIRouter(prefix="/chat", tags=["Chat"])

# testing celery tasks
# @router.post('/create_chat_id')
# async def create_chat_id() -> Any:
#     """
#     Endpoint for creating the tasks
#     """
#     task = long_running_task.delay(10)
#     return {"message": "Task received", "task_id": task.id}


# @router.get("/get_chat_room_id/{task_id}")
# async def get_task_status(task_id: str) -> Any:
#     """
#     Endpoint to check the status of a Celery task.
#     """
#     task: CeleryAsyncResult = celery_app.AsyncResult(task_id)  # type: ignore
#     if task.ready():  # type: ignore
#         # type: ignore
#         return {"task_id": task_id, "status": "COMPLETED", "result": task.result}
#     return {"task_id": task_id, "status": task.status}  # type: ignore

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Chat</title>
</head>
<body>
    <h1>WebSocket Chat</h1>

    <label>Enter Chat Room ID:</label>
    <input type="text" id="chat-room-id" autocomplete="off"/>
    <button onclick="connectToWebSocket()">Join Room</button>

    <form onsubmit="sendMessage(event)">
        <input type="text" id="messageText" autocomplete="off"/>
        <button>Send</button>
    </form>

    <ul id="messages"></ul>

    <script>
        let ws = null;

        function connectToWebSocket() {
            const roomId = document.getElementById('chat-room-id').value;
            if (!roomId) {
                alert("Please enter a room ID");
                return;
            }

            ws = new WebSocket(`ws://localhost:8000/api/v1/chat/chat-ws/${roomId}`);

            ws.onopen = () => {
                console.log("Connected to WebSocket room:", roomId);
            };

            ws.onmessage = function(event) {
                const messages = document.getElementById('messages');
                
                const data = JSON.parse(event.data);
                
                if(Array.isArray(data.message)){
                    for(let m in data.message){
                       message.textContent = `[${m.sender}] ${m.text}`;
                        messages.appendChild(message); 
                    }
                    return
                }
                const message = document.createElement('li');
                message.textContent = `[${data.sender}] ${data.text}`;
                messages.appendChild(message);
            };

            ws.onclose = () => {
                console.log("WebSocket closed");
            };

            ws.onerror = (err) => {
                console.error("WebSocket error:", err);
            };
        }

        function sendMessage(event) {
            event.preventDefault();
            const input = document.getElementById("messageText");
            const text = input.value;
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    sender: "user",
                    text: text
                }));
                input.value = '';
            } else {
                alert("WebSocket is not connected.");
            }
        }
    </script>
</body>
</html>

"""


@router.get("/ws-test")
async def get() -> HTMLResponse:
    return HTMLResponse(html)


@router.get("/create_room_id")
async def create_chat_room() -> dict[str, str]:
    room_id: str = create_room()
    return {"room_id": room_id}


@router.websocket("/chat-ws/{room_id}")
async def chat_room(websocket: WebSocket, room_id: str):
    logger = Logger.get_logger(
        name=__name__,
    )
    await websocket.accept()

    has_chat = get_chat_history(room_id)

    if has_chat is not None:
        await websocket.send_json({"message": [m.model_dump() for m in has_chat]})
        # return

    try:
        worker = ChatAgentWorker()
        graph = None
        while True:
            data = await websocket.receive_json()
            msg = Message(
                sender=data["sender"],
                text=data["text"],
                timestamp=datetime.utcnow(),  # type: ignore
            )
            add_message(room_id, msg)

            # if worker.get_complied_graph is None:
            #     worker.get_graph()
            #     message = HumanMessage(content=data["text"])

            #     graph, response = worker.compile_graph(
            #         thread_id=room_id, start_message=[message]
            #     )
            #     graph = graph

            #     if response is not None:
            #         await websocket.send_text(
            #             f"{response.get('messages', [])[-1].content}"
            #         )
            #         return

            worker.get_graph()

            graph, response = worker.compile_graph(
                thread_id=room_id, start_message=[HumanMessage(content=data["text"])]
            )
            assert graph is not None, "Graph not initialed"

            # response = graph.invoke(
            #     input=[HumanMessage(content=data["text"])],
            #     config={"configurable": {"thread_id": room_id}},
            # )
            ai_message = response.get("messages", [])[-1]
            print(response)

            await websocket.send_text(f"{ai_message.content}")
    except WebSocketDisconnect:
        logger.error(f"Websocket disconnected for room if {room_id}")
