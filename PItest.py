import PIStage
import time
import gevent
from gevent import monkey
monkey.patch_all()


def delay(duration):
    time.sleep(duration)
    print('delay over')


c413 = PIStage.PIStage('117018374')

c413.connect()
print(c413.last_error)
c413.move_absolute(-4)
tasks = [
    gevent.spawn(c413.move_absolute, 8),
    gevent.spawn(delay, 5),
    gevent.spawn(delay, 5),
    gevent.spawn(delay, 5)
]
gevent.joinall(tasks)
c413.move_absolute(2)
print(c413.on_target_state())
c413.move_absolute(-9)
c413.move_absolute(-40)
c413.move_absolute(8.5)
for i in range(10):
    print(c413.position_get())
    time.sleep(.001)
c413.disconnect()
