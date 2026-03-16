from src.agents.engineer.prompt import engineer_prompt_template
from src.agents.engineer.tools import engineer_tools
from src.core.state import DeLabsState
from src.core.llm_gateway import get_llm

def engineer_node(state : DeLabsState) -> dict:
    """
    LangGraph node for Engineer Agent
    """

    engineer_llm = get_llm(persona="engineer", temperature=0.1)
    engineer_llm_with_tools = engineer_llm.bind_tools(engineer_tools)

    engineer_chain = engineer_prompt_template | engineer_llm_with_tools

    architect_blueprint = state.get("archeiture_draft", "No blueprint provided, Ask the Architect for details.")

    response = engineer_chain.invoke({
        "messages" : state["messages"],
        "architecture_draft" : architect_blueprint,
    })

    new_filepaths = state.get("code_filepaths", {})
    new_filepaths["latest_build"] = "./workspace/experiments/model.py"

    return {
        "messages" : [response],
        "code_filepaths" : new_filepaths,
    }