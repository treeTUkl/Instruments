from ctypes import *
import time
import os
import sys
import tempfile
import re
if sys.version_info >= (3,0):
    import urllib.parse
try:
    from pyximc import *
except ImportError as err:
    print ("Can't import pyximc module. The most probable reason is that you haven't copied pyximc.py to the working directory. See developers' documentation for details.")
    exit()
except OSError as err:
    print ("Can't load libximc library. Please add all shared libraries to the appropriate places (next to pyximc.py on Windows). It is decribed in detail in developers' documentation. On Linux make sure you installed libximc-dev package.")
    exit()
def StandaConnect():
    # variable 'lib' points to a loaded library
    # note that ximc uses stdcall on win
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
            print("Enumerated device #{} name (port name): ".format(dev_ind) + repr(enum_name) + ". Friendly name: " + repr(controller_name.ControllerName) + ".")

    open_name = None
    if len(sys.argv) > 1:
        open_name = sys.argv[1]
    elif dev_count > 0:
        open_name = lib.get_device_name(devenum, 0)
    elif sys.version_info >= (3,0):
        # use URI for virtual device when there is new urllib python3 API
        tempdir = tempfile.gettempdir() + "/testdevice.bin"
        if os.altsep:
            tempdir = tempdir.replace(os.sep, os.altsep)
        # urlparse build wrong path if scheme is not file
        uri = urllib.parse.urlunparse(urllib.parse.ParseResult(scheme="file", \
                netloc=None, path=tempdir, params=None, query=None, fragment=None))
        open_name = re.sub(r'^file', 'xi-emu', uri).encode()

    if not open_name:
        exit(1)

    if type(open_name) is str:
        open_name = open_name.encode()

    print("\nOpen device " + repr(open_name))
    device_id = lib.open_device(open_name)
    print("Device id: " + repr(device_id))
return device_id