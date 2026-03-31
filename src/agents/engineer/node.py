import json
from langchain_core.messages import AIMessage, HumanMessage
from src.core.state import DeLabsState
from src.core.llm_gateway import get_llm
from src.agents.engineer.prompt import engineer_prompt_template
from src.agents.engineer.tools import engineer_tools

def engineer_node(state: DeLabsState) -> dict:
    print("💻 [Swarm] ML Engineer is writing code (ReAct Mode)...")
    
    # 1. Get the hyper-fast Llama 3 8B model
    llm = get_llm(persona="engineer", temperature=0.1)
    chain = engineer_prompt_template | llm

    # 2. Prepare state variables
    current_messages = state["messages"].copy()
    blueprint = str(state.get("architecture_draft", "No blueprint provided."))
    
    # We copy the existing dictionary so we don't accidentally overwrite past files
    code_filepaths = state.get("code_filepaths", {}).copy()

    # 3. The ReAct Execution Loop
    for iteration in range(5):
        response = chain.invoke({
            "messages": current_messages,
            "architecture_draft": blueprint
        })
        
        try:
            raw_text = response.content.strip().replace("```json", "").replace("```", "")
            output = json.loads(raw_text)
        except json.JSONDecodeError as e:
            print(f"⚠️ [Warning] Engineer failed JSON format: {e}")
            print(f"--- RAW TEXT ATTEMPT ---\n{raw_text}\n------------------------")
            
            current_messages.append(AIMessage(content=response.content))
            current_messages.append(HumanMessage(content="Error: Invalid JSON. You must properly escape all newlines (\\n) and quotes (\") inside your code_content string."))
            continue

        print(f"   🤔 Thought: {output.get('thought')}")

        # 4. Final Answer Check (Applying our defensive string casting fix!)
        if output.get("final_answer"):
            print("   ✅ Engineering complete.")
            final_ans = output["final_answer"]
            if not isinstance(final_ans, str):
                final_ans = json.dumps(final_ans, indent=2)
                
            current_messages.append(AIMessage(content=final_ans))
            break

        # 5. Tool Execution Check
        tool_name = output.get("tool_to_call")
        if tool_name:
            args = output.get("tool_arguments", {})
            filename = args.get("filename", "unknown_file.py")
            print(f"   🔧 Executing: {tool_name} to save '{filename}'")
            
            tool_result = "Error: Tool not found."
            for tool in engineer_tools:
                if tool.name == tool_name:
                    tool_result = tool.invoke(args)
                    # If successful, track the newly created file in the LangGraph State!
                    code_filepaths[filename] = f"./workspace/experiments/{filename}"
                    break
            
            print(f"   📥 Result: {tool_result}")
            
            current_messages.append(AIMessage(content=json.dumps(output)))
            current_messages.append(HumanMessage(content=f"System Tool Result for '{tool_name}': {tool_result}"))

    return {
        "messages": current_messages,
        "code_filepaths": code_filepaths
    }