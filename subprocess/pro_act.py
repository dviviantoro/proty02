import ctypes
import numpy as np
import pandas as pd
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import adc2mV, assert_pico_ok
import plotly.express as px
import time
import sys
from influxdb import InfluxDBClient
import json
import redis
from datetime import datetime

json_path = 'subprocess/data.json'
temp_json_path = 'subprocess/temp.json'
r = redis.Redis(host='localhost', port=6379, db=0)

multipierBGN = 1

bgn = r.get('bgn').decode()
src = r.get('src').decode()
project = r.get('project').decode()

count = 0
yarrSrc = []
yarrR = []

print(bgn)
print(project)

chandle = ctypes.c_int16()
status = {}
status["openunit"] = ps.ps2000aOpenUnit(ctypes.byref(chandle), None)
assert_pico_ok(status["openunit"])
print("device started")

def load_json(object1, object2):
    arr = []
    with open(json_path, 'r') as openfile:
        json_object = json.load(openfile)
    for project in json_object[object1]:
        options = project[object2]
        arr.append(options)
    return arr

def load_bgn():
    global pos_bgnR,neg_bgnR,pos_bgnS,neg_bgnS,pos_bgnT,neg_bgnT
    idx_bgn = load_json("background", "project").index(bgn)
    a_file = open(json_path, "r")
    json_object = json.load(a_file)
    pos_bgnR = max(json_object["background"][idx_bgn]["volR"])*multipierBGN
    neg_bgnR = min(json_object["background"][idx_bgn]["volR"])*multipierBGN
    print(pos_bgnR)
    print(neg_bgnR)
    
def sigGen():
    wavetype = ctypes.c_int16(0)
    sweepType = ctypes.c_int32(0)
    triggertype = ctypes.c_int32(0)
    triggerSource = ctypes.c_int32(0)

    status["SetSigGenBuiltIn"] = ps.ps2000aSetSigGenBuiltIn(chandle,        #handle
                                                            0,              #offsetVoltage
                                                            1200000,         #pkToPk
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

load_bgn()
sigGen()
chARange = 6
chBRange = 6
while True:
    count = count + 1

    """Cahnnel Setup"""
    status["setChA"] = ps.ps2000aSetChannel(chandle, 0, 1, 1, chARange, 0)
    assert_pico_ok(status["setChA"])
    status["setChB"] = ps.ps2000aSetChannel(chandle, 1, 1, 1, chBRange, 0)
    assert_pico_ok(status["setChB"])

    """Set up single trigger"""
    status["trigger"] = ps.ps2000aSetSimpleTrigger(chandle, 1, 0, 1024, 4, 0, 1000)
    assert_pico_ok(status["trigger"])

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


    valAMax = max(adc2mV(bufferAMax, chARange, maxADC))
    valAMin = min(adc2mV(bufferAMax, chARange, maxADC))

    valBMax = max(adc2mV(bufferBMax, chBRange, maxADC))
    valBMin = min(adc2mV(bufferBMax, chBRange, maxADC))

    if valAMax > valAMin*-1:
        max_val_A = valAMax
    else:
        max_val_A = valAMin*-1

    if max_val_A > 1999:
        chARange = 9
    elif max_val_A > 999:
        chARange = 8
    elif max_val_A > 499:
        chARange = 7
    elif max_val_A > 199:
        chARange = 6
    elif max_val_A > 99:
        chARange = 5
    elif max_val_A > 49:
        chARange = 4
    elif max_val_A > 24:
        chARange = 3
    elif max_val_A > 9:
        chARange = 2
    elif max_val_A < 9:
        chARange = 1
    
    if valBMax > valBMin*-1:
        max_val_B = valBMax
    else:
        max_val_B = valBMin*-1

    if max_val_B > 1999:
        chBRange = 9
    elif max_val_B > 999:
        chBRange = 8
    elif max_val_B > 499:
        chBRange = 7
    elif max_val_B > 199:
        chBRange = 6
    elif max_val_B > 99:
        chBRange = 5
    elif max_val_B > 49:
        chBRange = 4
    elif max_val_B > 24:
        chBRange = 3
    elif max_val_B > 9:
        chBRange = 2
    elif max_val_B < 9:
        chBRange = 1
    time.sleep(0.75)

    if count%3 == 0:

        yarrSrc =  np.array(adc2mV(bufferAMax, chARange, maxADC))
        yarrR =  np.array(adc2mV(bufferBMax, chBRange, maxADC))

        maxIdxSrc = yarrSrc.argmax(axis = 0)
        half = int(len(yarrSrc)/2)
        quarter = int(len(yarrSrc)/4)
        thirdqua = int(len(yarrSrc)*3/4)

        if maxIdxSrc  <= quarter:
            quad_11 = yarrR[(maxIdxSrc + thirdqua):]
            quad_12 = yarrR[:maxIdxSrc]
            quad_1R = np.concatenate((quad_11, quad_12))
            quad_2R = yarrR[maxIdxSrc:(maxIdxSrc + quarter)]
            quad_3R = yarrR[(maxIdxSrc + quarter):(maxIdxSrc + half)]
            quad_4R = yarrR[(maxIdxSrc + half):(maxIdxSrc + thirdqua)]
        elif maxIdxSrc <= half:
            quad_1R = yarrR[(maxIdxSrc - quarter):maxIdxSrc]
            quad_2R = yarrR[maxIdxSrc:(maxIdxSrc + quarter)]
            quad_3R = yarrR[(maxIdxSrc + quarter):(maxIdxSrc + half)]
            quad_41 = yarrR[(maxIdxSrc + half):]
            quad_42 = yarrR[:(maxIdxSrc - quarter)]
            quad_4R = np.concatenate((quad_41,quad_42))    
        elif maxIdxSrc <= thirdqua:
            quad_1R = yarrR[(maxIdxSrc - quarter):maxIdxSrc]
            quad_2R = yarrR[maxIdxSrc:(maxIdxSrc + quarter)]
            quad_31 = yarrR[(maxIdxSrc + quarter):]
            quad_32 = yarrR[:(maxIdxSrc - half)]
            quad_3R = np.concatenate((quad_31,quad_32))
            quad_4R = yarrR[(maxIdxSrc - half):(maxIdxSrc - quarter)]
        else:
            quad_1R = yarrR[(maxIdxSrc - quarter):maxIdxSrc]
            quad_21 = yarrR[maxIdxSrc:]
            quad_22 = yarrR[:(maxIdxSrc - thirdqua)]
            quad_2R = np.concatenate((quad_21,quad_22))
            quad_3R = yarrR[(maxIdxSrc - thirdqua):(maxIdxSrc - half)]
            quad_4R = yarrR[(maxIdxSrc - half):(maxIdxSrc - quarter)]

        yarrR = np.concatenate((quad_1R,quad_2R,quad_3R,quad_4R))

        xArr = np.arange(0,360,360/len(yarrR))
        xsens = np.reshape(xArr, (-1,1))

        kind = []
        for element in xArr:
            kind.append('sensR')
        ysensR = np.reshape(yarrR, (-1,1))
        ksensR = np.reshape(kind, (-1,1))
        sensR = np.concatenate((xsens, ysensR, ksensR), axis=1, dtype=object)
        fsensR = sensR[ ((sensR[:,1] > int(pos_bgnR)) | (sensR[:,1] < int(neg_bgnR))) & (sensR[:,2] == 'sensR') ]
        
        print(pos_bgnR)
        print(neg_bgnR)
        # print(yarrR)
        # print(fsensR)

        combine = fsensR
        print("data process done")

        try:
            maxR = fsensR[:,1].max(axis=0)
            minR = fsensR[:,1].min(axis=0)
        except:
            maxR = 0
            minR = 0
        nPosR = fsensR[fsensR[:,1]>0].size
        nNegR = fsensR[fsensR[:,1]<0].size
        arr = json.dumps(combine.tolist())

        json_body = [
            {
                "measurement": project,
                "tags": {
                    "host": "server01",
                    "region": "us-west"
                },
                "fields": {
                    "count": count,
                    "maxR": maxR,
                    "minR": minR,
                    "nPosR": nPosR,
                    "nNegR": nNegR,
                    "arr": json.dumps(combine.tolist())
                }
            }
        ]

        client = InfluxDBClient(host='127.0.0.1', port=8086, database='pd_1p')
        client.write_points(json_body)
        print("saved to influxdb")

        now = datetime.now()

        a_file = open(temp_json_path, "r")
        json_object = json.load(a_file)
        json_object["iteration"][0]["time"] = now.strftime("%Y-%d-%mT%H:%M:%SZ")
        json_object["iteration"][0]["count"] = count
        json_object["iteration"][0]["maxR"] = maxR
        json_object["iteration"][0]["minR"] = minR
        json_object["iteration"][0]["nPosR"] = nPosR
        json_object["iteration"][0]["nNegR"] = nNegR
        json_object["iteration"][0]["arr"] = json.dumps(combine.tolist())

        a_file = open(temp_json_path, "w")
        json.dump(json_object, a_file)
        a_file.close()
        print("owrite done")

        r.set('count', count)
        
        print("acq",end="=")
        print(count,flush=True)

        time.sleep(5)


status["stop"] = ps.ps2000aStop(chandle)
assert_pico_ok(status["stop"])

status["close"] = ps.ps2000aCloseUnit(chandle)
assert_pico_ok(status["close"])

print('finish')