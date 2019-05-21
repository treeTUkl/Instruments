from ctypes import *
import time
import os
import sys
import tempfile
import re
import Stage
import math

if sys.version_info >= (3, 0):
    import urllib.parse
try:
    from pyximc import *
except ImportError as err:
    print(
        "Can't import pyximc module. The most probable reason is that you haven't copied pyximc.py to the working directory. See developers' documentation for details.")
    exit()
except OSError as err:
    print(
        "Can't load libximc library. Please add all shared libraries to the appropriate places (next to pyximc.py on Windows). It is decribed in detail in developers' documentation. On Linux make sure you installed libximc-dev package.")
    exit()


def roundTraditional(val, digits):
    return round(val + 10 ** (-len(str(val)) - 1), digits)


class StandaStage(Stage.Stage):
    def __init__(self):
        """Aus Stage"""
        self.position= {
            "position_current_Steps": 0,
            "position_current_uSteps": 0,
            "position_new_Steps":0,
            "position_new_uSteps":0,
        }
        """Aus Instrument"""
        self.connection_type='XIMC'
        self.configuration={}
        self.load_configurution()
        self.position_zero = 0
        self.TerraFaktor = 5
        self.MicrostepMode = 1
        self.MicrostepValue = 2 ** self.MicrostepMode / 2
        self.SetpsPerRev = 1
        self.Laser = 633 * 10 ** -9  # should be 633*10^-9
        self.LichtinLuft = 299705518
        self.velocity = 10
        self.device_id = None

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    """Aus Instrument"""
    def connect(self):
        if self.device_id is not None:
            print('Device already connected')
            return True
        else:
            self.device_id = self.Standa_Connect()
            if self.device_id <= 0:
                print('kein Verbundenes Gerät...exiting')
                return False
            else:
                """rufe hier ximcStage_functionCalls get engine settings auf"""
                engine_settings = self.Standa_get_engine_settings()
                self.MicrostepMode = engine_settings.MicrostepMode
                self.SetpsPerRev = engine_settings.SepsPerRev

                print('Verbundenes Gerät' + str(self.device_id))
                return True

    def disconnect(self):
        if self.device_id is not None:
            self.Standa_Close()
            self.device_id = None
            print('Connection has been closed')

    def read(self):"""Direct Read not possible through ximc"""
        pass

    def write(self):"""Direct write not possible through ximc"""
        pass
    def save_configurution(self):"""Not implemented"""
        pass
    def load_configurution(self):"""Not implemented"""
        pass
    def set_configurution(self):"""Not implemented"""
        pass
    def get_configurution(self):"""Not implemented"""
        pass
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    """Standa Stage Befehle"""
    def position_get(self):
        self.position_current = self.Standa_get_position()

    def set_zero_position(self):
        self.lib.command_zero(self.device_id)"does this work?"

    def move_absolute_in_as(self, new_position_in_as):
        position_as_to_steps(new_position_in_as)
        self.lib.command_move(self.device_id, self.position_current_Steps, self.position_current_uSteps)

    def move_absolute_in_steps(self, new_position_fullSteps, new_position_uSteps)
        self.position_current_Steps= new_position_fullSteps
        self.position_current_uSteps=new_position_uSteps
        self.lib.command_move(self.device_id, self.position_current_Steps, self.position_current_uSteps)

    def move_relative_in_as(self, shift):pass

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    """Stuff notwendig für Stage Befehle"""
    def Umrechnungsfaktor(self):

        return (self.Laser / self.LichtinLuft) / (
                (self.SetpsPerRev * 3 / 2) * self.MicrostepValue) * 1 ** +18  # Umrechungsfaktor in uSteps/as

    def position_current_in_as(self):
        return roundTraditional(
            self.position_current_Steps * self.MicrostepValue +
            self.position_current_uSteps * self.Umrechnungsfaktor * self.TerraFaktor,
            1)
    def position_as_to_steps(self,new_position_in_as)
        value= new_position_in_as/self.Terra/Umrechnungsfaktor(self)
        self.position_current_Steps = math.floor(value/self.MicrostepValue)
        self.position_current_uSteps = value-self.MicrostepValue*self.position_current_Steps
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    """Standa Stuff"""
    def Standa_Connect(self):
        # variable 'lib' points to a loaded library
        # note that ximc uses stdcall on win
        lib = self.lib
        print("Library loaded")

        sbuf = create_string_buffer(64)
        lib.ximc_version(sbuf)
        print("Library version: " + sbuf.raw.decode())

        # This is device search and enumeration with probing. It gives more information about devices.
        devenum = lib.enumerate_devices(self.EnumerateFlags.ENUMERATE_PROBE, None)
        print("Device enum handle: " + repr(devenum))
        print("Device enum handle type: " + repr(type(devenum)))

        dev_count = lib.get_device_count(devenum)
        print("Device count: " + repr(dev_count))

        controller_name = self.controller_name_t()
        for dev_ind in range(0, dev_count):
            enum_name = lib.get_device_name(devenum, dev_ind)
            result = lib.get_enumerate_device_controller_name(devenum, dev_ind, byref(controller_name))
            if result == self.Result.Ok:
                print("Enumerated device #{} name (port name): ".format(dev_ind) + repr(
                    enum_name) + ". Friendly name: " + repr(controller_name.ControllerName) + ".")

        open_name = None
        if len(sys.argv) > 1:
            open_name = sys.argv[1]
        elif dev_count > 0:
            open_name = lib.get_device_name(devenum, 0)
        elif sys.version_info >= (3, 0):
            # use URI for virtual device when there is new urllib python3 API
            tempdir = tempfile.gettempdir() + "/testdevice.bin"
            if os.altsep:
                tempdir = tempdir.replace(os.sep, os.altsep)
            # urlparse build wrong path if scheme is not file
            uri = urllib.parse.urlunparse(urllib.parse.ParseResult(scheme="file", \
                                                                   netloc=None, path=tempdir, params=None, query=None,
                                                                   fragment=None))
            open_name = re.sub(r'^file', 'xi-emu', uri).encode()

        if not open_name:
            exit(1)

        if type(open_name) is str:
            open_name = open_name.encode()

        print("\nOpen device " + repr(open_name))
        device_id = lib.open_device(open_name)
        print("Device id: " + repr(device_id))
        'does the free_enum work?'
        lib.free_enumerate_devices(lib.enumerate_devices.restype)
        return device_id

    def Standa_Close(self):
        #self.lib.close_device(self.device_id)
        self.lib.close_device(byref(cast(self.device_id, POINTER(c_int))))# aus testpython

    def Standa_get_engine_settings(self):
        engine_settings = self.engine_settings_t
        result = self.lib.engine_settings(self.device_id, byref(engine_settings))
        if result == self.Result.Ok:
            return result

    def Standa_get_position(self):
        print("\nRead position")
        x_pos = self.get_position_t()
        result = self.lib.get_position(self.device_id, byref(x_pos))
        print("Result: " + repr(result))
        if result == self.Result.Ok:
            print("Position: " + repr(x_pos.Position))
        return x_pos.Position

#########################################################################
#poistion noch auf self.position übertragen!!
    """	x_pos.Position:
        _fields_ = [
		("Position", c_int),
		("uPosition", c_int),
		("EncPosition", c_longlong),
	]"""#########################################################################

    def Standa_status(self):
        """ possible status_mode should be:
            MoveSts         Flags of move state
    		MvCmdSts        Move command state
    	    PWRSts          Flags of power state of stepper motor
    		EncSts          Encoder state
    		WindSts         Winding state
    		CurPosition     Current position
    		uCurPosition    Step motor shaft position in 1/256 microsteps
    		EncPosition     Cureent encoder position
    		CurSpeed        Motor shaft speed
    		uCurSpeed       Part of motor shaft speed in 1/2256 microsteps
    		Ipwr            Engine current
    		Upwr            Power supply voltage
    		Iusb            USB current consumption
    		Uusb            USB voltage
    		CurT            Temperature in thnths od degress C
    		Flags           Status flags
    		GPIOFlags       Status flags
    		CmdBufFreeSpace This field shows the amount of free cells buffer synchronizazion chain
    	"""
        print("\nGet status")
        x_status = self.status_t()
        result = lib.get_status(self.device_id, byref(x_status))
        print("Result: " + repr(result))
        if result == Result.Ok:
            print("Status.MoveSts: " + repr(x_status.MoveSts))
            print("Status.CurPosition : " + repr(x_status.CurPosition ))
            print("Status.uCurPosition: " + repr(x_status.uCurPosition))
            print("Status.Flags: " + repr(hex(x_status.Flags)))
            'does status_mode selection work? ' \
            'and the return? '
        """How to handle lists of tupels:       
        https://thispointer.com/python-how-to-convert-a-list-to-dictionary/
        """
        status_dict = dict(x_status._fields_)
        return status_dict

    #
    # def move_absolute(self, new_position):
    #     # pos=new_position-self.position_zero
    #     time_to_sleep = (abs(self.position_current - new_position)) / self.velocity
    #      if (new_position <= self.position_max) and (new_position >= self.position_min):
    #         'here should be command for real stage; use pos for the real stage'
    #         self.position_current = new_position
    #         time.sleep(time_to_sleep)
    #         print('Fake stage was moved to ' + str(new_position))
    #     else:
    #         print('position is out of range')
    #
    #     def move_relative(self, shift):
    #         if (self.position_current + shift <= self.position_max) and (
    #                 self.position_current + shift >= self.position_min):
    #             self.move_absolute(self.position_current + shift)
    #             print('Fake stage was moved by ' + str(shift))
    #         else:
    #             print('position is out of range')
    #
    #     def set_zero_position(self):
    #         self.position_zero = self.position_current
    #         self.position_max -= self.position_current
    #         self.position_min -= self.position_current
    #         self.position_current = 0


if __name__ == "__main__":
    stage = StandaStage()
    stage.Standa_connect()
    stage.Standa_status()
    # stage.move_absolute(100)
