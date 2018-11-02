import PIStage
from tango import AttrQuality, AttrWriteType, DispLevel
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command, pipe
from PyTango.server import class_property, device_property

serial_number = '117018374'
stage = PIStage.PIStage(serial_number)

class PIStageTango(Device, metaclass=DeviceMeta):

    frf = False
    stage.connect()
    frf = True
    testpos = float(stage.position_get())
    print(testpos)

    position = attribute(label="Position", dtype=float,
                        display_level=DispLevel.EXPERT,
                        access=AttrWriteType.READ,
                        unit="mm",
                        min_value=stage.position_min, max_value=stage.position_max,
                        fget="position_get",
                        doc="stage position")

    @attribute
    def position_get(self):
        return stage.position_get()

    @command(dtype_in=float)
    def Move_absolute(self, new_pos):
        stage.move_absolute(new_pos)
        print('moved stage...TANGO to: ' + str(new_pos))

    @command()
    def Zero_reference_move(self):
        stage.pi_zero_reference_move()

    @pipe
    def info(self):
        return ('Information',
                dict(manufacturer='PI',
                     model='C-413.2GA',
                     serial_number=serial_number))


if __name__ == "__main__":
    run([PIStageTango])

