import random

from flask import Flask, jsonify

import requests
import logging

import redis

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.flask import FlaskInstrumentor

app = Flask(__name__)

# Set up the TracerProvider
trace.set_tracer_provider(TracerProvider())

# Instrument Flask
FlaskInstrumentor().instrument_app(app)

# Connect to Redis
# Replace 'localhost' and '6379' with your Redis server's host and port if different
redis_client = redis.Redis(host='localhost', port=6379, db=0)


@app.route('/weather')
def get_weather():
    if random.random() < 0.5:
        # Return an error response 50% of the time
        return jsonify({'error': 'Random error occurred'}), 500

    logging.info('Fetching weather data from Open-Meteo')
    # Define the parameters for your request here
    params = {
        'latitude': 52.52,  # Example latitude
        'longitude': 13.41,  # Example longitude
        'hourly': 'temperature_2m'
    }

    # Make a GET request to the Open-Meteo API
    response = requests.get('https://api.open-meteo.com/v1/forecast', params=params)

    logging.info('Received response from Open-Meteo', response=response)
    if response.status_code == 200:
        # Set a key-value pair in Redis
        # Here 'my_key' is the key, and 'my_value' is the value
        redis_client.set('weather_data', str(response.json()))
        # Return the JSON response if the request was successful
        return jsonify(response.json())
    else:
        # Handle errors
        return jsonify({'error': 'Failed to fetch data from Open-Meteo'}), 500


if __name__ == '__main__':
    app.run(debug=False)
