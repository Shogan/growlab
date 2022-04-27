import json
import os
import time
from datetime import datetime
from influxdb import InfluxDBClient
from sensors import growbme280, growbmp280

sensor_name = os.getenv("SENSOR")
sample_duration = 30  # seconds
sensor = None
sensor_type = os.getenv("SENSOR_TYPE", "bme280")
print("Sensor type: {}", sensor_type)

if sensor_type == "bme280":
    sensor = growbme280()
elif sensor_type == "bmp280":
    sensor = growbmp280()

def get_cpu_temp():
    path="/sys/class/thermal/thermal_zone0/temp"
    f = open(path, "r")
    temp_raw = int(f.read().strip())
    temp_cpu = float(temp_raw / 1000.0)
    return temp_cpu

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """

    # Parse NodeMCU data packet into JSON
    r = json.loads(req)

    influx_host = "192.168.2.69"
    influx_port = "8086"
    influx_db = "readings"

    influx_user = "root"
    influx_pass = "ojQikfArz5HycKfTyLHBBLU5"
    
    client = InfluxDBClient(influx_host, influx_port, influx_user, influx_pass, influx_db)
    try:
      client.create_database(influx_db)
    except:
      print("Database {} may already exist", influx_db)

    points = make_points(r)

    res = client.write_points(points)
    client.close()
    print("response: {}", res)

    return json.dumps(res)

def get_file(path):
    v = ""
    with open(path) as f:
        v = f.read()
        f.close()
    return v.strip()

def make_points(r):
    tags = {"sensor": r["sensor"]}
    my_date = datetime.now()
    iso_time = my_date.isoformat()
    points = []

    points.append({
      "measurement": "temp",
      "tags":  tags,
      "time": iso_time,
      "fields": {
        "value": float(r["temperature"])
      }
     })

    if "cpu_temperature" in r:
        points.append({
          "measurement": "cpu_temperature",
          "tags":  tags,
          "time": iso_time,
          "fields": {
            "value": float(r["cpu_temperature"])
          }
     })

    if "humidity" in r:
        points.append({
              "measurement": "humidity",
              "tags":  tags,
              "time": iso_time,
              "fields": {
              "value": float(r["humidity"])
             }
            })

    if "pressure" in r:
        points.append({
              "measurement": "pressure",
              "tags":  tags,
              "time": iso_time,
              "fields": {
              "value": float(r["pressure"])
             }
            })

    return points


try:
    while True:
        print("Gathering sensor data.")
        temp_cpu = get_cpu_temp()

        readings = sensor.get_readings()

        readings["sensor"] = sensor_name
        readings["cpu_temperature"] = temp_cpu

        my_date = datetime.now()
        readings["iso_time"] = my_date.isoformat()
        data = json.dumps(readings)
        print(data)

        try:
            res = handle(function_url, data=data, headers={"Content-type": "application/json"})
            if res.status_code != 200:
                print("Unexpected status code: {}".format(res.status_code))
            else:
                print("Sent to function..OK.")

        except Exception as e:
            print(e)
            continue
        time.sleep(sample_duration)

except KeyboardInterrupt:
    pass

