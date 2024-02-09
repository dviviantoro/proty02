import ctypes
import numpy as np
import pandas as pd
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import adc2mV, assert_pico_ok
import plotly.express as px
import time

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
                                                            5000,         #pkToPk
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


chARange = 7
iteration = 6
while (count < iteration):
    sigGen()
    count = count + 1
    # print("loop: ", count)

    """Cahnnel Setup"""
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
                                                0)         #pointer to overflow
    assert_pico_ok(status["getValues"])
    # print(overflow)

    # find maximum ADC count value
    # handle = chandle
    # pointer to value = ctypes.byref(maxADC)
    maxADC = ctypes.c_int16()
    status["maximumValue"] = ps.ps2000aMaximumValue(chandle,                #handle
                                                    ctypes.byref(maxADC))   #pointer to value
    assert_pico_ok(status["maximumValue"])

    adc2mVChAMax =  np.array(adc2mV(bufferAMax, chARange, maxADC))

    if np.max(adc2mVChAMax) > np.min(adc2mVChAMax)*-1:
        max_val = np.max(adc2mVChAMax)
    else: 
        max_val = np.min(adc2mVChAMax)*-1

    print(max_val) 
    if max_val > 1999:
        chARange = 9
    elif max_val > 999:
        chARange = 8
    elif max_val > 499:
        chARange = 7
    elif max_val > 199:
        chARange = 6
    elif max_val > 99:
        chARange = 5
    elif max_val > 49:
        chARange = 4
    elif max_val > 24:
        chARange = 3
    elif max_val > 9:
        chARange = 2
    elif max_val < 9:
        chARange = 1

    print(chARange)
    time.sleep(0.5)

    if count%3 == 0:
        times = np.linspace(0, ((cTotalSamples.value)-1) * timeIntervalns.value, cTotalSamples.value)
        df = pd.DataFrame({'x':times, 'y':adc2mVChAMax})
        print(len(df))
        # df.to_csv('file2.csv', header=False, index=False)
        # print(len(df))
        # maxvalue = df['y'].max()
        # maxValueIndex = df['y'].idxmax()
        # print(maxValueIndex)
        # print(maxvalue)

        fig = px.scatter(df, x="x", y="y")
        fig.show()





status["stop"] = ps.ps2000aStop(chandle)
assert_pico_ok(status["stop"])

status["close"] = ps.ps2000aCloseUnit(chandle)
assert_pico_ok(status["close"])

print('finish')