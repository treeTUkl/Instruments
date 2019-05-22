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
        "Can't import pyximc module. The most probable reason is that you haven't copied pyximc.py to the working "
        "directory. See developers' documentation for details.")
    exit()
except OSError as err:
    print(
        "Can't load libximc library. Please add all shared libraries to the appropriate places (next to pyximc.py on "
        "Windows). It is decribed in detail in developers' documentation. On Linux make sure you installed "
        "libximc-dev package.")
    exit()


def roundTraditional(val, digits):
    return round(val + 10 ** (-len(str(val)) - 1), digits)


class StandaStage(Stage.Stage):
    def __init__(self):
        """Aus Stage"""
        self.position = {
            "position_current_Steps": 0,
            "position_current_uSteps": 0,
            "position_new_Steps": 0,
            "position_new_uSteps": 0,
        }
        """Aus Instrument"""
        self.connection_type = 'XIMC'
        self.configuration = {}
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

    def read(self):
        print("Direct Read not possible through ximc")

    def write(self):
        print("Direct write not possible through ximc")

    def save_configurution(self):
        print("Not implemented")

    def load_configurution(self):
        print("Not implemented")

    def set_configurution(self):
        print("Not implemented")

    def get_configurution(self):
        print("Not implemented")

    def in_case_terra_sends_SDN(self):
        time.sleep(.100)

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    """Standa Stage Befehle"""

    def position_get(self):
        positionHandler = dict(self.Standa_get_position())
        self.position["position_current_Steps"] = positionHandler["Position"]
        self.position["position_current_uSteps"] = positionHandler["uPosition"]

    def set_zero_position(self):
        self.lib.command_zero(self.device_id)  # "does this work?"

    def move_absolute_in_as(self, new_position_in_as):
        print('Move Ab in as aufgerufen!')
        print('neue Position in as: ' + repr(new_position_in_as))
        self.position_as_to_steps(new_position_in_as)
        print('neue Position in steps: ' + repr(self.position["position_new_Steps"]) + ', uSteps' + repr(
            self.position["position_new_uSteps"]))
        self.lib.command_move(self.device_id, self.position["position_new_Steps"], self.position["position_new_uSteps"])
        if self.statusHandler():
            print('Move Ab in as has arrived!')
        else:
            print('Move Ab in as something went wrong!')
        # TODO: hier antwort an SERVER Übergeben "POSXXXX" in as
        # position_current_in_as + POS übergeben
        # TODO: hier Diodenmessung von Redpit übernehmen!!!!
        #  An welcher stelle wird die Aufforderung für diodenmessung übergeben? aufruf über: AC_first_order(file_name)

    def move_absolute_in_steps(self, new_position_fullSteps, new_position_uSteps):
        print('Move Ab in steps aufgerufen!')
        self.position["position_new_Steps"] = new_position_fullSteps
        self.position["position_new_uSteps"] = new_position_uSteps
        print('neue Position in steps: ' + repr(self.position["position_new_Steps"]) + ', uSteps' + repr(
            self.position["position_new_uSteps"]))
        self.lib.command_move(self.device_id, self.position["position_new_Steps"], self.position["position_new_uSteps"])
        if self.statusHandler():
            print('Move Ab in steps has arrived!')
        else:
            print('Move Ab in steps something went wrong!')
        # TODO: hier antwort an SERVER Übergeben ?? "POSXXXX" in as
        # position_current_in_as + POS übergeben

    def move_relative_in_as(self, Shift_in_as):
        print('move_relative_in_as aufgerufen!')
        print('shift Position in as um: ' + repr(Shift_in_as))
        self.position_as_to_steps(Shift_in_as)
        print('position_new enthält jetzt die Shift Werte!')

        self.lib.command_movr(self.device_id, self.position["position_new_Steps"], self.position["position_new_uSteps"])
        self.position["position_new_Steps"] = self.position["position_current_Steps"] + self.position[
            "position_new_Steps"]
        self.position["position_new_uSteps"] = self.position["position_current_uSteps"] + self.position[
            "position_new_uSteps"]
        print('position_new enthält jetzt die neuen Ziel Werte!')
        print('position_new Steps' + repr(self.position["position_new_Steps"]) + ',position_new uSteps' + repr(
            self.position["position_new_uSteps"]))
        if self.position["position_new_uSteps"] >= self.MicrostepValue:
            self.position["position_new_Steps"] += 1
            self.position["position_new_uSteps"] -= self.MicrostepValue
            print('position korrigiert:')
            print('position_new Steps' + repr(self.position["position_new_Steps"]) + ',position_new uSteps' + repr(
                self.position["position_new_uSteps"]))
        if self.statusHandler():
            print('move_relative_in_as has arrived!')
        else:
            print('move_relative_in_as something went wrong!')
        # TODO: hier antwort an SERVER Übergeben ?? "POSXXXX" in as
        # position_current_in_as + POS übergeben

    def move_relative_in_steps(self, new_position_fullSteps, new_position_uSteps):
        print('move_relative_in_steps aufgerufen!')
        self.position["position_new_Steps"] = new_position_fullSteps
        self.position["position_new_uSteps"] = new_position_uSteps
        self.lib.command_movr(self.device_id, self.position["position_new_Steps"], self.position["position_new_uSteps"])

        self.position["position_new_Steps"] = self.position["position_current_Steps"] + self.position[
            "position_new_Steps"]
        self.position["position_new_uSteps"] = self.position["position_current_uSteps"] + self.position[
            "position_new_uSteps"]

        if self.position["position_new_uSteps"] >= self.MicrostepValue:
            self.position["position_new_Steps"] += 1
            self.position["position_new_uSteps"] -= self.MicrostepValue
            print('position korrigiert:')
            print('position_new Steps' + repr(self.position["position_new_Steps"]) + ',position_new uSteps' + repr(
                self.position["position_new_uSteps"]))

        if self.statusHandler():
            print('move_relative_in_steps has arrived!')
        else:
            print('move_relative_in_steps something went wrong!')
        # TODO: hier antwort an SERVER Übergeben ?? "POSXXXX" in as
        # position_current_in_as + POS übergeben

    def go_home(self):
        print('go_home aufgerufen!')
        self.position["position_new_Steps"] = 0
        self.position["position_new_uSteps"] = 0
        self.lib.command_home(self.device_id)
        if self.statusHandler():
            print('go_home has arrived!')
            # TODO: hier antwort an SERVER Übergeben ?? "POSXXXX" in as
        else:
            print('go_home something went wrong!')
            print('will set current position to new home')
            self.set_zero_position()

    def set_zero_position(self):
        print('set_zero_position aufgerufen!')
        self.position["position_new_Steps"] = 0
        self.position["position_new_uSteps"] = 0
        self.lib.command_zero(self.device_id)
        self.position_get()
        if self.statusHandler():
            print('set_zero_position has arrived!')
            # TODO: hier antwort an SERVER Übergeben ?? "POSXXXX" in as
        else:
            print('set_zero_position went wrong!')

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    """Stuff notwendig für Stage Befehle"""

    def Umrechnungsfaktor(self):
        return (self.Laser / self.LichtinLuft) / (
                (self.SetpsPerRev * 3 / 2) * self.MicrostepValue) * 1 ** +18  # Umrechungsfaktor in uSteps/as

    def position_current_in_as(self):
        Umrechnungsfaktor = self.Umrechnungsfaktor()
        return roundTraditional(
            self.position["position_current_Steps"] * self.MicrostepValue +
            self.position["position_current_uSteps"] * Umrechnungsfaktor * self.TerraFaktor, 1)

    def position_as_to_steps(self, new_position_in_as):
        value = new_position_in_as / self.Terra / self.Umrechnungsfaktor()
        self.position["position_new_Steps"] = math.floor(value / self.MicrostepValue)
        self.position["position_new_uSteps"] = value - self.MicrostepValue * self.position["position_new_Steps"]

    def statusHandler(self):
        statushand = self.lib.status_t()
        statushand["MoveSts"] = 1
        while statushand["MoveSts"] != 0:  # -> if move Flag is on w8
            time.sleep(.100)
            statushand = self.Standa_status()
            print('Moving...')
            self.position["position_current_Steps"] = statushand["CurPosition"]
            self.position["position_current_uSteps"] = statushand["uCurPosition"]
            print('Now at: Steps' + repr(self.position["position_current_Steps"]) + ', uSteps' + repr(
                self.position["position_current_uSteps"]))
            continue
        if self.position["position_current_Steps"] == self.position["position_new_Steps"]:
            print('Steps angekommen')
            if self.position["position_current_uSteps"] == self.position["position_new_uSteps"]:
                print('uSteps angekommen')
                return True
        else:
            print('something went wrong')
            return False
    def POS(self):
        self.position_get()
        print('pos in steps:' + stage.self.position["position_current_Steps"] + +'uSteps: ' +
              stage.self.position["position_current_uSteps"])
        POS = stage.position_current_in_as
        return POS
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    """Standa Stuff"""

    def Standa_Connect(self):
        # variable 'lib' points to a loaded library
        # note that ximc uses stdcall on win
        # lib = self.lib
        print("Library loaded")

        sbuf = create_string_buffer(64)
        lib.ximc_version(sbuf)
        print("Library version: " + sbuf.raw.decode())

        # This is device search and enumeration with probing. It gives more information about devices.
        devenum = lib.enumerate_devices(EnumerateFlags.ENUMERATE_PROBE, None)
        print("Device enum handle: " + repr(devenum))
        print("Device enum handle type: " + repr(type(devenum)))

        dev_count = lib.get_device_count(devenum)
        print("Device count: " + repr(dev_count))

        controller_name = controller_name_t()
        for dev_ind in range(0, dev_count):
            enum_name = lib.get_device_name(devenum, dev_ind)
            result = lib.get_enumerate_device_controller_name(devenum, dev_ind, byref(controller_name))
            if result == Result.Ok:
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
        lib.free_enumerate_devices(devenum)
        return device_id

    def Standa_Close(self):
        # self.lib.close_device(self.device_id)
        lib.close_device(byref(cast(self.device_id, POINTER(c_int))))  # aus testpython

    def Standa_get_engine_settings(self):
        engine_settings = engine_settings_t
        result = lib.engine_settings(self.device_id, byref(engine_settings))
        if result == Result.Ok:
            return result

    def Standa_get_position(self):
        print("\nRead position")
        x_pos = get_position_t()
        result = lib.get_position(self.device_id, byref(x_pos))
        print("Result: " + repr(result))
        if result == Result.Ok:
            print("Position: " + repr(x_pos.Position))
        return x_pos.Position

    def Standa_Status(self):
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
        x_status = status_t()
        result = lib.get_status(self.device_id, byref(x_status))
        print("Result: " + repr(result))
        if result == Result.Ok:
            print("Status.MoveSts: " + repr(x_status.MoveSts))
            print("Status.CurPosition : " + repr(x_status.CurPosition))
            print("Status.uCurPosition: " + repr(x_status.uCurPosition))
            print("Status.Flags: " + repr(hex(x_status.Flags)))
            #TODO:'does status_mode selection work? ' \            'and the return? '
        """How to handle lists of tupels:       
        https://thispointer.com/python-how-to-convert-a-list-to-dictionary/
        """
        status_dict = dict(x_status._fields_)
        return status_dict
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # redpitaya stuff
    def get_diode_voltage(self, redpitdatahandler):
#TODO:get_diode_voltage
# welche methode soll verwendet werden?
# #wie wird pyrpl eingebunden?-> pyrpl wird von Windows aus gestartet! also wie die Daten intern auf den Redpitaya hier her importieren?
#
        from pyrpl import Pyrpl
        r=pyrpl.Pyrpl().redpitaya
        if r.lockbox().islogging==True:

            if redpitdatahandler==1:
                voltage=r.sampler.in1
                print("Voltage at analog input1: %.3f" % r.sampler.in1)
                #voltage is 1 data point

            elif redpitdatahandler ==2:
                # take oscilloscope traces of the demodulated and pid signal
                voltage = r.scope.curve(input1='in1', input2='in2',
                                     duration=1.0, trigger_source='immediately')

            elif redpitdatahandler==3:
                # see how the adc reading fluctuates over time
                import time
                from matplotlib import pyplot as plt
                times, data = [], []
                t0 = time.time()
                n = 3000
                for i in range(n):
                    times.append(time.time() - t0)
                    data.append(r.scope.voltage_in1)
                print("Rough time to read one FPGA register: ", (time.time() - t0) / n * 1e6, "?s")
                % matplotlib
                inline
                f, axarr = plt.subplots(1, 2, sharey=True)
                axarr[0].plot(times, data, "+")
                axarr[0].set_title("ADC voltage vs time")
                axarr[1].hist(data, bins=10, normed=True, orientation="horizontal")
                axarr[1].set_title("ADC voltage histogram")
                voltage=data
            else:
                voltage=1
        else:
            print('redpitaya not in loggin mode')
            print('no logging no data!')
            voltage=0
        return voltage

    def AC_first_order(self,file_name):
        #voltage zerlegen?#TODO:funktioniert so das kontinuierliche schreiben in die csv?
        #case of redpitayahander ==1
        voltage=0
        for i in range(1, 11):
            voltage += self.get_diode_voltage(1)

        voltage=voltage/10
        with open(file_name +".csv", "w") as out_file:
                out_string = ""
                out_string += str(voltage)
                out_string += "," + str(self.position_current_in_as)
                out_string += "\n"
                out_file.write(out_string)

if __name__ == "__main__":
    stage = StandaStage()
    stage.Standa_Connect()
    #TODO: test this shit #debuggin #live
    stage.Standa_Status()
    stage.position_get()
    stage.Standa_get_position()
    stage.Umrechnungsfaktor()
    stage.Standa_get_engine_settings()
    stage.move_absolute_in_as(190)
    stage.in_case_terra_sends_SDN()

