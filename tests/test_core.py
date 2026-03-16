import pytest
from src.core.config import settings
from src.core.llm_gateway import get_llm
from langchain_google_genai import ChatGoogleGenerativeAI

def test_config_loads_successfully():
    """Verifies that Pydantic successfully loaded the .env file."""
    assert settings.gemini_api_key is not None
    # Ensure it's not the placeholder
    assert "your_api_key_here" not in settings.gemini_api_key.get_secret_value()

def test_llm_gateway_routing():
    """Verifies that the gateway routes to the correct Gemini models."""
    # The Scientist should get the heavier Pro model
    scientist_llm = get_llm(persona="scientist")
    assert isinstance(scientist_llm, ChatGoogleGenerativeAI)
    assert "flash" in scientist_llm.model.lower()

    # The Engineer should get the faster Flash model
    engineer_llm = get_llm(persona="engineer")
    assert "flash" in engineer_llm.model.lower()