# -*- coding: utf-8 -*-
"""
Created on Tue Aug 7 16:00:00 2018

@author: larpid
"""


import sys
#import clr
#import System
import Stage
import time
import serial
import parse

class PIStage(Stage.Stage):
    
    def __init__(self):
        self.position_zero = 0
        self.position_current = 0
#        self.path = 1
        self.position_max = 0   # gets set when stage connects
        self.position_min = 0   # gets set when stage connects
#        self.position_in_ps = 2 * 3.33333 * self.path * self.position_current
#        self.configuration = {'zero position': 0}
        self.velocity=10    # unit: mm/s
        self.ser=serial.Serial()
        print('init succ')

#    def PI_Open(self):

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
        print(self.ser.readline())
        self.ser.write('TMN?\n')
        print(parse("{}={}",self.ser.readline()))
        # todo: get position_min/_max

    def disconnect(self):
        self.ser.close()
        print('Stage has been disconnected')