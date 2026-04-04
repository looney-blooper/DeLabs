import subprocess
import tempfile
import os
import sys

from langchain_core.tools import tool

@tool
def validate_tensor_shapes(input_shape: str, operations: str) -> str:
    """
    Validates tensor dimensions by running a dry-pass through PyTorch.
    - input_shape: A tuple string, e.g., "(1, 3, 32, 32)"
    - operations: Valid PyTorch nn.Sequential code, e.g., "nn.Sequential(nn.Conv2d(3, 16, 3), nn.Flatten())"
    """
    # We dynamically generate a PyTorch script to test the AI's math
    script_content = f"""
import torch
import torch.nn as nn

try:
    # 1. Create a dummy input tensor based on the AI's shape
    x = torch.randn({input_shape})
    
    # 2. Instantiate the layers the AI designed
    model = {operations}
    
    # 3. Push the tensor through the model
    out = model(x)
    
    # 4. Success! Print the final shape
    print(f"SUCCESS: Dimensions align. Final output shape is {{tuple(out.shape)}}")
    
except Exception as e:
    # If the math is wrong, PyTorch catches it here
    print(f"DIMENSION ERROR: {{str(e)}}")
"""
    try:
        # Create a temporary file to safely execute the script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            temp_path = f.name

        # Run the script in an isolated subprocess
        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=5
        )

        os.remove(temp_path) # Clean up the temp file

        # Return whatever PyTorch printed (either the success shape or the error)
        if result.stdout:
            return result.stdout.strip()
        else:
            return f"EXECUTION FAILED: {result.stderr.strip()}"

    except Exception as e:
        return f"SYSTEM ERROR: Could not run validation. {str(e)}"

architect_tools = [validate_tensor_shapes]