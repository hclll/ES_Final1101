# Embedding System HW2

### Tool used
* matplotlib
* socket
* mbed

### How to use

#### At first, please change some wifi setting to yours.   
  * change "./mbed_app.json"  line 14-15
    ```
      "nsapi.default-wifi-ssid": "\"YourWIFIname\"",
      "nsapi.default-wifi-password": "\"Password\"",
    ```
    for example,
    ```
      "nsapi.default-wifi-ssid": "\"myphone\"",
      "nsapi.default-wifi-password": "\"abcdefg\"",
    ```
    
    !!! ATTENTION
    * If your wifi name includes characters not in english, it may have problem while connecting
    * Please do not take off   ```\"```, it is important for maintaining string type.
 
  * change "./ws_server.py" line 13, line 25-26
    ```
    # line 1
      mode = 2  # can switch between 1 and 2 to test
    # line 25 - 26
      HOST = 'xxx.xxx.xxx.xxx' # change to the IPv4 address of your computer
      PORT = 62023 # change to any number you like from 49152-65535
    ```
    
  * change "./source/main.cpp" line 51, line 119, line 157
    ```
    // line 51
      static constexpr size_t REMOTE_PORT = 62023; // standard HTTP port // change to the same number as the one in "./ws_server.py"
    // line 119
      address.set_ip_address("xxx.xxx.xxx.xxx"); // change to the HOST address as the one in "./ws_server.py"
    // line 157
      ThisThread::sleep_for(10000); // you can change the sample interval (default is 10000 ms)
    ```
    
#### Start the server
  ```
  python3 ws_server.py
  ```
  
#### Run mbed
Press "Run Program" button
  
 
##### !!! ATTENTION
* The server should be started before the mbed program runs. Or there may be the error
  ```
  OSError: [Errno 48] Address already in use
  ```
  Then you should change a new port number, or restart both mbed and server.
* If you choose the port number out of range, the error may occur
  ```
  OverflowError: getsockaddrarg: port must be 0-65535.
  ```

### Expected output

#### PYTHON

```
Connected by ('172.20.10.2', 24555)
Received from socket server :  GET / HTTP/1.1
Host: ifconfig.io
Connection: close


Received from socket server :  {"x":-361,"y":287,"z":894,"s":1}
Received from socket server :  {"x":-328,"y":195,"z":941,"s":2}
Received from socket server :  {"x":460,"y":890,"z":286,"s":3}
Received from socket server :  {"x":376,"y":870,"z":293,"s":4}
Received from socket server :  {"x":378,"y":872,"z":287,"s":5}
Received from socket server :  {"x":377,"y":871,"z":287,"s":6}
Received from socket server :  {"x":383,"y":873,"z":271,"s":7}
Received from socket server :  {"x":383,"y":874,"z":271,"s":8}
Received from socket server :  {"x":382,"y":875,"z":275,"s":9}
Received from socket server :  {"x":382,"y":873,"z":278,"s":10}
...
```

While choosing mode 1 (colorbar), the figure will be:

![image](https://user-images.githubusercontent.com/71332212/138418071-4266115c-b80e-4557-8025-47fa059e658c.png)


Choosing mode 2 (color the newest one), the figure will be

![image](https://user-images.githubusercontent.com/71332212/138418201-97a42481-3935-426b-8f47-22e6c1876935.png)



#### MBED
```
Starting socket demo

Start sensor init
3 networks available:
Network: banana secured: WPA2 BSSID: B0:6E:BF:49:39:70 RSSI: -92 Ch: 1
Network:  secured: WPA2 BSSID: 26:52:25:70:de:f0 RSSI: -26 Ch: 6
Network: 0917572720 secured: WPA2 BSSID: 20:10:7A:c7:7e:aa RSSI: -64 Ch: 11

Connecting to the network...
IP address: 172.20.10.2
Netmask: 255.255.255.240
Gateway: 172.20.10.1
Opening connection to remote port 62022

Sending message: 
GET / HTTP/1.1
Host: ifconfig.io
Connection: close

sent 56 bytes
Complete message sent
Sample 1

Sending message: 
{"x":-361,"y":287,"z":894,"s":1}
sent 32 bytes
Complete message sent
Sample 2

Sending message: 
{"x":-328,"y":195,"z":941,"s":2}
sent 32 bytes
Complete message sent
...

```
