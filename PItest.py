import PIStage
import time
import gevent
from gevent import monkey
monkey.patch_all()


def delay(duration):
    time.sleep(duration)
    print('delay over')


def wait():
    while not c413.on_target_state():
        time.sleep(.01)
        print(c413.position_get())
        print("ONT: " + str(c413.on_target_state()))
        print(c413.position_get())


c413 = PIStage.PIStage('117018374')

c413.connect()
print(c413.last_error)
c413.move_absolute(0)
wait()
print("ONT: " + str(c413.on_target_state()))
c413.move_absolute(-.4)
print("ONT: " + str(c413.on_target_state()))
wait()
tasks = [
    gevent.spawn(c413.move_absolute, 8),
    gevent.spawn(delay, 5),
    gevent.spawn(delay, 5)
]
gevent.joinall(tasks)
c413.disconnect()
