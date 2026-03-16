from src.agents.architect.prompt import architect_prompt_template
from src.agents.architect.tools import architect_tools
from src.core.llm_gateway import get_llm
from src.core.state import DeLabsState


def architect_node(state: DeLabsState) -> dict:
    architect_llm = get_llm(persona="architect", temperature=0.1)
    architect_llm_with_tools = architect_llm.bind_tools(architect_tools)

    architect_chain = architect_prompt_template | architect_llm_with_tools

    research_content = "\n".join(state["research_content"])

    response = architect_chain.invoke({
        "messages": state["messages"],
        "Research_Content": research_content,
    })

    architecture_draft = ""

    # If LLM called a tool
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        for tool in architect_tools:
            if tool.name == tool_name:
                tool_result = tool.invoke(tool_args)
                architecture_draft = tool_result

    # If LLM responded normally
    if response.content:
        architecture_draft = response.content

    return {
        "messages": state["messages"] + [response],
        "architecture_draft": architecture_draft,
        "hyperparameters": {
            "learning_rate": 1e-3,
            "optimizer": "AdamW"
        }
    }