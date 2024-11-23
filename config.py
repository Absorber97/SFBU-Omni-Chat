import os
from dotenv import load_dotenv
from typing import Dict, TypedDict
from enum import Enum

# Load environment variables
load_dotenv()

# Type definitions for better type safety
class ModelParams(TypedDict):
    temperature: float
    max_tokens: int

class ModelConfig(TypedDict):
    formatter: str
    trainer: str
    chat: str

class ModelType(Enum):
    FORMATTER = 'formatter'
    TRAINER = 'trainer'
    CHAT = 'chat'

# API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found in environment variables")

# Default model for all services
DEFAULT_MODEL = "gpt-4o-mini"

# Centralized model configuration
OPENAI_MODELS: ModelConfig = {
    ModelType.FORMATTER.value: DEFAULT_MODEL,  # For generating Q&A pairs
    ModelType.TRAINER.value: DEFAULT_MODEL,    # For fine-tuning base model
    ModelType.CHAT.value: DEFAULT_MODEL,       # For chat interface
}

# Model parameters with type safety
MODEL_PARAMS: Dict[str, ModelParams] = {
    ModelType.FORMATTER.value: {
        'temperature': 0.7,
        'max_tokens': 1000,
    },
    ModelType.TRAINER.value: {
        'temperature': 0.7,
        'max_tokens': 2000,
    },
    ModelType.CHAT.value: {
        'temperature': 0.8,
        'max_tokens': 1500,
    }
}

# Validation function
def validate_model_config() -> None:
    """Validate model configuration"""
    for model_type in ModelType:
        if model_type.value not in OPENAI_MODELS:
            raise ValueError(f"Missing model configuration for {model_type.value}")
        if model_type.value not in MODEL_PARAMS:
            raise ValueError(f"Missing parameters for {model_type.value}")

# Run validation on import
validate_model_config() 