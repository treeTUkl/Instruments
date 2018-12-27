import PIStage
from tango import AttrWriteType, DispLevel, GreenMode
from PyTango import DevState, DebugIt, CmdArgType
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command, pipe
from PyTango import Device_4Impl, get_green_mode, set_green_mode
#import gevent
#from gevent import monkey
#monkey.patch_all()


class PIStageTango(Device, metaclass=DeviceMeta):

    controller_serial_number = '117018374'
    stage = PIStage.PIStage(controller_serial=controller_serial_number)
    #set_green_mode(GreenMode.Gevent)
    #green_mode = GreenMode.Gevent
    print(get_green_mode())

    def init_device(self):
        Device.init_device(self)
        self.set_state(DevState.OFF)

    cmd_connect = attribute(access=AttrWriteType.WRITE,
                            fset="connect")

    @command
    def connect(self, _):
        self.set_state(DevState.INIT)
        self.stage.connect()
        self.set_state(DevState.ON)

    cmd_disconnect = attribute(access=AttrWriteType.WRITE,
                               fset="disconnect")

    @command
    def disconnect(self, _):
        self.stage.disconnect()
        self.set_state(DevState.OFF)

    @attribute(dtype=str)
    def controller_serial(self):
        return self.controller_serial_number

    position = attribute(label="absolute Position", dtype=float,
                         display_level=DispLevel.EXPERT,
                         access=AttrWriteType.READ_WRITE,
                         unit="mm",
                         min_value=stage.position_min, max_value=stage.position_max,
                         fset="move_absolute",
                         doc="stages absolute position")

    cmd_move_absolute = attribute(access=AttrWriteType.WRITE,
                                  dtype=float,
                                  unit="mm",
                                  fset="move_absolute")

    def read_position(self):
        return self.stage.position_get()

    @command(dtype_in=float)
    def move_absolute(self, new_pos):
        self.set_state(DevState.MOVING)
        #gevent.spawn(self.stage.move_absolute, new_pos)  # + self.zero_position)
        self.stage.move_absolute(new_pos)

    @attribute(dtype=bool)
    def on_target_state(self):
        if self.stage.on_target_state():
            self.set_state(DevState.ON)
            return True
        else:
            return False

    @attribute(dtype=float)
    def position_min(self):
        return self.stage.position_min

    @attribute(dtype=float)
    def position_max(self):
        return self.stage.position_max

    velocity = attribute(label="Velocity", dtype=float,
                         display_level=DispLevel.EXPERT,
                         access=AttrWriteType.READ_WRITE,
                         unit="mm/s",
                         fget="get_velocity",
                         fset="set_velocity",
                         doc="stage position")

    def get_velocity(self):
        return self.stage.velocity

    def set_velocity(self, velocity):
        self.stage.pi_set_velocity(velocity)

    cmd_set_zero_position = attribute(access=AttrWriteType.WRITE,
                                      unit="mm",
                                      fset="set_zero_position")

    def set_zero_position(self, _):
        self.stage.set_zero_position()

    cmd_zero_reference_move = attribute(access=AttrWriteType.WRITE,
                                        fset="zero_reference_move")

    def zero_reference_move(self, _):
        self.stage.pi_zero_reference_move()
        self.stage.pi_handle_limits()

    @pipe
    def info(self):
        return ('Information',
                dict(manufacturer='PI',
                     model='C-413.2GA',
                     serial_number=self.controller_serial))

    @attribute(dtype=str)
    def last_error(self):
        return str(self.stage.last_error)


if __name__ == "__main__":
    run([PIStageTango])
