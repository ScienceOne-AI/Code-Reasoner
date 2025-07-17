import os
import io
import base64
import signal
from typing import Tuple, Any
import matplotlib.pyplot as plt
import numpy as np
from utils.logger import get_logger
from utils.config_loader import load_config
from datetime import datetime
import traceback
from playwright.sync_api import sync_playwright

def draw_figure(code: str) -> str:
    """Execute Python code to draw a figure and return base64 encoded image"""
    plt.figure()
    exec(code)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def draw_figure_sync(code: str, question_id: str, image_id: str) -> str:
    """Execute Python code to draw a figure, save it to a file, and return the saved image path"""
    logger = get_logger()
    
    # Close all existing figures
    plt.close('all')
    
    try:
        # Preprocess code to ensure proper execution
        code = code.replace('plt.close()', '').replace('plt.close("all")', '')
        code = code.replace('plt.show()', '')
        if 'import matplotlib.pyplot as plt' not in code:
            code = 'import matplotlib.pyplot as plt\n' + code
        if 'import numpy as np' not in code:
            code = 'import numpy as np\n' + code
        code = code.replace('\\n', '\n')
        before_figs = set(plt.get_fignums())
        exec(code)
        after_figs = set(plt.get_fignums())
        new_fig_nums = list(after_figs - before_figs)
        if new_fig_nums:
            fig = plt.figure(new_fig_nums[-1])
        else:
            fig = plt.gcf()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_dir = os.path.join('results', 'rendered_images', str(question_id))
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"{image_id}_{timestamp}.png")
        fig.savefig(save_path)
        logger.info(f"Saved rendered image to {save_path}")
        return save_path
    except Exception as e:
        tb_str = traceback.format_exc()
        logger.error(f"Error drawing figure: {str(e)}\n{tb_str}")
        raise
    finally:
        plt.close('all') 
        
def draw_html_figure(html_code: str, question_id: str, image_id: str) -> str:
    """Execute HTML code using Playwright to draw a figure, save it to a file, and return the saved image path"""
    logger = get_logger()
    
    try:
        # Load config to get html_images path
        config = load_config('config.yml')
        html_images_path = config['output_paths']['html_images']
        
        # Create a temporary HTML file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_dir = os.path.join(html_images_path, str(question_id))
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"{image_id}_{timestamp}.png")
        
        # Use Playwright to render the HTML and take a screenshot
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # Set the HTML content directly
            page.set_content(html_code)
            # Wait for any canvas or SVG elements to render
            page.wait_for_load_state('networkidle')
            
            # Find the canvas or SVG element
            element = page.query_selector('canvas, svg')
            if element:
                # Get the bounding box of the element
                box = element.bounding_box()
                if box:
                    # Take screenshot of just the element
                    element.screenshot(path=save_path)
                else:
                    # Fallback to full page if bounding box not found
                    page.screenshot(path=save_path, full_page=True)
            else:
                # Fallback to full page if no canvas/SVG found
                page.screenshot(path=save_path, full_page=True)
            
            browser.close()
        
        logger.info(f"Saved rendered HTML image to {save_path}")
        return save_path
        
    except Exception as e:
        tb_str = traceback.format_exc()
        logger.error(f"Error rendering HTML figure: {str(e)}\n{tb_str}")
        raise

