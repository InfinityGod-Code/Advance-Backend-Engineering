import asyncio
import json
import logging
import os
from typing import Dict, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import HTMLResponse
import redis.asyncio as aioredis
from config import settings
from contextlib import asynccontextmanager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EventDistributor")




@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    # Initialize the asynchronous Redis client pool
    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    # Start the background cluster listener
    asyncio.create_task(redis_cluster_listener())
    logger.info("Application startup complete. Redis connection pool established.")
    yield

    """Shutdown logic for the FastAPI application."""
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection pool closed cleanly.")


app = FastAPI(
    title="Enterprise Real-Time Event Distribution Cluster",
    lifespan=lifespan,
)


@app.get("/test")
def test() :
    return {"content": "hello world"}

# Global Redis Pool Client
redis_client: aioredis.Redis = None


class ConnectionManager:
    """Manages local WebSocket connections for THIS specific cluster node."""

    def __init__(self):
        # Maps a unique tracking ID (e.g., tenant/user ID) to a set of active connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        self.active_connections[client_id].add(websocket)
        logger.info(
            f"Client {client_id} connected to this node. Total active keys: {len(self.active_connections)}"
        )

    def disconnect(self, client_id: str, websocket: WebSocket):
        if client_id in self.active_connections:
            self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
        logger.info(f"Client {client_id} disconnected from this node.")

    async def broadcast_locally(self, message: str):
        """Broadcasts a message to ALL connections currently held on this specific node."""
        payload = json.loads(message)
        target_client = payload.get("target_client")  # Routing key

        # If a target is specified, only route to them; otherwise broadcast to everyone on this node
        if target_client:
            sockets = self.active_connections.get(target_client, set())
            for connection in sockets.copy():
                try:
                    await connection.send_text(message)
                except Exception:
                    self.disconnect(target_client, connection)
        else:
            for client_id, sockets in list(self.active_connections.items()):
                for connection in sockets.copy():
                    try:
                        await connection.send_text(message)
                    except Exception:
                        self.disconnect(client_id, connection)


manager = ConnectionManager()


async def redis_cluster_listener():
    """Background task subscribing to Redis Pub/Sub to listen for cross-node events."""
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(settings.EVENT_CHANNEL)
    logger.info(f"Subscribed globally to Redis channel: {settings.EVENT_CHANNEL}")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = message["data"]
                # Forward the event received from the broker to connections on this local node
                await manager.broadcast_locally(data)
    except asyncio.CancelledError:
        logger.info("Redis cluster listener task cancelled.")
    except Exception as e:
        logger.error(f"Error in Redis listener loop: {e}")
        # In production, implement an exponential backoff reconnection strategy here
        await asyncio.sleep(5)
        asyncio.create_task(redis_cluster_listener())


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Edge gateway endpoint handling stateful TCP client connections."""
    await manager.connect(client_id, websocket)
    try:
        while True:
            # Keep-alive heartbeat or receiving upstream messages from client
            data = await websocket.receive_text()
            # If clients send upstream messages, you can route them back into Redis if necessary
            logger.debug(f"Received upstream message from client {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id, websocket)
    except Exception as e:
        logger.error(f"Unexpected WebSocket error on client {client_id}: {e}")
        manager.disconnect(client_id, websocket)


@app.post("/publish")
async def publish_event(payload: dict, background_tasks: BackgroundTasks):
    """
    Stateless REST Endpoint.
    Can be hit on ANY app instance. It offloads the event payload to Redis Pub/Sub.
    """
    # Example expected payload: {"target_client": "user_123", "event": "order_dispatched", "data": {}}
    message_str = json.dumps(payload)

    # Offload I/O to background tasks to return HTTP 202 immediately
    background_tasks.add_task(redis_client.publish, settings.EVENT_CHANNEL, message_str)
    return {"status": "Accepted", "detail": "Event queued for cluster distribution."}



# Put this endpoint near the bottom of your main.py file
@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    # Looks for index.html in the same directory
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()
    return "<h3>Error: index.html not found in application directory.</h3>"
