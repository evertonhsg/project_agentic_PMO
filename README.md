# AI-Powered Agentic Workflow for Project Management

An agentic workflow that turns a product specification into a complete development plan: user stories, product features and engineering tasks. Pilot input: InnovateNext Solutions' **Email Router** spec.

## Structure
```
starter/
├── phase_1/                       # Agentic toolkit + one test script per agent
│   ├── workflow_agents/base_agents.py
│   ├── direct_prompt_agent.py
│   ├── augmented_prompt_agent.py
│   ├── knowledge_augmented_prompt_agent.py
│   ├── rag_knowledge_prompt_agent.py
│   ├── evaluation_agent.py
│   ├── routing_agent.py
│   ├── action_planning_agent.py
│   └── outputs/                   # terminal output of each test run
└── phase_2/                       # Project-management workflow
    ├── workflow_agents/base_agents.py
    ├── agentic_workflow.py
    ├── Product-Spec-Email-Router.txt
    ├── reflection.md
    └── outputs/agentic_workflow_output.txt
```

## Agents (`workflow_agents/base_agents.py`)
| Agent | Role |
|---|---|
| `DirectPromptAgent` | Sends the prompt straight to `gpt-4.1-mini` (no system prompt). |
| `AugmentedPromptAgent` | Answers in a given persona. |
| `KnowledgeAugmentedPromptAgent` | Answers in a persona using **only** the supplied knowledge. |
| `RAGKnowledgePromptAgent` | Retrieval-augmented answers over chunked text (provided). |
| `EvaluationAgent` | Worker → evaluate → correct loop (up to `max_interactions`, `temperature=0`). |
| `RoutingAgent` | Routes a prompt to the best agent via `text-embedding-3-large` cosine similarity. |
| `ActionPlanningAgent` | Extracts a clean list of steps from a prompt. |

## Workflow (`phase_2/agentic_workflow.py`)
1. The `ActionPlanningAgent` breaks the TPM prompt into steps.
2. The `RoutingAgent` assigns each step to the **Product Manager**, **Program Manager** or **Development Engineer** team.
3. Each team is a knowledge agent paired with an evaluation agent that enforces the output structure.
4. A consolidated project plan is printed with labelled sections.

## Running
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
echo "OPENAI_API_KEY=your_key" > starter/phase_1/.env
cp starter/phase_1/.env starter/phase_2/.env
cd starter/phase_1 && python direct_prompt_agent.py     # ...and the other test scripts
cd ../phase_2 && python agentic_workflow.py
```
Requests go to the Vocareum OpenAI proxy by default. To use a native OpenAI key, set `OPENAI_BASE_URL=https://api.openai.com/v1`.
