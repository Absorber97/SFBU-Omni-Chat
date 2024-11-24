import os
from dotenv import load_dotenv
from typing import Dict, TypedDict, List
from enum import Enum

# Load environment variables
load_dotenv()

# Type definitions for better type safety
class ModelParams(TypedDict, total=False):
    temperature: float
    max_tokens: int
    n_epochs: int
    batch_size: int
    learning_rate_multiplier: float

class ModelConfig(TypedDict):
    formatter: str
    trainer: str
    chat: str
    allowed_base_models: List[str]

class ModelType(Enum):
    FORMATTER = 'formatter'
    TRAINER = 'trainer'
    CHAT = 'chat'

# Model naming configuration
MODEL_CONFIG = {
    'base_name': 'gpt-4o-mini',
    'fine_tuned_suffix': 'sfbu-omni-tune',
    'separator': '-',
    'avatars': {
        'user': 'Bayhawk.jpeg',
        'assistant': 'SFBU.jpeg'
    }
}

# Helper function to get full model name
def get_fine_tuned_model_name(base_name: str) -> str:
    """Generate full model name with suffix"""
    if not base_name:
        base_name = MODEL_CONFIG['base_name']
    return f"{MODEL_CONFIG['fine_tuned_suffix']}"

# Default model for all services
DEFAULT_MODEL = MODEL_CONFIG['base_name']

# Centralized model configuration
OPENAI_MODELS: ModelConfig = {
    ModelType.FORMATTER.value: MODEL_CONFIG['base_name'],
    ModelType.TRAINER.value: MODEL_CONFIG['base_name'],
    ModelType.CHAT.value: MODEL_CONFIG['base_name'],
    'allowed_base_models': [
        'gpt-4',
        'gpt-4-turbo-preview',
        'gpt-3.5-turbo',
        MODEL_CONFIG['base_name']
    ]
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