from dotenv import load_dotenv
load_dotenv()

import os
import google.generativeai as genai
from PIL import Image

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model=genai.GenerativeModel('gemini-1.5-flash')

def get_gemini_response(input,image):
    if input!="":
        response=model.generate_content([input,image])
    else:
        response=model.generate_content(image)
    return response.text


input="write a caption for this image"
image=Image.open('data/image.jpg')
response=get_gemini_response(input,image)
print(response)
