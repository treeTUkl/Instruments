import PIStage
from tango import AttrQuality, AttrWriteType, DispLevel
from PyTango import DevState, DebugIt, CmdArgType
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command, pipe
from PyTango.server import class_property, device_property


class PIStageTango(Device, metaclass=DeviceMeta):

    controller_serial = attribute(label="S/N",
                                  access=AttrWriteType.READ,
                                  dtype=CmdArgType.DevString,
                                  fget="get_controller_serial")

    controller_serial_number = '117018374'

    def get_controller_serial(self):
        return self.controller_serial_number

    stage = PIStage.PIStage(controller_serial=controller_serial_number)
    stage.connect()

    def init_device(self):
        Device.init_device(self)
        self.set_state(DevState.ON)

    @attribute(access=AttrWriteType.WRITE, fset="exec_connect")
    def connect(self, _):
        self.stage.connect()

    def exec_connect(self, _):
        print('connect test')

    @attribute(access=AttrWriteType.WRITE)
    def disconnect(self, _):
        self.stage.disconnect()

    def write_disconnect(self, _):
        pass

    position = attribute(label="Position", dtype=float,
                        display_level=DispLevel.EXPERT,
                        access=AttrWriteType.READ_WRITE,
                        unit="mm",
                        min_value=stage.position_min, max_value=stage.position_max,
                        fget="read_position",
                        fset="Move_absolute",
                        doc="stage position")

    def read_position(self):
        return self.stage.position_get()

    @command(dtype_in=float)
    def Move_absolute(self, new_pos):
        self.set_state(DevState.MOVING)
        self.stage.move_absolute(new_pos)
        self.set_state(DevState.ON)
        print('moved stage...TANGO to: ' + str(new_pos))

    CmdTrig_zero_reference_move = attribute(access=AttrWriteType.WRITE,
                                            fset="set_CmdTrig_zero_reference_move")

    def set_CmdTrig_zero_reference_move(self, value):
        print(value)
        self.Zero_reference_move()

    @command
    def Zero_reference_move(self):
        self.stage.pi_zero_reference_move()

    @pipe
    def info(self):
        return ('Information',
                dict(manufacturer='PI',
                     model='C-413.2GA',
                     serial_number=self.controller_serial))

if __name__ == "__main__":
    run([PIStageTango])

