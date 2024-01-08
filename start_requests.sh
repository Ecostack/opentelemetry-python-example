#!/usr/bin/env bash

while true
do
  curl "http://127.0.0.1:8000/weather?latitude=52.374&longitude=4.8897" -v
  sleep 1
done