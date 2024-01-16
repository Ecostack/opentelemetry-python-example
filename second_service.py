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
tracer = trace.get_tracer("open-telemetry.example.second-service")

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

logger.info("hello from startup second service")


@app.get('/test')
async def test():
    with tracer.start_as_current_span("second_service_http_test_server") as span:
        logger.info("test - hey there from the second service")
        return "Hey there"
