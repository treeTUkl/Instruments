"""
Tango Server for the linear delay stage
so far only used on stage with serial: 117018374
"""

from ximc import ximcStage
from tango import AttrWriteType, DispLevel
from PyTango import DevState, DebugIt, CmdArgType
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command, pipe


class PIStageTango(Device, metaclass=DeviceMeta):
    # controller_serial_number = sys.argv[1]
    stage = ximcStage.StandaStage()

    # move_step_size = 0.001

    def init_device(self):  # TODO why this? die stage wird über stage= initialisiert
        # i guess its Tango #damit die stage self wird?
        Device.init_device(self)
        self.set_state(DevState.OFF)

    cmd_connect = attribute(access=AttrWriteType.WRITE)

    @command
    def connect(self):
        self.set_state(DevState.INIT)
        if self.stage.connect():
            self.set_state(DevState.ON)
        else:
            self.set_state(DevState.OFF)

    def write_cmd_connect(self, _):  # TODO why this? #i guess its Tango
        self.connect()

    cmd_disconnect = attribute(access=AttrWriteType.WRITE)

    @command
    def disconnect(self):
        self.stage.disconnect()
        self.set_state(DevState.OFF)

    def write_cmd_disconnect(self, _):
        self.disconnect()

    @attribute(dtype=str)
    def controller_serial(self):
        self.controller_serial_number = self.stage.get_serial()
        return self.controller_serial_number

    position = attribute(label="Position relative to set zero point", dtype=float,
                         display_level=DispLevel.EXPERT,
                         access=AttrWriteType.READ,
                         unit="as",
                         min_value="250um", max_value="250um")

    def read_position(self):
        return self.stage.POS  # gives back the position in as

    position_fs = attribute(label="Position relative to set zero point", dtype=float,
                            display_level=DispLevel.EXPERT,
                            access=AttrWriteType.READ,
                            unit="fs",
                            min_value="250um", max_value="250um")

    def read_position_fs(self):
        return self.stage.POS / 1000.0  # gives back the position in fs

    position_unshifted_um = attribute(label="absolute position", dtype=float,
                                      display_level=DispLevel.EXPERT,
                                      access=AttrWriteType.READ,
                                      unit="fs",
                                      min_value="250um", max_value="250um")

    def read_position_unshifted_um(self):  # TODO
        # """'gibts nicht- im routation system auch unsinig falls PID regelung aktiv könnte die
        # verschiebung der Piezostage umgerechnet werden, falls logging inaktiv macht der wert keinen sinn...."""'
        return 0

    cmd_move_absolute = attribute(access=AttrWriteType.WRITE,
                                  dtype=float,
                                  unit="as")

    @command(dtype_in=float)
    def move_absolute(self, new_position_in_as):
        self.set_state(DevState.MOVING)
        self.stage.move_absolute_in_as(new_position_in_as)

    def write_cmd_move_absolute(self, new_pos):
        self.move_absolute(new_pos)

    cmd_move_absolute_fs = attribute(access=AttrWriteType.WRITE,
                                     dtype=float,
                                     unit="fs")
    @command(dtype_in=float)
    def move_absolute_fs(self, new_position_in_fs):
        self.set_state(DevState.MOVING)
        new_position_in_as= new_position_in_fs*1000
        self.stage.move_absolute_in_as(new_position_in_as)

    def write_cmd_move_absolute_fs(self, new_pos):
        self.move_absolute_fs(new_pos)

    cmd_move_relative_as = attribute(access=AttrWriteType.WRITE,
                                     dtype=float,
                                     unit="as")


    @command(dtype_in=float)
    def move_relative_as(self, new_position_in_as):
        self.stage.move_relative_in_as(new_position_in_as)

    def write_cmd_move_relative_as(self, new_position_in_as):
        self.move_relative_in_as(new_position_in_as)

    cmd_move_absolute_steps = attribute(access=AttrWriteType.WRITE,
                                        dtype=float,
                                        unit="Steps",
                                        doc="move absolute in steps and microsteps")

    @command(dtype_in=float)
    def move_absolute_steps(self, new_pos_steps, new_pos_Usteps=0):
        self.stage.move_absolute_in_steps(new_pos_steps, new_pos_Usteps)

    def write_cmd_move_absolute_steps(self, new_pos_steps, new_pos_Usteps=0):
        self.move_absolute_in_steps(new_pos_steps, new_pos_Usteps)

    cmd_move_relative_steps = attribute(access=AttrWriteType.WRITE,
                                        dtype=float,
                                        unit="Steps",
                                        doc="move relative in steps and microsteps")

    @command(dtype_in=float)
    def move_relative_steps(self, new_pos_steps, new_pos_Usteps=0):
        self.stage.move_relative_in_steps(new_pos_steps, new_pos_Usteps)

    def write_cmd_move_relative_steps(self, new_pos_steps, new_pos_Usteps=0):
        self.move_relative_in_steps(new_pos_steps, new_pos_Usteps)

    @attribute(dtype=bool)
    def on_target_state(self):  # TODO: just becouse its not moving doenst mean its on target
        result = self.stage.Standa_Status()
        if str(result.MoveSts) is "0":
            self.set_state(DevState.ON)
            return True
        else:
            return False

    @attribute(dtype=float)
    def position_min(self):
        return "0"

    @attribute(dtype=float)
    def position_max(self):
        return "0"

    velocity = attribute(label="Velocity", dtype=float,
                         display_level=DispLevel.EXPERT,
                         access=AttrWriteType.READ_WRITE,
                         unit="Steps/s",
                         fget="get_velocity",
                         fset="set_velocity",
                         doc="stage position, recommended 200")

    acceleration = attribute(label="Acceleration", dtype=float,
                             display_level=DispLevel.EXPERT,
                             access=AttrWriteType.READ_WRITE,
                             unit="acceleration/s",
                             fget="get_settings",
                             fset="set_settings",
                             doc="acceleration, recommended 100")

    def get_settings(self):  # TODO get accel and decel and mitrostepMode too?
        y_status = self.stage.Standa_get_motor_settings()
        return str(y_status.Speed)

    def set_settings(self, velocity, acceleration=100):
        y_status = self.stage.Standa_get_motor_settings()
        result = self.stage.Standa_get_engine_settings()

        self.stage.Standa_set_settings(int(velocity), int(acceleration), int(y_status.Decel), int(result.MicrostepMode))

    cmd_set_zero_position = attribute(access=AttrWriteType.WRITE)

    @command
    def set_zero_position(self):
        self.stage.set_zero_position()

    def write_cmd_set_zero_position(self, _):
        self.set_zero_position()

    cmd_zero_reference_move = attribute(access=AttrWriteType.WRITE)

    @command
    def zero_reference_move(self):
        pass
        # self.stage.pi_zero_reference_move()
        # self.stage.pi_handle_limits()

    def write_cmd_zero_reference_move(self, _):
        self.zero_reference_move()

    cmd_stop_motion = attribute(access=AttrWriteType.WRITE)

    @command
    def stop_motion(self):
        self.stagestop_move()
        self.set_state(DevState.ON)

    def write_cmd_stop_motion(self, _):
        self.stop_motion()

    @attribute(dtype=str)
    def last_error(self):
        return str("error reporting with standa not implemented")

    cmd_move_step = attribute(access=AttrWriteType.WRITE,
                              dtype=float,
                              label="moves stage by defined motorspeed in input direction",
                              doc="moves stage by defined motorspeed in input direction")

    @command(dtype_in=float)
    def move_step(self, direction):
        self.set_state(DevState.MOVING)
        if direction >= 0:
            self.stage.move_right()
        else:
            self.stage.move_left()


if __name__ == "__main__":
    run([StandaStageTango])
