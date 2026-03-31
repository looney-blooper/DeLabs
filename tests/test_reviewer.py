import pytest
from langchain_core.messages import HumanMessage
from src.agents.reviewer.node import reviewer_node

def test_reviewer_node_execution():
    """Tests if the Reviewer can analyze mock code and output a PASS/FAIL decision."""
    mock_state = {
        "messages": [HumanMessage(content="Review the code.")],
        "research_content": [],
        "paper_references": [],
        "architecture_draft": "",
        "hyperparameters": {},
        "code_filepaths": {"model.py": "./workspace/experiments/model.py"},
        "hardware_telemetry": {},
        "training_metrics": {},
        "error_logs": [],
        "human_feedback": None,
        "requires_approval": False
    }

    result_state = reviewer_node(mock_state)

    assert "requires_approval" in result_state
    print(f"\n🔬 [Reviewer Passed QA?]: {result_state['requires_approval']}")