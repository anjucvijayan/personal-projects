from main import result
import streamlit as st


def main():
    st.title("YouTube Summarizer")

    url = st.chat_input("paste your url here...")

    if url:
        st.chat_message('user').markdown(url)
        res = result(url)
        print(res)
        st.chat_message('assistant').markdown(res)
    else :
        st.error('please give your url')




if __name__ == "__main__":
    main()