import json
import os
import yaml
import threading
import time
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.config_loader import load_config
from utils.logger import setup_logger, get_logger
from orchestrators.i2t_orchestrator import I2TOrchestrator
from orchestrators.critic_orchestrator import CriticOrchestrator
from tqdm import tqdm
from utils.path_utils import get_public_submit_file_path

def process_item(item: Dict[str, Any], critic_orchestrator: CriticOrchestrator, 
                output_path: str, lock: threading.Lock, logger) -> Dict[str, Any]:
    """Process a single item and save result safely with timeout and retry logic."""
    max_retries = 3
    timeout = 3600  # 1 hour in seconds
    retry_delay = 30  # 30 seconds between retries
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Processing item: {item['index']} (Attempt {attempt + 1}/{max_retries})")
            
            # Create a timer for timeout
            timer = threading.Timer(timeout, lambda: None)
            timer.start()
            
            try:
                result = critic_orchestrator.run(item)
                timer.cancel()  # Cancel timer if run completes successfully
            except Exception as e:
                timer.cancel()
                raise e
            
            # Safely save the result using the lock
            with lock:
                # Read existing results
                existing_results = []
                if os.path.exists(output_path):
                    try:
                        with open(output_path, 'r', encoding='utf-8') as f:
                            existing_results = json.load(f)
                    except json.JSONDecodeError:
                        logger.warning(f"Error reading existing results from {output_path}")
                
                # Add new result
                existing_results.append(result)
                
                # Save updated results
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_results, f, indent=4, ensure_ascii=False)
                
                logger.info(f"Saved result for item {item['index']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing item {item['index']} (Attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Max retries reached for item {item['index']}")
                return None
    
    return None

def resume_mode(input_data: List[Dict[str, Any]], resume_path: str):
    with open(resume_path, 'r', encoding='utf-8') as f:
        completed = json.load(f)
        completed_idx = {item['index'] for item in completed}
        return [item for item in input_data if item['index'] not in completed_idx]


def main():
    # Load configuration
    config = load_config('config.yml')
    # Load input data
    with open(config['data_paths']['final_set'], 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    
    # resume_path = 'results/public_submit/results_20250612_192043.json'
    resume_path = None # 'results/public_submit/results_20250623_195407.json'
    if resume_path:
        input_data = resume_mode(input_data, resume_path)
    
    # # # 根据指定 id 筛选 input_data，用于 debug
    # debug_ids = [
    #     444, 474, 486, 526, 471, 693, 773, 758, 774, 962,
    #     969, 1001, 1022, 1362, 1444, 1480, 1498, 1519, 1534
    # ]
    # input_data = [item for item in input_data if item['index'] in debug_ids]


    # Setup logger
    setup_logger(config.get('logging', {}))
    logger = get_logger()
    
    # Initialize orchestrators
    i2t_orchestrator = I2TOrchestrator(config)
    critic_orchestrator = CriticOrchestrator(config)
    
    # Create output directory and get output path
    output_path = get_public_submit_file_path()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create a lock for thread-safe file operations
    lock = threading.Lock()
    
    # Process items in parallel
    results = []
    max_workers = 64  # Set number of parallel workers
    if False:
        # 单线程
        for item in input_data:
            result = process_item(item, critic_orchestrator, output_path, lock, logger)
            results.append(result)
    else:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(
                    process_item, 
                    item, 
                    critic_orchestrator, 
                    output_path, 
                    lock, 
                    logger
                ): item for item in input_data
            }
            
            # Process completed tasks with progress bar
            with tqdm(total=len(future_to_item), desc="Processing items") as pbar:
                for future in as_completed(future_to_item):
                    item = future_to_item[future]
                    try:
                        result = future.result()
                        if result is not None:
                            results.append(result)
                    except Exception as e:
                        logger.error(f"Error processing item {item['index']}: {str(e)}")
                    pbar.update(1)
    
    logger.info(f"All results saved to {output_path}")

if __name__ == '__main__':
    main() 