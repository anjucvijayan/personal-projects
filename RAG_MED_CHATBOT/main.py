import streamlit as st
#from create_memmory import *
from connect_memory import *


def main():
    st.title("Medical Chatbot")

    if 'messages' not in st.session_state:
        st.session_state.messages = [] 
    for message in st.session_state.messages:
        st.chat_message(message['role']).markdown(message['content'])

    prompt = st.chat_input("write your Query here")


    if prompt:
        st.chat_message('user').markdown(prompt)
        st.session_state.messages.append({'role':'user','content':prompt})
        res = response(prompt)
        print(res)
        st.chat_message('assistant').markdown(res)
        st.session_state.messages.append({'role':'assistant','content':res})

# try:
#     vectorstore = get_vectorstore()
#     if vectorstore is None:
#         st.error("Failed to load the vector store")
# except:
#     pass  

if __name__ == "__main__":
    main()

