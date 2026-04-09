import pytest
import asyncio
from langchain_core.messages import HumanMessage
from src.orchestrator.builder import delabs_swarm
from src.core.mcp_gateway import mcp_gateway

@pytest.mark.asyncio
async def test_full_swarm_execution():
    """
    Integration test: Watches the entire multi-agent system run from start to finish.
    """
    await mcp_gateway.initialize()
    
    # The absolute bare-minimum starting state
    initial_state = {
        "messages": [HumanMessage(content="Design a simple 2-layer Convolutional Neural Network for CIFAR-10. Keep the code very brief.")],
        "research_content": [],
        "paper_references": [],
        "architecture_draft": "",
        "hyperparameters": {},
        "code_filepaths": {},
        "hardware_telemetry": {},
        "training_metrics": {},
        "error_logs": [],
        "human_feedback": None,
        "requires_approval": False
    }

    try:
        # 3. Stream the graph execution
        async for event in delabs_swarm.astream(initial_state):
            for node_name, node_state in event.items():
                print(f"\n--- 🏁 Finished Node: {node_name} ---")
                
        print("\n✅ [DeLabs] Swarm Execution Complete.")
        
    finally:
        # 4. CRITICAL: Shut down the servers even if the test crashes
        await mcp_gateway.cleanup()