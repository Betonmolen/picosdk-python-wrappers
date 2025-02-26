# -*- coding: utf-8 -*-

"""
Created on Wed Dec 14 14:40:38 2022

@author: youri
This is a script to log data of WEED-IT solenoid with the picoscope 3000 series

"""
import ctypes
from picosdk.ps3000a import ps3000a as ps
import numpy as np
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok
#Assert_pico_ok is a check to verify the setting of the picoscope is correctly executed


# Set sample frequency
inputSampleInterval = 1 # [s] Desired time between samples, needed to calculate timebase picoscope
timeToSample = 10 # Desired time to sample

# Create chandle and status ready for use
status = {}
chandle = ctypes.c_int16()

# Opens the device/s
status["openunit"] = ps.ps3000aOpenUnit(ctypes.byref(chandle), None)

try: 
    assert_pico_ok(status["openunit"])
except:

    # powerstate becomes the status number of openunit
    powerstate = status["openunit"]

    # If powerstate is the same as 282 then it will run this if statement
    if powerstate == 282:
        # Changes the power input to "PICO_POWER_SUPPLY_NOT_CONNECTED"
        status["ChangePowerSource"] = ps.ps3000aChangePowerSource(chandle, 282)
        # If the powerstate is the same as 286 then it will run this if statement
    elif powerstate == 286:
        # Changes the power input to "PICO_USB3_0_DEVICE_NON_USB3_0_PORT"
        status["ChangePowerSource"] = ps.ps3000aChangePowerSource(chandle, 286)
    else:
        raise

    assert_pico_ok(status["ChangePowerSource"])
    

# PICO_STATUS ps3000aSetChannel
# (
#   int16_t handle,
#   PS3000A_CHANNEL channel,
#   int16_t enabled,
#   PS3000A_COUPLING type,
#   PS3000A_RANGE range,
#   float analogueOffset
# )


# Set up channel X
# handle = chandle
# channel = PS3000A_CHANNEL_A = 0
# enabled = 1
# coupling type = PS3000A_DC = 1
# range = PS3000A_10V = 8
# analogue offset = 0 V

chRange = 7
status["setChA"] = ps.ps3000aSetChannel(chandle, 0, 1, 1, chRange, 0)
assert_pico_ok(status["setChA"])

status["setChB"] = ps.ps3000aSetChannel(chandle, 1, 1, 1, chRange, 0)
assert_pico_ok(status["setChB"])

status["setChC"] = ps.ps3000aSetChannel(chandle, 2, 1, 1, chRange, 0)
assert_pico_ok(status["setChC"])

status["setChD"] = ps.ps3000aSetChannel(chandle, 3, 1, 1, chRange, 0)
assert_pico_ok(status["setChD"])



status["trigger"] = ps.ps3000aSetSimpleTrigger(chandle, 0, 0, 1024, 3, 0, 1000)
assert_pico_ok(status["trigger"])

# Sets up single trigger
# Handle = Chandle
# Source = ps3000A_channel_B = 0
# Enable = 0
# Threshold = 1024 ADC counts
# Direction = ps3000A_Falling = 3
# Delay = 0
# autoTrigger_ms = 1000

# Setting the number of sample to be collected
preTriggerSamples = 5
postTriggerSamples = 1
maxsamples = preTriggerSamples + postTriggerSamples

# Gets timebase innfomation
# WARNING: When using this example it may not be possible to access all Timebases as all channels are enabled by default when opening the scope.  
# To access these Timebases, set any unused analogue channels to off.
# Handle = chandle
# Timebase = 2 = timebase
# Nosample = maxsamples
# TimeIntervalNanoseconds = ctypes.byref(timeIntervalns)
# MaxSamples = ctypes.byref(returnedMaxSamples)
# Segement index = 0
timebase = 2
timebase = int(125000000*inputSampleInterval+2)
timeIntervalns = ctypes.c_float()
returnedMaxSamples = ctypes.c_int16()
status["GetTimebase"] = ps.ps3000aGetTimebase2(chandle, timebase, maxsamples, ctypes.byref(timeIntervalns), 1, ctypes.byref(returnedMaxSamples), 0)
assert_pico_ok(status["GetTimebase"])
print(timeIntervalns.value)

# Creates a overlow location for data
overflow = ctypes.c_int16()
# Creates converted types maxsamples
cmaxSamples = ctypes.c_int32(maxsamples)

# Starts the block capture
# Handle = chandle
# Number of prTriggerSamples
# Number of postTriggerSamples
# Timebase = 2 = 4ns (see Programmer's guide for more information on timebases)
# time indisposed ms = None (This is not needed within the example)
# Segment index = 0
# LpRead = None
# pParameter = None
status["runblock"] = ps.ps3000aRunBlock(chandle, preTriggerSamples, postTriggerSamples, timebase, 1, None, 0, None, None)
assert_pico_ok(status["runblock"])

# Create buffers ready for assigning pointers for data collection
bufferAMax = (ctypes.c_int16 * maxsamples)()
bufferAMin = (ctypes.c_int16 * maxsamples)() # used for downsampling which isn't in the scope of this example
bufferBMax = (ctypes.c_int16 * maxsamples)()
bufferBMin = (ctypes.c_int16 * maxsamples)()
bufferCMax = (ctypes.c_int16 * maxsamples)()
bufferCMin = (ctypes.c_int16 * maxsamples)()
bufferDMax = (ctypes.c_int16 * maxsamples)()
bufferDMin = (ctypes.c_int16 * maxsamples)()


# Setting the data buffer location for data collection from channel A
# Handle = Chandle
# source = ps3000A_channel_A = 0
# Buffer max = ctypes.byref(bufferAMax)
# Buffer min = ctypes.byref(bufferAMin)
# Buffer length = maxsamples
# Segment index = 0
# Ratio mode = ps3000A_Ratio_Mode_None = 0
status["SetDataBuffers"] = ps.ps3000aSetDataBuffers(chandle, 0, ctypes.byref(bufferAMax), ctypes.byref(bufferAMin), maxsamples, 0, 0)
assert_pico_ok(status["SetDataBuffers"])
status["SetDataBuffers"] = ps.ps3000aSetDataBuffers(chandle, 1, ctypes.byref(bufferAMax), ctypes.byref(bufferAMin), maxsamples, 0, 0)
assert_pico_ok(status["SetDataBuffers"])
status["SetDataBuffers"] = ps.ps3000aSetDataBuffers(chandle, 2, ctypes.byref(bufferAMax), ctypes.byref(bufferAMin), maxsamples, 0, 0)
assert_pico_ok(status["SetDataBuffers"])
status["SetDataBuffers"] = ps.ps3000aSetDataBuffers(chandle, 3, ctypes.byref(bufferAMax), ctypes.byref(bufferAMin), maxsamples, 0, 0)
assert_pico_ok(status["SetDataBuffers"])
                                             
# Creates a overlow location for data
overflow = (ctypes.c_int16 * 10)()
# Creates converted types maxsamples
cmaxSamples = ctypes.c_int32(maxsamples)

# Checks data collection to finish the capture
ready = ctypes.c_int16(0)
check = ctypes.c_int16(0)
while ready.value == check.value:
    status["isReady"] = ps.ps3000aIsReady(chandle, ctypes.byref(ready))

# Handle = chandle
# start index = 0
# noOfSamples = ctypes.byref(cmaxSamples)
# DownSampleRatio = 0
# DownSampleRatioMode = 0
# SegmentIndex = 0
# Overflow = ctypes.byref(overflow)

status["GetValues"] = ps.ps3000aGetValues(chandle, 0, ctypes.byref(cmaxSamples), 0, 0, 0, ctypes.byref(overflow))
assert_pico_ok(status["GetValues"])


# Finds the max ADC count
# Handle = chandle
# Value = ctype.byref(maxADC)
maxADC = ctypes.c_int16()
status["maximumValue"] = ps.ps3000aMaximumValue(chandle, ctypes.byref(maxADC))
assert_pico_ok(status["maximumValue"])

# Converts ADC from channel A to mV
adc2mVChAMax =  adc2mV(bufferAMax, chRange, maxADC)
adc2mVChBMax =  adc2mV(bufferBMax, chRange, maxADC)
adc2mVChCMax =  adc2mV(bufferCMax, chRange, maxADC)
adc2mVChDMax =  adc2mV(bufferDMax, chRange, maxADC)

# Creates the time data
time = np.linspace(0, (cmaxSamples.value - 1) * timeIntervalns.value, cmaxSamples.value)

# Plots the data from channel A onto a graph
plt.plot((time/10**9), adc2mVChAMax[:])
plt.plot( adc2mVChBMax[:])
plt.plot( adc2mVChCMax[:])
plt.plot( adc2mVChDMax[:])
plt.xlabel('Time (s)')
plt.ylabel('Voltage (mV)')
plt.show()

# Stops the scope
# Handle = chandle
status["stop"] = ps.ps3000aStop(chandle)
assert_pico_ok(status["stop"])

# Closes the unit
# Handle = chandle
status["close"] = ps.ps3000aCloseUnit(chandle)
assert_pico_ok(status["close"])

# Displays the staus returns
print(status)
