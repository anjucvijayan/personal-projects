from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the generative AI model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")


# Initialize Flask app
app = Flask(__name__)

@app.route('/generate', methods=['GET', 'POST'])
def get_gemini_response():
    
    if request.method == "POST":
        # Get the 'question' from the JSON body in a POST request
        # data = request.get_json()
        # question = data.get("question")
        question = request.get_data(as_text=True)

    # Ensure question is provided
    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Generate the response from the AI model
    response = model.generate_content(question)
    
    # Return the AI model's response as JSON
    return jsonify({"response": response.text})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
