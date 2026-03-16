import pytest
from langchain_core.messages import HumanMessage
from src.agents.architect.node import architect_node

def test_architect_node_execution():
    """
    Tests the Architect node by providing mock research notes
    and verifying it generates a tensor blueprint.
    """
    # 1. Create a mock state simulating the Scientist's output
    mock_state = {
        "messages": [HumanMessage(content="Design the architecture.")],
        "research_content": [
            "MOCK ARXIV RESULT: Recent papers suggest using a Graph-based Vision Transformer with a Gated mechanism for hyperspectral anomaly detection."
        ],
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

    # 2. Execute the Architect node
    result_state = architect_node(mock_state)

    # 3. Verify it drafted the architecture
    assert "architecture_draft" in result_state
    assert len(result_state["architecture_draft"]) > 0
    
    print(f"\n📐 [Architect Draft Preview]:\n{result_state['architecture_draft'][:300]}...\n")