# IoT_bridge_zone

## Overview
This bridge build up the connection beetween our parking sensor and our backend

## Bridge operations
- we create the bridge object that contains all the utils
- in the init we build up the serial connection searching for a port with Arduino connected
- bridge perform login in into the server and retrives the bearer token, used for auth operation
- the collector daemon is started; it collects periodically the state of all parking slot, and then it post it into an history table
- now our bridge goes in the loop where it continuously look for data from the serial channel

## Update Parking slot
The major feature of our bridge is the updating of slot state. It is done by waiting from serial data, then parsing the byte readed and contacting the server to update the slot's state
