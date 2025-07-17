from typing import Dict, Any
from utils.logger import get_logger
from .gemini_model import GeminiModel
from .doubao_model import DoubaoModel
from .openai_model import OpenAIModel
from .claude_model import ClaudeModel
from .deepseek import DeepSeekModel

class ModelFactory:
    @staticmethod
    def create_model(config: Dict[str, Any], agent_type: str = 'i2t'):
        logger = get_logger()
        model_type = config['model']['type']
        config['agent_type'] = agent_type
        
        if model_type == 'gemini':
            logger.info("Creating Gemini model")
            return GeminiModel(config)
        elif model_type == 'doubao':
            logger.info("Creating Doubao model")
            return DoubaoModel(config)
        elif model_type == 'openai':
            logger.info("Creating OpenAI model")
            return OpenAIModel(config)
        elif model_type == 'claude':
            logger.info("Creating Claude model")
            return ClaudeModel(config)
        elif model_type == 'deepseek':
            logger.info("Creating DeepSeek model")
            return DeepSeekModel(config)
        else:
            raise ValueError(f"Unknown model type: {model_type}") 