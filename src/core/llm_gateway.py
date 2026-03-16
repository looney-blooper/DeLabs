from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from src.core.config import settings


def get_llm(persona : str = "default", temperature : float = 0.2):
    """
    Centralized LLM Provider
    Routes to LLM based on the Agents Call
    """

    gemini_api_key = settings.gemini_api_key.get_secret_value()

    if persona in ["archeitect", "scientist"]:
        return ChatGoogleGenerativeAI(
            model = "gemini-2.5-flash",
            temperature = temperature,
            google_api_key = gemini_api_key,
            max_retries = 3,
        )
    
    elif persona in ["engineer", "reviewer"]:
        return ChatGoogleGenerativeAI(
            model = "gemini-2.5-flash",
            temperature = temperature,
            google_api_key = gemini_api_key,
            max_retries = 3,
        )

    return ChatGoogleGenerativeAI(
            model = "gemini-2.5-flash",
            temperature = temperature,
            google_api_key = gemini_api_key,
            max_retries = 3,
        )

def get_fallback_llm(temperature : float = 0.2):
    """
    If gemini hits rate limit,  system fallback to groq
    """

    if not settings.groq_api_key:
        raise ValueError("Groq API KEY is not configered.")
    
    return ChatGroq(
        model = "llama3-70b-8192",
        temperature = temperature,
        api_key = settings.groq_api_key,
        max_retries = 3,
    )
