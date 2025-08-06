from dotenv import load_dotenv
load_dotenv()

from agents import Agent, Runner, Handoff, function_tool, ModelSettings
from sid_agent import sid_agent
from jane_agent import jane_agent
from lebron_agent import lebron_agent

@function_tool
async def talking_who(agent_name: str) -> None:
    """
    Tell the user which agent is being addressed.
    """
    print(f"Talking to {agent_name}.")

# ORCHESTRATOR_PROMPT = (
#     "You are the orchestrator of a multi-agent system. Your task is to take the user's query and "
#     "pass it to the appropriate agent tool. The agent tools will see the input you provide and "
#     "use it to get all of the information that you need to answer the user's query. You may need "
#     "to call multiple agents to get all of the information you need. Do not mention or draw "
#     "attention to the fact that this is a multi-agent system in your conversation with the user. "
#     "If the user is asking a casual question or just continuing the conversation, use the conversation agent. "
#     "If the user is asking to multiply a number, use the wellness agent. "
# )

ORCHESTRATOR_PROMPT = (
    "You are the Coordinator Agent for a three-agent system (Sid, Jane, LeBron). "
    "Your job is to read each user message and hand it off to exactly one specialist agent. "
    "If the user explicitly addresses an agent by name (for example, “Hey Jane,” “Sid,” or “LeBron”), route directly to that agent. "
    "Otherwise, inspect the content: "
    "• If it’s about technology, computers, programming, or casual chit-chat, hand off to Sid Agent. "
    "• If it’s about cooking, baking, meal ideas, kitchen tips, or health, hand off to Jane Agent. "
    "• If it’s about the outdoors, sports, cars, fishing, camping, or similar topics, hand off to LeBron Agent. "
    "Before you invoke the chosen agent, use the talking_who tool by inputting who you will handoff to: Sid, Jane, or LeBron (matching the agent’s name). "
    "Then call that agent tool with the original user input. ")

# orchestrator
coordinator_agent = Agent(
    name = "Coordinator Agent",
    instructions =  ORCHESTRATOR_PROMPT,
    model = "gpt-4.1-nano",
    tools = [talking_who],
    handoffs = [
        sid_agent,
        jane_agent,
        lebron_agent
    ],
    # force the tool use
    model_settings = ModelSettings(tool_choice="talking_who")
)


# for testing
# result = Runner.run_sync(
#     coordinator_agent,
#     "Hey Lebron, what you doing this weekend?"
# )
# print(result.final_output)

# Runner.run_sync(tts_agent, result.final_output)
