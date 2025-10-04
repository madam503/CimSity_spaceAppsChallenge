import google.generativeai as genai
import pandas as pd
import ee
from apiFile import GOOGLE_API_KEY

# --- 1. API and GEE Initialization ---
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except (KeyError, AttributeError):
    print("Please set your GOOGLE_API_KEY in apiFile.py.")
    exit()

try:
    ee.Initialize(project='pivotal-bonbon-342314')
    print("Google Earth Engine initialization successful!")
except Exception as e:
    print(f"GEE initialization failed: {e}")
    pass

# --- 2. Prompt Generation Function ---
def create_prompt_with_context(user_question, context=None):
    if context:
        prompt_core = f"""
        **Instructions:**
        - Based on the provided 'Context' information, answer the user's question.
        - The answer should be a **concise summary of 4-5 sentences** focusing on the key points.
        - Get straight to the point without unnecessary introductions or extra explanations.
        - Respond in a clear and eloquent style from the perspective of an expert.

        **Context:**
        {context}
        """
    else:
        prompt_core = """
        **Instructions:**
        - Based on your knowledge of global urban environments, answer the user's question.
        - The answer should be a **concise summary of 4-5 sentences** focusing on the key points.
        - Get straight to the point without unnecessary introductions or extra explanations.
        - Respond in a clear and eloquent style from the perspective of an expert.
        """

    prompt = f"""
    You are a top urban environmental expert.
    {prompt_core}

    **User Question:**
    {user_question}
    """
    return prompt

# --- 3. NDVI Calculation Function ---
def get_ndvi_for_area(area_name):
    """Calculates the average NDVI for a specified region and returns it as a string."""
    try:
        gaul_level1 = ee.FeatureCollection("FAO/GAUL/2015/level1")
        aoi = gaul_level1.filter(ee.Filter.eq('ADM1_NAME', area_name)).first()
        
        if not aoi:
            return f"Could not find data for '{area_name}'. Please use a correct administrative name."

        ndvi_collection = ee.ImageCollection('MODIS/061/MOD13Q1').filterDate('2024-01-01', '2024-12-31')
        latest_image = ndvi_collection.sort('system:time_start', False).first()
        ndvi = latest_image.select('NDVI').multiply(0.0001)

        mean_ndvi_dict = ndvi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi.geometry(),
            scale=250
        ).getInfo()
        
        mean_ndvi = mean_ndvi_dict.get('NDVI')
        
        if mean_ndvi is not None:
            image_date = ee.Date(latest_image.get('system:time_start')).format('YYYY-MM-dd').getInfo()
            return f"The average NDVI value for {area_name} on the most recent date ({image_date}) is {mean_ndvi:.4f}."
        else:
            return f"Could not retrieve NDVI data for {area_name} for the specified period."
            
    except Exception as e:
        return f"An error occurred while calculating NDVI information: {e}"

# --- 4. Natural Environment Information Retrieval Function ---
def get_natural_environment_info(city_name):
    """Reads and analyzes a city's natural environment information from a CSV file and returns the result as a string."""
    if 'Jeju' not in city_name:
        return "Currently, natural environment information is only available for Jeju City."
        
    try:
        df = pd.read_csv('jeju_atl08_analysis.csv')
        df_cleaned = df[(df['canopy_height_m'] >= 0) & (df['canopy_height_m'] < 100)].copy()
        
        avg_canopy_height = df_cleaned['canopy_height_m'].mean()
        avg_canopy_openness = df_cleaned['canopy_openness_percent'].mean()
        urban_area_percentage = (df_cleaned['urban_flag'].sum() / len(df_cleaned)) * 100

        response = (
            f"Based on the jeju_atl08_analysis.csv file, here is the natural environment information for Jeju City:\n"
            f"- Average tree height: {avg_canopy_height:.2f} meters\n"
            f"- Average canopy openness: {avg_canopy_openness:.2f} %\n"
            f"- Urban area percentage among data points: {urban_area_percentage:.2f} %\n"
        )
        return response
        
    except FileNotFoundError:
        return "Natural environment data file (jeju_atl08_analysis.csv) not found."
    except Exception as e:
        return f"An error occurred while analyzing natural environment information: {e}"

# --- 5. Main Execution Logic ---
def main():
    print("Loading Gemini model...")
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    print("Model loading complete!")

    chat = model.start_chat(history=[])
    
    MAX_HISTORY_TURNS = 10
    MAX_MESSAGES = MAX_HISTORY_TURNS * 2

    print("\nAsk me about urban environments!")

    city_mapping = {
        'jeju': 'Cheju-do',
        'seoul': 'Seoul',
        'busan': 'Pusan',
        'daegu': 'Taegu',
        'daejeon': 'Taejon'
    }

    while True:
        user_question = input("Question: ")
        stop_keywords = ['exit', 'stop', 'quit', 'end']
        if any(keyword in user_question.lower() for keyword in stop_keywords):
            print("Ending the conversation.")
            break
        
        context = None

        # 1. Handle natural environment questions
        if 'natural environment' in user_question.lower():
            city_name = next((key for key in city_mapping if key in user_question.lower()), 'jeju')
            print(f"Analyzing natural environment information for {city_name}...")
            context = get_natural_environment_info(city_name)

        # 2. Handle NDVI related questions
        elif 'ndvi' in user_question.lower():
            area_name = next((value for key, value in city_mapping.items() if key in user_question.lower()), city_mapping['jeju'])
            
            # Check for comparison requests
            if any(k in user_question.lower() for k in ['compare', 'other cities', 'higher']):
                print("Analyzing NDVI for major cities for comparison...")
                jeju_ndvi_str = get_ndvi_for_area(city_mapping['jeju'])
                comparison_data = {key: get_ndvi_for_area(value) for key, value in city_mapping.items()}
                
                context = f"Jeju NDVI: {jeju_ndvi_str}\n"
                for city, ndvi_info in comparison_data.items():
                    context += f"{city} NDVI: {ndvi_info}\n"
            else:
                print(f"Calculating NDVI information for {area_name}...")
                context = get_ndvi_for_area(area_name)
        
        # 3. All answers are now generated via the Gemini model
        prompt = create_prompt_with_context(user_question, context)
        response = model.generate_content(prompt, generation_config={"candidate_count":1})
        print(f"Gemini Answer: {response.text}")

        # Update chat history
        chat.history.extend([
            {'role': 'user', 'parts': [user_question]},
            {'role': 'model', 'parts': [response.text]}
        ])

if __name__ == "__main__":
    main()