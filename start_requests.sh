#!/usr/bin/env bash

while true
do
  curl http://127.0.0.1:5000/weather -v
  sleep 10
done