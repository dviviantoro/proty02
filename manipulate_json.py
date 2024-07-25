import json

json_path = 'database/cal.json'

# def write_json(new_data, filename=json_path):
#     with open(filename,'r+') as file:
#         file_data = json.load(file)
#         file_data["background"].append(new_data)
#         file.seek(0)
#         json.dump(file_data, file, indent = 4)

# def load_json(object1, object2):
#     arr = []
#     with open(json_path, 'r') as openfile:
#         json_object = json.load(openfile)
#     for project in json_object[object1]:
#         options = project[object2]
#         arr.append(options)
#     return arr

# def mod_json(valBMax, valBMin):
#     idx_project = load_json("background", "project").index(project)
#     a_file = open(json_path, "r")
#     json_object = json.load(a_file)
#     xaxis = json_object["background"][idx_project]["xaxis"]
#     volR = json_object["background"][idx_project]["volR"]

#     volR.append(valBMax)
#     volR.append(valBMin)
#     xaxis.append(len(volR)/2)

#     json_object["background"][idx_project]["xaxis"] = xaxis
#     json_object["background"][idx_project]["volR"] = volR
    
#     a_file = open(json_path, "w")
#     json.dump(json_object, a_file)
#     a_file.close()

# load json file
def load_json():
    with open(json_path, 'r') as openfile:
        json_object = json.load(openfile)
        return json_object

def get_xy(index):
    arr_charge = []
    arr_volt = []
    loaded_data = load_json()
    for element in loaded_data[index]['data']:
        arr_charge.append(element['charge'])
        arr_volt.append(element['volt'])
    # print(arr_charge)
    # print(arr_volt)
    return arr_charge, arr_volt
# for project in json_object[object1]:
#     options = project[object2]
#     arr.append(options)

# get_xy()