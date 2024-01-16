import requests
import logging
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
tracer = trace.get_tracer("open-telemetry.part1")

# Setup the logger and set minimum log level to info, everything below will not be logged
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Instrument FastAPI and Requests
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

# Example logging from part 1
logger.info("hello from part 1")

# Tracer annotation which will automatically create a span for this function
@tracer.start_as_current_span("fetch_data_from_open_meteo")
def fetch_data_from_open_meteo(latitude, longitude):
    # Alternative way of creating a span
    # with tracer.start_as_current_span("fetch_data_from_open_meteo") as span:

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


# Endpoint for getting weather data, defined via annotation and using Query parameters
@app.get('/weather')
async def get_weather(latitude: float = Query(..., description="Latitude of the location"),
                      longitude: float = Query(..., description="Longitude of the location")):
    data = fetch_data_from_open_meteo(latitude, longitude)

    return data
