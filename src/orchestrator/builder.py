from langgraph.graph import StateGraph, END

from src.agents.architect.node import architect_node
from src.agents.engineer.node import engineer_node
from src.agents.reviewer.node import reviewer_node
from src.agents.scientist.node import scientist_node

from src.core.state import DeLabsState


def route_after_QA(state : DeLabsState) -> str:
    """
    The conditional routing logic. 
    This decides what happens after the Reviewer inspects the code.
    """
    print("🔄 [Orchestrator] Evaluating QA results...")
    
    # If the QA agent flipped the approval flag to True, we are done!
    if state.get("requires_approval", False):
        print("✅ [Orchestrator] Code passed QA. Routing to END (Ready for Execution).")
        return END
    else:
        # If it failed, we send the state back to the Engineer to fix the errors
        print("❌ [Orchestrator] Code failed QA. Routing back to ML Engineer.")
        return "Engineer"
    

def build_delabs_graph():
    """
    Compiles the individual agents node into a cyclic graph.
    """

    builder = StateGraph(DeLabsState)

    builder.add_node("Scientist", scientist_node)
    builder.add_node("Engineer", engineer_node)
    builder.add_node("Architect", architect_node)
    builder.add_node("Reviewer", reviewer_node)

    builder.set_entry_point("Scientist")
    builder.add_edge("Scientist", "Architect")
    builder.add_edge("Architect", "Engineer")
    builder.add_edge("Engineer", "Reviewer")

    builder.add_conditional_edges(
        "Reviewer",
        route_after_QA,
        {
            "Engineer" : "Engineer",
            END : END,
        }
    )

    graph = builder.compile()

    return graph


delabs_swarm = build_delabs_graph()