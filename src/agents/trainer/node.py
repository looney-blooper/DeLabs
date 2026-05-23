import os
import asyncio
from langchain_core.messages import AIMessage
from langchain_core.runnables.config import RunnableConfig
from src.agents.trainer.tools import deploy_and_train

async def trainer_node(state: dict, config: RunnableConfig):
    """
    The LangGraph node responsible for orchestrating remote execution.
    Takes the approved code, securely tunnels to Colab, and streams telemetry.
    """
    print("🚀 [Trainer Node] Initializing model training sequence...")
    
    messages = state.get("messages", [])
    filepaths = state.get("code_filepaths", {})

    # Extract the live telemetry queue from LangGraph config
    telemetry_queue = config.get("configurable", {}).get("telemetry_queue")
    
    # Capture the main asyncio event loop BEFORE we go into the background thread
    main_loop = asyncio.get_running_loop()
    
    # 1. Locate the generated file from the ML Engineer's state
    if not filepaths:
        error_msg = "Trainer Agent failed: No code filepaths provided in state."
        print(f"❌ {error_msg}")
        return {"error_logs": state.get("error_logs", []) + [error_msg]}
        
    # Grab the target file (e.g., mnist_cnn.py)
    local_filepath = list(filepaths.values())[0]
    
    # 2. Retrieve Colab Credentials
    # (For now we use .env, eventually this comes from the user's DB session)
    colab_host = os.getenv("COLAB_SSH_HOST")
    colab_port = int(os.getenv("COLAB_SSH_PORT", 22))
    colab_password = os.getenv("COLAB_SSH_PASSWORD", "delabs_admin_123")
    
    if not colab_host:
        msg = "⚠️ Colab SSH host missing in .env. Halting remote execution."
        print(msg)
        messages.append(AIMessage(content=msg))
        return {"messages": messages}

    # 3. Handling Telemetery data 
    # 🚨 The Live UI Bridge 🚨
    def handle_telemetry(data: dict):
        # 1. Print to terminal for debugging
        print(f"📈 [Live Telemetry] Epoch: {data.get('epoch')} | Loss: {data.get('loss')}")
        
        # 2. Push to the UI WebSocket queue safely from this background thread
        if telemetry_queue:
            payload = {
                "type": "telemetry",
                "data": data
            }
            main_loop.call_soon_threadsafe(telemetry_queue.put_nowait, payload)

    print(f"🔧 [Trainer Node] Handing off {local_filepath} to Colab execution tool...")

    # 4. Execute the SSH Deployment in a background thread to prevent blocking
    print(f"🔧 [Trainer Node] Handing off {local_filepath} to Colab execution tool...")
    
    result = await asyncio.to_thread(
        deploy_and_train,
        local_filepath=local_filepath,
        colab_host=colab_host,
        colab_port=colab_port,
        colab_password=colab_password,
        on_telemetry=handle_telemetry
    )
    
    # 5. Process the Final Results
    if result.get("status") == "success":
        final_report = result.get("final_report", {})
        success_msg = f"✅ Training complete. Final metrics: {final_report}"
        print(success_msg)
        messages.append(AIMessage(content=success_msg))
        
        return {
            "messages": messages,
            "training_metrics": final_report
        }
    else:
        error_msg = f"❌ Training failed: {result.get('error')}"
        print(error_msg)
        return {
            "error_logs": state.get("error_logs", []) + [error_msg]
        }