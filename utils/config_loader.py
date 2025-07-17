import yaml
from typing import Dict, Any
from utils.logger import get_logger

def load_config(config_path: str) -> Dict[str, Any]:
    logger = get_logger()
    logger.info(f"Loading configuration from {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config 