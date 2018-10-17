import PIStage
import time
from PyTango import AttrWriteType, DispLevel
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command, pipe


class PIStageTango(Device, metaclass=DeviceMeta):

    c413 = PIStage.PIStage('117018374')
    c413.connect()

    position = attribute(label="Position", dtype=float,
                        display_level=DispLevel.EXPERT,
                        access=AttrWriteType.READ,
                        unit="mm",
                        min_value=c413.position_min, max_value=c413.position_max,
                        fget="position_get",
                        doc="stage position")

    @attribute
    def position_get(self):
        return c413.position_get()

    @command(dtype_in=float)
    def move_absolute(self, position_new):
        c413.move_absolute(position_new)
        print('moved stage...TANGO')

    @pipe
    def info(self):
        return ('Information',
                dict(manufacturer='PI',
                     model='C-413.2GA',
                     serial_number='117018374'))


if __name__ == "__main__":
    run([PIStageTango])

