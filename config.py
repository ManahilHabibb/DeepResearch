import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the application"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Search Configuration
    MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    SEARCH_TIMEOUT = int(os.getenv("SEARCH_TIMEOUT", "30"))
    
    # CrewAI Configuration
    CREWAI_VERBOSE = os.getenv("CREWAI_VERBOSE", "false").lower() == "true"
    CREWAI_DEBUG = os.getenv("CREWAI_DEBUG", "false").lower() == "true"
    
    # Ollama Configuration
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    
    # Application Settings
    APP_TITLE = "🔍 AI Research Assistant"
    APP_ICON = "🔍"
    
    @classmethod
    def has_openai_key(cls) -> bool:
        """Check if OpenAI API key is configured"""
        return cls.OPENAI_API_KEY is not None and cls.OPENAI_API_KEY.strip() != ""
    
    @classmethod
    def get_llm_config(cls) -> dict:
        """Get LLM configuration based on available options"""
        if cls.has_openai_key():
            return {
                "provider": "openai",
                "api_key": cls.OPENAI_API_KEY,
                "model": "gpt-3.5-turbo"
            }
        else:
            return {
                "provider": "ollama",
                "base_url": cls.OLLAMA_HOST,
                "model": cls.OLLAMA_MODEL
            }