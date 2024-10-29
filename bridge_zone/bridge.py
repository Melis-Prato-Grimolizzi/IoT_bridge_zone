# from SX127x.LoRa import LoRa
import SessionHTTP as Http


def sendInitData(zone, data):
    # send data to the microcontroller using LoRa

    """

    :param zone: the unique identifier for microcontroller
    :param data: the JSON data to send
    :return: return True if no error occurs, False otherwise
    """

    pass


def getSlotDataByZone(zone, uri):
    if zone < 0 or zone is None:
        print(f"Error: zone is {zone} but it should be greater not None and greater than zero")

    # http://melis.prato.grimos.dev/parking/{zone}/
    uri += zone
    session = Http.getSession()
    header = {
        'Content-Type': 'application/json'
    }
    response = session.get(uri, headers=header)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    else:
        data = response.json()
        print('Data:')
        for key, value in data.items():
            print(f'{key}: {value}\n')
        return data

def handleMessage():
    pass


def loop():
    while True:
        # if there is a message
        handleMessage()


def startBridge():
    initList = [False for i in range(0, 255)]

    """"
    we will stay in this loop until all the microcontrollers have contacted the bridge
    """
    while initList.count(False) > 0:
        # if channel.available > 0
        # suppose we riceved a dictionary from microcontroller
        data = {
            'head': {
                'start': 0xff,
                'type': 0xAA,  # stands for initialization request packet
                'size': 1,
            },
            'zone': 0,
            'end': 0xFE
        }

        if data['head']['type'] == 0xAA:
            zone = data['zone']
            if zone and not initList[zone]:
                data = getSlotDataByZone(zone, url='http://esempio.com')
                if sendInitData(zone, data):
                    initList[zone] = True




def setup():
    """
    we will create the LoRa connection and other stuff
    """
    pass


if __name__ == '__main__':
    getSlotDataByZone('http://')
    setup()
    startBridge()
    loop()
