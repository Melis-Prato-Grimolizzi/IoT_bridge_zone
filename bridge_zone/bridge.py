# from SX127x.LoRa import LoRa
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
        print(response.text)


    def createBridgeUser(self):
        session = SessionHTTP.getSession()
        body = {
            'username': 'bridge',
            'password': 'qwertyui'
        }
        response = session.post('http://localhost:3000/users/signup', data=body)
        print(response.text)

    def bridgeLoginSerice(self):
        session = SessionHTTP.getSession()
        data = {
            'username': 'bridge',
            'password': 'password'
        }
        response = session.post('http://localhost:3000/users/login', data=data)
        self.bearer = 'Bearer ' + response.text
        print(response.text)
        print(self.bearer)

    def verifyBridgeService(self):
        session = SessionHTTP.getSession()
        header = {
            'Authorization': self.bearer
        }
        response = session.get('http://localhost:3000/users/verify', headers=header)
        print(response.text)

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
        print(response.text)

    def addSlotList(self):
        session = SessionHTTP.getSession()
        header = {
            'Authorization': self.bearer
        }
        for slot in self.slots:
            data = {
                'zone': slot[0],  # zone
                'latitude': slot[2],  # latitude
                'longitude': slot[3], # longitude
                'parking_id': slot[1]  # parking_id
            }
            response = session.post('http://localhost:3000/slots/add_slot', headers=header, data=data)
            print(response.text)

    def updateSlotState(self, park_id):
        session = SessionHTTP.getSession()
        header = {
            'Authorization': self.bearer
        }
        url = 'http://localhost:3000/slots/update_slot_state/' + str(park_id)
        response = session.post(url, headers=header)
        print(response.text)

    def deleteSlot(self, park_id):
        session = SessionHTTP.getSession()
        header = {
            'Authorization': self.bearer
        }
        url = 'http://localhost:3000/slots/delete_slot/' + str(park_id)
        response = session.delete(url, headers=header)
        print(response.text)

    def getSlotState(self, park_id):
        session = SessionHTTP.getSession()
        url = 'http://localhost:3000/slots/get_slot_state/' + str(park_id)
        response = session.get(url)
        print(response.text)

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

    def startBridge(self):
        data = self.getSlotData('http://melis.prato.grimos.dev/parking/')

        # TODO: mandare i dati a tutti i microcontrollori
        pass

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

        print('Finito!')

    def loop(self):
        while True:
            if self.ser.in_waiting > 0:
                time.sleep(0.1)
                id = self.ser.read()
                id_int = int.from_bytes(id)
                print(f'ID: {id_int}\n')
                print('Entrato')
                self.updateSlotState(id_int)
                '''
                time.sleep(0.01)
                id = self.ser.read()
                print('ID: ', id[0])
                zone = self.ser.read()
                print('Zone: ', zone[0])
                if self.ser.in_waiting >= 4:
                    lat_data = self.ser.read(4)  # Legge i 4 byte per lat
                    lat = struct.unpack('<f', lat_data)[0]  # Decodifica in float
                    print('Lat: ', lat)
                if self.ser.in_waiting >= 4:
                    lon_data = self.ser.read(4)  # Legge i 4 byte per lon
                    lon = struct.unpack('<f', lon_data)[0]  # Decodifica in float
                    print('Lon: ', lon)
                error = self.ser.read()
                print('CODE: ', error[0])
                '''



if __name__ == '__main__':
    br = Bridge()
    #br.createBridgeUser()

    br.bridgeLoginSerice()
    #br.verifyBridgeService()
    # br.addSlotList()
    # br.getSlotState(id)
    # br.updateSlotState(id)
    # br.getSlotState(id)
    # br.deleteSlot(id)
    # br.addSlot()
    # br.sendData()
    br.loop()
    br.ser.close()
