# TODO: 1 - Import the AugmentedPromptAgent class
from workflow_agents.base_agents import AugmentedPromptAgent
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the capital of France?"
persona = "You are a college professor; your answers always start with: 'Dear students,'"

# TODO: 2 - Instantiate an object of AugmentedPromptAgent with the required parameters
augmented_agent = AugmentedPromptAgent(openai_api_key, persona)

# TODO: 3 - Send the 'prompt' to the agent and store the response in a variable named 'augmented_agent_response'
augmented_agent_response = augmented_agent.respond(prompt)

# Print the agent's response
print(f"Prompt: {prompt}")
print(augmented_agent_response)

# TODO: 4 - Add a comment explaining:
# - What knowledge the agent likely used to answer the prompt.
#   The agent used the general world knowledge embedded in the gpt-4.1-mini model from its
#   pre-training (no external knowledge was supplied), which is why it answers "Paris".
# - How the system prompt specifying the persona affected the agent's response.
#   The system prompt made the model adopt a college-professor persona, so the answer opens
#   with "Dear students," and uses an explanatory, teaching tone. The persona changes the
#   style/framing of the output, not the underlying facts.
print(
    "\nKnowledge source: general knowledge from the gpt-4.1-mini model (no external knowledge provided).\n"
    "Persona impact: the system prompt made the agent answer as a college professor, starting with "
    "'Dear students,' and using an instructional tone; the facts themselves are unchanged."
)
