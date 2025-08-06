import os
from dotenv import load_dotenv
from agents import Agent, function_tool, ModelSettings, Runner
from elevenlabs.client import ElevenLabs
import sounddevice as sd
import soundfile as sf
import re

load_dotenv()
eleven_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# extracts the voice id to give to elevenlabs for the corresponding person who responded (sid, lebron, or jane)
def extract_voice_id(text: str) -> str:
    match = re.search(r"\(voice_id:\s*(.*?)\)", text)
    return match.group(1) if match else "9BWtsMINqrJLrRacOk9x"
    # the "else" is just for testing in case something goes wrong, we default to Aria (middle-aged female)

# gets rid of the voice tag before passing the dialogue to tts
def strip_voice_tag(text: str) -> str:
    return re.sub(r"\(voice_id:.*?\)", "", text).strip()

# for testing if the functions work (they do!)
# if __name__ == "__main__":
#     text = input("Enter text: ")
#     vid = extract_voice_id(text)
#     st = strip_voice_tag(text)
#     print("Extracted voice_id:", vid)
#     print("Stripped text:", st)

# TTS tool: from text to MP3 file path
@function_tool
async def tts_tool(text: str) -> str:
    """Generate TTS for text and save to out.mp3, using embedded voice_id tag."""

    voice_id = extract_voice_id(text)
    clean_text = strip_voice_tag(text)

    chunks = eleven_client.text_to_speech.convert(
        text=clean_text,
        voice_id=voice_id,
        model_id='eleven_flash_v2',
        output_format='mp3_44100_128'
    )

    data = b''.join(chunks)
    path = 'out.mp3'
    with open(path, 'wb') as f:
        f.write(data)
    return path

tts_agent = Agent(
    name = "TTS Agent",
    instructions=(
        "Use the tool to generate a TTS MP3 file. "
        "Pass the entire input that you received into the tts_tool WITHOUT CHANGING ANYTHING. "
        "Do not say anything about the wav file or the transcription. ONLY RETURN THE TEXT OUTPUT OF THE FILE. "
    ),
    model="gpt-4.1-mini",
    tools=[tts_tool],
    handoff_description = (
        "TTS for all the people agents"
    ),
    # force the tool use
    model_settings = ModelSettings(tool_choice = "tts_tool"),
    tool_use_behavior = "stop_on_first_tool"
)


# for testing
# result = Runner.run_sync(
#     tts_agent,
#     "Fixing a bug and wondering why computers hate me today. You still holding out hope that Wi-Fi is magic? (voice_id: RFo9sOyas7g4QyIvNgit)"
# )
# print(result.final_output)

