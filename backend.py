from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import add_messages

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

checkpointer = MemorySaver()
# Creating graph
graph = StateGraph(ChatState)

# add nodes to graph
graph.add_node("chat node", chat_node)

# Creating Edges in graph 
graph.add_edge(START, "chat node")
graph.add_edge("chat node", END)

# Compile Graph 
workflow = graph.compile(checkpointer= checkpointer)

