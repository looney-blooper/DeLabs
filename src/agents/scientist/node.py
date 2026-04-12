import json
from langchain_core.messages import AIMessage, HumanMessage
from src.core.state import DeLabsState
from src.core.llm_gateway import get_llm
from src.agents.scientist.prompt import scientist_prompt_template
from src.core.mcp_gateway import mcp_gateway

async def scientist_node(state: DeLabsState) -> dict:
    print("🧠 [Swarm] Chief Scientist is researching (ReAct Mode)...")
    
    # 1. Get the Groq Llama 3 70B model
    llm = get_llm(persona="scientist", temperature=0.1)
    chain = scientist_prompt_template | llm

    # 2. Prepare the local state for the loop
    current_messages = state["messages"].copy()
    research_content = state.get("research_content", [])

    scientist_tools = mcp_gateway.get_tools("literature")

    # 3. The ReAct Execution Loop (Capped at 5 iterations to prevent infinite loops)
    for iteration in range(5):
        response = await chain.ainvoke({"messages": current_messages})
        
        try:
            # Clean the text: Models sometimes ignore the "No Markdown" rule
            raw_text = response.content.strip().replace("```json", "").replace("```", "")
            output = json.loads(raw_text)
        except json.JSONDecodeError:
            print("⚠️ [Warning] LLM failed to output valid JSON. Forcing correction...")
            # If it fails, we tell the LLM it made a mistake and loop again
            current_messages.append(AIMessage(content=response.content))
            current_messages.append(HumanMessage(content="Error: Your response was not valid JSON. You MUST use the exact JSON schema provided in the system prompt."))
            continue

        # Print the LLM's inner monologue to your terminal!
        print(f"   🤔 Thought: {output.get('thought')}")

        # 4. Check for Final Answer
        if output.get("final_answer"):
            print("   ✅ Research complete.")
            
            final_ans = output["final_answer"]
            
            # 1. Safely extract the data so Pydantic doesn't crash
            if isinstance(final_ans, dict):
                research_data = json.dumps(final_ans, indent=2)
            else:
                research_data = str(final_ans)
                
            # 2. Append a clean, string-only summary to the UI chat
            current_messages.append(
                AIMessage(content="I have completed the research phase. The recommended approach for the MNIST CNN has been added to the context.")
            )
            
            # 3. IMPORTANT: Make sure you actually save the research to your state variables!
            # Example: research_content.append(research_data)
            break

        # 5. Check for Tool Call
        tool_name = output.get("tool_to_call")
        if tool_name:
            args = output.get("tool_arguments", {})
            print(f"   🔧 Executing: {tool_name} with {args}")
            
            # Find and run the specific tool
            tool_result = "Error: Tool not found."
            for tool in scientist_tools:
                if tool.name == tool_name:
                    tool_result = await tool.ainvoke(args)
                    break
            
            print(f"   📥 Result: {tool_result}")
            
            # 6. Update the memory with the action and the result, then loop again!
            current_messages.append(AIMessage(content=json.dumps(output)))
            current_messages.append(HumanMessage(content=f"System Tool Result for '{tool_name}': {tool_result}"))

    # Return the updated state back to LangGraph
    return {
        "messages": current_messages,
        "research_content": research_content
    }