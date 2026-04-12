import json
from langchain_core.messages import AIMessage, HumanMessage
from src.core.state import DeLabsState
from src.core.llm_gateway import get_llm
from src.agents.architect.prompt import architect_prompt_template
from src.core.mcp_gateway import mcp_gateway

async def architect_node(state: DeLabsState) -> dict:
    print("📐 [Swarm] Architect is designing (ReAct Mode)...")
    
    # 1. Get the Groq Llama 3 70B model
    llm = get_llm(persona="architect", temperature=0.1)
    chain = architect_prompt_template | llm

    # 2. Prepare state variables
    current_messages = state["messages"].copy()
    research_content = "\n".join([str(item) for item in state.get("research_content", [])])
    architecture_draft = ""
    hyperparameters = {"learning_rate": 1e-3, "optimizer": "AdamW"}

    architect_tools = mcp_gateway.get_tools("sysadmin")

    # 3. The ReAct Execution Loop
    for iteration in range(5):
        response = await chain.ainvoke({
            "messages": current_messages,
            "research_notes": research_content
        })
        
        try:
            raw_text = response.content.strip().replace("```json", "").replace("```", "")
            output = json.loads(raw_text)
        except json.JSONDecodeError:
            print("⚠️ [Warning] Architect failed JSON format. Forcing correction...")
            current_messages.append(AIMessage(content=response.content))
            current_messages.append(HumanMessage(content="Error: Invalid JSON. Use the exact JSON schema provided."))
            continue

        print(f"   🤔 Thought: {output.get('thought')}")

        # 4. Final Answer Check
        # 4. Final Answer Check
        if output.get("final_answer"):
            print("   ✅ Architecture design complete.")
            
            final_ans = output["final_answer"]
            
            # If it's a dictionary, split the data nicely
            if isinstance(final_ans, dict):
                # Save the structure as a string for the state
                architecture_draft = json.dumps(final_ans.get("architecture", final_ans), indent=2)
                
                # If the LLM provided specific hyperparameters, update our defaults!
                if "hyperparameters" in final_ans:
                    hyperparameters.update(final_ans["hyperparameters"])
            else:
                # Fallback if the LLM just wrote a plain text paragraph
                architecture_draft = str(final_ans)
                
            # --- THE MAGIC FIX FOR THE FRONTEND ---
            # Instead of appending the raw JSON to the chat, we append a clean summary.
            # The actual JSON data is still safely stored in architecture_draft for the Engineer to use!
            current_messages.append(AIMessage(content="I have finalized the architecture design and defined the necessary hyperparameters. I am handing the blueprint off to the Engineer."))
            break

        # 5. Tool Execution Check
        tool_name = output.get("tool_to_call")
        if tool_name:
            args = output.get("tool_arguments", {})
            print(f"   🔧 Executing: {tool_name} with {args}")
            
            tool_result = "Error: Tool not found."
            for tool in architect_tools:
                if tool.name == tool_name:
                    tool_result = await tool.ainvoke(args)
                    break
            
            print(f"   📥 Result: {tool_result}")
            
            current_messages.append(AIMessage(content=json.dumps(output)))
            current_messages.append(HumanMessage(content=f"System Tool Result for '{tool_name}': {tool_result}"))

    return {
        "messages": current_messages,
        "architecture_draft": architecture_draft,
        "hyperparameters": hyperparameters
    }