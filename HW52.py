# HW52.py — LangGraph + Tavily + Wikipedia (minimal changes)
import re
from typing import List, Sequence

from dotenv import load_dotenv
import streamlit as st

from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode, tools_condition

# Setup
load_dotenv()

st.set_page_config(page_title="HW 52: LangGraph + Tavily", layout="centered")
st.title("HW 52 — LangGraph + Tavily + Wikipedia")
st.caption("A LangGraph agent that decides when to search and responds with short citations.")

# Sidebar: runtime knobs & status
with st.sidebar:
    st.header("Settings")
    temperature = st.slider("Model temperature", 0.0, 1.0, 0.2, 0.05)
    max_results = st.slider("Tavily max results", 1, 10, 5, 1)


# Tools & Model
tavily_tool = TavilySearch(max_results=max_results)

wiki_wrapper = WikipediaAPIWrapper(
    lang="en",
    top_k_results=3
)

wikipedia_tool = WikipediaQueryRun(api_wrapper=wiki_wrapper)

# Register both tools (only change here)
TOOLS = [tavily_tool, wikipedia_tool]

# Tool-enabled LLM (same idea)
model = ChatOpenAI(model="gpt-4o-mini", temperature=temperature)
llm_with_tools = model.bind_tools(TOOLS)


sys_msg = SystemMessage(
    content=(
        "You are a helpful research assistant. Use tools when needed:\n"
        "- Use Tavily for up-to-date facts, news, or current names.\n"
        "- Use Wikipedia for general background and stable reference info.\n"
        "Keep answers concise and include 1–3 short source URLs in parentheses."
    )
)


# Agent Node 
def agent_node(state: MessagesState):
    msgs: Sequence[BaseMessage] = state["messages"]
    if not msgs:
        return {"messages": []}
    # convert to list when invoking the LLM if it expects a mutable sequence
    response = llm_with_tools.invoke(list(msgs))
    return {"messages": [response]}


# Graph setup
graph = StateGraph(MessagesState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(TOOLS))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition, {"tools": "tools", "__end__": END})
graph.add_edge("tools", "agent")
app = graph.compile()

# Small UI helpers
_URL_RE = re.compile(r"https?://\S+")


def extract_urls(text: str):
    if not text:
        return []
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
    with st.container(border=True):
        st.markdown(answer)
    urls = extract_urls(answer)
    if urls:
        st.markdown("**Sources**")
        for i, u in enumerate(urls, start=1):
            st.markdown(f"{i}. <{u}>")


# Examples row
st.write("Try one of these:")
ex1, ex2, ex3, ex4 = st.columns(4)
with ex1:
    if st.button("Current bears Quarterback?", use_container_width=True):
        st.session_state["q"] = "Who is the quarterback for the Chicago Bears right now?"
with ex2:
    if st.button("Latest LangGraph release?", use_container_width=True):
        st.session_state["q"] = "What is the latest LangGraph release version?"
with ex3:
    if st.button("What is LangGraph?", use_container_width=True):
        st.session_state["q"] = "What is LangGraph and who maintains it?"
with ex4:
    if st.button("Who is Tim Berners-Lee?", use_container_width=True):
        st.session_state["q"] = "Who is Tim Berners-Lee? Provide a concise summary."


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
            for event in app.stream(state, stream_mode="values"):
                msgs = event.get("messages", [])
                if msgs:
                    last = msgs[-1]
                    role = type(last).__name__.replace("Message", "")
                    preview = (getattr(last, "content", "") or "")[:220]
                    collected_lines.append(f"- **{role}**: {preview}")
                    trace_box.markdown("\n".join(collected_lines))
            final = app.invoke(state)
    else:
        with st.spinner("Running agent..."):
            final = app.invoke(state)

    st.subheader("Answer")
    msgs = final.get("messages", [])
    answer = msgs[-1].content if msgs else ""
    render_answer(answer)
