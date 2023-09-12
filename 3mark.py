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

my_input = sys.argv
bgn_pos = int(my_input[1])
bgn_neg = int(my_input[2])
project = my_input[3]

chandle = ctypes.c_int16()
status = {}
status["openunit"] = ps.ps2000aOpenUnit(ctypes.byref(chandle), None)
assert_pico_ok(status["openunit"])

print("device started")

count = 0

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


# while (count < 5):
while True:
    sigGen()
    count = count + 1
    # print("loop: ", count)

    """Cahnnel Setup"""
    chARange = 7
    status["setChA"] = ps.ps2000aSetChannel(chandle,    #handle
                                            0,          #PS2000A_CHANNEL
                                            1,          #enabled
                                            1,          #PS2000A_COUPLING
                                            chARange,   #PS2000A_RANGE
                                            0)          #analogOffset
    assert_pico_ok(status["setChA"])

    """Set up single trigger"""
    status["trigger"] = ps.ps2000aSetSimpleTrigger( chandle,    #handle
                                                    1,          #enabled
                                                    0,          #source
                                                    1024,       #threshold
                                                    2,          #direction
                                                    0,          #delay
                                                    1000)       #autoTrigger
    assert_pico_ok(status["trigger"])

    preTriggerSamples = 207750
    postTriggerSamples = 207750
    totalSamples = preTriggerSamples + postTriggerSamples
    timebase = 8
    timeIntervalns = ctypes.c_float()
    returnedMaxSamples = ctypes.c_int32()
    oversample = ctypes.c_int16(0)
    imeIntervalNanoseconds = ctypes.byref(timeIntervalns)
    maxSamples = ctypes.byref(returnedMaxSamples)
    status["getTimebase2"] = ps.ps2000aGetTimebase2(chandle,                #handle
                                                    timebase,               #timebase
                                                    totalSamples,           #noSample
                                                    imeIntervalNanoseconds, #pointer to timeIntervalNanoseconds
                                                    oversample,             #pointer to totalSample
                                                    maxSamples,   
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

    status["setDataBuffersA"] = ps.ps2000aSetDataBuffers(chandle,                   #hamdle
                                                        0,                         #source
                                                        ctypes.byref(bufferAMax),  #pointer to buffer max
                                                        ctypes.byref(bufferAMin),  #pointer to buffer min
                                                        totalSamples,              #buffer length
                                                        0,                         #segment index
                                                        0)                         #ratio mode
    assert_pico_ok(status["setDataBuffersA"])

    overflow = ctypes.c_int16()
    cTotalSamples = ctypes.c_int32(totalSamples)
    status["getValues"] = ps.ps2000aGetValues(  chandle,                        #handle
                                                0,                              #start index
                                                ctypes.byref(cTotalSamples),    #pointer to number of samples
                                                0,                              #downsample ratio
                                                0,                              #downsample ratio mode
                                                0,                              
                                                ctypes.byref(overflow))         #pointer to overflow
    assert_pico_ok(status["getValues"])

    # find maximum ADC count value
    # handle = chandle
    # pointer to value = ctypes.byref(maxADC)
    maxADC = ctypes.c_int16()
    status["maximumValue"] = ps.ps2000aMaximumValue(chandle,                #handle
                                                    ctypes.byref(maxADC))   #pointer to value
    assert_pico_ok(status["maximumValue"])

    # time = np.linspace(0, ((cTotalSamples.value)-1) * timeIntervalns.value, cTotalSamples.value)
    adc2mVChAMax =  np.array(adc2mV(bufferAMax, chARange, maxADC))
    yArr = adc2mVChAMax
    maxValueIndex = yArr.argmax(axis = 0)
    # print(maxValueIndex)

    half = int(len(yArr)/2)
    quarter = int(len(yArr)/4)
    thirdqua = int(len(yArr)*3/4)

    if maxValueIndex  <= quarter:
        quadrant11 = yArr[(maxValueIndex + thirdqua):]
        quadrant12 = yArr[:maxValueIndex]
        quadrant1 = np.concatenate((quadrant11, quadrant12))
        quadrant2 = yArr[maxValueIndex:(maxValueIndex + quarter)]
        quadrant3 = yArr[(maxValueIndex + quarter):(maxValueIndex + half)]
        quadrant4 = yArr[(maxValueIndex + half):(maxValueIndex + thirdqua)]
    elif maxValueIndex <= half:
        quadrant1 = yArr[(maxValueIndex - quarter):maxValueIndex]
        quadrant2 = yArr[maxValueIndex:(maxValueIndex + quarter)]
        quadrant3 = yArr[(maxValueIndex + quarter):(maxValueIndex + half)]
        quadrant41 = yArr[(maxValueIndex + half):]
        quadrant42 = yArr[:(maxValueIndex - quarter)]
        quadrant4 = np.concatenate((quadrant41,quadrant42))
    elif maxValueIndex <= thirdqua:
        quadrant1 = yArr[(maxValueIndex - quarter):maxValueIndex]
        quadrant2 = yArr[maxValueIndex:(maxValueIndex + quarter)]
        quadrant31 = yArr[(maxValueIndex + quarter):]
        quadrant32 = yArr[:(maxValueIndex - half)]
        quadrant3 = np.concatenate((quadrant31,quadrant32))
        quadrant4 = yArr[(maxValueIndex - half):(maxValueIndex - quarter)]
    else:
        quadrant1 = yArr[(maxValueIndex - quarter):maxValueIndex]
        quadrant21 = yArr[maxValueIndex:]
        quadrant22 = yArr[:(maxValueIndex - thirdqua)]
        quadrant2 = np.concatenate((quadrant21,quadrant22))
        quadrant3 = yArr[(maxValueIndex - thirdqua):(maxValueIndex - half)]
        quadrant4 = yArr[(maxValueIndex - half):(maxValueIndex - quarter)]

    yArrR = np.concatenate((quadrant1,quadrant2,quadrant3,quadrant4))
    pertama = yArrR[:(int(len(yArrR)*1/3))]
    kedua = yArrR[int(len(yArrR)*1/3):int(len(yArrR)*2/3)]
    ketiga = yArrR[int(len(yArrR)*2/3):]
    yArrS = np.concatenate((kedua,ketiga,pertama))
    yArrT = np.concatenate((ketiga,pertama,kedua))

    xArr = np.arange(0,360,360/len(yArrR))

    kind = []
    for element in xArr:
        kind.append('sine')

    xsine = np.reshape(xArr, (-1,1))
    ysine = np.reshape(yArrR, (-1,1))
    ksine = np.reshape(kind, (-1,1))
    sine = np.concatenate((xsine, ysine, ksine), axis=1, dtype=object)
    fsine = sine[ ((sine[:,1] > bgn_pos) | (sine[:,1] < bgn_neg)) & (sine[:,2] == 'sine') ]

    # print(sine)
    # print(sine.tolist())
    # time.sleep(1)
    # print(xArr)

    # fig = px.scatter(x = xArr, 
    #                 y = yArrR)
    # fig.show()

    json_body = [
        {
            "measurement": project,
            "tags": {
                "host": "server01",
                "region": "us-west"
            },
            # "time": "2009-11-10T23:00:00Z",
            "fields": {
                "kambing": json.dumps(fsine.tolist())
            }
        }
    ]

    client = InfluxDBClient(host='127.0.0.1', port=8086, database='example')
    client.write_points(json_body)
    # result = client.query('select value from cpu_load_short;')
    # print("Result: {}".format(result))

    print("acq",end="=")
    print(count,flush=True)
    time.sleep(5)


    

status["stop"] = ps.ps2000aStop(chandle)
assert_pico_ok(status["stop"])

status["close"] = ps.ps2000aCloseUnit(chandle)
assert_pico_ok(status["close"])

print('finish')