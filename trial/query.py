from influxdb import InfluxDBClient
import json
import numpy as np
 
client = InfluxDBClient(host='127.0.0.1', port=8086, database='example')

# untuk multiple dataset
# result = client.query('select ayam from cpu_load_short order by time desc limit 2;')
# list_result = list(result)[0]
# json_result = json.loads(json.dumps(list_result))
# arr = []
# for project in json_result:
#     options = project['ayam']
#     arr.append(options)
# print(arr)
# print(np.array(arr))
# print(type(np.array(arr)))

# untuk single dataset
result = client.query('select kambing from trial_first order by time desc limit 1;')
array_points = list(result.get_points(measurement='trial_first'))
for element in array_points:
    array = np.array(json.loads(element['kambing']), dtype=object)

print(array)
print(array.size)