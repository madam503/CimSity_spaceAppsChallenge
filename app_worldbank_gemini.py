from flask import Flask, jsonify
import requests
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@app.route('/')
def home():
    return "✅ Jeju-si Economic Data + Gemini Integration Running!"

@app.route('/get_data')
def get_data():
    # World Bank API Example (GDP, population, etc. for South Korea)
    url = "http://api.worldbank.org/v2/country/KR/indicator/NY.GDP.MKTP.CD?format=json"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch World Bank data"}), 500

    data = response.json()

    # Extract recent GDP value
    if len(data) > 1 and "value" in data[1][0]:
        gdp_value = data[1][0]["value"]
    else:
        gdp_value = "Unavailable"

    # Generate a Gemini-based summary
    prompt = f"Summarize Jeju-si's economic situation based on South Korea's GDP value of {gdp_value} USD."
    model = genai.GenerativeModel("gemini-pro")
    summary = model.generate_content(prompt)

    return jsonify({
        "country": "South Korea (Jeju-si focus)",
        "GDP (USD)": gdp_value,
        "Gemini Summary": summary.text
    })

if __name__ == "__main__":
    app.run(debug=True)
