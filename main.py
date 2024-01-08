import random

import requests
import logging
import redis
from fastapi import FastAPI, HTTPException, Query
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider

# Create FastAPI app
app = FastAPI()

# Set up the TracerProvider
trace.set_tracer_provider(TracerProvider())

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("open-telemetry.example")

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

# Connect to Redis
# Replace 'localhost' and '6379' with your Redis server's host and port if different
redis_client = redis.Redis(host='localhost', port=6379, db=0)

logger.info("hello from startup")

@app.get('/weather')
async def get_weather(latitude: float = Query(..., description="Latitude of the location"),
                      longitude: float = Query(..., description="Longitude of the location")):
    # This creates a new span that's the child of the current one
    with tracer.start_as_current_span("get_weather") as roll_span:
        if random.random() < 0.5:
            logger.error('Random error occurred')
            # Return an error response 50% of the time
            raise HTTPException(status_code=500, detail='Random error occurred')

        redisKey = 'weather_data_' + str(latitude) + '_' + str(longitude)

        logger.info('Checking Redis for weather data')

        redisData = redis_client.get(redisKey)
        if redisData is not None:
            logger.info('Found weather data in Redis')
            return redisData

        logger.info('Fetching weather data from Open-Meteo 2')
        # Define the parameters for your request here
        params = {
            'latitude': latitude,  # Example latitude
            'longitude': longitude,  # Example longitude
            'hourly': 'temperature_2m'
        }

        # Make a GET request to the Open-Meteo API using requests
        response = requests.get('https://api.open-meteo.com/v1/forecast', params=params)

        logger.info('Received response from Open-Meteo %s', response)
        if response.status_code == 200:
            # Set a key-value pair in Redis
            redis_client.set(redisKey, str(response.json()), ex=4)
            # Return the JSON response if the request was successful
            return response.json()
        else:
            # Handle errors
            raise HTTPException(status_code=500, detail='Failed to fetch data from Open-Meteo')
