import PIStage
import time

c413=PIStage.PIStage()

c413.connect()
time.sleep(5)
c413.move_absolute('1',-4)
time.sleep(4.5)
c413.move_absolute('1', 2)
time.sleep(6.5)
c413.move_absolute('1', -9)
time.sleep(11.5)
c413.move_absolute('1', 9)
c413.disconnect()