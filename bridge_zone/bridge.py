# from SX127x.LoRa import LoRa
import json

import SessionHTTP as Http
import serial
import configparser
import serial.tools.list_ports
import struct



class Bridge:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.slots = None
        self.ser = None
        self.port_name = None

        self.setupSerial()
        self.getFakeData()

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
            self.ser = serial.Serial(port_name, 9600)
        except:
            print(f'Error occured while connecting to {port_name}')
            return None

        print(f'Connect to {port_name}!')

    def sendData(self):
        for i, slot in enumerate(self.slots):
            msg = bytearray()
            msg.append(0xFF)
            msg.append(len(slot))
            print(i)
            self.ser.write(len(slot))
            for elem in slot:
                msg.extend(bytearray(struct.pack("f", elem)))
            msg.append(0xFE)
        print('Finito!')


if __name__ == '__main__':
    br = Bridge()
    br.sendData()
