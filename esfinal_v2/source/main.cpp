/* Sockets Example
 * Copyright (c) 2016-2020 ARM Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "File.h"
#include "NetworkInterface.h"
#include "PinNameAliases.h"
#include "ThisThread.h"
#include "mbed.h"
#include "wifi_helper.h"

// for sensors
#include "mbed-trace/mbed_trace.h"
#include "stm32l475e_iot01_tsensor.h"
#include "stm32l475e_iot01_hsensor.h"
#include "stm32l475e_iot01_psensor.h"
#include "stm32l475e_iot01_magneto.h"
#include "stm32l475e_iot01_gyro.h"
#include "stm32l475e_iot01_accelero.h"

// for microphone
#include "stm32l475e_iot01_audio.h"

// for beep
#include "beep.h"

#include <cstdint>

#if MBED_CONF_APP_USE_TLS_SOCKET
static constexpr size_t REMOTE_PORT = 443; // tls port
#else
static constexpr size_t REMOTE_PORT = 61052 ;                                                                                                                                                                                                                                                                ; // standard HTTP port
#endif // MBED_CONF_APP_USE_TLS_SOCKET

float sensor_value = 0;
int16_t pDataXYZ[3] = {0};
float pGyroDataXYZ[3] = {0};

Semaphore send_sem(1);
InterruptIn button(BUTTON1);

static BSP_AUDIO_Init_t MicParams;
static uint16_t PCM_Buffer[PCM_BUFFER_LEN / 2];

int8_t pressed = 0;

//


#if MBED_CONF_APP_USE_TLS_SOCKET
#include "root_ca_cert.h"

#ifndef DEVICE_TRNG
#error "mbed-os-example-tls-socket requires a device which supports TRNG"
#endif
#endif // MBED_CONF_APP_USE_TLS_SOCKET


static DigitalOut led(LED1);
static EventQueue ev_queue;

// Place to store final audio (alloc on the heap), here two seconds...
static size_t TARGET_AUDIO_BUFFER_NB_SAMPLES = AUDIO_SAMPLING_FREQUENCY / 200; // 0.02 sec
static int16_t *TARGET_AUDIO_BUFFER = (int16_t*)calloc(TARGET_AUDIO_BUFFER_NB_SAMPLES, sizeof(int16_t));
static size_t TARGET_AUDIO_BUFFER_IX = 0;

// we skip the first 50 events (100 ms.) to not record the button click
static size_t SKIP_FIRST_EVENTS = 0;
static size_t half_transfer_events = 0;
static size_t transfer_complete_events = 0;

/* functions */
void print_network_info();
bool send_http_request();
bool receive_http_response();
char receive_server_message();
bool send_json(char * );
void send_data();

void start_recording();

char wav_json[325];
char acc_json[100]; 

Beep buzzer(A0);

void target_audio_buffer_full() {
    // pause audio stream
    // int32_t ret = BSP_AUDIO_IN_Pause(AUDIO_INSTANCE);
    // if (ret != BSP_ERROR_NONE) {
    //     printf("Error Audio Pause (%d)\n", ret);
    // }
    // else {
    //     printf("OK Audio Pause\n");
    // }
    int32_t ret = BSP_AUDIO_IN_Stop(AUDIO_INSTANCE);
    if (ret != BSP_ERROR_NONE) {
        printf("Error Audio Stop (%d)\n", ret);
    }
    else {
        printf("OK Audio Stop\n");
    }

    // create WAV file
    size_t wavFreq = AUDIO_SAMPLING_FREQUENCY;
    size_t dataSize = (TARGET_AUDIO_BUFFER_NB_SAMPLES * 2);
    size_t fileSize = 44 + (TARGET_AUDIO_BUFFER_NB_SAMPLES * 2);

    uint8_t wav_header[44] = {
        0x52, 0x49, 0x46, 0x46, // RIFF
        (uint8_t)(fileSize & 0xff), (uint8_t)((fileSize >> 8) & 0xff), (uint8_t)((fileSize >> 16) & 0xff), (uint8_t)((fileSize >> 24) & 0xff),
        0x57, 0x41, 0x56, 0x45, // WAVE
        0x66, 0x6d, 0x74, 0x20, // fmt
        0x10, 0x00, 0x00, 0x00, // length of format data
        0x01, 0x00, // type of format (1=PCM)
        0x01, 0x00, // number of channels
        (uint8_t)(wavFreq & 0xff), (uint8_t)((wavFreq >> 8) & 0xff), (uint8_t)((wavFreq >> 16) & 0xff), (uint8_t)((wavFreq >> 24) & 0xff),
        0x00, 0x7d, 0x00, 0x00, // 	(Sample Rate * BitsPerSample * Channels) / 8
        0x02, 0x00, 0x10, 0x00,
        0x64, 0x61, 0x74, 0x61, // data
        (uint8_t)(dataSize & 0xff), (uint8_t)((dataSize >> 8) & 0xff), (uint8_t)((dataSize >> 16) & 0xff), (uint8_t)((dataSize >> 24) & 0xff),
    };

    printf("Total complete events: %lu, index is %lu\n", transfer_complete_events, TARGET_AUDIO_BUFFER_IX);

    // print both the WAV header and the audio buffer in HEX format to serial
    // you can use the script in `hex-to-buffer.js` to make a proper WAV file again
    // printf("WAV file:\n");
    // for (size_t ix = 0; ix < 44; ix++) {
    //     printf("%02x", wav_header[ix]);
    // }

    // uint8_t *buf = (uint8_t*)TARGET_AUDIO_BUFFER;
    // for (size_t ix = 0; ix < TARGET_AUDIO_BUFFER_NB_SAMPLES * 2; ix++) {
    //     printf("%02x", buf[ix]);
    // }
    // printf("\n");
    
    send_sem.acquire();
    sprintf(wav_json, "W ");
    // for (size_t ix = 0; ix < 44; ix++) {
    //     sprintf(acc_json+2+ix, "%02x", wav_header[ix]);
    // }
    
    uint8_t *buf = (uint8_t*)TARGET_AUDIO_BUFFER;
    for (size_t ix = 0; ix < TARGET_AUDIO_BUFFER_NB_SAMPLES * 2; ix++) {
        sprintf(wav_json+2+(ix<<1), "%02x", buf[ix]);
    }
    sprintf(wav_json+2+TARGET_AUDIO_BUFFER_NB_SAMPLES * 4, "\n");
    // printf("%s\n", acc_json);
    int response = send_json(wav_json); 

    if (0 >= response){
        printf("Error seding: %d\n", response); 
    }
    send_sem.release();

    ev_queue.call(&send_data);
}



/**
* @brief  Half Transfer user callback, called by BSP functions.
* @param  None
* @retval None
*/
void BSP_AUDIO_IN_HalfTransfer_CallBack(uint32_t Instance) {
    half_transfer_events++;
    if (half_transfer_events < SKIP_FIRST_EVENTS) return;

    uint32_t buffer_size = PCM_BUFFER_LEN / 2; /* Half Transfer */
    uint32_t nb_samples = buffer_size / sizeof(int16_t); /* Bytes to Length */

    if ((TARGET_AUDIO_BUFFER_IX + nb_samples) > TARGET_AUDIO_BUFFER_NB_SAMPLES) {
        return;
    }

    /* Copy first half of PCM_Buffer from Microphones onto Fill_Buffer */
    memcpy(((uint8_t*)TARGET_AUDIO_BUFFER) + (TARGET_AUDIO_BUFFER_IX * 2), PCM_Buffer, buffer_size);
    TARGET_AUDIO_BUFFER_IX += nb_samples;

    if (TARGET_AUDIO_BUFFER_IX >= TARGET_AUDIO_BUFFER_NB_SAMPLES) {
        ev_queue.call(&target_audio_buffer_full);
        return;
    }
}

/**
* @brief  Transfer Complete user callback, called by BSP functions.
* @param  None
* @retval None
*/
void BSP_AUDIO_IN_TransferComplete_CallBack(uint32_t Instance) {
    transfer_complete_events++;
    if (transfer_complete_events < SKIP_FIRST_EVENTS) return;

    uint32_t buffer_size = PCM_BUFFER_LEN / 2; /* Half Transfer */
    uint32_t nb_samples = buffer_size / sizeof(int16_t); /* Bytes to Length */

    if ((TARGET_AUDIO_BUFFER_IX + nb_samples) > TARGET_AUDIO_BUFFER_NB_SAMPLES) {
        return;
    }

    /* Copy second half of PCM_Buffer from Microphones onto Fill_Buffer */
    memcpy(((uint8_t*)TARGET_AUDIO_BUFFER) + (TARGET_AUDIO_BUFFER_IX * 2),
        ((uint8_t*)PCM_Buffer) + (nb_samples * 2), buffer_size);
    TARGET_AUDIO_BUFFER_IX += nb_samples;

    if (TARGET_AUDIO_BUFFER_IX >= TARGET_AUDIO_BUFFER_NB_SAMPLES) {
        ev_queue.call(&target_audio_buffer_full);
        return;
    }
}

/**
  * @brief  Manages the BSP audio in error event.
  * @param  Instance Audio in instance.
  * @retval None.
  */
void BSP_AUDIO_IN_Error_CallBack(uint32_t Instance) {
    printf("BSP_AUDIO_IN_Error_CallBack\n");
}

void print_stats() {
    printf("Half %lu, Complete %lu, IX %lu\n", half_transfer_events, transfer_complete_events,
        TARGET_AUDIO_BUFFER_IX);
}

void start_recording() {
    int32_t ret;
    uint32_t state;

    ret = BSP_AUDIO_IN_GetState(AUDIO_INSTANCE, &state);
    if (ret != BSP_ERROR_NONE) {
        printf("Cannot start recording: Error getting audio state (%d)\n", ret);
        return;
    }
    if (state == AUDIO_IN_STATE_RECORDING) {
        printf("Cannot start recording: Already recording\n");
        return;
    }

    // reset audio buffer location
    TARGET_AUDIO_BUFFER_IX = 0;
    transfer_complete_events = 0;
    half_transfer_events = 0;

    ret = BSP_AUDIO_IN_Record(AUDIO_INSTANCE, (uint8_t *) PCM_Buffer, PCM_BUFFER_LEN);
    if (ret != BSP_ERROR_NONE) {
        printf("Error Audio Record (%ld)\n", ret);
        return;
    }
    else {
        printf("OK Audio Record\n");
    }
}




static constexpr size_t MAX_NUMBER_OF_ACCESS_POINTS = 10;
static constexpr size_t MAX_MESSAGE_RECEIVED_LENGTH = 100;






NetworkInterface *_net;

#if MBED_CONF_APP_USE_TLS_SOCKET
    TLSSocket _socket;
#else
    TCPSocket _socket;
#endif // MBED_CONF_APP_USE_TLS_SOCKET

    // SocketDemo() : _net(NetworkInterface::get_default_instance())
    // {
    // }

    // ~SocketDemo()
    // {
    //     if (_net) {
    //         _net->disconnect();
    //     }
    // }

void run()
{
    buzzer.beep(500); 
    ThisThread::sleep_for(100);
    buzzer.beep(500); 
    if (!_net) {
        printf("Error! No network interface found.\r\n");
        buzzer.beep(500); 
        ThisThread::sleep_for(100);
        buzzer.beep(500); 
        return;
    }

    /* if we're using a wifi interface run a quick scan */
    // if (_net->wifiInterface()) {
    //     /* the scan is not required to connect and only serves to show visible access points */
    //     wifi_scan();

    //     /* in this example we use credentials configured at compile time which are used by
    //      * NetworkInterface::connect() but it's possible to do this at runtime by using the
    //      * WiFiInterface::connect() which takes these parameters as arguments */
    // }

    /* connect will perform the action appropriate to the interface type to connect to the network */

    printf("Connecting to the network...\r\n");

    nsapi_size_or_error_t result = _net->connect();
    if (result != 0) {
        printf("Error! _net->connect() returned: %d\r\n", result);
        buzzer.beep(500); 
        ThisThread::sleep_for(100);
        buzzer.beep(500); 
        return;
    }

    print_network_info();

    /* opening the socket only allocates resources */
    result = _socket.open(_net);
    if (result != 0) {
        printf("Error! _socket.open() returned: %d\r\n", result);
        buzzer.beep(500); 
        ThisThread::sleep_for(100);
        buzzer.beep(500); 
        return;
    }

#if MBED_CONF_APP_USE_TLS_SOCKET
    result = _socket.set_root_ca_cert(root_ca_cert);
    if (result != NSAPI_ERROR_OK) {
        printf("Error: _socket.set_root_ca_cert() returned %d\n", result);
        buzzer.beep(500); 
        ThisThread::sleep_for(100);
        buzzer.beep(500); 
        return;
    }
    _socket.set_hostname(MBED_CONF_APP_HOSTNAME);
#endif // MBED_CONF_APP_USE_TLS_SOCKET

    /* now we have to find where to connect */

    SocketAddress address;

    // if (!resolve_hostname(address)) {
    //     return;
    // }

    address.set_ip_address("172.20.10.4");
    address.set_port(REMOTE_PORT);

    /* we are connected to the network but since we're using a connection oriented
        * protocol we still need to open a connection on the socket */

    printf("Opening connection to remote port %d\r\n", REMOTE_PORT);

    result = _socket.connect(address);
    if (result != 0) {
        printf("Error! _socket.connect() returned: %d\r\n", result);
        buzzer.beep(500); 
        ThisThread::sleep_for(100);
        buzzer.beep(500); 
        return;
    }

    /* exchange an HTTP request and response */

    if (!send_http_request()) {
        buzzer.beep(500); 
        ThisThread::sleep_for(100);
        buzzer.beep(500); 
        return;
    }

    ThisThread::sleep_for(3000); 


    // int sample_num = 0;
    
    # define SCALE_MULTIPLIER 1
    ev_queue.call(&start_recording);
    // ev_queue.call_every(10000, &send_data);
    // ev_queue.call_every(1000, &start_recording);
    ev_queue.dispatch_forever();
    

    if (!receive_http_response()) {
        return;
    }

    printf("Demo concluded successfully \r\n");
}

void send_data(){
    // ev_queue.call(&start_recording);
    send_sem.acquire();
    BSP_ACCELERO_AccGetXYZ(pDataXYZ);
    BSP_GYRO_GetXYZ(pGyroDataXYZ);
    
    
    int x = (int)pDataXYZ[0]*SCALE_MULTIPLIER, y = (int)pDataXYZ[1]*SCALE_MULTIPLIER, z = (int)pDataXYZ[2]*SCALE_MULTIPLIER;
    int gx = (int)pGyroDataXYZ[0]*SCALE_MULTIPLIER, gy = (int)pGyroDataXYZ[1]*SCALE_MULTIPLIER, gz = (int)pGyroDataXYZ[2]*SCALE_MULTIPLIER;
    // int len = sprintf(acc_json,"{\"x\":%d,\"y\":%d,\"z\":%d,\"s\":%d}", x, y, z);
    int len = sprintf(acc_json, "%d %d %d %d %d %d %d\n", x, y, z, gx, gy, gz, pressed);
    // printf("%s\n", acc_json);
    int response = send_json(acc_json); 
    if (0 >= response){
        printf("Error seding: %d\n", response); 
    }
    pressed = 0;
    send_sem.release();

    char mode = receive_server_message();
    
    if (mode == '1'){
        ev_queue.call(&send_data);
    }else if (mode == '2'){
        ev_queue.call(&start_recording);
    }else if (mode == '3'){
        printf("buzzer\n"); 
        buzzer.beep(1000); 
        ev_queue.call(&send_data);
    }else{
        ev_queue.call(&start_recording);
    }
    // receive_http_response();

    
    
    // ThisThread::sleep_for(10000); 
}

bool send_json(char * buffer)
{
    /* loop until whole request sent */
    
    nsapi_size_t bytes_to_send = strlen(buffer);
    nsapi_size_or_error_t bytes_sent = 0;

    // printf("\r\nSending message: \r\n%s", buffer);

    while (bytes_to_send) {
        bytes_sent = _socket.send(buffer + bytes_sent, bytes_to_send);
        if (bytes_sent < 0) {
            printf("Error! _socket.send() returned: %d\r\n", bytes_sent);
            return false;
        } 
        // else {
        //     printf("\nsent %d bytes\r\n", bytes_sent);
        // }

        bytes_to_send -= bytes_sent;
    }
    
    // printf("Complete message sent\r\n");

    return true;
}

bool resolve_hostname(SocketAddress &address)
{
    const char hostname[] = MBED_CONF_APP_HOSTNAME;

    /* get the host address */
    printf("\nResolve hostname %s\r\n", hostname);
    nsapi_size_or_error_t result = _net->gethostbyname(hostname, &address);
    if (result != 0) {
        printf("Error! gethostbyname(%s) returned: %d\r\n", hostname, result);
        return false;
    }

    printf("%s address is %s\r\n", hostname, (address.get_ip_address() ? address.get_ip_address() : "None") );

    return true;
}

bool send_http_request()
{
    /* loop until whole request sent */
    const char buffer[] = "GET / HTTP/1.1\r\n"
                            "Host: ifconfig.io\r\n"
                            "Connection: close\r\n"
                            "\r\n";

    nsapi_size_t bytes_to_send = strlen(buffer);
    nsapi_size_or_error_t bytes_sent = 0;

    printf("\r\nSending message: \r\n%s", buffer);

    while (bytes_to_send) {
        bytes_sent = _socket.send(buffer + bytes_sent, bytes_to_send);
        if (bytes_sent < 0) {
            printf("Error! _socket.send() returned: %d\r\n", bytes_sent);
            return false;
        } else {
            printf("sent %d bytes\r\n", bytes_sent);
        }

        bytes_to_send -= bytes_sent;
    }

    printf("Complete message sent\r\n");

    return true;
}


bool receive_http_response()
{
    char buffer[MAX_MESSAGE_RECEIVED_LENGTH];
    int remaining_bytes = MAX_MESSAGE_RECEIVED_LENGTH;
    int received_bytes = 0;

    /* loop until there is nothing received or we've ran out of buffer space */
    nsapi_size_or_error_t result = remaining_bytes;
    while (result > 0 && remaining_bytes > 0) {
        result = _socket.recv(buffer + received_bytes, remaining_bytes);
        if (result < 0) {
            printf("Error! _socket.recv() returned: %d\r\n", result);
            return false;
        }

        received_bytes += result;
        remaining_bytes -= result;
    }

    /* the message is likely larger but we only want the HTTP response code */

    printf("received %d bytes:\r\n%.*s\r\n\r\n", received_bytes, strstr(buffer, "\n") - buffer, buffer);

    return true;
}

char receive_server_message(){
    char buffer[1];
    // int remaining_bytes = 3;
    // int received_bytes = 0;

    /* loop until there is nothing received or we've ran out of buffer space */
    nsapi_size_or_error_t result = 0;
    // while (result == 0) {
        result = _socket.recv(buffer, 2);
        if (result < 0) {
            printf("Error! _socket.recv() returned: %d\r\n", result);
            return false;
        }
    // }
    /* the message is likely larger but we only want the HTTP response code */

    printf("%c\n", buffer[0]);

    return buffer[0];
}


void wifi_scan()
{
    WiFiInterface *wifi = _net->wifiInterface();

    WiFiAccessPoint ap[MAX_NUMBER_OF_ACCESS_POINTS];

    /* scan call returns number of access points found */
    int result = wifi->scan(ap, MAX_NUMBER_OF_ACCESS_POINTS);

    if (result <= 0) {
        printf("WiFiInterface::scan() failed with return value: %d\r\n", result);
        return;
    }

    printf("%d networks available:\r\n", result);

    for (int i = 0; i < result; i++) {
        printf("Network: %s secured: %s BSSID: %hhX:%hhX:%hhX:%hhx:%hhx:%hhx RSSI: %hhd Ch: %hhd\r\n",
                ap[i].get_ssid(), get_security_string(ap[i].get_security()),
                ap[i].get_bssid()[0], ap[i].get_bssid()[1], ap[i].get_bssid()[2],
                ap[i].get_bssid()[3], ap[i].get_bssid()[4], ap[i].get_bssid()[5],
                ap[i].get_rssi(), ap[i].get_channel());
    }
    printf("\r\n");
}

void print_network_info()
{
    /* print the network info */
    SocketAddress a;
    _net->get_ip_address(&a);
    printf("IP address: %s\r\n", a.get_ip_address() ? a.get_ip_address() : "None");
    _net->get_netmask(&a);
    printf("Netmask: %s\r\n", a.get_ip_address() ? a.get_ip_address() : "None");
    _net->get_gateway(&a);
    printf("Gateway: %s\r\n", a.get_ip_address() ? a.get_ip_address() : "None");
}

    



void button_pressed()
{
    pressed = 1;
}


int main() {
    printf("\r\nStarting socket demo\r\n\r\n");

#ifdef MBED_CONF_MBED_TRACE_ENABLE
    mbed_trace_init();
#endif

    // sensor init
    printf("Start sensor init\n");

    BSP_TSENSOR_Init();
    BSP_HSENSOR_Init();
    BSP_PSENSOR_Init();

    BSP_MAGNETO_Init();
    BSP_GYRO_Init();
    BSP_ACCELERO_Init();
    //

    // set up the microphone
    MicParams.BitsPerSample = 16;
    MicParams.ChannelsNbr = AUDIO_CHANNELS;
    MicParams.Device = AUDIO_IN_DIGITAL_MIC1;
    MicParams.SampleRate = AUDIO_SAMPLING_FREQUENCY;
    MicParams.Volume = 32;

    int32_t ret = BSP_AUDIO_IN_Init(AUDIO_INSTANCE, &MicParams);

    if (ret != BSP_ERROR_NONE) {
        printf("Error Audio Init (%ld)\r\n", ret);
        return 1;
    } else {
        printf("OK Audio Init\t(Audio Freq=%ld)\r\n", AUDIO_SAMPLING_FREQUENCY);
    }
    

    // ret = BSP_AUDIO_IN_Record(AUDIO_INSTANCE, (uint8_t *) PCM_Buffer, PCM_BUFFER_LEN);

    // SocketDemo * example = new SocketDemo();
    _net = NetworkInterface::get_default_instance();
    button.fall(&button_pressed); // Change led delay
    run();
    // ev_queue.dispatch_forever();

    return 0;
}
