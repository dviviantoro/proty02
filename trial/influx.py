from influxdb import InfluxDBClient
import json
import numpy as np
 

list = [5, 27, 34, 54, 91] 
sample_array = np.array(list)

json_body = [
    {
        "measurement": "cpu_load_short",
        "tags": {
            "host": "server01",
            "region": "us-west"
        },
        # "time": "2009-11-10T23:00:00Z",
        "fields": {
            # "value": 31.3331
            "ayam": json.dumps(list)
        }
    }
]
client = InfluxDBClient(host='127.0.0.1', port=8086, database='example')
# client = InfluxDBClient('localhost', 8086, 'root', 'root', 'example')

# client.create_database('example')

client.write_points(json_body)

# result = client.query('select ayam from cpu_load_short;')

# print("Result: {}".format(result))