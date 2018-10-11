# -*- coding: utf-8 -*-
"""
Created on Tue Aug 7 16:00:00 2018

@author: larpid
"""

import Stage
import sys
import time
import serial
from serial.tools import list_ports


class PIStage(Stage.Stage):

    def __init__(self, controller_serial_number, axis='1', velocity=2):
        super(PIStage, self).__init__()
        self.axis = axis
        self.controller_serial_number = controller_serial_number
        self.velocity = velocity  # unit: mm/s
        self.ser = serial.Serial()

    def connect(self):
        self.pi_connect()
        self.pi_handle_limits()
        self.pi_set_velocity()
        self.pi_zero_reference_move()

    def disconnect(self):
        self.ser.close()
        print('Connection has been closed')

    def move_absolute(self, new_position):
        """Move the stage to the given position in its range"""

        time_to_sleep = (abs(self.position_current - new_position)) / self.velocity
        if self.position_min <= new_position <= self.position_max:
            self.pi_servo()
            self.ser.write('MOV ' + self.axis + ' ' + str(new_position) + '\n')
            self.position_current = new_position
            time.sleep(time_to_sleep)
            print('Stage was moved to ' + str(new_position))
        else:
            print('position is out of range')

    def position_get(self):
        """return stage position"""

        for answer_line in self.pi_request('POS?\n'):
            if answer_line[:len(self.axis)] == self.axis:
                return answer_line[len(self.axis) + 1:]

    def pi_connect(self):
        """connect to PI stage controller and confirm serial number"""

        for each_port in list_ports.comports():
            if each_port.manufacturer == 'PI':
                self.ser = serial.Serial(
                    port=each_port.device, baudrate=57600, timeout=1, bytesize=8, parity='N', stopbits=1)
                print('test connection established to device:' + each_port.device)
                response_idn = self.pi_request('IDN?\n')
                if int(response_idn[0].split(',')[2]) == int(self.controller_serial_number):
                    # int conversion is to get rid of leading zero
                    print('connection established, stage respond on command \"IDN?\":')
                    print(response_idn)
                    return
                self.ser.close()
                print('test connection closed')
        print('connection failed:\n' +
              'no controller with serial number ' + controller_serial_number + ' found.')

    def pi_handle_limits(self):
        """save minimum and maximum position"""
        # set minimum positions:
        for line in self.pi_request('TMN?\n'):
            if line.split('=')[0] == self.axis:
                self.position_min = float(line.split('=')[1])
        print('position_min is now set to: ' + str(self.position_min))
        self.pi_error_check()
        #
        # get maximum positions:
        for line in self.pi_request('TMX?\n'):
            if line.split('=')[0] == self.axis:
                self.position_max = float(line.split('=')[1])
        print('position_max is now set to: ' + str(self.position_max))
        self.pi_error_check()

    def pi_set_velocity(self):
        self.ser.write('VEL ' + self.axis + ' ' + str(self.velocity) + '\n')
        print('velocities:')
        print(self.pi_request('VEL?\n'))
        self.pi_error_check()

    def pi_zero_reference_move(self):
        self.pi_error_check()
        self.ser.write('FRF 1\n')
        time.sleep(5)  # this leaves room for optimization
        self.pi_error_check()
        print('FRF result:')
        print(self.pi_request('FRF?\n'))
        self.pi_error_check()

    def pi_request(self, request_command):
        """request controller respond"""

        self.ser.reset_input_buffer()
        self.ser.write(request_command)
        line_current = self.ser.read_until('\n')
        lines_read = [line_current.strip()]
        while line_current[-2] == ' ':
            line_current = self.ser.read_until('\n')
            lines_read.append(line_current.strip())
        return lines_read

    def pi_servo(self):
        """check servo state"""

        self.ser.write('SVO ' + self.axis + ' 1\n')
        print('servo state:')
        print(self.pi_request('SVO? ' + self.axis + '\n'))

    def pi_error_check(self, force_output=False):
        """request controller errors"""

        err_answer = self.pi_request('ERR?\n')
        if err_answer[0][0] != '0' or force_output:
            print('Controller reports Error Code: ' + err_answer[0])
        if err_answer[0][0] != '0':
            exit()
