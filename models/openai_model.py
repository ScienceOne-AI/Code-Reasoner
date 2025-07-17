from typing import Dict, Any, List
from .base_model import BaseModel
from utils.logger import get_logger
from openai import OpenAI
import base64

class OpenAIModel(BaseModel):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Get API key based on agent type
        agent_type = config.get('agent_type', 'i2t')
        key_type = 'image2text' if agent_type == 'i2t' else 'selfcritic'
        self.api_key = config['keys'][key_type]
        self.model_name = 'gpt-4.1'
        self.logger = get_logger()
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://aihubmix.com/v1"
        )

    def generate(self, prompt: str) -> str:
        self.logger.info(f"Generating text with OpenAI {self.model_name}")  
        response = self.client.responses.create(
            model=self.model_name,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt}
                    ]
                }
            ]
        )
        return response.output_text

    def generate_with_image(self, prompt: str, image_paths: List[str]) -> str:
        self.logger.info(f"Generating text with OpenAI {self.model_name} for images: {image_paths}")
        content = []
        # 文本
        content.append({"type": "input_text", "text": prompt})
        # 图片
        image_paths = [p for p in image_paths if p is not None]
        for image_path in image_paths:
            with open(image_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")
            content.append({
                "type": "input_image",
                "image_url": f"data:image/png;base64,{img_b64}"
            })
        response = self.client.responses.create(
            model=self.model_name,
            input=[
                {
                    "role": "user",
                    "content": content
                }
            ]
        )
        return response.output_text