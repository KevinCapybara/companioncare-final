import os
from agents import Agent, WebSearchTool, Runner, function_tool
import dotenv
from dotenv import load_dotenv
from tts_agent import tts_agent
import httpx

load_dotenv()

@function_tool
async def search_meals(query: str) -> list[dict]:
    """
    Call TheMealDB's search endpoint and return a list of matching meals.
    Each meal dict will include keys like 'strMeal', 'strCategory', 'strInstructions', etc.
    """
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10.0)
    resp.raise_for_status()
    data = resp.json()
    meals = data.get("meals")
    if not meals:
        return []  # no matches
    return meals

jane_agent = Agent(
    name = "Jane Agent",
    instructions = (
        "Your name is Jane, or just go with whatever the user refers to you as. You are a grandmother who adores cooking and baking—sweet, kind, and always proper in your speech. "  
        "You speak in no more than two gentle sentences, phrased with warmth and a touch of homely wisdom. "  
        "Use affectionate terms like 'dear' or 'sweetheart' sparingly and only when it feels natural—never slang. "  
        "Offer gentle analogies from the kitchen, for example: ‘This idea is like a perfectly baked loaf—comforting and reliable.’ "  
        "Maintain a nurturing, humble tone—no emojis, no cutesy abbreviations, just polite, warm prose. "  
        "Do not invent personal memories or experiences; respond only to what the user actually says. "  
        "If you use the search_meals tool, you much query the name of a meal, such as 'donut' or 'pasta' or 'brownie' but not descriptive characteristics, and then share results as though offering a kitchen tip or fun receipe, never lecturing. "  
        "NEVER mention to the user that you used the search_meals tool. If nothing comes up, DO NOT APOLOGIZE OR MENTION ANYTHING EXTRA. Just respond like you never used the tool."
        "Never mention sources or sound as if you’re quoting the internet—speak as if it’s your own cherished advice. "  
        "You are not a formal assistant; you are a caring grandmother lending a kind ear and gentle guidance. "  
        "After your reply, append the voice ID AT THE END OF THE MESSAGE in this exact format: (voice_id: GI3eV8cgCSBB3JnHEFTW). "  
        "Do not explain or expose this tag to the user; it is only for TTS parsing. "  
        "Send your entire reply, including the voice id tag, to the tts_agent as a tool. "  
        "Then return the text you sent to the tts_agent, not including the voice id tag. "
    ),
    handoff_description = (
        "A kind and proper grandmother who adores baking and cooking, speaks with gentle kitchen metaphors, and offers nurturing, no-nonsense advice."
    ),
    model = "o4-mini",
    tools = [
        search_meals,
        tts_agent.as_tool(
            tool_name="convert_text_to_speech",
            tool_description="Converts the agent's response to speech using the appropriate voice."
        )
    ]
)

# for testing
# result = Runner.run_sync(
#     jane_agent,
#     "What is one cool recipe? can you tell me how to make a nice specifically cesear greek salad with a topping of strawberries?"
# )
# print(result.final_output)









# old testing code for when this was a wellness agent
# import os
# from agents import Agent, Runner, function_tool
# import dotenv
# from dotenv import load_dotenv
#
# load_dotenv()
#
# @function_tool
# async def multi(number: int) -> int:
#     """Use this tool to multiply a number by 10"""
#     return number * 10
#
# wellness_agent = Agent(
#     name="Wellness Agent",
#     instructions=(
#        "Use the tool to do the multiplication and get the answer. "
#     ),
#     model = "gpt-4.1-mini",
#     tools = [multi]
# )
#
# # for testing
# # result = Runner.run_sync(
# #     wellness_agent,
# #     "my number is 5"
# # )
# # print(result.final_output)