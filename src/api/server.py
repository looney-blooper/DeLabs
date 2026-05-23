import json 
import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.orchestrator.builder import delabs_swarm
from src.core.mcp_gateway import mcp_gateway
from src.db.database import init_db

@asynccontextmanager
async def lifespan(app : FastAPI):

    print("🚀 [Backend] Booting up...")

    #Initialize Postgres database schema
    print("📦 [Database] Verifying database schemas...")
    try:
        init_db()
        print("✅ [Database] Database schemas are ready.")
    except Exception as e:
        print(f"❌ [Database] Failed to initialize database: {e}")
    
    #initialize MCP Gateway
    print("🌐 [MCP] Initializing Gateway...")
    try:
        await mcp_gateway.initialize()
        print("✅ [MCP] Gateway initialized successfully.")
    except Exception as e:
        print(f"❌ [MCP] Failed to initialize Gateway: {e}")
        raise e

    yield #app is now running

    #teardown logics
    await mcp_gateway.cleanup()
    print("🛑 [Backend] Shutting down...")


app = FastAPI(title="DeLabs API", lifespan = lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.websocket("/ws/swarm")
async def swarm_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🟢 Client connected to Swarm.")

    try:
        data = await websocket.receive_text()
        payload = json.loads(data)
        user_prompt = payload.get("prompt", "")

        await websocket.send_json({"type": "status", "message": "🚀 Initializing Swarm..."})

        initial_state = {
            "messages": [HumanMessage(content=user_prompt)],
            "research_content": [],
            "paper_reference": [],
            "architecture_draft": "",
            "hyperparameters": {},
            "code_filepaths": {},
            "hardware_telemetry": {},
            "training_metrics": {},
            "error_logs": [],
            "human_feedback": None,
            "requires_approval": False,
        }

        # 1. Create the Telemetry Queue
        telemetry_queue = asyncio.Queue()

        # 2. Define the background task that listens to the queue
        async def telemetry_sender():
            while True:
                message = await telemetry_queue.get()
                if message is None:  # A None payload tells the loop to shut down
                    break
                await websocket.send_json(message)

        # 3. Start the listener in the background concurrently
        sender_task = asyncio.create_task(telemetry_sender())

        # 4. Pass the queue into LangGraph
        config = {"configurable": {"telemetry_queue": telemetry_queue}}
        final_state = None

        # Notice we pass `config` here now
        async for event in delabs_swarm.astream(initial_state, config=config):
            for node_name, node_state in event.items():
                await websocket.send_json({
                    "type": "update",
                    "node": node_name,
                    "message": f"[{node_name}] finished processing."
                })
                final_state = node_state

        # 5. Shut down the background telemetry listener gracefully
        await telemetry_queue.put(None)
        await sender_task

        # Send final completion
        if final_state:
            await websocket.send_json({
                "type": "complete",
                "message": "✅ Swarm Execution Complete.",
                "architecture": final_state.get("architecture_draft", ""),
                "files": final_state.get("code_filepaths", {}),
                "errors": final_state.get("error_logs", [])
            })

    except WebSocketDisconnect:
        print("🔴 Client disconnected.")
    
    except Exception as e:
        await websocket.send_json({"type":"error", "message":str(e)})


if __name__ == "__main__":
    uvicorn.run(
        "src.api.server:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True, 
        reload_dirs=["src"],
        reload_excludes=["workspace/*", "workspace"],
    )