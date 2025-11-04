# HW 5 — Generative AI Apps with LangChain / LangGraph

This assignment contains two Streamlit applications demonstrating the use of
generative AI tools in interactive web apps:

* HW51.py — Hangman:
  A simple text-based game built with Streamlit and a language model.

* HW52.py — LangGraph + Tavily + Wikipedia:
  A LangGraph agent that decides when to call the Tavily Search and Wikipedia APIs to answer factual and background questions with up to date information.

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
pip install streamlit python-dotenv langchain langchain-openai langchain-tavily langchain-community langgraph wikipedia
```

---

## 2. API Keys and Environment Variables

Create a file named `.env` in the project root (same directory as your `.py` files):

```bash
OPENAI_API_KEY=sk-...your-openai-key...
TAVILY_API_KEY=tvly-...your-tavily-key...
```

* These keys allow the apps to access OpenAI’s LLM models and Tavily’s web-search API.
* Wikipedia requires no API key.
* You can obtain a Tavily API key at [https://tavily.com](https://tavily.com).

---

## 3. Running Each App

### HW 5-1 — Hangman

```bash
streamlit run HW51.py
```

* Uses Streamlit for the interface.
* The app chooses a hidden word via an LLM; you guess letters interactively.

### HW 5-2 — LangGraph + Tavily + Wikipedia

```bash
streamlit run HW52.py
```

* Demonstrates LangGraph for state-based orchestration of AI agents.
* Uses ChatOpenAI for reasoning and decision-making.

* Integrates:
    * Tavily Search. for real-time, up-to-date web results.
    * WikipediaQueryRun for background and general knowledge.

* The LLM autonomously decides which tool to use before generating its answer.
* Includes a Streamlit sidebar to adjust temperature and search depth dynamically.
* Displays sources and trace output for transparency.

---

## Project Structure

```
HW5/
│
├── HW51.py          # Hangman Streamlit app
├── HW52.py          # LangGraph + Tavily + Wikipedia app
├── .env             # API keys (ignored by Git)
└── README.md        
```

---

## Extra Credit

HW52 includes a Wikipedia integration in addition to Tavily Search — fulfilling the extra credit requirement by incorporating more tools and functionality into the LangGraph app.

---

**Author:** Kahlil Wassell
**Course:** UChicago MPCS - Generative AI
**Date:** November 2025
