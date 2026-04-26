from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import redis.asyncio as aioredis
from app.config import settings
from app.services.auth_service import decode_token

router = APIRouter()

@router.websocket("/ws/scan/{scan_id}")
async def scan_progress(
    websocket: WebSocket,
    scan_id: str,
    token: str = Query(...)
):
    # verify token first before accepting
    user_id = decode_token(token)
    if not user_id:
        await websocket.close(code=4001)
        return

    await websocket.accept()

    redis_client = aioredis.from_url(settings.REDIS_URL)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(f"reconx:scan:{scan_id}")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"].decode())

    except WebSocketDisconnect:
        await pubsub.unsubscribe(f"reconx:scan:{scan_id}")
        await redis_client.close()