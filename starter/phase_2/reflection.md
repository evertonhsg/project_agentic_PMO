# Reflection: Agentic Workflow for Technical Project Management

## Strengths
- **Reusable building blocks.** Every agent in `workflow_agents/base_agents.py` is generic (persona, knowledge and criteria are injected), so the same library can plan any product by swapping the spec and prompts.
- **Self-correcting output.** Each specialist team pairs a worker (`KnowledgeAugmentedPromptAgent`) with an `EvaluationAgent`. Responses that miss the required structure (user-story template, feature template, task template) are sent back with correction instructions until they pass, which gives consistent output quality.
- **Dynamic orchestration.** The `ActionPlanningAgent` derives the steps from the TPM's request and the `RoutingAgent` assigns each one by semantic similarity, so the flow adapts to the prompt instead of being a hard-coded pipeline.
- **Robustness.** Each step runs inside error handling, so one failed API call is logged without losing the rest of the plan. The final output is assembled into labelled sections (User Stories, Product Features, Engineering Tasks).

## Limitations
- **No hand-off between steps.** Each step is routed on its own, so the Program Manager never sees the stories the Product Manager actually wrote, and tasks reference story IDs that the agent invented (e.g. `US-01`). Several steps also produce overlapping or duplicate artifacts.
- **Routing on short step text.** Some steps such as "Specify the desired outcomes for each action" have low similarity to every route (≈0.23) and can be routed to an unexpected team.
- **Evaluator leniency and cost.** A Yes/No LLM judgement can accept near-misses (e.g. Markdown-bolded labels), and every refinement loop adds several API calls and more latency.
- **Non-determinism.** Even at `temperature=0` the number and wording of planned steps vary between runs.

## Suggested improvement
Add a **shared workflow context (blackboard)**. Store every validated output in a context object and pass the relevant prior artifacts into each support function: the user stories to the Program Manager, and the stories plus features to the Development Engineer. Features and tasks would then be derived from, and traceable to, the stories actually generated, with consistent IDs. A deduplication/merge step at the end would also remove overlap between steps.
