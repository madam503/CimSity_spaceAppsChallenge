import google.generativeai as genai
from city_env_toolkit.config import GOOGLE_API_KEY

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    print("Gemini model initialized for AI core.")
except Exception as e:
    model = None
    print(f"Warning: Gemini model initialization failed. {e}")

def generate_insight(city_name: str, weather_data, air_data, ndvi_info, natural_env_info):
    """Generates expert insight from Gemini by synthesizing all data."""
    if not model:
        return "AI model is not available."

    # 1. Construct rich context to send to Gemini
    context = f"""
    **1. Real-time Weather:** {weather_data}
    **2. Real-time Air Quality:** {air_data}
    **3. Satellite Vegetation Index:** {ndvi_info}
    **4. Natural Environment Profile:** {natural_env_info}
    """

    # 2. Generate the prompt
    prompt = f"""
    You are a leading urban environmental expert. Based on the following data for {city_name}, provide a concise, expert-level summary and insight in about 3-4 paragraphs. 
    Use headings to organize the information and conclude with a brief summary of key findings and recommendations.

    **Context:**
    {context}
    """

    # 3. Call Gemini and return the result
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI insight generation failed: {e}"