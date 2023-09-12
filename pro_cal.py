import sys
import time
import json
import ctypes
import redis
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import adc2mV, assert_pico_ok

json_path = 'subprocess/data.json'
r = redis.Redis(host='localhost', port=6379, db=0)

project =  r.get('project').decode()
charge = int(r.get('charge').decode())
iteration = int(r.get('iteration').decode())*3

chandle = ctypes.c_int16()
status = {}
status["openunit"] = ps.ps2000aOpenUnit(ctypes.byref(chandle), None)
assert_pico_ok(status["openunit"])

print("device started")

count = 0
arrR = []

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

def mod_json(valBMax):
    idx_project = load_json("calibration", "project").index(project)
    a_file = open(json_path, "r")
    json_object = json.load(a_file)
    xaxis = json_object["calibration"][idx_project]["xaxis"]
    volR = json_object["calibration"][idx_project]["volR"]

    if  xaxis == 0 and volR == 0:
        volR = valBMax
    else:
        volR.append(valBMax)
        xaxis.append(charge)

    json_object["calibration"][idx_project]["xaxis"] = xaxis
    json_object["calibration"][idx_project]["volR"] = volR
    a_file = open(json_path, "w")
    json.dump(json_object, a_file)
    a_file.close()    

def sigGen():
    wavetype = ctypes.c_int16(0)
    sweepType = ctypes.c_int32(0)
    triggertype = ctypes.c_int32(0)
    triggerSource = ctypes.c_int32(0)

    status["SetSigGenBuiltIn"] = ps.ps2000aSetSigGenBuiltIn(chandle,        #handle
                                                            0,              #offsetVoltage
                                                            1100000,         #pkToPk
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

chBRange = 7
# sigGen()
while (count < iteration):
    count = count + 1

    """Cahnnel Setup"""
    status["setChA"] = ps.ps2000aSetChannel(chandle, 0, 1, 1, chBRange, 0)
    assert_pico_ok(status["setChA"])
    status["setChB"] = ps.ps2000aSetChannel(chandle, 1, 1, 1, chBRange, 0)
    assert_pico_ok(status["setChB"])

    """Set up single trigger"""
    status["trigger"] = ps.ps2000aSetSimpleTrigger(chandle, 1, 0, 1024, 4, 0, 1000)
    assert_pico_ok(status["trigger"])

    preTriggerSamples = 207750*3
    postTriggerSamples = 207750*3
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

    overflow = ctypes.c_int16()
    cTotalSamples = ctypes.c_int32(totalSamples)
    status["getValues"] = ps.ps2000aGetValues(chandle, 0, ctypes.byref(cTotalSamples), 0, 0, 0, ctypes.byref(overflow))
    assert_pico_ok(status["getValues"])

    maxADC = ctypes.c_int16()
    status["maximumValue"] = ps.ps2000aMaximumValue(chandle, ctypes.byref(maxADC))
    assert_pico_ok(status["maximumValue"])

    # adc2mVChAMax =  np.array(adc2mV(bufferAMax, chARange, maxADC))
    adc2mVChAMax =  adc2mV(bufferAMax, chBRange, maxADC)
    adc2mVChBMax =  adc2mV(bufferBMax, chBRange, maxADC)
    
    valAMax = max(adc2mVChAMax)
    valAMin = min(adc2mVChAMax)

    valBMax = max(adc2mVChBMax)
    valBMin = min(adc2mVChBMax)

    if valBMax > valBMin*-1:
        max_val = valBMax
    else:
        max_val = valBMin*-1

    if max_val > 1999:
        chBRange = 9
    elif max_val > 999:
        chBRange = 8
    elif max_val > 499:
        chBRange = 7
    elif max_val > 199:
        chBRange = 6
    elif max_val > 99:
        chBRange = 5
    elif max_val > 49:
        chBRange = 4
    elif max_val > 24:
        chBRange = 3
    elif max_val > 9:
        chBRange = 2
    elif max_val < 9:
        chBRange = 1
    time.sleep(0.25)

    print(max_val)
    print(chBRange)
    
    r.set('count', count)

    if count%3 == 0:
        if count == iteration:
            mod_json(valBMax)

        print("acq",end="=")
        print(count,flush=True)
        time.sleep(1)
    
status["stop"] = ps.ps2000aStop(chandle)
assert_pico_ok(status["stop"])

status["close"] = ps.ps2000aCloseUnit(chandle)
assert_pico_ok(status["close"])

print('finish')