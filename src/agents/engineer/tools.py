from langchain_core.tools import tool

import os
from pathlib import Path

@tool
def write_code_to_workspace(filename: str, code_content: str) -> str:
    """
    Saves the Python code to isolated local workspace
    """
    # TODO: Connect this to the Workspace MCP Server to actually write to disk securely.
    
    try:
        base_dir = Path("./workspace/experiments").resolve()
        base_dir.mkdir(parents=True, exist_ok=True)

        safe_filename = os.path.basename(filename)
        file_path = base_dir / safe_filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code_content)

        return f"SUCCESS: File '{safe_filename}' securely written to {file_path}"

    except Exception as e:
        return f"ERROR: failed to write file. {str(e)}"
    
    

engineer_tools = [write_code_to_workspace]