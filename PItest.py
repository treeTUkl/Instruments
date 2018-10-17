import PIStage
import time

c413 = PIStage.PIStage('117018374')

c413.connect()
c413.move_absolute(-4)
c413.move_absolute(2)
c413.move_absolute(-9)
c413.move_absolute(-40)
c413.move_absolute(8.5)
for i in range(10):
    print(c413.position_get())
    time.sleep(.005)
c413.disconnect()
