import os
import sys
import ast
import subprocess
import tempfile
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DeLabs Sysadmin Server")

@mcp.tool()
def run_ast_linter(filepath: str) -> str:
    """Runs a Python Abstract Syntax Tree (AST) linter on the file."""
    try:
        path = Path(filepath)
        if not path.exists():
            return f"ERROR: File not found at {filepath}"
        code = path.read_text(encoding="utf-8")
        ast.parse(code) 
        return f"SUCCESS: AST Linter passed. No syntax errors found in {path.name}."
    except SyntaxError as e:
        return f"SYNTAX ERROR: {e.msg} on line {e.lineno}, offset {e.offset}"
    except Exception as e:
        return f"ERROR: Linter failed to execute. {str(e)}"

@mcp.tool()
def validate_tensor_shapes(input_shape: str, operations: str) -> str:
    """Validates tensor dimensions by running a dry-pass through PyTorch."""
    script_content = f"""
import torch
import torch.nn as nn
try:
    x = torch.randn({input_shape})
    model = {operations}
    out = model(x)
    print(f"SUCCESS: Dimensions align. Final output shape is {{tuple(out.shape)}}")
except Exception as e:
    print(f"DIMENSION ERROR: {{str(e)}}")
"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            temp_path = f.name

        result = subprocess.run([sys.executable, temp_path], capture_output=True, text=True, timeout=5)
        os.remove(temp_path)

        if result.stdout:
            return result.stdout.strip()
        return f"EXECUTION FAILED: {result.stderr.strip()}"
    except Exception as e:
        return f"SYSTEM ERROR: Could not run validation. {str(e)}"

if __name__ == "__main__":
    mcp.run()