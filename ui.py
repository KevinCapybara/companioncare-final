# session memory for chat history
from agents import SQLiteSession
session = SQLiteSession(session_id="session1", db_path=":memory:")

import os
import sys
import shutil
import datetime
import uuid
from dotenv import load_dotenv
import gradio as gr
import io, contextlib

# allow imports from your project root
sys.path.insert(0, os.getcwd())

from agents import Runner
from coordinator_agent import coordinator_agent
from stt_agent import stt_agent     # speech -> text only

load_dotenv()
runner = Runner()

FIXED_AUDIO = r"C:\Users\kevin\PycharmProjects\CompanionCare\out.mp3"
INPUT_DIR   = os.path.join(os.getcwd(), "inputs")
OUTPUT_DIR  = os.path.join(os.getcwd(), "outputs")

async def transcribe_audio(mic_audio: str) -> str:
    """
    Copy incoming mic file to inputs folder, transcribe via stt_agent, and return text.
    """
    os.makedirs(INPUT_DIR, exist_ok=True)
    ts_in = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    input_dest = os.path.join(INPUT_DIR, f"input_{ts_in}.wav")
    shutil.copy(mic_audio, input_dest)
    try:
        stt_res = await runner.run(stt_agent, input_dest, session = session)
        return stt_res.final_output
    except Exception as e:
        print(f"[STT ERROR] {e}")
        return ""

async def converse(user_text, mic_audio, history, mic_actually_used):
    # for testing
    # print(user_text)
    # print(mic_audio)
    # print(mic_actually_used)

    # for when you click "x" to close the speaker mic voice playback thing
    if mic_actually_used and mic_audio is None:
        return "", history, None, ""

    # Skip ghost calls
    if not user_text and not mic_actually_used:
        return "", history, None, ""

    # If audio provided, transcribe it
    if mic_actually_used:
        user_text = await transcribe_audio(mic_audio)

    # Coordinator chain for assistant reply text
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        coord_res = await runner.run(coordinator_agent, user_text, session = session)
    assistant_text = coord_res.final_output
    # grab the last non-empty line (e.g. "Talking to Sid.")
    printed = buf.getvalue().strip().splitlines()
    current_status = printed[-1] if printed else ""

    # Archive fixed TTS output to outputs/ with unique name + fsync
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts_out   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    unique_id = uuid.uuid4().hex
    output_fname = f"reply_{ts_out}_{unique_id}.mp3"
    output_dest  = os.path.join(OUTPUT_DIR, output_fname)
    with open(FIXED_AUDIO, "rb") as src, open(output_dest, "wb") as dst:
        shutil.copyfileobj(src, dst)
        dst.flush()
        os.fsync(dst.fileno())

    # Update chat history for UI
    history = history + [
        {"role": "user",      "content": user_text},
        {"role": "assistant", "content": assistant_text},
    ]

    # return status as fourth output
    return "", history, FIXED_AUDIO, current_status

async def on_text_submit(user_text, mic_audio, history):
    return await converse(user_text, mic_audio, history, False)

async def on_mic_submit(user_text, mic_audio, history):
    return await converse(user_text, mic_audio, history, True)

with gr.Blocks() as demo:
    gr.Markdown("## 🧸 CompanionCare Chat")
    # this will show “Talking to …” while model is running
    status = gr.Markdown("", elem_id="status")

    chatbot   = gr.Chatbot([], elem_id="chatbox", type="messages")
    txt       = gr.Textbox(placeholder="Type your message…", show_label=False)
    mic       = gr.Audio(sources=["microphone"], type="filepath", elem_id="mic-record", label="🎙️ Tap to speak", show_label=True)
    audio_out = gr.Audio(type="filepath", show_label=False, autoplay=True)

    txt.submit(
        on_text_submit,
        inputs=[txt, mic, chatbot],
        outputs=[txt, chatbot, audio_out, status]
    )

    mic.change(
        on_mic_submit,
        inputs=[txt, mic, chatbot],
        outputs=[txt, chatbot, audio_out, status]
    )

if __name__ == "__main__":
    demo.launch(share=True)
