from src.agents.reviewer.prompt import reviewer_prompt_template
from src.agents.reviewer.tools import reviewer_tools
from src.core.state import DeLabsState
from src.core.llm_gateway import get_llm

def reviewer_agent(state : DeLabsState) -> dict:
    """
    LangGrapg node for Reviewer Agent
    """

    reviewer_llm = get_llm(persona="reviewer", temperature=0.3)
    reviewer_llm_with_tools = reviewer_llm.bind_tools(reviewer_tools)

    reviewer_chain = reviewer_prompt_template | reviewer_llm_with_tools

    filepaths = str(state.get("code_filepaths", "No files provided by the Engineer."))

    response = reviewer_chain.invoke({
        "messages" : state["messages"],
        "code_filepaths" : filepaths,
    })

    response_text = response.content.upper() if response.content else ""
    passed_qa = "PASS" in response_text

    error_logs = state.get("error_logs", [])
    if not passed_qa and response.content:
        error_logs.append(response.content)

    return {
        "messages": [response],
        "error_logs": error_logs,
        # If it passed QA, it now requires YOUR manual approval before executing!
        "requires_approval": passed_qa 
    }