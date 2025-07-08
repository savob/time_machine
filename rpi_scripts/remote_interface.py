import os
import serial
import serial.tools.list_ports

# Set to RPi Picos programmed using the Arduino IDE
REMOTE_VID = int("2E8A", 16)
REMOTE_PID = int("00C0", 16)

def find_usb_serial_by_id(target_vid, target_pid, fallback):
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if port.vid == target_vid and port.pid == target_pid:
            return port.device
    return fallback

class remote_control:
    port = serial.Serial(port=None, baudrate=115200, timeout=0)
    running = False

    def __init__(self):
        pass


    def shutdown(self):
        if self.running == True:
            self.port.close()
        self.running = False
        self.port.port = None

    def connect(self):
        # Check if the port still exists
        if (self.port.port == None):
            self.running = False
            self.port.port = find_usb_serial_by_id(REMOTE_VID, REMOTE_PID, self.port.port)
            return -1
        
        if os.path.exists(self.port.port) == False:
            self.shutdown()
            self.port.port = find_usb_serial_by_id(REMOTE_VID, REMOTE_PID, self.port.port)
            return -1
        
        if self.running == True:
            return 0
        
        self.port.open()
        self.running = True

        return 0

    def send(self, top : int, bottom :int):
        ret = self.connect()
        if ret != 0:
            return ret

        for number in [top, bottom]:
            self.port.write(number.to_bytes(2, 'big'))

        return 0
    
    def read(self) -> bytes:
        ret = self.connect()
        if ret != 0:
            return bytes()

        return self.port.readall()