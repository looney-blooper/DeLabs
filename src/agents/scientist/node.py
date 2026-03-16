from langchain_core.messages import AIMessage
from src.agents.scientist.prompt import scientist_prompt_template
from src.agents.scientist.tools import scientist_tools
from src.core.llm_gateway import get_llm
from src.core.state import DeLabsState


def scientist_node(state: DeLabsState) -> dict:
    scientist_llm = get_llm(persona="scientist", temperature=0.3)
    scientist_llm_with_tools = scientist_llm.bind_tools(scientist_tools)

    scientist_chain = scientist_prompt_template | scientist_llm_with_tools

    response = scientist_chain.invoke({
        "messages": state["messages"]
    })

    research_content = state.get("research_content", [])

    # 🔧 Handle tool calls
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        for tool in scientist_tools:
            if tool.name == tool_name:
                tool_result = tool.invoke(tool_args)
                research_content.append(tool_result)

    # Also capture normal LLM responses
    if response.content:
        research_content.append(response.content)

    return {
        "messages": state["messages"] + [response],
        "research_content": research_content
    }