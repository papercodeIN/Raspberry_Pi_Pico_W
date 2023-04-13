# import modbus host classes
from umodbus.tcp import ModbusTCP
import time
from machine import Pin
import network

myLED = Pin('LED',Pin.OUT)
# ===============================================
# connect to a network
station = network.WLAN(network.STA_IF)
if station.active() and station.isconnected():
    station.disconnect()
    time.sleep(1)
station.active(False)
time.sleep(1)
station.active(True)

station.connect('WIFI SSID', 'WIFI PASSWORD')
time.sleep(1)

while True:
    print('Waiting for WiFi connection...')
    if station.isconnected():
        print('Connected to WiFi.')
        print(station.ifconfig())
        break
    time.sleep(2)
# ===============================================
tcp_port = 502
local_ip = station.ifconfig()[0]

# ModbusTCP can get TCP requests from a host device to provide/set data
client = ModbusTCP()
is_bound = False

# check whether client has been bound to an IP and port
is_bound = client.get_bound_status()

if not is_bound:
    client.bind(local_ip=local_ip, local_port=tcp_port)


def my_coil_set_cb(reg_type, address, val):
    #print('Custom callback, called on setting {} at {} to: {}'.format(reg_type, address, val))
    if int(val[0]) == 1:myLED.on()
    elif int(val[0]) == 0:myLED.off()

def my_coil_get_cb(reg_type, address, val):
    #print('Custom callback, called on getting {} at {}, currently: {}'.format(reg_type, address, val))
    if int(val[0]) == 1:myLED.on()
    elif int(val[0]) == 0:myLED.off()

# commond slave register setup, to be used with the Master example above
register_definitions = {"COILS": {"EXAMPLE_COIL": {"register": 2,"len": 1,"val": 1}}}

register_definitions['COILS']['EXAMPLE_COIL']['on_set_cb'] = my_coil_set_cb
register_definitions['COILS']['EXAMPLE_COIL']['on_get_cb'] = my_coil_get_cb


print('Setting up registers ...')
client.setup_registers(registers=register_definitions)
print('Register setup done')
print('Serving as TCP client on {}:{}'.format(local_ip, tcp_port))

while True:
    try:
        result = client.process()
    except KeyboardInterrupt:
        print('KeyboardInterrupt, stopping TCP client...')
        break
    except Exception as e:
        print('Exception during execution: {}'.format(e))

print("Finished providing/accepting data as client")
