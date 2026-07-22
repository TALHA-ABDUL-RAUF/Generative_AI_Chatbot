"""
Custom AI Chatbot with Memory (Debug Mode)
--------------------------------------------
Project 1 - DecodeLabs Generative AI Internship

This version clearly displays every request and response in the
terminal, so you can see for yourself what's happening in the "backend".
"""

"""
Improvements over the original version:
  1. Persistent memory  -> conversation is saved to / loaded from a JSON
                            file, so memory survives closing the terminal.
  2. System prompt       -> defines the assistant's behavior/persona.
  3. In-chat commands    -> /save, /clear, /help, /exit
  4. Graceful shutdown   -> Ctrl+C / Ctrl+D no longer crash the program.
  5. Config section       -> all tunable settings live in one place.
  6. Debug log file       -> debug info is written to a log file, not just
                              printed, so it can be attached to a report.
"""

import os
import sys
from openai import OpenAI
from datetime import datetime
from openai import Open
# ---------------------------------------------------------
# STEP 0: DEBUG MODE ON/OFF
# ---------------------------------------------------------
# Keep it True to see detailed request/response info in the terminal.
# Set it to False to run like a clean, normal chatbot.
DEBUG_MODE = True

# ---------------------------------------------------------
# STEP 1: API KEY SETUP
# ---------------------------------------------------------
API_KEY = os.environ.get("GROQ_API_KEY")

if not API_KEY:
    print("ERROR: GROQ_API_KEY environment variable is not set.")
    print("Run this command in PowerShell:")
    print('  $env:GROQ_API_KEY="paste_your_actual_key_here"')
    sys.exit(1)

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

MODEL_NAME = "llama-3.3-70b-versatile"

# ---------------------------------------------------------
# STEP 2: MEMORY SETUP
# ---------------------------------------------------------
history = []
MAX_MESSAGES = 15


def load_history():
    """Load saved conversation from disk, if it exists."""
    global history
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
            print(f"[Memory] Loaded {len(history)} messages from {MEMORY_FILE}")
        except (json.JSONDecodeError, OSError):
            print("[Memory] Could not read saved memory file, starting fresh.")
            history = []
    if not history or history[0].get("role") != "system":
        history.insert(0, {"role": "system", "content": SYSTEM_PROMPT})


def save_history():
    """Save current conversation to disk."""
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"[Memory] Could not save history: {e}")


def clear_history():
    global history
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    save_history()
    print("[Memory] Conversation history cleared.")


def trim_history():
    global history
    if len(history) > MAX_MESSAGES:
        history = history[-MAX_MESSAGES:]
      
# ---------------------------------------------------------
# STEP 3: DEBUG HELPERS
# ---------------------------------------------------------
def log_line(line: str):
    """Write a line to both terminal (if DEBUG_MODE) and the log file."""
    if DEBUG_MODE:
        print(line)
    try:
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass

def debug_print_request():
    """Clearly displays the payload that's being sent to the backend."""
    print("\n" + "-" * 50)
    print("[BACKEND REQUEST] This full history is being sent to Groq:")
    for i, msg in enumerate(history, start=1):
        role = msg["role"].upper()
        content_preview = msg["content"][:70]
        print(f"  {i}. [{role}] {content_preview}")
    print(f"  Total messages being sent: {len(history)}")
    print(f"  Model: {MODEL_NAME}")
    print(f"  Endpoint: https://api.groq.com/openai/v1/chat/completions")
    print("-" * 50)


def debug_print_response(response):
    """Displays the important parts of the response received from the backend."""
    print("[BACKEND RESPONSE] This came back from Groq:")
    print(f"  Model that actually ran: {response.model}")
    print(f"  Input tokens used: {response.usage.prompt_tokens}")
    print(f"  Output tokens generated: {response.usage.completion_tokens}")
    print(f"  Total tokens: {response.usage.total_tokens}")
    print("-" * 50 + "\n")

# ---------------------------------------------------------
# STEP 4: CHAT FUNCTION
# ---------------------------------------------------------

def chat(user_input: str) -> str:
    if not user_input.strip():
        return "[Empty messages are not allowed. Please type something.]"

    history.append({"role": "user", "content": user_input})
    trim_history()

    if DEBUG_MODE:
        debug_print_request()

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=history,
        )
        reply = response.choices[0].message.content
    except Exception as e:
        return f"[An error occurred: {e}]"

    if DEBUG_MODE:
        debug_print_response(response)

    history.append({"role": "assistant", "content": reply})

    return reply


# ---------------------------------------------------------
# STEP 3: MAIN LOOP
# ---------------------------------------------------------

HELP_TEXT = """
Available commands:
  /save   - Manually save the conversation to disk
  /clear  - Clear conversation memory (keeps system prompt)
  /help   - Show this help message
  /exit   - Quit the chatbot (also: /quit, exit, quit)
"""

def main():
    print("=" * 50)
    print(" Custom AI Chatbot with Memory - DecodeLabs")
    print(f" Debug Mode: {'ON' if DEBUG_MODE else 'OFF'}")
    print(" Type 'exit' or 'quit' to close")
    print("=" * 50)

    while True:
        user_input = input("\nYou: ")

        if user_input.lower().strip() in ("exit", "quit"):
            print("Shutting down the chatbot. Goodbye!")
            break

        reply = chat(user_input)
        print(f"AI: {reply}")


if __name__ == "__main__":
    main()
