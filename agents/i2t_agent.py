import re
import os
from typing import Dict, Any, List, Tuple
from .base import BaseAgent
from utils.drawing import draw_figure_sync, draw_html_figure
from utils.path_utils import PathResolver
from utils.config_loader import load_config
import traceback

class I2TAgent(BaseAgent):
    def __init__(self, model, prompt_manager):
        super().__init__(model, prompt_manager)
        self.max_iterations = 1

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        iteration = 1
        
        # Get language for prompts
        lang = 'en' if input_data['language'] == 'English' else 'zh'
        
        for image_path in input_data['image_path']:
            while iteration <= self.max_iterations:
                self.logger.info(f"Iteration {iteration} for item {input_data['index']}")
                # Get image path
                resolved_path = PathResolver.resolve_image_path(image_path)
                image_id = image_path.split('/')[-1].split('.')[0]  # e.g., "images/460_0.png" -> "460_0"
                
                generate_prompt = self.prompt_manager.get_prompt('i2t', 'generate', lang=lang).format(
                    question=input_data['question'],
                    img_type=input_data['img_category']
                )
                self.logger.info(f"[LLM INPUT] prompt (generation):\n{generate_prompt}\nimages: { [resolved_path] }")
                response = self.model.generate_with_image(generate_prompt, [resolved_path])
                self.logger.info(f"[LLM OUTPUT] response (generation):\n{response}")
                code = self._extract_code(response, image_id)
                if code:
                    try:
                        rendered_image_path = draw_html_figure(code, input_data['index'], image_id)
                    except Exception as e:
                        tb_str = traceback.format_exc()
                        self.logger.error(f"Drawing failed for image {image_id}: {e}\n{tb_str}")
                        continue
                else:
                    continue
                # identical_prompt = self.prompt_manager.get_prompt('i2t', 'identical', lang=lang)
                # self.logger.info(f"[LLM INPUT] prompt (identical):\n{identical_prompt}\nimages: { [resolved_path, rendered_image_path]}")
                # identical_response = self.model.generate_with_image(identical_prompt, [resolved_path, rendered_image_path])
                # self.logger.info(f"[LLM OUTPUT] response (identical):\n{identical_response}")
                
                # is_identical = identical_response.strip().lower() == "identical"
                
                # if is_identical:
                #     self.logger.info(f"Image {image_id} is identical after {iteration} iterations")
                #     break
                
                iteration += 1
        
        return {'status': 'finished'}

    def _extract_code(self, response: str, image_id: str) -> str:
        """Extract Python code from model response and save it to a file"""
        pattern = r"```html\n(.*?)\n```"
        match = re.search(pattern, response, re.DOTALL)
        if not match:
            return None
            
        code = match.group(1)
        
        # Load config to get generated_html_code path
        config = load_config('config.yml')
        generated_html_code_path = config['output_paths']['generated_html_code']
        
        # Save code to file
        save_dir = generated_html_code_path
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"{image_id}.html")
        
        with open(save_path, 'w') as f:
            f.write(code)
        self.logger.info(f"Saved generated code to {save_path}")
        
        return code 