#!/bin/bash

export FUNCTION_URL="http://192.168.2.45:8080/function/submit-sample-to-influxdb"
export SENSOR="growlab"
export SENSOR_TYPE="bmp280"
python3 main.py

