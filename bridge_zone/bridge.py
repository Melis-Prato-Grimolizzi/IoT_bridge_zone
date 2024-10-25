# from SX127x.LoRa import LoRa
import SessionHTTP as Http

def sendInitData(data):
    # send data to the microcontroller using LoRa
    pass


def fetchInitData(zone, url):
    if zone < 0 or zone is None:
        print(f"Error: zone is {zone} but it should be greater not None and greater than zero")

    # http://melis.prato.grimos.dev/parking/{zone}/
    url += zone
    session = Http.getSession()
    response = session.get(url)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    else:
        data = response.json()
        print('Data:')
        for key, value in data.items():
            print(f'{key}: {value}\n')
        return sendInitData(data)


def handleMessage():
    pass

def loop():
    while True:
        # if there is a message
        handleMessage()

def startBridge():
    """"
    we will stay in this loop until all the microcontrollers have contacted the bridge
    """
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
