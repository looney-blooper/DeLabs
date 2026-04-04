from src.agents.architect.tools import validate_tensor_shapes

def test_pytorch_validator_success():
    """Tests if the tool successfully validates correct tensor math."""
    print("\n✅ Testing CORRECT math...")
    
    # A standard CIFAR-10 image (Batch of 1, 3 channels, 32x32 pixels)
    input_shape = "(1, 3, 32, 32)"
    
    # A valid convolution that takes 3 channels to 16
    operations = "nn.Sequential(nn.Conv2d(3, 16, kernel_size=3, padding=1), nn.MaxPool2d(2))"
    
    result = validate_tensor_shapes.invoke({"input_shape": input_shape, "operations": operations})
    print(f"Result: {result}")
    assert "SUCCESS" in result

def test_pytorch_validator_failure():
    """Tests if the tool successfully catches incorrect tensor math."""
    print("\n❌ Testing BROKEN math...")
    
    input_shape = "(1, 3, 32, 32)"
    
    # BROKEN: The input has 3 channels, but this Conv2d expects 10 channels!
    operations = "nn.Sequential(nn.Conv2d(10, 16, kernel_size=3))"
    
    result = validate_tensor_shapes.invoke({"input_shape": input_shape, "operations": operations})
    print(f"Result: {result}")
    assert "DIMENSION ERROR" in result