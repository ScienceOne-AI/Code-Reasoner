import os
import json
from datetime import datetime
from typing import Dict, Any
from .base_orchestrator import BaseOrchestrator
from utils.logger import get_logger
from agents.critic_agent import CriticAgent
from models.model_factory import ModelFactory
from prompts.prompt_manager import PromptManager

logger = get_logger()

class CriticOrchestrator(BaseOrchestrator):
    def __init__(self, config: Dict[str, Any]):
        """Initialize the critic orchestrator."""
        super().__init__(config)
        self.model = ModelFactory.create_model(config, agent_type='critic')
        self.prompt_manager = PromptManager(config)
        self.agent = CriticAgent(self.model, self.prompt_manager)
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logger.info("Initialized critic orchestrator")
        
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the critic process."""
        self.logger.info(f"Running critic process for question {input_data['index']}")
        # Do not get prompt here; let agent handle prompt retrieval
        result = self.agent.run(input_data)
        self.logger.info(f"Critic orchestrator completed for item {input_data['index']}")
        return result
        
    def _load_image_code(self, question_id: str, image_id: str) -> str:
        """Load generated Python code for image"""
        code_path = os.path.join(
            self.base_path,
            'results',
            'image_pycode',
            question_id,
            f"{image_id}.py"
        )
        
        with open(code_path, 'r') as f:
            return f.read()
            
    def _save_feedback(self, question_id: str, image_id: str, feedback: str):
        """Save critic feedback"""
        feedback_path = os.path.join(
            self.base_path,
            'results',
            'image_pycode',
            question_id,
            'feedback.json'
        )
        
        feedback_data = {
            'image_id': image_id,
            'feedback': feedback,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(feedback_path, 'w') as f:
            json.dump(feedback_data, f, indent=2) 