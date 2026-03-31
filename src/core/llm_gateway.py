from langchain_groq import ChatGroq
from src.core.config import settings

def get_llm(persona: str = "default", temperature: float = 0.2):
    """
    Centralized LLM provider using Groq for open-weights models.
    """
    
    if not settings.groq_api_key:
        raise ValueError("CRITICAL: Groq API key is missing from the .env file.")
        
    groq_key = settings.groq_api_key.get_secret_value()
    
    # 🧠 Heavy Reasoning Models (The Thinkers)
    # Llama 3 70B is incredibly smart and great at strict JSON formatting.
    if persona in ["scientist", "architect"]:
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=temperature,
            api_key=groq_key,
            max_retries=3
        )
        
    # ⚡ Fast Execution Models (The Doers)
    # Llama 3 8B is lightning fast, perfect for code generation and review.
    elif persona in ["engineer", "reviewer"]:
        return ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=temperature,
            api_key=groq_key,
            max_retries=3
        )
        
    # Default routing
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=temperature,
        api_key=groq_key,
        max_retries=3
    )