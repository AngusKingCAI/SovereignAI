# Agents Learn Their Runtime: Interpreter Persistence as Training-Time Semantics

**Source URL:** https://arxiv.org/abs/2603.01209  
**arXiv ID:** 2603.01209  
**DOI:** https://doi.org/10.48550/arxiv.2603.01209  
**Submitted:** 1 Mar 2026 (v1), last revised 5 Mar 2026 (v2)  
**Categories:** Computer Science > Artificial Intelligence (cs.AI); Machine Learning (cs.LG)

## Authors
- Victor May
- Aaditya Salgarkar (Ontocord)
- Yishan Wang (Carnegie Mellon University)
- Diganta Misra (MPI-IS Tübingen, Tübingen AI Center, ELLIS Institute Tübingen)
- Huu Nguyen (Ontocord)

## Abstract

Tool-augmented LLMs are increasingly deployed as agents that interleave natural-language reasoning with executable Python actions, as in CodeAct-style frameworks. In deployment, these agents rely on runtime state that persists across steps. By contrast, the traces used to post-train these models rarely encode how interpreter state is managed. We ask whether interpreter persistence is merely a runtime scaffold, or a property of the training data that shapes how agents learn to use the interpreter.

We isolate state persistence as a training-time variable. We introduce Opaque Knapsack, a procedurally generated family of partially observable optimization tasks designed to prevent one-shot solutions. Item attributes and constraints are hidden behind budgeted tool calls, forcing multi-turn control flow and iterative state revision. Holding task instances, prompts, tools, model, and supervision fixed, we generate matched trajectories differing only in whether interpreter state persists across steps or resets after each action. We then fine-tune identical base models (Qwen3-8B) on each trace variant and evaluate all four train-runtime combinations.

Our 2x2 cross-evaluation shows that interpreter persistence shapes how agents reach solutions, not whether they do: solution quality is statistically indistinguishable across conditions, but token cost and stability differ substantially. A persistent-trained model in a stateless runtime triggers missing-variable errors in roughly 80% of episodes; a stateless-trained model in a persistent runtime redundantly re-derives retained state, using roughly 3.5x more tokens. Interpreter persistence should be treated as a first-class semantic of agent traces. Aligning fine-tuning data with deployment runtimes improves efficiency and reduces brittle train-runtime mismatches.

## Key Findings

### Main Results
- **Solution Quality**: No statistically significant difference in solution quality across training/runtime semantics
- **Token Efficiency**: Stateless-trained models in persistent runtimes use ~3.5x more tokens due to redundant state re-derivation
- **Error Rates**: Persistent-trained models in stateless runtimes trigger missing-variable errors in ~80% of episodes
- **Training Semantics Matter**: Interpreter persistence must be learned during training, not just implemented at runtime

### Contributions
1. **Execution semantics as a training variable**: Identified interpreter persistence as part of the agent trace contract
2. **Non-collapsible benchmark**: Introduced Opaque Knapsack with paired trace generation pipeline
3. **Evidence that persistence is learned**: Demonstrated that exposure to persistence during fine-tuning shapes state-management behavior

## Code Availability
Code is available at: https://github.com/mrcabbage972/agents-learn-runtime

## License
CC BY 4.0 (http://creativecommons.org/licenses/by/4.0/)

## Keywords
Tool-Augmented Language Models, Synthetic Training Data, Training–Inference Alignment

## Additional Sources

Content was also retrieved from multiple sources:
- Hugging Face Papers: https://huggingface.co/papers/2603.01209
- arXiv.gg: https://arxiv.gg/abs/2603.01209
- DOI: https://doi.org/10.48550/arxiv.2603.01209

The Hugging Face version provides additional markdown-formatted content with the complete paper text, including detailed methodology, experiments, and analysis beyond the abstract.