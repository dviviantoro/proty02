import ctypes
from picosdk.ps2000a import ps2000a as ps
import time
from picosdk.functions import assert_pico_ok

status = {}
chandle = ctypes.c_int16()

# Opens the device/s
status["openunit"] = ps.ps2000aOpenUnit(ctypes.byref(chandle), None)

try:
    assert_pico_ok(status["openunit"])
except:
    # powerstate becomes the status number of openunit
    powerstate = status["openunit"]

    # If powerstate is the same as 282 then it will run this if statement
    if powerstate == 282:
        # Changes the power input to "PICO_POWER_SUPPLY_NOT_CONNECTED"
        status["ChangePowerSource"] = ps.ps2000aChangePowerSource(chandle, 282)
    # If the powerstate is the same as 286 then it will run this if statement
    elif powerstate == 286:
        # Changes the power input to "PICO_USB3_0_DEVICE_NON_USB3_0_PORT"
        status["ChangePowerSource"] = ps.ps2000aChangePowerSource(chandle, 286)
    else:
        raise

    assert_pico_ok(status["ChangePowerSource"])

status["SetSigGenBuiltIn"] = ps.ps2000aSetSigGenBuiltIn(chandle,            #handle
                                                        0,                  #offsetVoltage
                                                        1000000,            #pkToPk
                                                        ctypes.c_int16(0),  #waveType
                                                        50,                 #startFrequency
                                                        50,                #stopFrequency
                                                        0,                  #increment
                                                        0,                  #dwelltime
                                                        ctypes.c_int32(0),  #sweepTime
                                                        0,                  #operation
                                                        0,                  #shots
                                                        0,                  #sweeps
                                                        ctypes.c_int32(0),  #triggerType
                                                        ctypes.c_int32(0),  #triggerSource
                                                        1)                  #extInThreshold 
assert_pico_ok(status["SetSigGenBuiltIn"])

time.sleep(30)

# Closes the unit
status["close"] = ps.ps2000aCloseUnit(chandle)
assert_pico_ok(status["close"])

print(status)