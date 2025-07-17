import os
import yaml
from utils.logger import get_logger

logger = get_logger()

class PromptManager:
    def __init__(self, config):
        self.config = config
        self.prompts = {}
        self._load_prompts()
        
    def _load_prompts(self):
        """Load prompts from YAML files in the prompts/templates directory."""
        templates_dir = os.path.join('prompts', 'templates')
        
        # Load i2t prompts
        i2t_dir = os.path.join(templates_dir, 'i2t')
        for lang in ['en', 'zh']:
            prompt_file = os.path.join(i2t_dir, f'{lang}.yaml')
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    self.prompts[f'i2t_{lang}'] = yaml.safe_load(f)
                    logger.info(f"Loaded i2t prompt for {lang}")
        
        # Load critic prompts
        critic_dir = os.path.join(templates_dir, 'critic')
        for lang in ['en', 'zh']:
            prompt_file = os.path.join(critic_dir, f'{lang}.yaml')
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    self.prompts[f'critic_{lang}'] = yaml.safe_load(f)
                    logger.info(f"Loaded critic prompt for {lang}")
    
    def get_prompt(self, prompt_type: str, section: str, lang: str = 'en') -> str:
        """Get a prompt template by type, section and language.
        
        Args:
            prompt_type: Type of prompt (e.g., 'i2t', 'critic')
            section: Section of the prompt (e.g., 'first_attempt', 'iteration', 'compare')
            lang: Language code ('en' or 'zh')
            
        Returns:
            The prompt template string
        """
        key = f'{prompt_type}_{lang}'
        if key not in self.prompts:
            raise ValueError(f"Prompt not found for type {prompt_type} and language {lang}")
            
        if section not in self.prompts[key]:
            raise ValueError(f"Section {section} not found in prompt type {prompt_type} for language {lang}")
            
        return self.prompts[key][section] 