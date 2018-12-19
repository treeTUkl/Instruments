# -*- coding: utf-8 -*-
"""
Created on Tue Aug 7 16:00:00 2018

@author: larpid
"""

import Stage
import serial
from serial.tools import list_ports
import time


class PIStage(Stage.Stage):

    def __init__(self, controller_serial, axis='1', velocity=2):
        # inherits position variables in unit: mm
        super(PIStage, self).__init__()
        self.axis = axis  # axis id can be any string
        self.controller_serial = controller_serial
        self.velocity = velocity  # unit: mm/s
        self.ser = None
        self.logfile_name = 'PIStageLog.txt'
        self.last_error = 0

    def connect(self):
        if self.ser is not None:
            print('Device already connected')
            return
        self.pi_connect()
        self.pi_handle_limits()
        self.pi_set_velocity()
        self.ser.write(('SVO ' + self.axis + ' 1\n').encode())
        self.pi_zero_reference_move()

    def disconnect(self):
        if self.ser is not None:
            self.ser.close()
            self.ser = None
            print('Connection has been closed')

    def move_absolute(self, new_position):
        """Move the stage to the given position in its range"""

        if self.position_min <= new_position <= self.position_max:
            if self.pi_servo_check():
                self.ser.write(('MOV ' + self.axis + ' ' + str(new_position) + '\n').encode())
                self.position_current = new_position
                print('Stage is moving to ' + str(new_position) + ' mm')
            else:
                print('stage not moved (servo problem)')
        else:
            print('position: ' + str(new_position) + ' mm is out of range')
        self.pi_error_check()

    def position_get(self):
        """return stage position"""
        return float(self.pi_request('POS? ' + self.axis + '\n')[0][len(self.axis) + 1:]) - self.position_zero

    def on_target_state(self):
        if self.pi_request('ONT? ' + self.axis + '\n')[0][len(self.axis) + 1:] is '1':
            return True
        else:
            return False

    def pi_connect(self):
        """connect to PI stage controller and confirm serial number"""

        for each_port in list_ports.comports():
            if each_port.manufacturer == 'PI':
                self.ser = serial.Serial(
                    port=each_port.device, baudrate=57600, timeout=1, bytesize=8, parity='N', stopbits=1)
                response_idn = self.pi_request('IDN?\n')
                # int conversion is to get rid of leading zero
                if int(response_idn[0].split(',')[2]) == int(self.controller_serial):
                    print('connection established, stage respond on command \"IDN?\":')
                    print(response_idn)
                    self.pi_error_check(force_output=True)
                    return
                self.ser.close()
                print('test connection closed')
        print('connection failed:\n' +
                        'no controller with serial number ' + self.controller_serial + ' found.')
        exit()

    def pi_handle_limits(self):
        """save minimum and maximum position"""
        # get minimum positions:
        for line in self.pi_request('TMN?\n'):
            if line.split('=')[0] == self.axis:
                self.position_min = float(line.split('=')[1])
        print('position_min is now set to: ' + str(self.position_min) + ' mm')
        # get maximum positions:
        for line in self.pi_request('TMX?\n'):
            if line.split('=')[0] == self.axis:
                self.position_max = float(line.split('=')[1])
        print('position_max is now set to: ' + str(self.position_max) + ' mm')
        self.pi_error_check()

    def pi_zero_reference_move(self):
        self.ser.write(('FRF ' + self.axis + '\n').encode())
        # this 5s timer leaves room for optimization
        # nevertheless, reference moves are expected to be pretty rare (only on startup), so it won't cause much delay
        time.sleep(5)
        print('FRF result:', end=' ')
        if self.pi_request('FRF? ' + self.axis + '\n')[0].split('=')[1] == '1':
            print('successful')
        else:
            print('not successfull, return value on request: \'FRF?\' was not 1')
        self.pi_error_check()

    def pi_request(self, request_command):
        """request controller respond, return array of read lines"""

        self.ser.reset_input_buffer()
        self.ser.write(request_command.encode())
        line_current = self.ser.read_until('\n'.encode()).decode()
        lines_read = [line_current.strip()]
        while line_current[-2] == ' ':
            line_current = self.ser.read_until('\n'.encode()).decode()
            lines_read.append(line_current.strip())
        return lines_read

    def pi_set_velocity(self, velocity=None):
        """set stage and class velocity value in mm/s"""
        if velocity is None:
            velocity = self.velocity
        self.ser.write(('VEL ' + self.axis + ' ' + str(velocity) + '\n').encode())
        stage_velocity = float(self.pi_request('VEL? ' + self.axis + '\n')[0].split('=')[1])
        self.velocity = stage_velocity

        print('velocity is now set to:', end=' ')
        print(str(stage_velocity) + ' mm/s')
        self.pi_error_check()

    def pi_servo_check(self):
        """checks if servo is turned on"""

        for svo_answer_line in self.pi_request('SVO?\n'):
            if svo_answer_line.split('=') == [self.axis, '0']:
                print('servo not turned on')
                return False
        return True

    def pi_error_check(self, force_output=False):
        """request current controller error report"""

        err_answer_first_line = self.pi_request('ERR?\n')[0]
        if err_answer_first_line[0] != '0' or force_output:
            print('Controller reports Error Code: ' + err_answer_first_line)
        if err_answer_first_line[0] != '0':
            self.pi_log('Controller reports Error Code: ' + err_answer_first_line)
            self.last_error = err_answer_first_line

    def pi_log(self, message):
        logfile = open(self.logfile_name, 'a')
        logfile.write(time.strftime('%y%m%d %H:%M:%S') + ' S/N:' + self.controller_serial + ' - '
                      + message + '\n')
        logfile.close()
