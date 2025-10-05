import ee
import pandas as pd
from city_env_toolkit.config import GEE_PROJECT_ID, CITIES

try:
    ee.Initialize(project=GEE_PROJECT_ID)
    print("Google Earth Engine has been initialized.")
except Exception as e:
    print(f"Google Earth Engine initialize error: {e}")

def get_ndvi_for_area(city_name: str):
    """Calculates the average NDVI for a specified region and returns it as a string."""
    city_info = CITIES[city_name]
    gee_name = city_info["gee_adm_name"]
    try:
        gaul_level1 = ee.FeatureCollection("FAO/GAUL/2015/level1")
        aoi = gaul_level1.filter(ee.Filter.eq('ADM1_NAME', gee_name)).first()
        
        if not aoi:
            return f"Could not find data for '{gee_name}'. Please use a correct administrative name."

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
            return f"The average NDVI value for {gee_name} on the most recent date ({image_date}) is {mean_ndvi:.4f}."
        else:
            return f"Could not retrieve NDVI data for {gee_name} for the specified period."
            
    except Exception as e:
        return f"An error occurred while calculating NDVI information: {e}"

def get_natural_environment_info(city_name: str):
    """Reads and analyzes a city's natural environment information from a CSV file and returns the result as a string."""
    city_info = CITIES[city_name]
    csv_path = city_info["csv_path"]

    #if 'Jeju' not in csv_path:
    #    return "Currently, natural environment information is only available for Jeju City."
        
    try:
        df = pd.read_csv(csv_path)
        df_cleaned = df[(df['canopy_height_m'] >= 0) & (df['canopy_height_m'] < 100)].copy()
        
        avg_canopy_height = df_cleaned['canopy_height_m'].mean()
        avg_canopy_openness = df_cleaned['canopy_openness_percent'].mean()
        urban_area_percentage = (df_cleaned['urban_flag'].sum() / len(df_cleaned)) * 100

        response = (
            f"Based on the {csv_path} file, here is the natural environment information for Jeju City:\n"
            f"- Average tree height: {avg_canopy_height:.2f} meters\n"
            f"- Average canopy openness: {avg_canopy_openness:.2f} %\n"
            f"- Urban area percentage among data points: {urban_area_percentage:.2f} %\n"
        )
        return response
        
    except FileNotFoundError:
        return f"Natural environment data file ({csv_path}) not found for {city_name}."
    except Exception as e:

        return f"An error occurred while analyzing natural environment information: {e}"
