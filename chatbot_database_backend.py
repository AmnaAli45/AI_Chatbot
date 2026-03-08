from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver # database mein data ko store krne k lye
from langgraph.graph import add_messages
import sqlite3

load_dotenv()

model = ChatGroq(model = "llama-3.1-8b-instant")

# Creating State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]

# Defining chat node

def chat_node(state:ChatState):
    messages = state['messages']
    response = model.invoke(messages)
    return {'messages': [response]}

# Creating the Database
conn=sqlite3.connect(database='chatbot.db',check_same_thread=False) # agr is naam ka database exist nhi krta hoga to us ko create kre ga 
# check_same_thread=False --> humm apne workflow mwin multiplw threads k sath kaam kr rhy hain ... lekin sqlite by  default single thread 
#allow krta hai .. is parameter ko false krne se multiple threads k sath working allow ho jaye gy 

checkpointer = SqliteSaver(conn=conn) # we have to create database and connect this checkpointer with that database
# Creating graph
graph = StateGraph(ChatState)

# add nodes to graph
graph.add_node("chat node", chat_node)

# Creating Edges in graph 
graph.add_edge(START, "chat node")
graph.add_edge("chat node", END)

# Compile Graph 
workflow = graph.compile(checkpointer= checkpointer)

def retreive_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None): # ye function jitne bhi checkpoints database mein exist krty hain wo nikal kr de ga 
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)