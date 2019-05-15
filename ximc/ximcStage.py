import Instruments.Stage
import ximcStage_connect
import ximcStage_functionCall


def roundTraditional(val,digits):
   return round(val+10**(-len(str(val))-1), digits)


class StandaStage(Instruments.Stage.Stage):
    def __init__(self):
        self.position_zero = 0
        self.position_current_Steps = 0
        self.position_current_uSteps = 0
        self.TerraFaktor=5
        #self.path = 1   #was das?
        #self.position_max = 150 not needed because its round
        #self.position_min = -150 not needed because its round
        self.MicrostepMode = 0
        self.MicrostepValue=2**MicrostepMode/2
        self.SetpsPerRev = 0
        self.Laser=633*10**-9 #should be 633*10^-9
        self.LichtinLuft=299705518
        self.Umrechnungsfaktor=(Laser/LichtinLuft)/((SetpsPerRev*3/2)*MicrostepValue)*1**+18 #Umrechungsfaktor in uSteps/as
        self.position_current_as = roundTraditional(
            position_current_Steps * MicrostepValue + position_current_uSteps * Umrechnungsfaktor * TerraFaktor, 1)
        #self.position_in_ps = 2 * 3.33333 * self.path * self.position_current
        #self.configuration = {'zero position': 0}
        self.velocity = 10

    def connect(self):
            ###
          #  '''rufe hier ximcStage_connect.py auf'''
            device_id= ximcStage_connect.StandaConnect()
            ###
            if device_id <= 0:
                print('kein Verbundenes Gerät...exiting')
                exit()
            else:
                #'''rufe hier ximcStage_functionCalls get engine settings auf'''
                engine_settings=ximcStage_functionCall.get_engine_settings(lib, device_id)
                MicrostepMode=engine_settings.MicrostepMode
                MicrostepValue=2**MicrostepMode/2
                SetpsPerRev=engine_settings.SepsPerRev
            ###########################################################################################
                Umrechnungsfaktor=(Laser/LichtinLuft)/((SetpsPerRev*3/2)*MicrostepValue)*1**+18
                position_current_as=roundTraditional(
                     position_current_Steps * MicrostepValue + position_current_uSteps * Umrechnungsfaktor * TerraFaktor, 1)
            #####muss ich hier Umrechungsfaktor etc aktuallisieren??? wenn ja wie? reicht? Umrechnungsfaktor=Umrechnungsfaktor?###



         print('connetcted to fake stage. current position=' + str(self.position_current) + '; zero possition' + str(
            self.position_zero)

    def disconnect(self):
        print('Fake stage has been disconnected')

    def move_absolute(self, new_position):
        # pos=new_position-self.position_zero
        time_to_sleep = (abs(self.position_current - new_position)) / self.velocity
        if (new_position <= self.position_max) and (new_position >= self.position_min):
            'here should be command for real stage; use pos for the real stage'
            self.position_current = new_position
            time.sleep(time_to_sleep)
            print('Fake stage was moved to ' + str(new_position))
        else:
            print('position is out of range')

    def move_relative(self, shift):
        if (self.position_current + shift <= self.position_max) and (
                self.position_current + shift >= self.position_min):
            self.move_absolute(self.position_current + shift)
            print('Fake stage was moved by ' + str(shift))
        else:
            print('position is out of range')

    def set_zero_position(self):
        self.position_zero = self.position_current
        self.position_max -= self.position_current
        self.position_min -= self.position_current
        self.position_current = 0

    def position_get(self):
        return self.position_current




if __name__ == "__main__":
    stage = StandaStage()
    stage.move_absolute(100)