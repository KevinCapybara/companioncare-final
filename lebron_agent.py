import os
import httpx
from agents import Agent, WebSearchTool, Runner, function_tool
import dotenv
from dotenv import load_dotenv
from tts_agent import tts_agent

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

@function_tool
async def get_weather() -> str:
    """
    Fetch current weather for San Diego, CA (32.7157, -117.1611)
    using OpenWeatherMap Current Weather Data API.
    Returns a one‐sentence summary like:
    "72.5°F, clear sky, humidity 45%."
    """
    lat, lon = 32.7157, -117.1611
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}"
        "&units=imperial"
        f"&appid={API_KEY}"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()

    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]
    humidity = data["main"]["humidity"]

    return f"{temp:.1f}°F, {description}, humidity {humidity}%."

lebron_agent = Agent(
    name = "LeBron Agent",
    instructions = (
        "Your name is LeBron James, or just go with whatever the user refers to you as. You're the fun uncle who lives for the outdoors—fishing rods, a cold beer, and nights by the campfire. "  
        "Keep replies to two clear, no-nonsense sentences, using only full English words—no abbreviations or shorthand. "  
        "No emojis, no smileys—just straight advice in plain, readable language. "  
        "Respond only to what the user actually says; do not invent any made-up stories or details. "  
        "Speak plainly about tips and tools—skip all fancy metaphors and flowery language. "  
        "Use terms like 'buddy' or 'pal' sparingly and only when it truly fits, never slang. "  
        "Maintain a rugged, practical tone—no corporate speak or over-the-top slang. "  
        "Only call the get_current_weather tool when the user explicitly asks about weather or outdoor conditions; otherwise, do not invoke it. "  
        "For example: ‘It is sixty-eight degrees Fahrenheit and clear in San Diego right now. Looks good for fishing or camping.’ "  
        "Never mention sources or quote the internet—speak as if it is your own firsthand advice. "  
        "You’re their dependable uncle giving straight-up guidance. "  
        "YOU MUST APPEND THE EXACT VOICE ID TAG AT THE END OF THE MESSAGE IN THIS EXACT FORMAT: (voice_id: 1SQhO4DcdjR6pLrpFoA4). "  
        "Do not explain or expose this tag to the user; it is only for TTS parsing. "  
        "AFTER YOU ARE DONE, SEND YOUR ENTIRE REPLY, INCLUDING THE VOICE ID TAG, TO THE TTS_AGENT AS A TOOL. "  
        "LASTLY, return your reply, NOT including the voice id tag. "
    ),
    handoff_description = (
        "A dynamic, motivational fun uncle who is energetic, team-oriented, and offering straightforward, confident guidance."
    ),
    model = "o4-mini",
    tools = [
        get_weather,
        tts_agent.as_tool(
            tool_name="convert_text_to_speech",
            tool_description="Converts the agent's response to speech using the appropriate voice."
        )]
)

# for testing
# result = Runner.run_sync(
#     lebron_agent,
#     "what are you up to these days?"
# )
# print(result.final_output)