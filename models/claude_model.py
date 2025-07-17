from typing import Dict, Any, List
from .base_model import BaseModel
from utils.logger import get_logger
import anthropic
import base64
import os
import time

class ClaudeModel(BaseModel):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Get API key based on agent type
        agent_type = config.get('agent_type', 'i2t')
        key_type = 'image2text' if agent_type == 'i2t' else 'selfcritic'
        self.api_key = config['keys'][key_type]
        self.model_name = 'claude-sonnet-4-20250514'
        self.logger = get_logger()
        self.client = anthropic.Anthropic(
            api_key=self.api_key,
            base_url="https://aihubmix.com"
        )

    def generate(self, prompt: str, max_retries: int = 3, retry_delay: int = 20) -> str:
        self.logger.info(f"Generating text with Claude: {self.model_name}")
        for attempt in range(1, max_retries + 1):
            try:
                with self.client.messages.stream(
                    model=self.model_name,
                    max_tokens=32768,
                    messages=[{"role": "user", "content": prompt}]
                ) as stream:
                    content = ""
                    for text in stream.text_stream:
                        content += text
                    return content
            except Exception as e:
                self.logger.error(f"Claude generate attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    self.logger.error("Max retries reached for Claude generate.")
                    raise

    def generate_with_image(self, prompt: str, image_paths: List[str], max_retries: int = 3, retry_delay: int = 20) -> str:
        self.logger.info(f"Generating text with {self.model_name} for images: {image_paths}")
        content = []
        image_paths = [p for p in image_paths if p is not None]
        for image_path in image_paths:
            if not os.path.isfile(image_path) or not image_path.lower().endswith('.png'):
                raise ValueError(f"Only local PNG files are supported, got: {image_path}")
            with open(image_path, "rb") as f:
                image_data = base64.standard_b64encode(f.read()).decode("utf-8")
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": image_data,
                }
            })
        content.append({
            "type": "text",
            "text": prompt
        })
        for attempt in range(1, max_retries + 1):
            try:
                with self.client.messages.stream(
                    model=self.model_name,
                    max_tokens=32768,
                    messages=[
                        {
                            "role": "user",
                            "content": content
                        }
                    ]
                ) as stream:
                    result = ""
                    for text in stream.text_stream:
                        result += text
                    return result
            except Exception as e:
                self.logger.error(f"Claude generate_with_image attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    self.logger.error("Max retries reached for Claude generate_with_image.")
                    raise
