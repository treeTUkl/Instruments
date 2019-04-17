import sys
import redpitaya_scpi as scpi
import numpy
from tango import AttrWriteType
from PyTango import DevState, DevFailed
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command, pipe


class RedPitayaPhotodiodeTango(Device, metaclass=DeviceMeta):

    IP = sys.argv[1]
    rp_s = None

    def init_device(self):
        Device.init_device(self)
        self.set_state(DevState.OFF)

    cmd_connect = attribute(access=AttrWriteType.WRITE)
    cmd_disconnect = attribute(access=AttrWriteType.WRITE)

    voltage = attribute(label="voltage", dtype=float,
                        access=AttrWriteType.READ,
                        unit="V",
                        doc="Voltage on fast analog IN1 on HV Jumper setting")

    def read_voltage(self):
        self.rp_s.tx_txt('ACQ:START')
        self.rp_s.tx_txt('ACQ:TRIG NOW')

        while True:
            self.rp_s.tx_txt('ACQ:TRIG:STAT?')
            if self.rp_s.rx_txt() == 'TD':
                break

        self.rp_s.tx_txt('ACQ:SOUR1:DATA?')

        buff_string = self.rp_s.rx_txt()  # server often crashes when not receiving an answer here

        self.rp_s.tx_txt('ACQ:STOP')

        buff_strings = buff_string.strip('{}\n\r').replace("  ", "").split(',')
        buff = list(map(float, buff_strings))
        return numpy.mean(buff)

    @command
    def connect(self):
        if self.rp_s is None:
            self.rp_s = scpi.scpi(self.IP)  # setting a timeout does not help (random crashes)
            self.rp_s.tx_txt('ACQ:RST')
            self.rp_s.tx_txt('ACQ:DEC 1')
            self.rp_s.tx_txt('ACQ:TRIG:DLY 16384')
            self.rp_s.tx_txt('ACQ:DATA:UNITS VOLTS')
            self.rp_s.tx_txt('ACQ:AVG ON')
            self.rp_s.tx_txt('ACQ:SOUR1:GAIN HV')
            self.set_state(DevState.ON)
            print('diode connected')

    def write_cmd_connect(self, _):
        self.connect()

    @command
    def disconnect(self):
        if self.rp_s is not None:
            self.rp_s.close()
            self.rp_s = None
            print('diode disconnected')
        self.set_state(DevState.OFF)

    def write_cmd_disconnect(self, _):
        self.disconnect()


if __name__ == "__main__":
    run([RedPitayaPhotodiodeTango])
