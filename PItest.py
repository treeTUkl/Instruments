import PIStage

c413 = PIStage.PIStage('117018374')

c413.connect()
c413.pi_error_check(True)
c413.move_absolute(-4)
print(c413.position_get())
c413.move_absolute(2)
print(c413.position_get())
c413.pi_error_check(True)
c413.move_absolute(-9)
print(c413.position_get())
c413.move_absolute(-40)
c413.move_absolute(9)
print(c413.position_get())
c413.pi_error_check(True)
c413.disconnect()
