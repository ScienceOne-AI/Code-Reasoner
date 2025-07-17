import os
import json
from datetime import datetime
from typing import Dict, Any
from .base_orchestrator import BaseOrchestrator
from utils.logger import get_logger
from agents.i2t_agent import I2TAgent
from models.model_factory import ModelFactory
from prompts.prompt_manager import PromptManager

logger = get_logger()

class I2TOrchestrator(BaseOrchestrator):
    def __init__(self, config: Dict[str, Any]):
        """Initialize the I2T orchestrator."""
        super().__init__(config)
        self.model = ModelFactory.create_model(config, agent_type='i2t')
        self.prompt_manager = PromptManager(config)
        self.agent = I2TAgent(self.model, self.prompt_manager)
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logger.info("Initialized I2T orchestrator")
        
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the I2T process."""
        self.logger.info(f"Running I2T process for question {input_data['index']}")
        
        # Run the agent
        result = self.agent.run(input_data)
        self.logger.info(f"I2T orchestrator completed for item {input_data['index']}")
        return result
        
    def _save_pycode(self, question_id: str, image_id: str, code: str):
        """Save generated Python code to file"""
        base_path = os.path.join(self.base_path, 'results', 'image_pycode', question_id)
        os.makedirs(base_path, exist_ok=True)
        
        # Save code
        code_path = os.path.join(base_path, f"{image_id}.py")
        with open(code_path, 'w') as f:
            f.write(code)
            
        # Update metadata
        metadata_path = os.path.join(base_path, 'metadata.json')
        metadata = {
            'question_id': question_id,
            'image_id': image_id,
            'timestamp': datetime.now().isoformat()
        }
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    def run_sync(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        同步处理单个数据项
        """
        try:
            # 运行代理
            result = self.agent.run(item)
            return result
            
        except Exception as e:
            self.logger.error(f"Error in I2T orchestrator: {str(e)}")
            raise 