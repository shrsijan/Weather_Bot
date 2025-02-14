from flask import Flask, render_template, request, jsonify
import ollama
from weather_fetcher import get_weather

app = Flask(__name__)

def get_llm_recommendations(weather_info):
    # Construct prompt for the LLM
    prompt = f"""    
    
Based on the current weather conditions:

Temperature: {weather_info['temperature']}°C
Feels Like: {weather_info['feels_like']}°C
Humidity: {weather_info['humidity']}%
Weather Condition: {weather_info['description']}
Wind Speed: {weather_info['wind_speed']} mph
Please provide a structured and detailed report including:

1. Weather Summary
Briefly describe the overall weather conditions in a clear and professional tone.
2. Clothing Recommendations
Suggest appropriate clothing based on the temperature, wind, and humidity levels.
Be practical and specific (e.g., type of fabric, layering suggestions, and accessories like hats or gloves if necessary).
3. Weather Advisory
Highlight any potential concerns (e.g., low visibility, extreme temperatures, wind effects).
Provide safety tips for individuals who need to be outdoors.
4. Suggested Activities
Recommend both indoor and outdoor activities that align with the weather conditions.
Be diverse in suggestions (e.g., recreational activities, work-from-home adjustments, fitness recommendations).
Ensure the response is concise, well-structured, and easy to read. Avoid redundancy and maintain a professional yet approachable tone."""
    
    try:
        # Get response from Deepseek model
        response = ollama.chat(model="llama3", messages=[
            {
                "role": "user",
                "content": prompt
            }
        ])
        # Filter out unwanted content
        recommendations = response['message']['content']
        filtered_recommendations = filter_recommendations(recommendations)
        return filtered_recommendations
    except ollama._types.ResponseError as e:
        return f"Error: {e}"

def filter_recommendations(recommendations):
    # Implement filtering logic to remove unwanted content inside <think> tags
    import re
    filtered_recommendations = re.sub(r'<think>.*?</think>', '', recommendations, flags=re.DOTALL)
    return filtered_recommendations.strip()

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        data = request.get_json()
        location = data['location']
        weather_info = get_weather(location)
        
        if isinstance(weather_info, dict):
            recommendations = get_llm_recommendations(weather_info)
            return jsonify({'recommendations': recommendations})
        else:
            return jsonify({'error': weather_info})
    
    return render_template('weather_input.html')

@app.route('/closing')
def closing():
    return render_template('closing.html')

if __name__ == "__main__":
    app.run(debug=True)