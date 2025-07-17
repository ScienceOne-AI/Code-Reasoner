[🇨🇳 中文版 README](./README_ZH.md)

# 🧑‍🔬✨ Code-Reasoner: Multimodal Physics Agent with Code Enhancement

2nd place in ICML 2025 AI4MATH Challenge [Track 2: Physics Reasoning with Diagrams and Expressions (SeePhys)](https://www.codabench.org/competitions/7925/#/pages-tab)

## 📖 Introduction
> **More inference token is all you need**

Our goal is to squeeze pass@k accuracy into pass@1. From an optimization perspective, auto-regressive models mostly learn to match token patterns, not the underlying physics. Giving the model more inference tokens expands its guessing space and can boost pass@1 accuracy. 

## 🗝️ Key Takeaways
- Descriptive code for input images is a great way to increase context tokens for reasoning tasks. We tried LaTeX, matplotlib, and HTML code. Canvas-based HTML worked best in our tests.
- Super-resolution on blurry images helps generate better drawing code.
- Majority voting is a simple and effective way to boost inference token usage.

## 😅 Unsuccessful Attempts
- **Interactive multi-step verification**: Interactive multi-step verification like [ReAct](https://arxiv.org/abs/2210.03629) didn’t help. The model tends to self-correct in CoT anyway, and adding explicit ReAct led to repetitive confirmations without fixing real errors (like misunderstanding the question or misapplying formulas). ReAct also failed to fix drawing errors in code generation.
- **Complex task instructions**: Adding more constraints or increasing problem difficulty led to worse results. Strong reasoning models perform best with direct, simple questions.
- **Weighted multi-model voting**: Weighting models based on dev set performance didn’t generalize—10% win/loss on a subset didn’t transfer to the rest.
- **Few-shot output format templates**: Didn’t help with output format consistency.

## 🧭 Not Yet Explored Directions
- Framing problem-solving as a code generation task, using code execution for calculation or proof verification.
- Integrating a search API to retrieve similar problems or solution paths as additional context.

## 📦 About This Repo
- Easy starting point for SeePhys, supports switching between major model backends (Deepseek, Doubao, OpenAI, Gemini, Claude).
- Clean modular design—prompting, agent flow, and model calls are all decoupled for fast iteration.
- Comprehensive logging for easy error analysis and debugging.

## 🚀 Quick Start
1. Add your model API key to `config.yml`.
2. Run `main.py`.
>  We provide all HTML code for images in the `results` folder. To keep the repo size down.

## 📚 Citation

```bibtex
@misc{jiahao2025codephysics,
  author       = {Jiahao Zhao and Nan Xu and Liwei Dong},
  title        = {Multimodal Physics Agent with Code Enhancement},
  year         = {2025},
  url          = {https://github.com/ScienceOne-AI/Code-Reasoner}
}
```