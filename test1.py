import ctypes
import numpy as np
import matplotlib.pyplot as plt
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import adc2mV, assert_pico_ok
import time

# Create chandle and status ready for use
chandle = ctypes.c_int16()
status = {}

# Open 2000 series PicoScope
# Returns handle to chandle for use in future API functions
status["openunit"] = ps.ps2000aOpenUnit(ctypes.byref(chandle), None)
assert_pico_ok(status["openunit"])

# Output a sine wave with peak-to-peak voltage of 2 V and frequency of 10 kHz
wavetype = ctypes.c_int16(0)
sweepType = ctypes.c_int32(0)
triggertype = ctypes.c_int32(0)
triggerSource = ctypes.c_int32(0)

status["SetSigGenBuiltIn"] = ps.ps2000aSetSigGenBuiltIn(chandle,        #handle
                                                        0,              #offsetVoltage
                                                        2000000,        #pkToPk
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

chARange = 7
chAEnable = 1
status["setChA"] = ps.ps2000aSetChannel(chandle,    #handle
                                        0,          #PS2000A_CHANNEL
                                        chAEnable,  #enabled
                                        1,          #PS2000A_COUPLING
                                        chARange,   #PS2000A_RANGE
                                        0)          #analogOffset
assert_pico_ok(status["setChA"])
"""
chBRange = 7
chBEnable = 1
status["setChB"] = ps.ps2000aSetChannel(chandle,    #handle
                                        0,          #PS2000A_CHANNEL
                                        chBEnable,  #enabled
                                        1,          #PS2000A_COUPLING
                                        chBRange,   #PS2000A_RANGE
                                        0)          #analougeOffset
assert_pico_ok(status["setChB"])

chCRange = 7
chCEnable = 1
status["setChC"] = ps.ps2000aSetChannel(chandle,    #handle
                                        0,          #PS2000A_CHANNEL
                                        chCEnable,  #enabled
                                        1,          #PS2000A_COUPLING
                                        chCRange,   #PS2000A_RANGE
                                        0)          #analougeOffset
assert_pico_ok(status["setChC"])

chDRange = 7
chDEnable = 1
status["setChD"] = ps.ps2000aSetChannel(chandle,    #handle
                                        0,          #PS2000A_CHANNEL
                                        chDEnable,  #enabled
                                        1,          #PS2000A_COUPLING
                                        chDRange,   #PS2000A_RANGE
                                        0)          #analougeOffset
assert_pico_ok(status["setChD"])
"""
# Set up single trigger
status["trigger"] = ps.ps2000aSetSimpleTrigger( chandle,    #handle
                                                1,          #enabled
                                                0,          #source
                                                1024,       #threshold
                                                2,          #direction
                                                0,          #delay
                                                1000)       #autoTrigger
assert_pico_ok(status["trigger"])

# Set number of pre and post trigger samples to be collected
preTriggerSamples = 2500
postTriggerSamples = 2500
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

# Run block capture
# handle = chandle
# number of pre-trigger samples = preTriggerSamples
# number of post-trigger samples = PostTriggerSamples
# timebase = 8 = 80 ns = timebase (see Programmer's guide for mre information on timebases)
# oversample = 0 = oversample
# time indisposed ms = None (not needed in the example)
# segment index = 0
# lpReady = None (using ps2000aIsReady rather than ps2000aBlockReady)
# pParameter = None
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
"""
bufferBMax = (ctypes.c_int16 * totalSamples)()
bufferBMin = (ctypes.c_int16 * totalSamples)()
bufferCMax = (ctypes.c_int16 * totalSamples)()
bufferCMin = (ctypes.c_int16 * totalSamples)()
bufferDMax = (ctypes.c_int16 * totalSamples)()
bufferDMin = (ctypes.c_int16 * totalSamples)()
"""

status["setDataBuffersA"] = ps.ps2000aSetDataBuffers(chandle,                   #hamdle
                                                     0,                         #source
                                                     ctypes.byref(bufferAMax),  #pointer to buffer max
                                                     ctypes.byref(bufferAMin),  #pointer to buffer min
                                                     totalSamples,              #buffer length
                                                     0,                         #segment index
                                                     0)                         #ratio mode
assert_pico_ok(status["setDataBuffersA"])
"""
status["setDataBuffersB"] = ps.ps2000aSetDataBuffers(chandle,                   #handle
                                                     0,                         #source
                                                     ctypes.byref(bufferBMax),  #pointer to buffer max
                                                     ctypes.byref(bufferBMin),  #pointer to buffer min
                                                     totalSamples,              #buffer length
                                                     0,                         #segment index
                                                     0)                         #ratio mode
assert_pico_ok(status["setDataBuffersB"])

status["setDataBuffersC"] = ps.ps2000aSetDataBuffers(chandle,                   #handle
                                                     0,                         #source
                                                     ctypes.byref(bufferCMax),  #pointer to buffer max
                                                     ctypes.byref(bufferCMin),  #pointer to buffer min
                                                     totalSamples,              #buffer length
                                                     0,                         #segment index
                                                     0)                         #ratio mode
assert_pico_ok(status["setDataBuffersC"])

status["setDataBuffersD"] = ps.ps2000aSetDataBuffers(chandle,                   #handle
                                                     0,                         #source
                                                     ctypes.byref(bufferDMax),  #pointer to buffer max
                                                     ctypes.byref(bufferDMin),  #pointer to buffer min
                                                     totalSamples,              #buffer lenght
                                                     0,                         #segment index
                                                     0)                         #ratio mode
assert_pico_ok(status["setDataBuffersD"])
"""

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

# convert ADC counts data to mV
adc2mVChAMax =  adc2mV(bufferAMax, chARange, maxADC)
"""
adc2mVChBMax =  adc2mV(bufferBMax, chBRange, maxADC)
adc2mVChCMax =  adc2mV(bufferCMax, chCRange, maxADC)
adc2mVChDMax =  adc2mV(bufferDMax, chDRange, maxADC)
"""
# Create time data
time = np.linspace(0, ((cTotalSamples.value)-1) * timeIntervalns.value, cTotalSamples.value)

# plot data from channel A and B
plt.plot(time, adc2mVChAMax[:])
# plt.plot(time, adc2mVChBMax[:])
# plt.plot(time, adc2mVChCMax[:])
# plt.plot(time, adc2mVChDMax[:])
plt.xlabel('Time (ns)')
plt.ylabel('Voltage (mV)')
plt.show()

# Stop the scope
# handle = chandle
status["stop"] = ps.ps2000aStop(chandle)
assert_pico_ok(status["stop"])

# Close unitDisconnect the scope
# handle = chandle
status["close"] = ps.ps2000aCloseUnit(chandle)
assert_pico_ok(status["close"])

# display status returns
print(status)
