from typing import Dict, Any, List
from abc import ABC, abstractmethod
from utils.logger import get_logger

class BaseOrchestrator(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger()
        
    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the orchestration process"""
        pass
        
    def validate(self, result: Dict[str, Any]) -> bool:
        """Validate the orchestration result"""
        return True
        
    def log_step(self, step_name: str, data: Dict[str, Any] = None):
        """Log a step in the orchestration process"""
        if data is None:
            data = {}
        self.logger.log_step(step_name, data) 