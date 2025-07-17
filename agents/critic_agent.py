import logging
from typing import Dict, Any, List
from .base import BaseAgent
from utils.logger import get_logger
from utils.path_utils import PathResolver
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# Subject and level mapping
SUBJECT_MAP_EN = {
    "CM": "Classical Mechanics: The study of motion and forces on macroscopic objects, from linear motion, circular motion, projectile to planetary orbits.",
    "EM": "Electromagnetism: Examines electric/magnetic fields and their interactions with matter, covering RC circuits to Maxwell's equations.",
    "ACG": "Astrophysics, Cosmology & Gravitation: Investigates celestial phenomena, universe evolution, and gravitational interactions at all scales.",
    "OPT": "Optics: Focuses on light behavior (reflection/refraction) and its applications in lenses, lasers, and optical technologies, this section also covers wave-related physics of acoustics.",
    "AMONP": "Atomic, Molecular, Nuclear & Particle Physics: Studies fundamental particles and their interactions, spanning quarks to complex nuclei. It also contains emergent properties of solids/liquids and novel material design.",
    "QMIT": "Quantum Mechanics, Information & Technology: Explores quantum systems for computing and communication applications.",
    "TSM": "Thermodynamics & Statistical Mechanics: Analyzes energy transfer and microscopic behavior of particle ensembles."
}

SUBJECT_MAP_ZH = {
    "CM": "经典力学：研究宏观物体的运动和力，从线性运动、圆周运动、抛体运动到行星轨道。",
    "EM": "电磁学：研究电场/磁场及其与物质的相互作用，涵盖RC电路到麦克斯韦方程。",
    "ACG": "天体物理、宇宙学和引力：研究天体现象、宇宙演化和各种尺度的引力相互作用。",
    "OPT": "光学：研究光的行为（反射/折射）及其在透镜、激光和光学技术中的应用，本节还包括声学的波动相关物理。",
    "AMONP": "原子、分子、核和粒子物理：研究基本粒子及其相互作用，从夸克到复杂原子核。还包括固体/液体的涌现性质和新型材料设计。",
    "QMIT": "量子力学、信息与技术：探索量子系统在计算和通信中的应用。",
    "TSM": "热力学与统计力学：分析能量传递和粒子集合的微观行为。"
}

LEVEL_MAP_EN = {
    1: "Middle school",
    2: "High school",
    3: "Beginner Olympiad",
    4: "Advanced Olympiad",
    5: "Undergraduate",
    6: "Senior undergraduate",
    7: "Master's",
    8: "PhD qualifying exams"
}

LEVEL_MAP_ZH = {
    1: "初中水平",
    2: "高中水平",
    3: "初级奥赛",
    4: "高级奥赛",
    5: "本科水平",
    6: "高年级本科",
    7: "硕士水平",
    8: "博士资格考试"
}

def build_meta_info(input_data: dict) -> str:
    """Build meta information string based on input data and language."""
    language = input_data.get('language', 'English')
    subject_map = SUBJECT_MAP_ZH if language == 'Chinese' else SUBJECT_MAP_EN
    level_map = LEVEL_MAP_ZH if language == 'Chinese' else LEVEL_MAP_EN
    
    subject = subject_map.get(input_data.get('subject', ''), '')
    level = level_map.get(input_data.get('level', 0), '')
    sig_figs = input_data.get('sig_figs', '')
    vision_relevance = input_data.get('vision_relevance', '')
    
    if language == 'Chinese':
        if sig_figs:
            return f"难度：{level}\n有效数字：{sig_figs}\n"
        else:
            return f"难度：{level}\n"
    else:
        if sig_figs:
            return f"Level: {level}\nSignificant Figures: {sig_figs}"
        else:
            return f"Level: {level}"

def build_roll_out_responses(roll_out_solutions: List[str]) -> str:
    roll_out_responses = ""
    for i, solution in enumerate(roll_out_solutions):
        roll_out_responses += f"## roll_out_{i}\n{solution}\n"
    return roll_out_responses   

class CriticAgent(BaseAgent):
    def __init__(self, model, prompt_manager):
        super().__init__(model, prompt_manager)
        self.logger = get_logger()

    def _generate_single_roll_out(self, generate_prompt: str, resolved_paths: List[str], i: int) -> str:
        """Generate a single roll_out solution"""
        self.logger.info(f"[LLM INPUT] prompt (generate) for roll_out_{i}:\n{generate_prompt}")
        roll_out_solution = self.model.generate(generate_prompt)
        self.logger.info(f"[LLM OUTPUT] solution (generate) for roll_out_{i}:\n{roll_out_solution}")
        return roll_out_solution

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the critic agent workflow:
        1. First attempt to solve
        2. Critic analysis
        3. Check if solution is correct
        4. If not correct, iterate up to 3 times
        5. Final significant figures check (if sig_figs is provided)
        """
        self.logger.info(f"Running CriticAgent for item {input_data['index']}")
        roll_out_num = 3
        # Setup language and metadata
        lang = 'en' if input_data['language'] == 'English' else 'zh'
        meta_info = build_meta_info(input_data)
        sig_figs = input_data.get('sig_figs', '')
        # Get image codes for all images
        image_codes = [PathResolver.get_image_code(p) for p in input_data['image_path']]
        image_code_str = "\n\n".join(image_codes)
        
        question = input_data['question']

        # 1. First attempt
        generate_prompt = self.prompt_manager.get_prompt('critic', 'generate', lang=lang).format(
            question=question,
            image_code=image_code_str,
            meta_info=meta_info
        )
        
        resolved_paths = [PathResolver.resolve_image_path(p) for p in input_data['image_path']]
        
        # 并发执行 roll_out
        roll_out_solutions = []
        with ThreadPoolExecutor(max_workers=roll_out_num) as executor:
            # 提交所有任务
            future_to_index = {
                executor.submit(self._generate_single_roll_out, generate_prompt, resolved_paths, i): i 
                for i in range(roll_out_num)
            }
            
            # 收集结果，保持顺序
            temp_results = [None] * roll_out_num
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    temp_results[index] = result
                except Exception as exc:
                    self.logger.error(f"Roll_out {index} generated an exception: {exc}")
                    temp_results[index] = f"Error in roll_out_{index}: {exc}"
            
            # 确保所有结果都按顺序排列
            roll_out_solutions = [result for result in temp_results if result is not None]
        
        roll_out_responses = build_roll_out_responses(roll_out_solutions)
        self_consistency_prompt = self.prompt_manager.get_prompt('critic', 'self_consistency', lang=lang).format(
            roll_out_responses=roll_out_responses,
            question=question
        )
        self.logger.info(f"[LLM INPUT] prompt (self_consistency):\n{self_consistency_prompt}")
        self_consistency_solution = self.model.generate(self_consistency_prompt)
        self.logger.info(f"[LLM OUTPUT] solution (self_consistency):\n{self_consistency_solution}")
        
        return {
            "index": input_data['index'],
            "question": question,
            "subject": input_data['subject'],
            "img_category": input_data['img_category'],
            "vision_relevance": input_data['vision_relevance'],
            "language": input_data['language'],
            "level": input_data['level'],
            "sig_figs": input_data['sig_figs'],
            "caption": input_data['caption'],
            "prediction": self_consistency_solution
        }
