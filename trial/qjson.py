import json

# def write_json(new_data, filename='subprocess/data.json'):
#     with open(filename,'r+') as file:
#         file_data = json.load(file)
#         file_data["calibration"].append(new_data)
#         file.seek(0)
#         json.dump(file_data, file, indent = 4)

# def load_json(object1, object2):
#     arr = []
#     with open('subprocess/data.json', 'r') as openfile:
#         json_object = json.load(openfile)

#     for project in json_object[object1]:
#         options = project["data"][object2]
#         arr.append(options)
#     return arr

# y =load_json("background", "phaseR")[-1]


# a_file = open("trial/sample.json", "r")
# json_object = json.load(a_file)
# # a_file.close()
# # print(json_object)
# # OUTPUT
# # {'a': {'b': 1, 'c': 2}, 'd': 3}


# json_object["registration"][0]["material"] = "kampung"
# a_file = open("trial/sample.json", "w")
# json.dump(json_object, a_file)
# a_file.close()
# print(json_object["registration"][0]["material"])



json_path = 'subprocess/data.json'
charge = 3
def write_json(new_data, filename=json_path):
    with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data["background"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent = 4)

def load_json(object1, object2):
    arr = []
    with open(json_path, 'r') as openfile:
        json_object = json.load(openfile)
    for project in json_object[object1]:
        options = project[object2]
        arr.append(options)
    return arr

def mod_json(valBMax,valCMax,valDMax):
    idx_project = load_json("calibration", "project").index('trial1')
    a_file = open(json_path, "r")
    json_object = json.load(a_file)
    volR = json_object["calibration"][idx_project]["phaseR"]["vol"][0]
    colR = json_object["calibration"][idx_project]["phaseR"]["col"][0]
    volS = json_object["calibration"][idx_project]["phaseS"]["vol"][0]
    colS = json_object["calibration"][idx_project]["phaseS"]["col"][0]
    volT = json_object["calibration"][idx_project]["phaseT"]["vol"][0]
    colT = json_object["calibration"][idx_project]["phaseT"]["col"][0]

    if volR == 0 and colR == 0 and volS == 0 and colS == 0 and volT == 0 and colT == 0:
        phaseR = {
            "vol": [valBMax],
            "col": [charge]
        }
        phaseS = {
            "vol": [valCMax],
            "col": [charge]
        }
        phaseT = {
            "vol": [valDMax],
            "col": [charge]
        }
        print("phaseR")
    else:
        volR = json_object["calibration"][idx_project]["phaseR"]["vol"]
        colR = json_object["calibration"][idx_project]["phaseR"]["col"]
        volS = json_object["calibration"][idx_project]["phaseS"]["vol"]
        colS = json_object["calibration"][idx_project]["phaseS"]["col"]
        volT = json_object["calibration"][idx_project]["phaseT"]["vol"]
        colT = json_object["calibration"][idx_project]["phaseT"]["col"]

        print(type(volR))
        print(volS)
        print(volT)
        print(colR)
        print(colS)
        print(colT)
        
        volR.append(valBMax)
        print(volR)
        print(volS.append(valCMax))
        print(volT.append(valDMax))
        print(colR)
        print(colS)
        print(colT)

        phaseR = {
            "vol": volR,
            "col": colR
        }
        phaseS = {
            "vol": volS,
            "col": colS 
        }
        phaseT = {
            "vol": volT,
            "col": colT
        }

mod_json(123,456,789)