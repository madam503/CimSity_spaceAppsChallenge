from .services import get_weather_data, get_air_pollution_data
from .analysis import get_ndvi_for_area, get_natural_environment_info
from .ai_core import generate_insight

def get_city_environmental_insight(city_name: str):

    weather = get_weather_data(city_name)

    air_pollution = get_air_pollution_data(city_name)
    
    ndvi = get_ndvi_for_area(city_name)

    natural_env = get_natural_environment_info(city_name)

    insight = generate_insight(city_name, weather, air_pollution, ndvi, natural_env)

    return {
        "generated_insight": insight,
        "source_data": {
            "weather": weather,
            "air_pollution": air_pollution,
            "ndvi_analysis": ndvi,
            "natural_environment_profile": natural_env
        }
    }