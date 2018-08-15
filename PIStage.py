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
from serial.tools.list_ports import comports


class PIStage(Stage.Stage):

    def __init__(self):
        self.position_max = {}  # gets set per axis when stage connects
        self.position_min = {}  # gets set per axis when stage connects
        #        self.position_in_ps = 2 * 3.33333 * self.path * self.position_current
        #        self.configuration = {'zero position': 0}
        self.velocity = {'1': 2, '2': 1}  # unit: mm/s
        self.ser = serial.Serial()

    def connect(self):
        ports_available = comports()
        print(ports_available)
        print('select device:')
        for portindex, eachport in enumerate(ports_available):
            print(str(portindex)+' - '+eachport.device+'\t'+eachport.description)
        port=ports_available[input()].device
        self.ser = serial.Serial(
            port=port,
            baudrate=57600,
            # baudrate, timeout, bytesize, parity and stopbits values copied from PITerminal standard values
            timeout=1,
            bytesize=8,
            parity='N',
            stopbits=1)  # open serial port
        #
        # confirm connection:
        print('connection established, stage respond on command IDN?:')
        self.ser.write('IDN?\n')
        print(self.ser.readlines())
        #
        # get minimum positions:
        self.ser.write('TMN?\n')
        readbuffer = self.ser.readlines()
        for eachline in readbuffer:
            self.position_min[parse('{}={:e}{}', eachline)[0]] = parse('{}={:e}{}', eachline)[1]
        print('position_min is now set to: ' + str(self.position_min))
        self.pi_error_check()
        #
        # get maximum positions:
        self.ser.write('TMX?\n')
        readbuffer = self.ser.readlines()
        for eachline in readbuffer:
            self.position_max[parse('{}={:e}{}', eachline)[0]] = parse('{}={:e}{}', eachline)[1]
        print('position_max is now set to: ' + str(self.position_max))
        self.pi_error_check()
        #
        # TODO: use this for sth or remove
        self.ser.write('POS?\n')
        print('positions:')
        print(self.ser.readlines())
        self.pi_error_check()
        #
        # set velocities
        for axis_id in self.velocity:
            self.ser.write('VEL '+axis_id+' '+str(self.velocity[axis_id])+'\n')
        self.ser.write('VEL?\n')
        print('velocities:')
        print(self.ser.readlines())
        self.pi_error_check()
        #
        # FRF
        self.pi_error_check()
        self.ser.write('FRF 1\n')
        self.pi_error_check()
        self.ser.write('FRF?\n')
        print('FRF result:')
        print(self.ser.readlines())
        self.pi_error_check()

    def disconnect(self):
        self.ser.close()
        print('Connection has been closed')

    def move_absolute(self, axisID, newPos):
        if (newPos > self.position_min[axisID] and newPos < self.position_max[axisID]):
            self.PI_servo(axisID)
            self.ser.write('MOV '+axisID+' ' + str(newPos) + '\n')
        else:
            print('no')

    def PI_GetControllerIdentification(selfself):
        self.ser.write('IDN?\n')
        for eachline in self.ser.readlines():
            print(eachline)

    def PI_servo(self,axisID):
        self.ser.write('SVO '+axisID+' 1\n')
        self.ser.write('SVO? '+axisID+'\n')
        print('servo state:')
        print(self.ser.readline())

    def pi_error_check(self, force_output=False):
        self.ser.write('ERR?\n')
        readbuffer = self.ser.readlines()
        if (readbuffer[0][0] != '0' or force_output):
            print('Controller reports Error Code: ' + readbuffer[0])
        if readbuffer[0][0] != '0':
            exit()
