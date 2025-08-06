# MAIN.PY IS NOT NEEDED ANYMORE, WE JUST HAD THIS ORIGINALLY FOR TESTING
# UI.PY NOW HANDLES THE HIGH LEVEL



from dotenv import load_dotenv
from agents import Runner
from coordinator_agent import coordinator_agent


load_dotenv()

def chat_loop():
    print("🎧 Welcome to CompanionCare! (type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() == "exit":
            print("Goodbye!")
            break

        # Pass user input through the Coordinator Agent
        result = Runner.run_sync(coordinator_agent, user_input)
        print(f"CompanionCare: {result.final_output}")


if __name__ == "__main__":
    chat_loop()

# sample testing question: Hi honey. How's the weather outside in San Diego, CA right now? Also, I want to multiply 3.