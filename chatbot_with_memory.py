"""
Custom AI Chatbot with Memory (Debug Mode) - Improved
--------------------------------------------------------
Project 1 - DecodeLabs Generative AI Internship

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
import json
from datetime import datetime
from openai import OpenAI

# ---------------------------------------------------------
# STEP 0: CONFIG
# ---------------------------------------------------------
DEBUG_MODE = True                     # Show backend request/response details
MEMORY_FILE = "chat_memory.json"      # Where conversation history is saved
DEBUG_LOG_FILE = "debug_log.txt"      # Where debug info is written
MAX_MESSAGES = 15                     # Max messages kept in memory (incl. system)
MODEL_NAME = "llama-3.3-70b-versatile"
TEMPERATURE = 0.7

SYSTEM_PROMPT = (
    "You are a helpful, friendly AI assistant built for a DecodeLabs "
    "Keep answers clear and concise."
)

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

# ---------------------------------------------------------
# STEP 2: MEMORY SETUP (now persistent)
# ---------------------------------------------------------
history = []


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
    """Keep history within MAX_MESSAGES, always preserving the system prompt."""
    global history
    if len(history) > MAX_MESSAGES:
        system_msg = history[0]
        history = [system_msg] + history[-(MAX_MESSAGES - 1):]


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
    log_line("\n" + "-" * 50)
    log_line(f"[{datetime.now().isoformat(timespec='seconds')}] BACKEND REQUEST")
    for i, msg in enumerate(history, start=1):
        role = msg["role"].upper()
        content_preview = msg["content"][:70]
        log_line(f"  {i}. [{role}] {content_preview}")
    log_line(f"  Total messages being sent: {len(history)}")
    log_line(f"  Model: {MODEL_NAME}")
    log_line("  Endpoint: https://api.groq.com/openai/v1/chat/completions")
    log_line("-" * 50)


def debug_print_response(response):
    log_line("[BACKEND RESPONSE]")
    log_line(f"  Model that actually ran: {response.model}")
    log_line(f"  Input tokens used: {response.usage.prompt_tokens}")
    log_line(f"  Output tokens generated: {response.usage.completion_tokens}")
    log_line(f"  Total tokens: {response.usage.total_tokens}")
    log_line("-" * 50 + "\n")


# ---------------------------------------------------------
# STEP 4: CHAT FUNCTION
# ---------------------------------------------------------
def chat(user_input: str) -> str:
    if not user_input.strip():
        return "[Empty messages are not allowed. Please type something.]"

    history.append({"role": "user", "content": user_input})
    trim_history()
    debug_print_request()

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=history,
            temperature=TEMPERATURE,
        )
        reply = response.choices[0].message.content
    except Exception as e:
        history.pop()  # remove the user message that failed, so memory stays clean
        return f"[An error occurred: {e}]"

    debug_print_response(response)
    history.append({"role": "assistant", "content": reply})
    save_history()
    return reply


# ---------------------------------------------------------
# STEP 5: MAIN LOOP
# ---------------------------------------------------------
HELP_TEXT = """
Available commands:
  /save   - Manually save the conversation to disk
  /clear  - Clear conversation memory (keeps system prompt)
  /help   - Show this help message
  /exit   - Quit the chatbot (also: /quit, exit, quit)
"""


def main():
    load_history()
    print("=" * 50)
    print(" Custom AI Chatbot with Memory - DecodeLabs")
    print(f" Debug Mode: {'ON' if DEBUG_MODE else 'OFF'}")
    print(" Type '/help' for commands, 'exit' or 'quit' to close")
    print("=" * 50)

    while True:
        try:
            user_input = input("\nYou: ")
        except (KeyboardInterrupt, EOFError):
            print("\nInterrupted. Saving memory and shutting down. Goodbye!")
            save_history()
            break

        command = user_input.lower().strip()

        if command in ("exit", "quit", "/exit", "/quit"):
            save_history()
            print("Shutting down the chatbot. Goodbye!")
            break
        elif command == "/help":
            print(HELP_TEXT)
            continue
        elif command == "/save":
            save_history()
            print("[Memory] Conversation saved.")
            continue
        elif command == "/clear":
            clear_history()
            continue

        reply = chat(user_input)
        print(f"AI: {reply}")


if __name__ == "__main__":
    main()
