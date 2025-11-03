# HW 5 — Generative AI Apps with LangChain / LangGrap
This assignment contains two Streamlit applications demonstrating the use of
generative AI tools in interactive web apps:

* HW51.py - Hangman:
A simple text-based game built with Streamlit and a language model.

* HW52.py - LangGraph + Tavily:
A LangGraph agent that decides when to call the Tavily Search API to answer factual questions with up to date information.
---

## 1. Setup Instructions

### Create a virtual environment

```bash
python3 -m venv GenAI
source GenAI/bin/activate       # (macOS / Linux)
# OR
GenAI\Scripts\activate          # (Windows PowerShell)
```

### Install requirements

Both apps depend on the following packages:

```bash
pip install streamlit python-dotenv langchain langchain-openai langchain-tavily langgraph
```
---

## 2. API Keys and Environment Variables

Create a file named `.env` in the project root (same directory as your `.py` files):

```bash
OPENAI_API_KEY=sk-...your-openai-key...
TAVILY_API_KEY=tvly-...your-tavily-key...
```
* These keys allow the apps to access OpenAI’s LLM models and Tavily’s web-search API.
* You can obtain a Tavily API key at [https://tavily.com](https://tavily.com).

---

## 3. Running Each App

### HW 5-1 — Hangman

```bash
streamlit run HW51.py
```

* Uses Streamlit for the interface.
* The app chooses a hidden word; you guess letters interactively.

### HW 5-2 — LangGraph + Tavily Search

```bash
streamlit run HW52.py
```

* Demonstrates LangGraph for state-based orchestration.
* Uses ChatOpenAI for reasoning and Tavily Search as a retrieval tool.
* The LLM decides whether to call the search tool before answering.

---

## Project Structure

```
HW5/
│
├── HW51.py         # Hangman Streamlit app
├── HW52.py         # LangGraph + Tavily Search app
├── .env            # API keys (ignored by Git)
└── README.md       # (this file)
```

**Author:** Kahlil Wassell
**Course:** UChicago MPCS - Generative AI
**Date:** November 2nd, 2025
