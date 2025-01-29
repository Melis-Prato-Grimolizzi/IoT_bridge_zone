import json
import SessionHTTP
import SessionHTTP as Http
import serial
import configparser
import serial.tools.list_ports
import struct
import time

class Bridge:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.slots = None
        self.ser = serial.Serial()
        self.port_name = None

        self.bearer = None

        self.setupSerial()
        self.getFakeData()


    def getUser(self):
        session = SessionHTTP.getSession()
        response = session.get('http://localhost:3000/users/')
        print(f"DEBUG: Response for server (Get user): {response.text}")

    def createBridgeUser(self):
        session = SessionHTTP.getSession()
        body = {
            'username': 'bridge',
            'password': 'qwertyui'
        }
        response = session.post('http://localhost:3000/users/signup', data=body)
        print(f"DEBUG: Response for server (Create user): {response.text}")

    def bridgeLoginService(self):
        session = SessionHTTP.getSession()
        data = {
            'username': 'bridge',
            'password': 'password'
        }
        response = session.post('http://localhost:3000/users/login', data=data)
        self.bearer = 'Bearer ' + response.text
        print(f"DEBUG: Response for server (Login): {response.text}")

    def verifyBridgeService(self):
        session = SessionHTTP.getSession()
        header = {
            'Authorization': self.bearer
        }
        response = session.get('http://localhost:3000/users/verify', headers=header)
        print(f"DEBUG: Response for server (Verify login): {response.text}")

    def addSlotTest(self):
        session = SessionHTTP.getSession()
        header = {
            'Authorization': self.bearer
        }
        data = {
            'zone': 1,
            'latitude': 43.9,
            'longitude': 11.1
        }
        response = session.post('http://localhost:3000/slots/add_slot', headers=header, data=data)
        print(f"DEBUG: Response for server (Adding slot): {response.text}")

    def addSlotList(self):
        session = SessionHTTP.getSession()
        header = {
            'Authorization': self.bearer
        }
        for slot in self.slots:
            data = {
                'zone': slot[0],  # zone
                'latitude': slot[2],  # latitude
                'longitude': slot[3],  # longitude
                'parking_id': slot[1]  # parking_id
            }
            response = session.post('http://localhost:3000/slots/add_slot', headers=header, data=data)
            print(f"DEBUG: Response for server (Adding slot): {response.text}")

    def updateSlotState(self, park_id):
        session = SessionHTTP.getSession()
        header = {
            'Authorization': self.bearer
        }
        url = 'http://localhost:3000/slots/update_slot_state/' + str(park_id)
        response = session.post(url, headers=header)
        print(f"DEBUG: Response for server (Updating slot {park_id}): {response.text}")
        return response.status_code

    def deleteSlot(self, park_id):
        session = SessionHTTP.getSession()
        header = {
            'Authorization': self.bearer
        }
        url = 'http://localhost:3000/slots/delete_slot/' + str(park_id)
        response = session.delete(url, headers=header)
        print(f"DEBUG: Response for server (Deleting slot {park_id}): {response.text}")

    def getSlotState(self, park_id):
        session = SessionHTTP.getSession()
        url = 'http://localhost:3000/slots/get_slot_state/' + str(park_id)
        response = session.get(url)
        print(f"DEBUG: Response for server (Getting slot {park_id} state): {response.text}")

    def getFakeData(self):
        with open('slot.json', 'r') as file:
            self.slots = json.load(file)

    def getSlotData(self, uri):
        # http://melis.prato.grimos.dev/parking/
        session = Http.getSession()
        header = {
            'Content-Type': 'application/json'
        }
        response = session.get(uri, headers=header)
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return None
        else:
            data = response.json().to_dict()
            print('Data:')
            for value in data:
                print(f'{value}\n')
            return data

    def setupSerial(self):

        port_name = None
        for port in serial.tools.list_ports.comports():
            if self.config.get('Serial', 'PortDescription', fallback='Arduino') in port.description:
                print(port)
                port_name = port.device
        try:
            print(f'Connecting to {port_name}...')
            self.ser = serial.Serial(port_name, self.config.get('Serial', 'BaudRate', fallback=9600))
        except serial.SerialException as e:
            print(f'Error occurred while connecting to {port_name}')
            print('Error:', e)
            return None
        time.sleep(2)
        print(f'Connect to {port_name}!')

    def sendData(self):
        for i, slot in enumerate(self.slots):
            msg = bytearray()
            msg.append(0xFF)
            msg.append(len(slot))
            for elem in slot:
                if isinstance(elem, float):
                    msg.extend(struct.pack('f', elem))
                else:
                    msg.append(elem)
            msg.append(0xFE)
            time.sleep(0.02)
            self.ser.write(msg)
            print(msg)

    def readFloatData(self):
        time.sleep(0.01)
        id_b = self.ser.read()
        print('ID: ', id_b[0])
        zone = self.ser.read()
        print('Zone: ', zone[0])
        if self.ser.in_waiting >= 4:
            lat_data = self.ser.read(4)  # reading 4 bytes for lat
            lat = struct.unpack('<f', lat_data)[0]  # decoding in float
            print('Lat: ', lat)
        if self.ser.in_waiting >= 4:
            lon_data = self.ser.read(4)  # reading 4 bytes for lon
            lon = struct.unpack('<f', lon_data)[0]  # decoding in float
            print('Lon: ', lon)

    def loop(self):
        print("Loop is starting...")
        try:
            while True:
                # if there is data to read, read it
                if self.ser is not None and self.ser.is_open and self.ser.in_waiting > 0:
                    time.sleep(0.1)
                    id_b = self.ser.read()
                    id_int = int.from_bytes(id_b)
                    print(f'Trying to update slot {id_int}...\n')
                    status_code = self.updateSlotState(id_int)
                    if status_code == 200:
                        print(f'Slot {id_int} updated!')
                    else:
                        print(f'Error updating slot {id_int}!')
        except KeyboardInterrupt:
            print("Exiting...")
            self.ser.close()
            print("Serial port closed!")



if __name__ == '__main__':
    br = Bridge()
    br.bridgeLoginService()
    # br.verifyBridgeService()
    # br.getUser()
    # br.addSlotList()
    # br.getSlotState(5)
    # br.updateSlotState(5)
    # br.getSlotState(5)
    # br.getSlotState(id)
    # br.deleteSlot(id)
    # br.addSlot()
    # br.sendData()
    br.loop()
    br.ser.close()
