import json
from langchain_core.messages import AIMessage, HumanMessage
from src.core.state import DeLabsState
from src.core.llm_gateway import get_llm
from src.agents.architect.prompt import architect_prompt_template
from src.agents.architect.tools import architect_tools

def architect_node(state: DeLabsState) -> dict:
    print("📐 [Swarm] Architect is designing (ReAct Mode)...")
    
    # 1. Get the Groq Llama 3 70B model
    llm = get_llm(persona="architect", temperature=0.1)
    chain = architect_prompt_template | llm

    # 2. Prepare state variables
    current_messages = state["messages"].copy()
    research_content = "\n".join([str(item) for item in state.get("research_content", [])])
    architecture_draft = ""
    hyperparameters = {"learning_rate": 1e-3, "optimizer": "AdamW"}

    # 3. The ReAct Execution Loop
    for iteration in range(5):
        response = chain.invoke({
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
            
            # If the LLM returns a nested dictionary, convert it to a formatted string
            final_ans = output["final_answer"]
            if not isinstance(final_ans, str):
                final_ans = json.dumps(final_ans, indent=2)
                
            architecture_draft = final_ans
            current_messages.append(AIMessage(content=final_ans))
            break

        # 5. Tool Execution Check
        tool_name = output.get("tool_to_call")
        if tool_name:
            args = output.get("tool_arguments", {})
            print(f"   🔧 Executing: {tool_name} with {args}")
            
            tool_result = "Error: Tool not found."
            for tool in architect_tools:
                if tool.name == tool_name:
                    tool_result = tool.invoke(args)
                    break
            
            print(f"   📥 Result: {tool_result}")
            
            current_messages.append(AIMessage(content=json.dumps(output)))
            current_messages.append(HumanMessage(content=f"System Tool Result for '{tool_name}': {tool_result}"))

    return {
        "messages": current_messages,
        "architecture_draft": architecture_draft,
        "hyperparameters": hyperparameters
    }