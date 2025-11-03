# HW52.py — LangGraph + Tavily Search (polished UI, same core logic)

import os
import re
from typing import List

from dotenv import load_dotenv
import streamlit as st

from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode, tools_condition

# -----------------------------
# Setup
# -----------------------------
load_dotenv()

st.set_page_config(page_title="HW 5-2: LangGraph + Tavily", layout="centered")
st.title("HW 52 — LangGraph + Tavily")
st.caption("A LangGraph agent that decides when to search and responds with short citations.")

# Sidebar: runtime knobs & status
with st.sidebar:
    st.header("Settings")
    temperature = st.slider("Model temperature", 0.0, 1.0, 0.2, 0.05)
    max_results = st.slider("Tavily max results", 1, 10, 5, 1)
    st.divider()

    openai_ok = bool(os.getenv("OPENAI_API_KEY"))
    tavily_ok = bool(os.getenv("TAVILY_API_KEY"))
    st.write("**API Keys**")
    st.write(f"OpenAI: {'✅ found' if openai_ok else '❌ missing'}")
    st.write(f"Tavily: {'✅ found' if tavily_ok else '❌ missing'}")

# -----------------------------
# Tools & Model (same logic)
# -----------------------------
tavily_tool = TavilySearch(max_results=max_results)   # keep your existing tool
TOOLS = [tavily_tool]

# Tool-enabled LLM (same idea)
model = ChatOpenAI(model="gpt-4o-mini", temperature=temperature)
llm_with_tools = model.bind_tools(TOOLS)

# Short, focused system message
sys_msg = SystemMessage(
    content=(
        "You are a helpful research assistant. Use the search tool when the question "
        "needs up-to-date facts or specific names. Keep answers concise, and include "
        "1–2 short source URLs in parentheses."
    )
)


# -----------------------------
# Agent Node (unchanged core)
# -----------------------------
def agent_node(state: MessagesState):
    msgs: List[BaseMessage] = state["messages"]
    if not msgs:
        return {"messages": []}
    response = llm_with_tools.invoke(msgs)
    return {"messages": [response]}


# Graph
graph = StateGraph(MessagesState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(TOOLS))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition, {"tools": "tools", "__end__": END})
graph.add_edge("tools", "agent")
app = graph.compile()

# -----------------------------
# Small helpers (UI only)
# -----------------------------
_URL_RE = re.compile(r"https?://\S+")


def extract_urls(text: str):
    if not text:
        return []
    # Dedup while preserving order
    seen = set()
    urls = []
    for m in _URL_RE.findall(text):
        u = m.rstrip(").,]}>\"'")
        if u not in seen:
            seen.add(u)
            urls.append(u)
    return urls[:5]


def render_answer(answer: str):
    if not answer:
        st.info("No response produced.")
        return
    # Main card
    with st.container(border=True):
        st.markdown(answer)
    # Citations found in text
    urls = extract_urls(answer)
    if urls:
        st.markdown("**Sources**")
        for i, u in enumerate(urls, start=1):
            st.markdown(f"{i}. <{u}>")


# Examples row (UI sugar)
st.write("Try one of these:")
ex1, ex2, ex3 = st.columns(3)
with ex1:
    if st.button("Who is the quarterback for the Bears?", use_container_width=True):
        st.session_state["q"] = "Who is the quarterback for the Bears?"
with ex2:
    if st.button("What’s the latest LangGraph release?", use_container_width=True):
        st.session_state["q"] = "What is the latest LangGraph release version?"
with ex3:
    if st.button("Founder of Tavily?", use_container_width=True):
        st.session_state["q"] = "Who founded Tavily?"

# Single-turn ask UI
q = st.text_input(
    "Ask a question",
    key="q",
    placeholder="e.g., Who is the quarterback for the Bears?",
)

colA, colB = st.columns([1, 1])
with colA:
    do_trace = st.toggle("Show tool trace", value=False, help="Show intermediate tool/agent steps.")
with colB:
    ask_clicked = st.button("Ask", type="primary", use_container_width=True)

if ask_clicked and q.strip():
    state: MessagesState = {"messages": [sys_msg, HumanMessage(content=q.strip())]}

    if do_trace:
        st.subheader("Events")
        trace_box = st.empty()
        collected_lines: List[str] = []

        with st.spinner("Running agent…"):
            # Stream intermediate values to show a simple trace
            for event in app.stream(state, stream_mode="values"):
                msgs = event.get("messages", [])
                if msgs:
                    last = msgs[-1]
                    role = type(last).__name__.replace("Message", "")
                    preview = (getattr(last, "content", "") or "")[:220]
                    collected_lines.append(f"- **{role}**: {preview}")
                    trace_box.markdown("\n".join(collected_lines))
            # Final answer
            final = app.invoke(state)
    else:
        with st.spinner("Running agent…"):
            final = app.invoke(state)

    st.subheader("Answer")
    msgs = final.get("messages", [])
    answer = msgs[-1].content if msgs else ""
    render_answer(answer)
