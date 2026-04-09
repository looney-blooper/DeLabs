import json
from langchain_core.messages import AIMessage, HumanMessage
from src.core.state import DeLabsState
from src.core.llm_gateway import get_llm
from src.agents.reviewer.prompt import reviewer_prompt_template
from src.core.mcp_gateway import mcp_gateway

async def reviewer_node(state: DeLabsState) -> dict:
    print("🔬 [Swarm] QA Reviewer is analyzing code (ReAct Mode)...")
    
    # 1. Get the hyper-fast Llama 3 8B model
    llm = get_llm(persona="reviewer", temperature=0.0) 
    
    # 🚨 CRITICAL: Notice there is NO .bind_tools() here! 🚨
    chain = reviewer_prompt_template | llm

    # 2. Prepare state variables
    current_messages = state["messages"].copy()
    filepaths_dict = state.get("code_filepaths", {})
    filepaths_str = json.dumps(filepaths_dict, indent=2) if filepaths_dict else "No files provided."
    
    error_logs = state.get("error_logs", [])
    passed_qa = False

    reviewer_tools = mcp_gateway.get_tools("workspace") + mcp_gateway.get_tools("sysadmin")

    # 3. The ReAct Execution Loop
    for iteration in range(5):
        response = await chain.ainvoke({
            "messages": current_messages,
            "code_filepaths": filepaths_str
        })
        
        try:
            raw_text = response.content.strip().replace("```json", "").replace("```", "")
            output = json.loads(raw_text)
        except json.JSONDecodeError:
            print("⚠️ [Warning] Reviewer failed JSON format. Forcing correction...")
            current_messages.append(AIMessage(content=response.content))
            current_messages.append(HumanMessage(content="Error: Invalid JSON. Use the exact JSON schema provided."))
            continue

        print(f"   🤔 Thought: {output.get('thought')}")

        # 4. Final Answer Check
        if output.get("final_answer"):
            print("   ✅ QA Review complete.")
            final_ans = output["final_answer"]
            if not isinstance(final_ans, str):
                final_ans = json.dumps(final_ans, indent=2)
            
            # Check if the AI officially passed the code
            passed_qa = "PASS" in final_ans.upper()
            
            if not passed_qa:
                error_logs.append(final_ans)
                print("   ❌ QA Failed. Errors logged.")
            else:
                print("   🏆 QA Passed! Ready for human execution.")

            current_messages.append(AIMessage(content=final_ans))
            break

        # 5. Tool Execution Check
        tool_name = output.get("tool_to_call")
        if tool_name:
            args = output.get("tool_arguments", {})
            print(f"   🔧 Executing: {tool_name} with {args}")
            
            tool_result = "Error: Tool not found."
            for tool in reviewer_tools:
                if tool.name == tool_name:
                    tool_result = await tool.ainvoke(args)
                    break
            
            print(f"   📥 Result: {tool_result}")
            
            current_messages.append(AIMessage(content=json.dumps(output)))
            current_messages.append(HumanMessage(content=f"System Tool Result for '{tool_name}': {tool_result}"))

    return {
        "messages": current_messages,
        "error_logs": error_logs,
        "requires_approval": passed_qa
    }