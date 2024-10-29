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


def getSlotData(uri):
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

def handleMessage():
    pass


def loop():
    while True:
        # if there is a message
        handleMessage()


def startBridge():
    data = getSlotData('http://melis.prato.grimos.dev/parking/')

    # TODO: mandare i dati a tutti i microcontrollori
    pass




def setup():
    """
    we will create the LoRa connection and other stuff
    """
    pass


if __name__ == '__main__':
    setup()
    startBridge()
    loop()
