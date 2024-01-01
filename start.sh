#!/usr/bin/env bash

#export GRPC_VERBOSITY=debug
#export GRPC_TRACE=http,call_error,connectivity_state

export OTEL_SERVICE_NAME=opentelemetry-example

export OTEL_TRACES_EXPORTER=console,otlp
export OTEL_LOGS_EXPORTER=otlp
export OTEL_METRICS_EXPORTER=otlp

export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
export OTEL_PYTHON_LOG_CORRELATION=true

# Enable gzip compression.
export OTEL_EXPORTER_OTLP_COMPRESSION=gzip
# Prefer delta temporality.
export OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE=DELTA

# Uptrace Login
export OTEL_EXPORTER_OTLP_HEADERS="uptrace-dsn=http://SomeRandomToken@localhost:14318?grpc=14317"

# Export endpoint, local Uptrace instance
export OTEL_EXPORTER_OTLP_ENDPOINT=127.0.0.1:14317
export OTEL_EXPORTER_OTLP_INSECURE=true

opentelemetry-instrument python3 main.py
#opentelemetry-instrument flask --app main.py run