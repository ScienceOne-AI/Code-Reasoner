# 🧑‍🔬✨ Code-Reasoner：通过代码增强多模态物理智能体

ICML 2025 AI4MATH 挑战赛 [Track 2: Physics Reasoning with Diagrams and Expressions (SeePhys)](https://www.codabench.org/competitions/7925/#/pages-tab) 第二名

## 📖 简介
> **More inference token is all you need**

我们的目标是将 pass@k 的准确率压缩到 pass@1。从优化的角度来看，自回归模型主要学习匹配 token 模式，而不是理解底层物理规律。给予模型更多推理 token 可以扩展其猜测空间，从而提升 pass@1 的准确率。

## 🗝️ 主要结论
- 针对输入图片生成描述性代码，是提升推理任务上下文 token 的有效方式。我们尝试了 LaTeX、matplotlib 和 HTML 代码。实验证明基于 Canvas 的 HTML 效果最佳。
- 对模糊图片进行超分辨率处理，有助于生成更好的绘图代码。
- 多数投票是一种简单有效的方式，可以提升推理 token 的利用率。

## 😅 未成功的尝试
- **交互式多步验证**：类似 [ReAct](https://arxiv.org/abs/2210.03629) 的交互式多步验证并未带来提升。模型在 CoT（思维链）中本身就有自我修正能力，显式加入 ReAct 只会导致重复确认，无法修正真正的错误（如误解题意或公式应用错误）。ReAct 也无法修正代码生成中的绘图错误。
- **复杂任务指令**：增加约束或提升题目难度反而导致效果变差。强大的推理模型在面对直接、简单的问题时表现最佳。
- **加权多模型投票**：根据开发集表现对模型加权并未泛化——在子集上提升 10% 的胜率无法迁移到整体。
- **少样本输出格式模板**：对输出格式一致性没有帮助。

## 🧭 尚未探索的方向
- 将问题求解转为化为代码生成任务，利用代码执行进行计算或证明验证。
- 集成搜索 API，检索相似问题或解题路径作为额外上下文。

## 📦 关于本仓库
- SeePhys 的便捷起点，支持主流模型后端（Deepseek、Doubao、OpenAI、Gemini、Claude）一键切换。
- 结构清晰模块化——提示词、智能体流程、模型调用全部解耦，便于快速迭代。
- 全面日志记录，便于错误分析和调试。

## 🚀 快速开始
1. 在 `config.yml` 中添加你的模型 API key。
2. 运行 `main.py`。
>  我们在 `results` 文件夹中提供了所有图片的 HTML 代码，以减小仓库体积。

## 📚 引用

```bibtex
@misc{jiahao2025codephysics,
  author       = {Jiahao Zhao and Nan Xu and Liwei Dong},
  title        = {Multimodal Physics Agent with Code Enhancement},
  year         = {2025},
  url          = {https://github.com/ScienceOne-AI/Code-Reasoner}
}
``` 