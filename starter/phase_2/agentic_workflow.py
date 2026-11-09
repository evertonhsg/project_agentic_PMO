# agentic_workflow.py
"""
General-purpose agentic workflow for technical project management.

Pipeline:
    1. An ActionPlanningAgent breaks the TPM's high-level request into sub-tasks.
    2. A RoutingAgent sends each sub-task to the best-matching specialist team
       (Product Manager, Program Manager, Development Engineer).
    3. Each team is a KnowledgeAugmentedPromptAgent (worker) paired with an
       EvaluationAgent that iteratively checks and refines the worker's output.
    4. The results are assembled into one consolidated project plan.

Pilot input: Product-Spec-Email-Router.txt
"""

# TODO: 1 - Import the following agents: ActionPlanningAgent, KnowledgeAugmentedPromptAgent, EvaluationAgent, RoutingAgent from the workflow_agents.base_agents module
from workflow_agents.base_agents import (
    ActionPlanningAgent,
    KnowledgeAugmentedPromptAgent,
    EvaluationAgent,
    RoutingAgent,
)

import os
import logging
from dotenv import load_dotenv

# Basic logging so failures in an individual step are reported without aborting the whole run.
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("agentic_workflow")
logging.getLogger("httpx").setLevel(logging.WARNING)  # hide per-request HTTP logs

# Directory of this script, so the workflow can be launched from any working directory.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# TODO: 2 - Load the OpenAI key into a variable called openai_api_key
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise SystemExit("OPENAI_API_KEY is not set. Add it to a .env file next to this script.")

# load the product spec
# TODO: 3 - Load the product spec document Product-Spec-Email-Router.txt into a variable called product_spec
with open(os.path.join(SCRIPT_DIR, "Product-Spec-Email-Router.txt"), "r", encoding="utf-8") as spec_file:
    product_spec = spec_file.read()

# Maximum refinement rounds each evaluation agent may run.
MAX_EVAL_INTERACTIONS = 10

# Instantiate all the agents

# Action Planning Agent
knowledge_action_planning = (
    "Stories are defined from a product spec by identifying a "
    "persona, an action, and a desired outcome for each story. "
    "Each story represents a specific functionality of the product "
    "described in the specification. \n"
    "Features are defined by grouping related user stories. \n"
    "Tasks are defined for each story and represent the engineering "
    "work required to develop the product. \n"
    "A development Plan for a product contains all these components"
)
# TODO: 4 - Instantiate an action_planning_agent using the 'knowledge_action_planning'
action_planning_agent = ActionPlanningAgent(openai_api_key, knowledge_action_planning)

# Product Manager - Knowledge Augmented Prompt Agent
persona_product_manager = "You are a Product Manager, you are responsible for defining the user stories for a product."
knowledge_product_manager = (
    "Stories are defined by writing sentences with a persona, an action, and a desired outcome. "
    "The sentences always start with: As a "
    "Write several stories for the product spec below, where the personas are the different users of the product. "
    # TODO: 5 - Complete this knowledge string by appending the product_spec loaded in TODO 3
    f"{product_spec}"
)
# TODO: 6 - Instantiate a product_manager_knowledge_agent using 'persona_product_manager' and the completed 'knowledge_product_manager'
product_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key, persona_product_manager, knowledge_product_manager
)

# Product Manager - Evaluation Agent
# TODO: 7 - Define the persona and evaluation criteria for a Product Manager evaluation agent and instantiate it as product_manager_evaluation_agent. This agent will evaluate the product_manager_knowledge_agent.
# The evaluation_criteria should specify the expected structure for user stories (e.g., "As a [type of user], I want [an action or feature] so that [benefit/value].").
persona_product_manager_eval = "You are an evaluation agent that checks the answers of other worker agents"
evaluation_criteria_product_manager = (
    "The answer should be stories that follow the following structure: "
    "As a [type of user], I want [an action or feature] so that [benefit/value]."
)
product_manager_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_product_manager_eval,
    evaluation_criteria=evaluation_criteria_product_manager,
    worker_agent=product_manager_knowledge_agent,  # agent_to_evaluate
    max_interactions=MAX_EVAL_INTERACTIONS,
)

# Program Manager - Knowledge Augmented Prompt Agent
persona_program_manager = "You are a Program Manager, you are responsible for defining the features for a product."
knowledge_program_manager = "Features of a product are defined by organizing similar user stories into cohesive groups."
# Ground the Program Manager team in the same product spec so that features are specific to the
# product being planned (without it, the agent only sees the step text and invents generic features).
knowledge_program_manager += f" Define the features for the product spec below.\n{product_spec}"
# Instantiate a program_manager_knowledge_agent using 'persona_program_manager' and 'knowledge_program_manager'
# (This is a necessary step before TODO 8. Students should add the instantiation code here.)
program_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key, persona_program_manager, knowledge_program_manager
)

# Program Manager - Evaluation Agent
persona_program_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."

# TODO: 8 - Instantiate a program_manager_evaluation_agent using 'persona_program_manager_eval' and the evaluation criteria below.
evaluation_criteria_program_manager = (
    "The answer should be product features that follow the following structure: "
    "Feature Name: A clear, concise title that identifies the capability\n"
    "Description: A brief explanation of what the feature does and its purpose\n"
    "Key Functionality: The specific capabilities or actions the feature provides\n"
    "User Benefit: How this feature creates value for the user"
)
program_manager_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_program_manager_eval,
    evaluation_criteria=evaluation_criteria_program_manager,
    worker_agent=program_manager_knowledge_agent,  # agent_to_evaluate
    max_interactions=MAX_EVAL_INTERACTIONS,
)

# Development Engineer - Knowledge Augmented Prompt Agent
persona_dev_engineer = "You are a Development Engineer, you are responsible for defining the development tasks for a product."
knowledge_dev_engineer = "Development tasks are defined by identifying what needs to be built to implement each user story."
# Ground the Development Engineer team in the product spec for the same reason as above.
knowledge_dev_engineer += f" Define the development tasks for the product spec below.\n{product_spec}"
# Instantiate a development_engineer_knowledge_agent using 'persona_dev_engineer' and 'knowledge_dev_engineer'
# (This is a necessary step before TODO 9. Students should add the instantiation code here.)
development_engineer_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key, persona_dev_engineer, knowledge_dev_engineer
)

# Development Engineer - Evaluation Agent
persona_dev_engineer_eval = "You are an evaluation agent that checks the answers of other worker agents."
# TODO: 9 - Instantiate a development_engineer_evaluation_agent using 'persona_dev_engineer_eval' and the evaluation criteria below.
evaluation_criteria_dev_engineer = (
    "The answer should be tasks following this exact structure: "
    "Task ID: A unique identifier for tracking purposes\n"
    "Task Title: Brief description of the specific development work\n"
    "Related User Story: Reference to the parent user story\n"
    "Description: Detailed explanation of the technical work required\n"
    "Acceptance Criteria: Specific requirements that must be met for completion\n"
    "Estimated Effort: Time or complexity estimation\n"
    "Dependencies: Any tasks that must be completed first"
)
development_engineer_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_dev_engineer_eval,
    evaluation_criteria=evaluation_criteria_dev_engineer,
    worker_agent=development_engineer_knowledge_agent,  # agent_to_evaluate
    max_interactions=MAX_EVAL_INTERACTIONS,
)


# Job function persona support functions
# TODO: 11 - Define the support functions for the routes of the routing agent (e.g., product_manager_support_function, program_manager_support_function, development_engineer_support_function).
# Each support function:
#   1. Takes the input query (a step from the action plan).
#   2. Calls the evaluate() method of the matching EvaluationAgent with the step itself
#      (the EvaluationAgent invokes its own worker agent internally).
#   3. Returns the value stored under 'final_response'.
# The results are also recorded per role in `plan_sections` so a consolidated plan can be printed.

USER_STORIES = "User Stories"
PRODUCT_FEATURES = "Product Features"
ENGINEERING_TASKS = "Engineering Tasks"
plan_sections = {USER_STORIES: [], PRODUCT_FEATURES: [], ENGINEERING_TASKS: []}


def product_manager_support_function(query):
    """Product Manager team: generate and validate user stories for the given step."""
    result = product_manager_evaluation_agent.evaluate(query)
    plan_sections[USER_STORIES].append(result["final_response"])
    return result["final_response"]


def program_manager_support_function(query):
    """Program Manager team: generate and validate product features for the given step."""
    result = program_manager_evaluation_agent.evaluate(query)
    plan_sections[PRODUCT_FEATURES].append(result["final_response"])
    return result["final_response"]


def development_engineer_support_function(query):
    """Development Engineer team: generate and validate engineering tasks for the given step."""
    result = development_engineer_evaluation_agent.evaluate(query)
    plan_sections[ENGINEERING_TASKS].append(result["final_response"])
    return result["final_response"]


# Routing Agent
# TODO: 10 - Instantiate a routing_agent. You will need to define a list of agent dictionaries (routes) for Product Manager, Program Manager, and Development Engineer. Each dictionary should contain 'name', 'description', and 'func' (linking to a support function). Assign this list to the routing_agent's 'agents' attribute.
routing_agent = RoutingAgent(openai_api_key, [])
routes = [
    {
        "name": "Product Manager",
        "description": (
            "Responsible for defining product personas and user stories only. "
            "Does not define features or tasks. Does not group stories"
        ),
        "func": lambda x: product_manager_support_function(x),
    },
    {
        "name": "Program Manager",
        "description": (
            "Responsible for defining product features by grouping related user stories. "
            "Does not define user stories or development tasks"
        ),
        "func": lambda x: program_manager_support_function(x),
    },
    {
        "name": "Development Engineer",
        "description": (
            "Responsible for defining the development and engineering tasks needed to implement "
            "each user story. Does not define user stories or features"
        ),
        "func": lambda x: development_engineer_support_function(x),
    },
]
routing_agent.agents = routes


# Run the workflow

print("\n*** Workflow execution started ***\n")
# Workflow Prompt
# ****
workflow_prompt = "What would the development tasks for this product be?"
# ****
print(f"Task to complete in this workflow, workflow prompt = {workflow_prompt}")

print("\nDefining workflow steps from the workflow prompt")
# TODO: 12 - Implement the workflow.
#   1. Use the 'action_planning_agent' to extract steps from the 'workflow_prompt'.
#   2. Initialize an empty list to store 'completed_steps'.
#   3. Loop through the extracted workflow steps:
#      a. For each step, use the 'routing_agent' to route the step to the appropriate support function.
#      b. Append the result to 'completed_steps'.
#      c. Print information about the step being executed and its result.
#   4. After the loop, print a single consolidated project plan with labelled sections.
try:
    workflow_steps = action_planning_agent.extract_steps_from_prompt(workflow_prompt)
except Exception as exc:  # e.g. network error / API timeout
    logger.error("Action planning failed: %s", exc)
    raise SystemExit(1)

print("\nWorkflow steps:")
for number, step in enumerate(workflow_steps, 1):
    print(f"  {number}. {step}")

completed_steps = []
for number, step in enumerate(workflow_steps, 1):
    print(f"\n{'=' * 80}\nExecuting step {number}/{len(workflow_steps)}: {step}\n{'=' * 80}")
    try:
        result = routing_agent.route(step)
    except Exception as exc:  # keep going so one failed step does not lose the rest of the plan
        logger.error("Step %d failed (%s): %s", number, step, exc)
        result = f"[Step failed: {exc}]"
    completed_steps.append(result)
    print(f"\nResult of step {number}:\n{result}")

# Consolidated project plan
print("\n\n" + "#" * 80)
print("#  CONSOLIDATED PROJECT PLAN - EMAIL ROUTER")
print("#" * 80)
for section_title in (USER_STORIES, PRODUCT_FEATURES, ENGINEERING_TASKS):
    print(f"\n{'=' * 80}\n{section_title.upper()}\n{'=' * 80}")
    if plan_sections[section_title]:
        print("\n\n".join(plan_sections[section_title]))
    else:
        print("(No output was produced for this section by the workflow steps.)")

print("\n*** Workflow execution completed ***\n")
