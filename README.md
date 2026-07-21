
# 🤖 Custom AI Chatbot with Memory

A terminal-based conversational AI chatbot built in Python, powered by the **Groq API** (`llama-3.3-70b-versatile`). Built for the DecodeLabs, it maintains conversation context across turns and includes an optional **Debug Mode** for inspecting raw requests, responses, and token usage in real time.

---

## ✨ Features

- **Context-Aware Memory** — Retains up to the last 20 messages (`MAX_MESSAGES = 20`) using a sliding-window strategy, so the model stays aware of earlier turns without unbounded token growth.
- **Debug Mode** — Toggle a single flag to print the exact payload sent to Groq, the model that responded, and a full token usage breakdown (prompt / completion / total).
- **Secure by Design** — The API key is never hardcoded. It's read from the `GROQ_API_KEY` environment variable at runtime.
- **Input Validation** — Empty or whitespace-only messages are rejected before hitting the API.
- **Graceful Error Handling** — Network issues, rate limits, or invalid keys return a readable error instead of crashing the program.

---

## 📁 Project Structure

```
.
├── .gitignore
├── README.md
├── chatbot_with_memory.py
└── requirements.txt
```

---

## 🛠️ Prerequisites

- Python 3.8 or higher
- A free [Groq API key](https://console.groq.com/keys)

---

## 🚀 Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Create and activate a virtual environment

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Configure Your API Key

The chatbot reads your Groq API key from the `GROQ_API_KEY` environment variable — it is **never** stored in the code.

**Windows (PowerShell)**

```powershell
$env:GROQ_API_KEY="your_actual_api_key_here"
```

**Windows (Command Prompt)**

```cmd
set GROQ_API_KEY=your_actual_api_key_here
```

**Linux / macOS**

```bash
export GROQ_API_KEY="your_actual_api_key_here"
```

---

## 💬 Usage

Run the chatbot:

```bash
python chatbot_with_memory.py
```

Type your message and press Enter. Type `exit` or `quit` to end the session.

### Enable Debug Mode

Open `chatbot_with_memory.py` and set:

```python
DEBUG_MODE = True
```

This prints, for every turn:

- The full message history sent to Groq
- The model that responded
- Prompt / completion / total token counts

---

## 📦 requirements.txt

```
openai
```

---