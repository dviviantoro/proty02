import ctypes
import numpy as np
import pandas as pd
import polars as pl
import matplotlib.pyplot as plt
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import adc2mV, assert_pico_ok
import plotly.express as px
import time

chandle = ctypes.c_int16()
status = {}
status["openunit"] = ps.ps2000aOpenUnit(ctypes.byref(chandle), None)
assert_pico_ok(status["openunit"])

# Output a sine wave with peak-to-peak voltage of 2 V and frequency of 10 kHz
wavetype = ctypes.c_int16(0)
sweepType = ctypes.c_int32(0)
triggertype = ctypes.c_int32(0)
triggerSource = ctypes.c_int32(0)

status["SetSigGenBuiltIn"] = ps.ps2000aSetSigGenBuiltIn(chandle,        #handle
                                                        0,              #offsetVoltage
                                                        900000,        #pkToPk
                                                        wavetype,       #waveType
                                                        50,          #startFrequency
                                                        50,          #stopFrequency
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


"""Cahnnel Setup"""
status["setChA"] = ps.ps2000aSetChannel(chandle,    #handle
                                        0,          #PS2000A_CHANNEL
                                        1,          #enabled
                                        1,          #PS2000A_COUPLING
                                        5,          #PS2000A_RANGE
                                        0)          #analogOffset
assert_pico_ok(status["setChA"])

status["setChB"] = ps.ps2000aSetChannel(chandle,    #handle
                                        1,          #PS2000A_CHANNEL
                                        1,          #enabled
                                        1,          #PS2000A_COUPLING
                                        5,          #PS2000A_RANGE
                                        0)          #analogOffset
assert_pico_ok(status["setChB"])

status["setChC"] = ps.ps2000aSetChannel(chandle,    #handle
                                        2,          #PS2000A_CHANNEL
                                        1,          #enabled
                                        1,          #PS2000A_COUPLING
                                        5,          #PS2000A_RANGE
                                        0)          #analogOffset
assert_pico_ok(status["setChC"])

status["setChD"] = ps.ps2000aSetChannel(chandle,    #handle
                                        3,          #PS2000A_CHANNEL
                                        1,          #enabled
                                        1,          #PS2000A_COUPLING
                                        5,          #PS2000A_RANGE
                                        0)          #analogOffset
assert_pico_ok(status["setChD"])


"""Set up single trigger"""
status["trigger"] = ps.ps2000aSetSimpleTrigger( chandle,    #handle
                                                1,          #enabled
                                                0,          #source
                                                1024,       #threshold
                                                2,          #direction
                                                0,          #delay
                                                1000)       #autoTrigger
assert_pico_ok(status["trigger"])

# Set number of pre and post trigger samples to be collected
preTriggerSamples = 207750
postTriggerSamples = 207750
totalSamples = preTriggerSamples + postTriggerSamples

# Get timebase information
# WARNING: When using this example it may not be possible to access all Timebases as all channels are enabled by default when opening the scope.  
# To access these Timebases, set any unused analogue channels to off.
timebase = 8
timeIntervalns = ctypes.c_float()
returnedMaxSamples = ctypes.c_int32()
oversample = ctypes.c_int16(0)
status["getTimebase2"] = ps.ps2000aGetTimebase2(chandle,                            #handle
                                                timebase,                           #timebase
                                                totalSamples,                       #noSample
                                                ctypes.byref(timeIntervalns),       #pointer to timeIntervalNanoseconds
                                                oversample,                         #pointer to totalSample
                                                ctypes.byref(returnedMaxSamples),   
                                                0)                                  #segment index
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

# Retried data from scope to buffers assigned above
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

adc2mVChAMax =  np.array(adc2mV(bufferAMax, chARange, maxADC))
time = np.linspace(0, ((cTotalSamples.value)-1) * timeIntervalns.value, cTotalSamples.value)
df = pd.DataFrame({'x':time, 'y':adc2mVChAMax})
df.to_csv('file2.csv', header=False, index=False)
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
