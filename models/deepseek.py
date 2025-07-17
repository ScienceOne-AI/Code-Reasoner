import base64
from typing import List, Dict, Any
from volcenginesdkarkruntime import Ark
from utils.db_logger import DBLogger

class DeepSeekModel:
    def __init__(self, config):
        """Initialize the DeepSeek model."""
        self.model = Ark(
            api_key=config['keys']['ark'],
            timeout=3600.0
        )
        self.model_name = config['keys']['deepseek']
        self.db_logger = DBLogger()
    
    def generate(self, prompt: str) -> str:
        """Generate text using the Doubao model without images."""
        response = self.model.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": str(prompt)  # Ensure prompt is a string
                }
            ],
            stream=True
        )
        
        reasoning_content = ""
        content = ""
        
        with response:
            for chunk in response:
                if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                    reasoning_content += chunk.choices[0].delta.reasoning_content
                else:
                    content += chunk.choices[0].delta.content
        
        # Combine reasoning_content and content
        final_content = content
        if reasoning_content:
            final_content = reasoning_content + "\n\n" + content
        
        # Log the call to database
        call_id = self.db_logger.log_call(
            call_type="generate",
            input_prompt=prompt,
            reasoning_content=reasoning_content,
            content=content,
            model_name="doubao"
        )
        
        return final_content