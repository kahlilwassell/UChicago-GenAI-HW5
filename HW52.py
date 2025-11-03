from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import tools_condition, ToolNode
import streamlit as st

# load environment variables from a .env file
load_dotenv()

# set up the streamlit app page configuration
st.set_page_config(page_title="LangGraph + Tavily", layout="centered")
st.title("LangGraph + Tavily (HW 5.2)")
st.caption("The model decides when to search using Tavily, then answers with short citations.")

# Tavily tool
tavily_tool = TavilySearch(max_results=5)

# ---------- Minimal LangGraph agent section ----------
st.subheader("Ask the LangGraph Agent")

tools = [tavily_tool]

# LLM (tool-enabled)
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
llm_with_tools = model.bind_tools(tools)

# System message (add ONCE in initial state)
sys_msg = SystemMessage(
    content="You are a helpful assistant that uses Tavily to find information when needed. "
            "When you do search, include 1–2 short source URLs in parentheses."
)


def agent_node(state: MessagesState):
    msgs = state["messages"]
    if not msgs:
        return {"messages": []}
    response = llm_with_tools.invoke(msgs)
    return {"messages": [response]}


graph = StateGraph(MessagesState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition, {"tools": "tools", "__end__": END})
graph.add_edge("tools", "agent")

app = graph.compile()

# User question input
question = st.text_input("Ask a question (e.g., 'Who is the quarterback for the Bears?')", key="agent_q")
if st.button("Ask") and question.strip():
    try:
        state: MessagesState = {
            "messages": [
                sys_msg,
                HumanMessage(content=question.strip())  # <-- HumanMessage (not SystemMessage)
            ]
        }
        final = app.invoke(state)
        # Show only the last assistant message
        msgs = final.get("messages", [])
        if msgs:
            st.subheader("Answer")
            st.write(msgs[-1].content)
        else:
            st.info("No response produced.")
    except Exception as e:
        st.error(f"Agent error: {e}")
