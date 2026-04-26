import redis
import json

redis_client = redis.Redis.from_url("redis://localhost:6379")

def publish_event(scan_id: str, event: str, tool: str, progress: int):
    message = json.dumps({
        "event": event,
        "tool": tool,
        "progress": progress,
        "scan_id": scan_id
    })
    redis_client.publish(f"reconx:scan:{scan_id}", message)