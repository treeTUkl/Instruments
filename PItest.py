import PIStage
import time

c413=PIStage.PIStage()

c413.connect('117018374')
c413.move_absolute(-4)
c413.move_absolute(2)
c413.move_absolute(-9)
c413.move_absolute(-40)
c413.move_absolute(9)
c413.disconnect()