from langchain_core.messages import AIMessage
from src.agents.scientist.prompt import scientist_system_prompt_template
from src.agents.scientist.tools import scientist_tools
from src.core.llm_gateway import get_llm
from src.core.state import DeLabsState

def scientist_node(state : DeLabsState) -> dict:
    """
    LangGraph node for Cheif Scientist Agent.
    """

    scientist_llm = get_llm(persona="scientist", temperature=0.3)
    scientist_llm_with_tools = scientist_llm.bind_tools(scientist_tools)

    scientist_chain = scientist_system_prompt_template | scientist_llm_with_tools

    response = scientist_chain.invoke({
        "messages", state["messages"]
    })

    return {
        "messages" : [response],
        "research notes" : state.get("research_notes", []) + [response.content] if response.content else state.get("research_notes", [])
    }

