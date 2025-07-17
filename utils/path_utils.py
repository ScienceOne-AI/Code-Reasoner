import os
from datetime import datetime
from utils.logger import get_logger
from utils.config_loader import load_config
from typing import Optional

logger = get_logger()

class PathResolver:
    @staticmethod
    def resolve_image_path(image_path: str, base_path: Optional[str] = None) -> str:
        """
        Convert a relative image path to an absolute path.
        
        Args:
            image_path: The relative image path (e.g., 'images/example.png' or 'example.png')
            base_path: Optional base path. If not provided, will use project root.
            
        Returns:
            The absolute path to the image
        """
        # Remove 'images/' prefix if it exists
        if image_path.startswith('images/'):
            image_path = image_path[7:]
        
        # Get the base path (project root) if not provided
        if base_path is None:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Construct absolute path
        absolute_path = os.path.join(base_path, 'data', 'upscaled_images', image_path)
        
        # Log the path resolution
        logger.debug(f"Resolved image path: {image_path} -> {absolute_path}")
        
        return absolute_path
    
    def get_image_code(image_path: str) -> str:
        """
        获取生成 image 的 python 代码
        返回对应的代码文件内容
        """
        # Load config to get generated_html_code path
        config = load_config('config.yml')
        generated_html_code_path = config['output_paths']['generated_html_code']
        
        image_id = image_path.split('/')[-1].split('.')[0]
        code_file = os.path.join(generated_html_code_path, f"{image_id}.html")
        if os.path.exists(code_file):
            with open(code_file, 'r') as f:
                return f.read()
        return ""

def get_public_submit_file_path(experiment_name: str = None) -> str:
    logger = get_logger()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if experiment_name:
        filename = f"{experiment_name}_{timestamp}.json"
    else:
        filename = f"results_{timestamp}.json"
    path = os.path.join('results', 'public_submit', filename)
    logger.info(f"Generated public submit file path: {path}")
    return path

