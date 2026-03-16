from langgraph.graph import START,END,StateGraph
from typing import TypedDict,Annotated
from langchain_core.messages import HumanMessage,BaseMessage
from langgraph.graph import add_messages
from langchain_groq import ChatGroq
from dotenv import load_dotenv

from langgraph.prebuilt import ToolNode,tools_condition
from langchain_community.tools import DuckDuckGoSearchRun # ye prebuilt tool hai (search engine) lang chain ka 
from langchain_core.tools import tool  # hmm apna tools built krna chahty hain isi lye ye use hua hai 

import requests
import random


import asyncio

load_dotenv()

model = ChatGroq(model = "llama-3.1-8b-instant")


## Creating Tools 
search_tool = DuckDuckGoSearchRun(region = 'us-en')

@tool
def calculator (first_num:float,sec_num:float,operation:str) ->dict:
    """Perform basic arithmetic operations like add, subtract, multiply and divide."""
    try:
        if operation == 'add':
            result = first_num+sec_num
        elif operation == "sub":
            result = first_num-sec_num
        elif operation == "mul":
            result = first_num*sec_num
        elif operation == "div":
            if sec_num == 0:
                return {"error": "Division by zero is not possible."}
            result = first_num/sec_num
        else:
           return {"error": "Unsupported Operation."}
    except Exception as e:
        return {"error": str(e)} 

@tool
def stock_price_tool(symbol:str)->dict:
     """Get the latest stock price for a given company symbol using AlphaVantage API."""
     
     url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=X7SKKFUR19BWRM7V"
     r = requests.get(url)
     return r.json()


# make tool list 
tools =[search_tool,calculator,stock_price_tool]


# MAke LLM aware of tools
llm_with_tools = model.bind_tools(tools)

# Creating State
class chatState(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]



## Building Graph 
def build_graph():

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
    workflow = build_graph()

    out = await workflow.ainvoke({"messages": [HumanMessage(content="What is the stock price of apple?")]})
    print(out["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())

