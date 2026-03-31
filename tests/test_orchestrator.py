from langchain_core.messages import HumanMessage
from src.orchestrator.builder import delabs_swarm

def test_full_swarm_execution():
    """
    Integration test: Watches the entire multi-agent system run from start to finish.
    """
    print("\n🚀 [DeLabs] Initiating Full Swarm R&D Cycle...\n")
    
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

    # Stream the graph execution so we can watch it step-by-step
    for event in delabs_swarm.stream(initial_state):
        # The event dictionary keys are the names of the nodes that just finished
        for node_name, node_state in event.items():
            print(f"\n--- 🏁 Finished Node: {node_name} ---")
            
            if node_name == "Reviewer":
                print(f"Errors Found: {node_state.get('error_logs', [])}")
                print(f"Passed QA: {node_state.get('requires_approval', False)}")

    print("\n✅ [DeLabs] Swarm Execution Complete.")