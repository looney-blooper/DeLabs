import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DeLabs Workspace Server")

# Strict Sandbox Path
BASE_DIR = Path("./workspace/experiments").resolve()
BASE_DIR.mkdir(parents=True, exist_ok=True)

@mcp.tool()
def write_code_to_workspace(filename: str, code_content: str) -> str:
    """Saves generated Python code to the isolated local workspace."""
    try:
        safe_filename = os.path.basename(filename)
        file_path = BASE_DIR / safe_filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code_content)
        return f"SUCCESS: File '{safe_filename}' securely written to {file_path}"
    except Exception as e:
        return f"ERROR: Failed to write file. {str(e)}"

@mcp.tool()
def read_workspace_file(filepath: str) -> str:
    """Reads a file from the local workspace to review the code."""
    try:
        path = Path(filepath)
        if not path.exists():
            return f"ERROR: File not found at {filepath}"
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"ERROR: Could not read file. {str(e)}"

if __name__ == "__main__":
    mcp.run()