import PIStage
from tango import AttrQuality, AttrWriteType, DispLevel
from PyTango import DevState
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command, pipe
from PyTango.server import class_property, device_property




class PIStageTango(Device):  # , metaclass=DeviceMeta): (way to go on python3 instead of next line)
    __metaclass__ = DeviceMeta

    controller_serial_number = '117018374'
    stage = PIStage.PIStage(controller_serial_number=controller_serial_number)

    position = attribute(label="Position", dtype=float,
                        display_level=DispLevel.EXPERT,
                        access=AttrWriteType.READ,
                        unit="mm",
                        min_value=stage.position_min, max_value=stage.position_max,
                        fget="position_get",
                        doc="stage position")

    def init_device(self):
        Device.init_device(self)
        self.stage.connect()
        self.set_state(DevState.ON)

    def position_get(self):
        return self.stage.position_get()

    @attribute
    def position_get2(self):
        return self.stage.position_get()

    @command(dtype_in=float)
    def Move_absolute(self, new_pos):
        self.set_state(DevState.MOVING)
        self.stage.move_absolute(new_pos)
        self.set_state(DevState.ON)
        print('moved stage...TANGO to: ' + str(new_pos))

    @command
    def Zero_reference_move(self):
        self.stage.pi_zero_reference_move()

    @pipe
    def info(self):
        return ('Information',
                dict(manufacturer='PI',
                     model='C-413.2GA',
                     serial_number=self.controller_serial_number))


if __name__ == "__main__":
    run([PIStageTango])

