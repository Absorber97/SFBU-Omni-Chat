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

# Model naming configuration
MODEL_CONFIG = {
    'base_name': 'gpt-4o-mini',
    'fine_tuned_suffix': 'omni-sfbu',
    'separator': '-'  # Separator between base name and suffix
}

# Helper function to get full model name
def get_fine_tuned_model_name(base_name: str = None) -> str:
    """Generate full model name with suffix"""
    base = base_name or MODEL_CONFIG['base_name']
    return f"{base}{MODEL_CONFIG['separator']}{MODEL_CONFIG['fine_tuned_suffix']}"

# Default model for all services
DEFAULT_MODEL = MODEL_CONFIG['base_name']

# Centralized model configuration
OPENAI_MODELS: ModelConfig = {
    ModelType.FORMATTER.value: MODEL_CONFIG['base_name'],  # Keep gpt-4o-mini
    ModelType.TRAINER.value: None,  # Will be set dynamically from available models
    ModelType.CHAT.value: MODEL_CONFIG['base_name'],  # Keep gpt-4o-mini
}

# API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found in environment variables")

# Model parameters with type safety
MODEL_PARAMS: Dict[str, ModelParams] = {
    ModelType.FORMATTER.value: {
        'temperature': 0.7,
        'max_tokens': 1000,
    },
    ModelType.TRAINER.value: {
        'temperature': 0.7,
        'max_tokens': 2000,
        'n_epochs': 3,  # Number of training epochs
        'batch_size': 4,  # Training batch size
        'learning_rate_multiplier': 0.1  # Learning rate control
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