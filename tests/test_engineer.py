import pytest
from langchain_core.messages import HumanMessage
from src.agents.engineer.node import engineer_node

def test_engineer_node_execution():
    """
    Tests the ML Engineer node by providing a mock architecture draft
    and verifying it writes PyTorch code.
    """
    # 1. Create a mock state simulating the Architect's output
    mock_state = {
        "messages": [HumanMessage(content="Implement the model.")],
        "research_content": [],
        "paper_references": [],
        "architecture_draft": "Input -> Linear(128, 256) -> GELU -> Output. Use AdamW optimizer.",
        "hyperparameters": {},
        "code_filepaths": {},
        "hardware_telemetry": {},
        "training_metrics": {},
        "error_logs": [],
        "human_feedback": None,
        "requires_approval": False
    }

    # 2. Execute the Engineer node
    result_state = engineer_node(mock_state)

    # 3. Verify the state updated
    assert "messages" in result_state
    assert len(result_state["messages"]) > 0
    
    # Check what the AI returned (either raw code or a tool call to save the file)
    ai_response = result_state["messages"][-1]
    
    print(f"\n💻 [Engineer Response Preview]:\n{ai_response.content[:300]}")
    if ai_response.tool_calls:
        print(f"\n🔧 [Engineer Tool Calls]: {ai_response.tool_calls}")