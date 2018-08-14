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
        self.velocity = 1  # unit: mm/s
        self.ser = serial.Serial()
        print('init succ')

    def connect(self):
        self.ser = serial.Serial(
            port='/dev/ttyUSB0',  # todo: make not hardcoded
            baudrate=57600,
            timeout=2,
            bytesize=8,
            parity='N',
            stopbits=1)  # open serial port
        # baudrate, timeout, bytesize, parity and stopbits values copied from PITerminal standard values
        #print(self.ser.name)  # check which port is really used
        #
        # get minimum position:
        self.ser.write('TMN?\n')
        outs = self.ser.readlines()
        self.position_min = parse('{}={:e} \n', outs[0])[1]
        print('position_min is now set to: '+str(self.position_min))
        self.pi_error_check()
        #
        # get maximum position:
        self.ser.write('TMX?\n')
        outs = self.ser.readlines()
        self.position_max = parse('{}={:e} \n', outs[0])[1]
        print('position_max is now set to: ' + str(self.position_max))
        self.pi_error_check()
        #
        #
        self.ser.write('POS?\n')
        outs = self.ser.readlines()
        for eachLine in outs:
            print('position: '+eachLine)
        self.pi_error_check()
        #
        # set velocity
        self.ser.write('VEL 1 '+str(self.velocity)+'\n')
        self.ser.write('VEL?\n')
        print('velocities:')
        print(self.ser.readlines())
        self.pi_error_check()
        #
        # set servo
        self.ser.write('SVO 1 1\n')
        self.ser.write('SVO?\n')
        print('servo state:')
        print(self.ser.readlines())
        self.pi_error_check()
        self.ser.write('FRF 1\n')
        self.pi_error_check()
        self.ser.write('FRF?\n')
        print('FRF result:')
        print(self.ser.readlines())
        self.pi_error_check()
        self.ser.write('MOV 1 5\n')

    def disconnect(self):
        self.ser.close()
        print('Stage has been disconnected')

    def move_absolute(self,newPos):
        self.ser.write('MOV 1 '+str(newPos)+'\n')

    def PI_GetControllerIdentification(selfself):
        self.ser.write('IDN?\n')
        for eachline in self.ser.readlines():
            print(eachline)

    def pi_error_check(self, force_output=False):
        self.ser.write('ERR?\n')
        readbuffer=self.ser.readlines()
        if (readbuffer[0][0]!='0' or force_output):
            print('Controller reports Error Code: '+readbuffer[0])
