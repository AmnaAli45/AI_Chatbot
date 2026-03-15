import streamlit as st
from chatbot_database_backend import workflow,retreive_all_threads
from langchain_core.messages import  HumanMessage
import uuid # is library ki help se hmm hr baar naye conversation k laye nya thread id generate krwayen gy 

# ********************************************* Utility Functions ************************************************************

def generate_thread_id():
    thread_id = uuid.uuid4() # it will generate random thread ids
    return thread_id

def reset_chat():
    st.session_state['thread_id'] = generate_thread_id()
    add_thread(st.session_state['thread_id']) # hrr bar thread id list emin add ho jaye gy 
    st.session_state["message_history"] = []


def add_thread(thread_id):
    if thread_id not in st.session_state:
        st.session_state['chat_threads'].append(thread_id)

def load_conversations(thread_id):
    
    config = {"configurable": {"thread_id": thread_id}}
    state = workflow.get_state(config=config)

    if state is None:
        return []

    if not state.values:
        return []

    return state.values.get("messages", [])


# with st.chat_message("user"):
#     st.text("Hello, how are you?")

# with st.chat_message("assistant"):
#     st.text("I'm doing well, thank you for asking! How can I assist you today?")

# user_input = st.chat_input("Type your message here...")

# if user_input:
#     with st.chat_message("user"):
#         st.text(user_input)

# ******************************************************* Session Creating ***********************************************************

if "message_history" not in st.session_state:
    st.session_state["message_history"] = [] #session state me message history naam ki key bnayen ge aur us ko initialize krein ge

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id() # session state mein agr thread id nhi hai to us ko generate krwaye ga aur session mein add kre ga 

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retreive_all_threads() # is list mein saare create hue thread ki id store ho gy 


###                Creating a dumb assistant that echoes the user's message              ### 
# config = {'configurable':{'thread_id': st.session_state['thread_id'] }}

## agr hrr thread id k lye alag se observability add krny hai to ye config add krna ho ga

CONFIG = {'configurable':{'thread_id': st.session_state['thread_id'] },
          "meta data": {
              'thread_id': st.session_state['thread_id'] 
          },
          "run_name": "chat_turn"
          } 
 
user_input = st.chat_input("Type your message here...")

# message_history = [] # agr hmm koi history maintain nhi krty to jb bhi user koi input type krni hai to sirf wo hi dikhega, kyu k streamlit dubara se sara code execute krta hai, aur uss time pe user_input ke alawa koi aur message nahi hoga, isliye hum ek list bana lete hain jisme hum user ke messages ko store karenge, taki jab bhi user koi naya message type kare to hum uss list ko update kar sake aur purane messages bhi dikha sake.

# jb user ne enter ko preess krna hai to code saara dobara execute ho ga aur list hrr bar empy ho jaye gy .. hmein kisi aesi dictionary ki zroort hai jis mein values retain krein.

# st.session_state ek dictionary hai jisme hum apne variables ko store kar sakte hain, aur ye values tab tak retain rehti hain jab tak user session chal raha hota hai. isme hum message_history ko store karenge taki har baar user input dene par purane messages bhi dikha sake.
# ye sirf tb reset hoga jab user apna browser close karega ya session expire ho jayega ya manually refresh kya jaye ......





# ****************************************************** Creating Sidebar **************************************************************

st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Conversation"): # this function will create something new 
    reset_chat()

st.sidebar.header("My Conversations")

for thread_id in st.session_state['chat_threads'][::-1]:# Reverse list display ho gy .. naye chat top pr aye gy 
   if  st.sidebar.button(str(thread_id)): 
       st.session_state['thread_id'] = thread_id
       messages = load_conversations(thread_id)

       temp_message = []

       for msg in messages:
            if isinstance(msg,HumanMessage):
               role = 'user'
            else:
                role = 'assistant'
            temp_message.append({'role':role,'content':msg.content})
        
       st.session_state['message_history'] = temp_message






# ***********************************************************  Main UI  ******************************************************************

# Loading the conversation history 
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

if user_input:
    # first appent to message history
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)
    
    # Sending user input to chatbot 

    #response = workflow.invoke({'messages': [HumanMessage(content=user_input)]},config = config)
    # ai_message = response['messages'][-1].content
    # first append to message history
    # st.session_state["message_history"].append({"role": "assistant", "content": ai_message})
    with st.chat_message("assistant"):
        #st.text(ai_message)
        CONFIG = {'configurable':{'thread_id': st.session_state['thread_id'] },
          "meta data": {
              'thread_id': st.session_state['thread_id'] 
          },
          "run_name": "chat_turn"
          } 
 
        ai_message = st.write_stream(
            message_chunk.content for message_chunk,metadata in workflow.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config = CONFIG,
                stream_mode = 'messages'
            )
        )
    st.session_state["message_history"].append({"role": "assistant", "content": ai_message})

