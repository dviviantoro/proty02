import numpy as np
import json
# from influxdb import InfluxDBClient

temp_json_path = 'subprocess/temp.json'

# def query():
#     global com_arr,new_arr,new_maxR,new_maxS,new_maxT,new_minR,new_minS,new_minT

#     client = InfluxDBClient(host='127.0.0.1', port=8086, database='example')
#     result = client.query('select kambing from trial_first order by time desc limit 1;')
#     array_points = list(result.get_points(measurement='trial_first'))
#     for element in array_points:
#         new_arr = np.array(json.loads(element['kambing']), dtype=object)
#     print(new_arr)
#     print("query done")

def load_temp_json():
    a_file = open(temp_json_path,"r")
    # json_object = json.load(a_file)
    json_object = json.load(a_file)
    new_count = json_object["iteration"][0]["count"]
    new_maxR = json_object["iteration"][0]["maxR"]
    new_minR = json_object["iteration"][0]["minR"]
    new_maxS = json_object["iteration"][0]["maxS"]
    new_minS = json_object["iteration"][0]["minS"]
    new_maxT = json_object["iteration"][0]["maxT"]
    new_minT = json_object["iteration"][0]["minT"]
    # new_arr = np.array(json.loads(json_object["iteration"][0]["arr"]), dtype=object)
    new_arr = np.array(json.loads(json.dumps(json_object["iteration"][0]["arr"])), dtype=object)

    filtered = new_arr[new_arr[:,1]>2000]
    size_filtered = new_arr[new_arr[:,1]>2000].size
    try:
        max_filtered = filtered[:,1].max(axis=0)
    except:
        max_filtered = []

    # maxArr = new_arr[:,1].max(axis=0)
    # minArr = new_arr[:,1].min(axis=0)
    # nPosArr = new_arr[new_arr[:,1]>0].size
    # nNegArr = new_arr[new_arr[:,1]<0].size
    # nArr = new_arr.size

    print(new_arr)
    # print(maxArr)
    # print(minArr)
    # print(nPosArr)
    # print(nNegArr)
    # print(nArr)
    # print(new_maxT)
    print(filtered)
    print(size_filtered)
    print(max_filtered)

    if max_filtered == [1]:
        print("kosong")
    trial = np.append(filtered,max_filtered)
    print(trial)

load_temp_json()
# query()