from langchain_core.tools import tool

import ast
from pathlib import Path

@tool
def read_workspace_file(filepath: str) -> str:
    """
    Reads a file from the local workspace to review the code.
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return f"ERROR : File not found at {filepath}"
        
        return path.read_text(encoding="utf-8")
    
    except Exception as e:
        return f"ERROR: Could not read file. {str(e)}"

@tool
def run_ast_linter(filepath: str) -> str:
    """
    Runs a Python Abstract Syntax Tree(AST) linter on the file to catch syntax errors, missing parenthesis, or bad intentations
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return f"ERROR: file not found at {filepath}"
        
        code = path.read_text(encoding="utf-8")
        ast.parse(code)

        return f"SUCCESS: AST Linter passed. No Syntax errors found in {path.name}"
    
    except SyntaxError as e:
        return f"SYNTAX ERROR: {e.msg} on line {e.lineno}, offset {e.offset}"
    
    except Exception as e:
        return f"ERROR: Linter failed to execute. {str(e)}"

reviewer_tools = [read_workspace_file, run_ast_linter]