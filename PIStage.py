# -*- coding: utf-8 -*-
"""
Created on Tue Aug 7 16:00:00 2018

@author: larpid
"""

import sys
# import clr
# import System
import Stage
import time
import serial
from parse import *


class PIStage(Stage.Stage):

    def __init__(self):
        #        self.path = 1
        self.position_max = 0  # gets set when stage connects
        self.position_min = 0  # gets set when stage connects
        #        self.position_in_ps = 2 * 3.33333 * self.path * self.position_current
        #        self.configuration = {'zero position': 0}
        self.velocity = 10  # unit: mm/s
        self.ser = serial.Serial()
        print('init succ')

    def connect(self):
        self.ser = serial.Serial(
            port='/dev/ttyUSB0',  # todo: make not hardcoded
            baudrate=57600,
            timeout=3,
            bytesize=8,
            parity='N',
            stopbits=1)  # open serial port
        # baudrate, timeout, bytesize, parity and stopbits values copied from PITerminal standard values
        print(self.ser.name)  # check which port is really used
        self.ser.write('IDN?\n')
        print(self.ser.readlines())
        self.ser.write('TMN?\n')
        outs = self.ser.readlines()
        self.position_min = parse("{}={}", outs[0])[1]
        print(outs[1])
        self.ser.write('TMX?\n')
        out1 = self.ser.readline()
        out2 = self.ser.readline()
        self.position_max = parse("{}={}", out1)[1]
        print(out2)
        self.ser.write('POS?\n')
        outs = self.ser.readlines()
        for eachLine in outs:
            print(eachLine)

    def disconnect(self):
        self.ser.close()
        print('Stage has been disconnected')
