import os
from langchain_google_genai import ChatGoogleGenerativeAI
from config import get_settings

settings = get_settings()

def get_llm(temperature: float = 0):
    return ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.gemini_api_key,
        temperature=temperature,
        max_output_tokens=settings.max_tokens
    )