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

sbuf = create_string_buffer(64)
lib.ximc_version(sbuf)
def get_engine_settings(lib, device_id):
    engine_settings=engine_settings_t
    result = lib.engine_settings(device_id, byref(engine_settings))
    if result == Result.Ok:
        return result

def get_post