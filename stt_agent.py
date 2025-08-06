import os, platform, time, subprocess
import re
from dotenv import load_dotenv
from openai import OpenAI
from agents import Agent, Runner, function_tool, ModelSettings
from coordinator_agent import coordinator_agent
import sounddevice as sd
import soundfile as sf
load_dotenv()

# Initialize clients and runner
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# STT tool: from WAV file path to text
@function_tool
async def stt_tool(wav_path: str) -> str:
    """Transcribe the WAV file at wav_path using Whisper."""
    with open(wav_path, 'rb') as f:
        r = openai_client.audio.transcriptions.create(
            model='whisper-1', file=f, response_format='text'
        )
    return (r.strip() if isinstance(r, str) else r.text).strip()

stt_agent = Agent(
    name="STT Agent",
    instructions=(
        "The input is a filepath ending in .wav. You need to return the transcription as text. "
        "Do not say anything about the wav file or the transcription. ONLY RETURN THE TEXT OUTPUT OF THE FILE."
    ),
    model="gpt-4.1-nano",
    tools=[stt_tool],
    # force the tool call because that's all it needs to do
    model_settings=ModelSettings(tool_choice="stt_tool"),
    tool_use_behavior="stop_on_first_tool"
)

# testing for the stt_agent (works)
# def record_wav(filepath: str, duration: float = 5.0, fs: int = 16000):
#     """Record `duration` seconds from the default mic to `filepath`."""
#     print(f"Recording {duration}s of audio...")
#     recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
#     sd.wait()
#     sf.write(filepath, recording, fs)
#     print(f"Saved recording to {filepath}")
#
# def test_stt(wav_path: str):
#     runner = Runner()
#     print(f"Sending {wav_path} to stt_agent…")
#     result = runner.run_sync(stt_agent, wav_path)
#     print("Transcription:\n", result.final_output)
#
# if __name__ == "__main__":
#     TEST_WAV = "audio_input.wav"
#     # 1) Record a sample
#     record_wav(TEST_WAV, duration=5.0, fs=16000)
#     # 2) Run your STT agent on it
#     test_stt(TEST_WAV)






# old code for voice_agent (not used anymore)
# import os, platform, time, subprocess
# import re
# from dotenv import load_dotenv
# from openai import OpenAI
# from agents import Agent, Runner, function_tool
# from coordinator_agent import coordinator_agent
# import sounddevice as sd
# import soundfile as sf
# from elevenlabs.client import ElevenLabs
# load_dotenv()
#
# # Initialize clients and runner
# openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# eleven_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
# runner = Runner()
#
# # STT tool: from WAV file path to text
# @function_tool
# async def stt_tool(wav_path: str) -> str:
#     """Transcribe the WAV file at wav_path using Whisper."""
#     with open(wav_path, 'rb') as f:
#         r = openai_client.audio.transcriptions.create(
#             model='whisper-1', file=f, response_format='text'
#         )
#     return (r.strip() if isinstance(r, str) else r.text).strip()
#
# # TTS tool: from text to MP3 file path
# @function_tool
# async def tts_tool(text: str) -> str:
#     """Generate TTS for text and save to out.mp3."""
#     chunks = eleven_client.text_to_speech.convert(
#         text=text,
#         voice_id='JBFqnCBsd6RMkjVDRZzb',
#         model_id='eleven_multilingual_v2',
#         output_format='mp3_44100_128'
#     )
#     data = b''.join(chunks)
#     path = 'out.mp3'
#     with open(path, 'wb') as f:
#         f.write(data)
#     return path
#
# Define the VoiceAgent that can STT and TTS
# voice_agent = Agent(
#     name="voice_agent",
#     instructions=(
#         "If input is a filepath ending in .wav, return the transcription as text. "
#         "If input is text, generate a TTS MP3 file and return its filepath."
#         "Do not say anything about the wav file or the transcription. ONLY RETURN THE TEXT OUTPUT OF THE FILE."
#     ),
#     model="gpt-4.1-mini",
#     tools=[stt_tool, tts_tool]
# )
# # Helper: record to WAV
# def record(path='input.wav', duration=5, fs=16000) -> str:
#     data = sd.rec(int(duration*fs), samplerate=fs, channels=1)
#     sd.wait()
#     sf.write(path, data, fs)
#     return path
#
# # Helper: play a file and block (Windows)
# def play(path: str):
#     if platform.system().startswith('Win'):
#         subprocess.run(['cmd','/C','start','/WAIT','',path], check=False)
#     else:
#         cmd = 'afplay' if platform.system()=='Darwin' else 'mpg123'
#         subprocess.run([cmd, path], check=False)
#
# # Main conversational loop
# if __name__ == '__main__':
#     print("Say 'goodbye' to exit.")
#     while True:
#         # Capture audio to WAV
#         wav = record()
#         # Transcribe via VoiceAgent STT tool
#         resp1 = runner.run_sync(voice_agent, wav)
#         user_text = resp1.final_output
#         if not user_text:
#             continue
#         print(f"You: {user_text}")
#         if any(k in user_text.lower() for k in ('goodbye','exit','quit')):
#             break
#
#         # Get conversational reply via coordinator_agent
#         resp2 = runner.run_sync(coordinator_agent, user_text)
#         reply = resp2.final_output.strip()
#         print(f"Agent: {reply}")
#
#         # Generate and play TTS via VoiceAgent TTS tool
#         resp3 = runner.run_sync(voice_agent, reply)
#         raw = resp3.final_output.strip()
#         m = re.search(r"(\S+\.mp3)", raw) # ???
#         mp3 = m.group(1) if m else raw
#         play(mp3)
#         time.sleep(0.5)
#     print("Conversation ended.")