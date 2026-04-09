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

@asynccontextmanager
async def lifespan(app : FastAPI):
    await mcp_gateway.initialize()
    yield 
    await mcp_gateway.cleanup()

app = FastAPI(title="DeLabs API", lifespan = lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.websocket("/ws/swarm")
async def swarm_endpoint(websocket : WebSocket):
    await websocket.accept()
    print("🟢 Client connected to Swarm.")

    try:
        data = await websocket.receive_text()
        payload = json.loads(data)
        user_prompt = payload.get("prompt", "")

        await websocket.send_json({"type" : "status", "message" : "🚀 Initializing Swarm..."})

        initial_state = {
            "messages" : [HumanMessage(content = user_prompt)],
            "research_content" : [],
            "paper_reference" : [],
            "archeitecture_draft" : "",
            "hyperparameters" : {},
            "code_filepaths" : {},
            "hardware_telemetry" : {},
            "training_metrics" : {},
            "error_logs" : [],
            "human_feedback" : None,
            "requires_approval" : False,
        }

        final_state = None

        async for event in delabs_swarm.astream(initial_state):
            for node_name, node_state in event.items():
                await websocket.send_json({
                    "type" : "update",
                    "node" : node_name,
                    "message" : f"[{node_name}] finished processing."
                })
                final_state = node_state

        if final_state:
            await websocket.send_json({
                "type" : "complete",
                "message" : "✅ Swarm Execution Complete.",
                "architecture": final_state.get("architecture_draft", ""),
                "files": final_state.get("code_filepaths", {}),
                "errors": final_state.get("error_logs", [])
            })

    except WebSocketDisconnect:
        print("🔴 Client disconnected.")
    
    except Exception as e:
        await websocket.send_json({"type":"error", "message":str(e)})

if __name__ == "__main__":
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)