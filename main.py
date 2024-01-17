import random

import requests
import logging
import redis
from fastapi import FastAPI, HTTPException, Query
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)

metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
provider = MeterProvider(metric_readers=[metric_reader])

# Sets the global default meter provider
metrics.set_meter_provider(provider)

# Creates a meter from the global meter provider
meter = metrics.get_meter("my.meter.name")

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



exceptions_raised_counter = meter.create_counter(
    "exceptions.raised", unit="1", description="Counts the amount of exceptions raised"
)


def maybe_raise_random_error():
    # This creates a new span that's the child of the current one
    with tracer.start_as_current_span("maybe_raise_random_error") as span:
        if random.random() < 0.5:
            exceptions_raised_counter.add(1, {"exception.type": HTTPException})
            logger.error('Random error occurred')
            # Return an error response 50% of the time
            raise HTTPException(status_code=500, detail='Random error occurred')


def get_redis_key(latitude, longitude):
    return 'weather_data_' + str(latitude) + '_' + str(longitude)


def get_data_from_redis(latitude, longitude):
    with tracer.start_as_current_span("get_data_from_redis") as span:
        logger.info('Checking Redis for weather data')
        redisKey = get_redis_key(latitude, longitude)
        redisData = redis_client.get(redisKey)
        if redisData is not None:
            logger.info('Found weather data in Redis')
            return redisData


def store_data_in_redis(latitude, longitude, data):
    with tracer.start_as_current_span("store_data_in_redis") as span:
        logger.info('Storing weather data in Redis')
        redisKey = get_redis_key(latitude, longitude)
        redis_client.set(redisKey, str(data), ex=4)


def fetch_data_from_open_meteo(latitude, longitude):
    with tracer.start_as_current_span("fetch_data_from_open_meteo") as span:
        logger.info('Fetching weather data from Open-Meteo')
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
            return response.json()
        else:
            # Handle errors
            raise HTTPException(status_code=500, detail='Failed to fetch data from Open-Meteo')


def request_second_service_http_request():
    with tracer.start_as_current_span("request_second_service_http_request") as span:
        logger.info('Requesting second service')
        response = requests.get('http://localhost:8001/test')
        logger.info('Received response from second service %s', response)
        if response.status_code == 200:
            return response.json()
        else:
            # Handle errors
            raise HTTPException(status_code=500, detail='Failed to fetch data from second service')


@app.get('/weather')
async def get_weather(latitude: float = Query(..., description="Latitude of the location"),
                      longitude: float = Query(..., description="Longitude of the location")):
    maybe_raise_random_error()

    request_second_service_http_request()

    redisData = get_data_from_redis(latitude, longitude)
    if redisData is not None:
        return redisData

    data = fetch_data_from_open_meteo(latitude, longitude)

    store_data_in_redis(latitude, longitude, data)

    return data
