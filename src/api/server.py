import json 
import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
import sys
import os
import uuid

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
    
    # Generate a unique thread ID for this specific user's session
    thread_id = str(uuid.uuid4())
    
    # 1. Create the Telemetry Queue and background task (same as before)
    telemetry_queue = asyncio.Queue()
    async def telemetry_sender():
        while True:
            message = await telemetry_queue.get()
            if message is None:
                break
            await websocket.send_json(message)
            
    sender_task = asyncio.create_task(telemetry_sender())

    try:
        # 2. Keep the socket open to listen for multiple actions
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            action = payload.get("action", "prompt") # 'prompt' or 'approve'

            # Update config to include the thread_id so LangGraph can load memory
            config = {
                "configurable": {
                    "thread_id": thread_id,
                    "telemetry_queue": telemetry_queue
                }
            }

            if action == "prompt":
                user_prompt = payload.get("prompt", "")
                await websocket.send_json({"type": "status", "message": "🚀 Initializing Swarm..."})

                initial_state = {
                    "messages": [HumanMessage(content=user_prompt)],
                    # ... (keep your other initial state keys here) ...
                    "code_filepaths": {},
                    "error_logs": []
                }

                # Run the graph until it hits the interrupt breakpoint
                async for event in delabs_swarm.astream(initial_state, config=config):
                    for node_name, node_state in event.items():
                        await websocket.send_json({
                            "type": "update",
                            "node": node_name,
                            "message": f"[{node_name}] finished processing."
                        })

                # Check if the graph paused at the trainer
                snapshot = await delabs_swarm.aget_state(config)
                if snapshot.next and "trainer" in snapshot.next:
                    await websocket.send_json({
                        "type": "approval_required",
                        "message": "✅ Code generated and verified. Ready for Colab deployment. Awaiting approval."
                    })

            elif action == "approve":
                await websocket.send_json({"type": "status", "message": "🚀 Deploying to Colab..."})
                
                final_state = None
                # Passing `None` as the state tells LangGraph to RESUME from memory
                async for event in delabs_swarm.astream(None, config=config):
                    for node_name, node_state in event.items():
                        await websocket.send_json({
                            "type": "update",
                            "node": node_name,
                            "message": f"[{node_name}] finished processing."
                        })
                        final_state = node_state
                        
                # Graph fully completed
                if final_state:
                    await websocket.send_json({
                        "type": "complete",
                        "message": "✅ Deployment and Training Complete.",
                        "files": final_state.get("code_filepaths", {})
                    })

    except WebSocketDisconnect:
        print("🔴 Client disconnected.")
    
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
        
    finally:
        # Ensure we kill the background task when the socket drops
        await telemetry_queue.put(None)


if __name__ == "__main__":
    uvicorn.run(
        "src.api.server:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True, 
        reload_dirs=["src"],
        reload_excludes=["workspace/*", "workspace"],
    )