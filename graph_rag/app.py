import streamlit as st
import pandas as pd

from model import *

st.markdown("<h1 style='text-align: center;'>Retail Customer Segmentation</h1>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>Graph RAG APP</h1>", unsafe_allow_html=True)

sample_questions = [
    "Segment customers by age group and show average spending",
    "What are the top 5 resolved ticket catgeories",
    "What are common support issues and resolution times?",
]

# Dropdown to select sample question
selected_question = st.selectbox("Select a Sample Question", [""] + sample_questions)

# Prefill text input with selected sample question
question1 = st.text_input("Ask a Question:", value=selected_question if selected_question else "", key="input")


#question1 = st.text_input("Ask Question: ",key="input")
if question1:
    output = process_query(question1)
    print(output)
    st.markdown(f"**Question:** {output['question']}")


    df = pd.DataFrame(output['results'])
    st.dataframe(df)