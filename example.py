from city_env_toolkit.toolkit import get_city_environmental_insight

def main():
    print("="*40)
    print("City Environmental Analysis Toolkit Chatbot")
    print("Please enter the name of the city you want to analyze to get started.")
    print("Enter 'exit' to quit.")
    print("="*40)

    while True:
        city = input("Select a city to analyze (e.g., Jeju, Seoul, Busan): ")

        if city.lower() == 'exit':
            print("Shutting down the chatbot.")
            break

        print(f"\nStarting environmental analysis for {city}...")
        result = get_city_environmental_insight(city)
        
        print("\n--- AI Comprehensive Analysis Result ---")
        print(result["generated_insight"])
        print("-" * 25)

if __name__ == "__main__":
    main()