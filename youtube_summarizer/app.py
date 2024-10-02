import os
import streamlit as st
from dotenv import load_dotenv
load_dotenv() 
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

from youtube_transcript_api import YouTubeTranscriptApi

prompt="""you are youtube vedio summarizer. 
you will be takeing the transcript text and summarizing the entire video and provideing the important summary, in points
within 250 words. the transcript text will be appended here :"""



def extract_transcript_details(youtube_video_url):
    try:
        video_id=youtube_video_url.split("=")[1]
        transcript_text=YouTubeTranscriptApi.get_transcript(video_id)

        transcript=""
        for i in transcript_text:
            transcript += " "+i["text"]

        return transcript
    
    except Exception as e:
        raise e


def generate_gemini_content(transcript_text,prompt):
    model=genai.GenerativeModel("gemini-pro")
    response=model.generate_content(prompt+transcript_text)
    return response.text



youtube_video_url="https://www.youtube.com/watch?v=IRD-fFFkVkQ"
transcript_text=extract_transcript_details(youtube_video_url)
print(transcript_text)
summary=generate_gemini_content(transcript_text,prompt)
print(summary)
