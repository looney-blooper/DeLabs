from langchain_core.messages import AIMessage
from src.agents.architect.prompt import architect_prompt_template
from src.agents.architect.tools import architect_tools
from src.core.llm_gateway import get_llm
from src.core.state import DeLabsState


def architect_agent(state: DeLabsState) -> dict:
    """
    LangGraph Agent node for Architect Agent
    """

    architect_llm = get_llm(persona="architect", temperature=0.1)
    architect_llm_with_tools = architect_llm.bind_tools(architect_tools)

    architect_chain = architect_prompt_template | architect_llm_with_tools

    research_content = "\n".join(state["research_content"])

    response = architect_chain.invoke({
        "messages": state["messages"],
        "Research_Content" : research_content,
    })

    return {
        "messages" : [response],
        "archeiture_draft" : response.content,
        "hyperparameters" : {
            "learning_rate" : 1e-3,
            "optimizer" : "AdamW"
        }, 
    }