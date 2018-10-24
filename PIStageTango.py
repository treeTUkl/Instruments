import PIStage
from tango import AttrQuality, AttrWriteType, DispLevel
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command, pipe
from PyTango.server import class_property, device_property

stage = PIStage.PIStage('117018374')

class PIStageTango(Device, metaclass=DeviceMeta):



    stage.connect()
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
        return float(stage.position_get())

    @command(dtype_in=float)
    def move_absolute(self):
        # stage.move_absolute(5)
        print('moved stage...TANGO')

    @pipe
    def info(self):
        return ('Information',
                dict(manufacturer='PI',
                     model='C-413.2GA',
                     serial_number='117018374'))


if __name__ == "__main__":
    run([PIStageTango])

