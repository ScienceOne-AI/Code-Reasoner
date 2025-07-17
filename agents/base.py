from abc import ABC, abstractmethod
from typing import Any, Dict, List
from utils.logger import get_logger

class BaseAgent(ABC):
    def __init__(self, model, prompt_manager):
        self.model = model
        self.prompt_manager = prompt_manager
        self.logger = get_logger()
        
    @abstractmethod
    def run(self, input_data: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Run the agent's main logic"""
        pass
    
        
    def log_step(self, step_name: str, data: Dict[str, Any]):
        """Log a step in the agent's execution"""
        self.logger.info(f"Step: {step_name}", extra={
            'data': data
        }) 