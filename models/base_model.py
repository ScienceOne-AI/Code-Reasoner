from abc import ABC, abstractmethod
from typing import Dict, Any, List
from utils.logger import get_logger

class BaseModel(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger()

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

    @abstractmethod
    def generate_with_image(self, prompt: str, image_path: str) -> str:
        pass 