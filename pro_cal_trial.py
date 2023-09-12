import sys
import time
import json
import ctypes
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import adc2mV, assert_pico_ok

json_path = 'subprocess/data.json'

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
    idx_project = load_json("calibration", "project").index(project)
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
        volR.append(valBMax)
        volS.append(valCMax)
        volT.append(valDMax)
        colR.append(charge)
        colS.append(charge)
        colT.append(charge)

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
        print(volR)
        print(volS)
        print(volT)
        print(colR)
        print(colS)
        print(colT)

    json_object["calibration"][idx_project]["phaseR"] = phaseR
    a_file = open(json_path, "w")
    json.dump(json_object, a_file)
    a_file.close()

    json_object["calibration"][idx_project]["phaseS"] = phaseS
    a_file = open(json_path, "w")
    json.dump(json_object, a_file)
    a_file.close()
    
    json_object["calibration"][idx_project]["phaseT"] = phaseT
    a_file = open(json_path, "w")
    json.dump(json_object, a_file)
    a_file.close()
    
    print("saved to json")
    

def sigGen():
    wavetype = ctypes.c_int16(0)
    sweepType = ctypes.c_int32(0)
    triggertype = ctypes.c_int32(0)
    triggerSource = ctypes.c_int32(0)

    status["SetSigGenBuiltIn"] = ps.ps2000aSetSigGenBuiltIn(chandle,        #handle
                                                            0,              #offsetVoltage
                                                            1000000,         #pkToPk
                                                            wavetype,       #waveType
                                                            50,             #startFrequency
                                                            50,             #stopFrequency
                                                            0,              #increment
                                                            0,              #dwelltime
                                                            sweepType,      #sweepTime
                                                            0,              #operation
                                                            0,              #shots
                                                            0,              #sweeps
                                                            triggertype,    #triggerType
                                                            triggerSource,  #triggerSource
                                                            1)              #extInThreshold 
    assert_pico_ok(status["SetSigGenBuiltIn"])

my_input = sys.argv
project = my_input[1]
charge = int(my_input[2])
nsample = int(my_input[3])

chandle = ctypes.c_int16()
status = {}
status["openunit"] = ps.ps2000aOpenUnit(ctypes.byref(chandle), None)
assert_pico_ok(status["openunit"])

print("device started")

count = 0
arrR = []
arrS = []
arrT = []

# while (count < 5):
while (count < nsample):
# while True:
    sigGen()
    count = count + 1
    # print("loop: ", count)

    """Cahnnel Setup"""
    chRange_bgn = 7
    status["setChA"] = ps.ps2000aSetChannel(chandle, 0, 1, 1, chRange_bgn, 0)
    assert_pico_ok(status["setChA"])
    status["setChB"] = ps.ps2000aSetChannel(chandle, 1, 1, 1, chRange_bgn, 0)
    assert_pico_ok(status["setChB"])
    status["setChD"] = ps.ps2000aSetChannel(chandle, 2, 1, 1, chRange_bgn, 0)
    assert_pico_ok(status["setChD"])
    status["setChE"] = ps.ps2000aSetChannel(chandle, 3, 1, 1, chRange_bgn, 0)
    assert_pico_ok(status["setChE"])

    """Set up single trigger"""
    status["trigger"] = ps.ps2000aSetSimpleTrigger(chandle, 1, 0, 1024, 4, 0, 1000)
    assert_pico_ok(status["trigger"])
    # status["trigger"] = ps.ps2000aSetSimpleTrigger(chandle, 1, 1, 1024, 4, 0, 1000)
    # assert_pico_ok(status["trigger"])
    # status["trigger"] = ps.ps2000aSetSimpleTrigger(chandle, 1, 2, 1024, 4, 0, 1000)
    # assert_pico_ok(status["trigger"])
    # status["trigger"] = ps.ps2000aSetSimpleTrigger(chandle, 1, 3, 1024, 4, 0, 1000)
    # assert_pico_ok(status["trigger"])

    preTriggerSamples = 207750
    postTriggerSamples = 207750
    totalSamples = preTriggerSamples + postTriggerSamples
    
    timebase = 8
    timeIntervalns = ctypes.c_float()
    returnedMaxSamples = ctypes.c_int32()
    oversample = ctypes.c_int16(0)
    status["getTimebase2"] = ps.ps2000aGetTimebase2(chandle,                #handle
                                                    timebase,               #timebase
                                                    totalSamples,           #noSample
                                                    ctypes.byref(timeIntervalns), #pointer to timeIntervalNanoseconds
                                                    oversample,             #pointer to totalSample
                                                    ctypes.byref(returnedMaxSamples),   
                                                    0)                      #segment index
    assert_pico_ok(status["getTimebase2"])

    status["runBlock"] = ps.ps2000aRunBlock(chandle,            #handle
                                            preTriggerSamples,  #number of pre-trigger samples
                                            postTriggerSamples, #number of post-trigger samples
                                            timebase,           #timebase
                                            oversample,         #oversample
                                            None,               #time indisposed ms
                                            0,                  #segment index
                                            None,               #LpReady
                                            None)               #pParameter
    assert_pico_ok(status["runBlock"])

    # Check for data collection to finish using ps2000aIsReady
    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
    while ready.value == check.value:
        status["isReady"] = ps.ps2000aIsReady(chandle, ctypes.byref(ready))

    # Create buffers ready for assigning pointers for data collection
    bufferAMax = (ctypes.c_int16 * totalSamples)()
    bufferAMin = (ctypes.c_int16 * totalSamples)()
    bufferBMax = (ctypes.c_int16 * totalSamples)()
    bufferBMin = (ctypes.c_int16 * totalSamples)()
    bufferCMax = (ctypes.c_int16 * totalSamples)()
    bufferCMin = (ctypes.c_int16 * totalSamples)()
    bufferDMax = (ctypes.c_int16 * totalSamples)()
    bufferDMin = (ctypes.c_int16 * totalSamples)()

    status["setDataBuffersA"] = ps.ps2000aSetDataBuffers(chandle,                   #hamdle
                                                        0,                         #source
                                                        ctypes.byref(bufferAMax),  #pointer to buffer max
                                                        ctypes.byref(bufferAMin),  #pointer to buffer min
                                                        totalSamples,              #buffer length
                                                        0,                         #segment index
                                                        0)                         #ratio mode
    assert_pico_ok(status["setDataBuffersA"])
    status["setDataBuffersB"] = ps.ps2000aSetDataBuffers(chandle,                   #hamdle
                                                        1,                         #source
                                                        ctypes.byref(bufferBMax),  #pointer to buffer max
                                                        ctypes.byref(bufferBMin),  #pointer to buffer min
                                                        totalSamples,              #buffer length
                                                        0,                         #segment index
                                                        0)                         #ratio mode
    assert_pico_ok(status["setDataBuffersB"])
    status["setDataBuffersC"] = ps.ps2000aSetDataBuffers(chandle,                   #hamdle
                                                        2,                         #source
                                                        ctypes.byref(bufferCMax),  #pointer to buffer max
                                                        ctypes.byref(bufferCMin),  #pointer to buffer min
                                                        totalSamples,              #buffer length
                                                        0,                         #segment index
                                                        0)                         #ratio mode
    assert_pico_ok(status["setDataBuffersC"])
    status["setDataBuffersD"] = ps.ps2000aSetDataBuffers(chandle,                   #hamdle
                                                        3,                         #source
                                                        ctypes.byref(bufferDMax),  #pointer to buffer max
                                                        ctypes.byref(bufferDMin),  #pointer to buffer min
                                                        totalSamples,              #buffer length
                                                        0,                         #segment index
                                                        0)                         #ratio mode
    assert_pico_ok(status["setDataBuffersD"])

    overflow = ctypes.c_int16()
    cTotalSamples = ctypes.c_int32(totalSamples)
    status["getValues"] = ps.ps2000aGetValues(chandle, 0, ctypes.byref(cTotalSamples), 0, 0, 0, ctypes.byref(overflow))
    assert_pico_ok(status["getValues"])

    maxADC = ctypes.c_int16()
    status["maximumValue"] = ps.ps2000aMaximumValue(chandle, ctypes.byref(maxADC))
    assert_pico_ok(status["maximumValue"])

    # adc2mVChAMax =  np.array(adc2mV(bufferAMax, chARange, maxADC))
    adc2mVChAMax =  adc2mV(bufferAMax, chRange_bgn, maxADC)
    adc2mVChBMax =  adc2mV(bufferBMax, chRange_bgn, maxADC)
    adc2mVChCMax =  adc2mV(bufferCMax, chRange_bgn, maxADC)
    adc2mVChDMax =  adc2mV(bufferDMax, chRange_bgn, maxADC)
    
    valAMax = max(adc2mVChAMax)
    valBMax = max(adc2mVChBMax)
    valCMax = max(adc2mVChCMax)
    valDMax = max(adc2mVChDMax)

    print("acq",end="=")
    print(count,flush=True)

    half = int(len(df)/2)
    quarter = int(len(df)/4)
    thirdqua = int(len(df)*3/4)


    if count == nsample:
        mod_json(valBMax, valCMax, valDMax)

    time.sleep(1)
    
status["stop"] = ps.ps2000aStop(chandle)
assert_pico_ok(status["stop"])

status["close"] = ps.ps2000aCloseUnit(chandle)
assert_pico_ok(status["close"])

print('finish')