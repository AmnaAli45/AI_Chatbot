from langgraph.graph import START,END,StateGraph
from typing import TypedDict,Annotated
from langchain_core.messages import HumanMessage,BaseMessage
from langgraph.graph import add_messages
from langchain_groq import ChatGroq
from dotenv import load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_community.tools import DuckDuckGoSearchRun # ye prebuilt tool hai (search engine) lang chain ka 
from langchain_core.tools import tool  # hmm apna tools built krna chahty hain isi lye ye use hua hai 

import requests
import random
import asyncio

load_dotenv()

model = ChatGroq(model = "llama-3.1-8b-instant")


## Creating MCP Clients
client = MultiServerMCPClient(
    {
        "arith": {
            "transport": "stdio", # because it is a local server
            "command": "D:/LangGraph/myenv/Scripts/python.exe",
            "args": ["math_server.py"], # path of server
        },
        "expense": { # Remote MCP Server
            "transport": "streamable_http",  # if this fails, try "sse"
            "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
        }
    })







# Creating State
class chatState(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]



## Building Graph 
async def build_graph():
    tools = await client.get_tools() # ye function server prr available saare tools fetch kr k la kr de ga 
    llm_with_tools = model.bind_tools(tools)

    # Chat Node 
    async def chat_node(state: chatState):
        messages = state['messages']
        response= await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    # Tool NOde
    tool_node = ToolNode(tools) # Execute the tools (is ka implementation asynchronous hi hota hai by default ... hmein krne ki zroort hai hi nhi )
    
    graph = StateGraph(chatState)

    graph.add_node("chat_node",chat_node)
    graph.add_node("tools",tool_node)

    graph.add_edge(START,"chat_node")
    graph.add_conditional_edges("chat_node",tools_condition) # ye tools_condition ne decide krna hai k kon sa node execute ho ga (tool node) ya direct answer aaye ga 
    graph.add_edge("tools","chat_node")

    workflow = graph.compile()
    return workflow

async def main():
    workflow =await  build_graph()

    out = await workflow.ainvoke({"messages": [HumanMessage(content="Add an expense for a udemy course of Rs. 500 on 10 Nov")]})
    print(out["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())

