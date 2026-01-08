import os
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from .config import get_llm_api_key
from .errors import LLMError

def get_llm(temperature: float = 0) -> ChatOpenAI:
    """
    Get a LangChain-compatible LLM configured with OpenRouter.
    OpenRouter provides access to multiple models through an OpenAI-compatible API.
    
    Args:
        temperature: Controls randomness (0 = deterministic, 1 = more random)
                     MUST be 0 for reproducible planning and entity extraction.
    
    Returns:
        Configured ChatOpenAI instance pointing to OpenRouter
    
    Raises:
        LLMError: If API key is missing or invalid
    """
    if temperature != 0:
        raise ValueError(
            f"Jasper requires deterministic LLM (temperature=0) for planning and extraction. "
            f"Got temperature={temperature}. This is a non-negotiable requirement."
        )
    
    try:
        api_key = get_llm_api_key()  # Raises ConfigError if not set
    except Exception as e:
        raise LLMError(
            message=str(e),
            suggestion="Set OPENROUTER_API_KEY in .env file before running Jasper",
            debug_details=str(e)
        ) from e
    
    model = os.getenv("OPENROUTER_MODEL", "xiaomi/mimo-v2-flash:free")
    
    try:
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=SecretStr(api_key),
            base_url="https://openrouter.ai/api/v1",
            default_headers={"HTTP-Referer": "https://jasper.local"},
        )
    except Exception as e:
        raise LLMError(
            message=f"Failed to initialize LLM: {str(e)}",
            suggestion="Check that OPENROUTER_API_KEY is valid and model is available",
            debug_details=str(e)
        ) from e
