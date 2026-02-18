import streamlit as st
from backend import workflow
from langchain_core.messages import  HumanMessage

# with st.chat_message("user"):
#     st.text("Hello, how are you?")

# with st.chat_message("assistant"):
#     st.text("I'm doing well, thank you for asking! How can I assist you today?")

# user_input = st.chat_input("Type your message here...")

# if user_input:
#     with st.chat_message("user"):
#         st.text(user_input)

###                Creating a dumb assistant that echoes the user's message              ### 
config = {'configurable':{'thread_id': 'thread_id'}}
 
user_input = st.chat_input("Type your message here...")

# message_history = [] # agr hmm koi history maintain nhi krty to jb bhi user koi input type krni hai to sirf wo hi dikhega, kyu k streamlit dubara se sara code execute krta hai, aur uss time pe user_input ke alawa koi aur message nahi hoga, isliye hum ek list bana lete hain jisme hum user ke messages ko store karenge, taki jab bhi user koi naya message type kare to hum uss list ko update kar sake aur purane messages bhi dikha sake.

# jb user ne enter ko preess krna hai to code saara dobara execute ho ga aur list hrr bar empy ho jaye gy .. hmein kisi aesi dictionary ki zroort hai jis mein values retain krein.

# st.session_state ek dictionary hai jisme hum apne variables ko store kar sakte hain, aur ye values tab tak retain rehti hain jab tak user session chal raha hota hai. isme hum message_history ko store karenge taki har baar user input dene par purane messages bhi dikha sake.
# ye sirf tb reset hoga jab user apna browser close karega ya session expire ho jayega ya manually refresh kya jaye ......

if "message_history" not in st.session_state:
    st.session_state["message_history"] = [] #session state me message history naam ki key bnayen ge aur us ko initialize krein ge

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
    response = workflow.invoke({'messages': [HumanMessage(content=user_input)]},config = config)
    ai_message = response['messages'][-1].content
    # first append to message history
    st.session_state["message_history"].append({"role": "assistant", "content": ai_message})
    with st.chat_message("assistant"):
        st.text(ai_message)