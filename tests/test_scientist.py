import pytest
from langchain_core.messages import HumanMessage
from src.agents.scientist.node import scientist_node

def test_scientist_node_execution():
    """
    Tests the Scientist node in isolation by passing it a mocked LangGraph state.
    This will actually ping the Gemini API to ensure the chain works end-to-end.
    """
    # 1. Create a mock starting state
    mock_state = {
        "messages": [HumanMessage(content="I want to build a model for Hyperspectral Image Anomaly Detection. Give me a brief architectural paradigm.")],
        "research_notes": [],
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

    # 2. Execute the node exactly as LangGraph would
    result_state = scientist_node(mock_state)

    # 3. Assert the node did its job correctly
    assert "messages" in result_state
    assert len(result_state["messages"]) > 0
    
    # The AI's response should be the last message
    ai_response = result_state["messages"][-1]
    print(f"\n[Scientist Output]: {ai_response.content[:200]}...\n")
    
    # Check if it successfully appended to research notes
    assert "research_content" in result_state
    assert len(result_state["research_content"]) > 0