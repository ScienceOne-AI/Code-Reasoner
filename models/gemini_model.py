from typing import Dict, Any, List
from .base_model import BaseModel
from utils.logger import get_logger
import google.genai as genai
from google.genai import types
import time
from utils.db_logger import DBLogger

GEMINI_TIMEOUT = 10 * 60 * 1000 # 10 minutes

class GeminiModel(BaseModel):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Get API key based on agent type
        agent_type = config.get('agent_type', 'i2t')
        key_type = 'image2text' if agent_type == 'i2t' else 'selfcritic'
        self.client = genai.Client(
            api_key=config['keys'][key_type],
            http_options={"base_url": "https://aihubmix.com/gemini", "timeout": GEMINI_TIMEOUT}
        )
        self.model_name = "gemini-2.5-pro-preview-06-05"
        # self.model_name = "gemini-2.5-flash"
        self.logger = get_logger()
        self.db_logger = DBLogger()

    def generate(self, prompt: str) -> str:
        self.logger.info(f"Generating text with {self.model_name}")
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[{"text": prompt}]
        )
        result_text = response.text
        # Log the call to database
        call_id = self.db_logger.log_call(
            call_type="generate",
            input_prompt=prompt,
            content=result_text,
            model_name="gemini"
        )
        return result_text

    def generate_with_image(self, prompt: str, image_paths: List[str], max_retries: int = 5, retry_interval: float = 2.0) -> str:
        self.logger.info(f"Generating text with {self.model_name} for images: {image_paths}")
        parts = []
        image_paths = [p for p in image_paths if p is not None]
        for image_path in image_paths:
            with open(image_path, "rb") as image_file:
                img_bytes = image_file.read()
            parts.append(types.Part(
                inline_data=types.Blob(
                    data=img_bytes,
                    mime_type="image/png"
                )
            ))
        parts.append(types.Part(text=prompt))

        last_exception = None
        for attempt in range(1, max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=types.Content(parts=parts)
                )
                result_text = response.text
                # Log the call to database
                call_id = self.db_logger.log_call(
                    call_type="generate_with_image",
                    input_prompt=prompt,
                    input_images=image_paths,
                    content=result_text,
                    model_name="gemini"
                )
                return result_text
            except Exception as e:
                self.logger.warning(f"generate_with_image failed (attempt {attempt}/{max_retries}): {e}")
                last_exception = e
                if attempt < max_retries:
                    time.sleep(retry_interval)
        # 如果所有尝试都失败，抛出最后一次异常
        raise last_exception 