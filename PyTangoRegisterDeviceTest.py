from PyTango import Database, DbDevInfo

#  A reference on the DataBase
db = Database()

# The devices name we want to create
new_device_name = "PIStageTango/ktof/pi_stage/test/c413test"

# Define the Tango Class served by this  DServer
new_device_info_stage = DbDevInfo()
new_device_info_stage._class = "linear Stage"
new_device_info_stage.server = "TangoTest"

# add the device
print("Creating device: %s" % new_device_name)
new_device_info_stage.name = new_device_name
db.add_device(new_device_info_stage)
