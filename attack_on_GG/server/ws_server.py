#!/usr/bin/env python3
# from gettext import npgettext
from logging import NullHandler
import socket
import wave
import numpy as np
import json
import time
import random
import ast

import threading

import numpy as np
import matplotlib.pyplot as plt
from numpy.core.shape_base import block
from math import log10, sqrt, atan
from statistics import mean


from scipy.io.wavfile import read
from scipy.io.wavfile import _read_riff_chunk, _skip_unknown_chunk, _read_fmt_chunk
import warnings

# PCM

# 2 sec
# size 64000
# n_samples 3200


class Server:

    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.HOST, self.PORT))
        self.bias = [0 for i in range(6)]
        self.fRad2Deg = 57.295779513 # Coefficient from Rad to Deg
        self.dt_1 = 0.005 # Time Period
        self.angle = [0,0,0] 
        self.angle_last = [0,0,0]
        self.R = 0.98

        self.last_data = 'NULL'
        self.last_data2 = 'NULL'
        self.connected = False
        self.connected2 = False

        self.loudness = 0
        self.loudness2 = 0
        self.keyDirection = "No"
        self.keyDirection2 = "No"
        self.attack = 0
        self.attack2 = 0
        self.pressed = 0
        self.pressed2 = 0
        self.button_last = 0
        self.button_last2 = 0

        self.cutOffFrequency = 400.0
        self.sampleRate = 16000

        self.freqRatio = (self.cutOffFrequency/self.sampleRate)
        self.N = int(sqrt(0.196196 + self.freqRatio**2)/self.freqRatio)

        self.idle_time = 0
        self.idle_time2 = 0


    def _read_data_chunk(self, input, format_tag, channels, bit_depth, is_big_endian,
                        block_align, mmap=False):
        if is_big_endian:
            fmt = '>'
        else:
            fmt = '<'

        # Size of the data subchunk in bytes
        # size = 160
        size = 80

        # Number of bytes per sample (sample container size)
        bytes_per_sample = block_align // channels
        n_samples = size // bytes_per_sample

        if bit_depth <= 64:
            # Remaining bit depths can map directly to signed numpy dtypes
            dtype = f'{fmt}i{bytes_per_sample}'


        if len(input) < 2*n_samples:
            return []
        
        count = n_samples
        data = np.frombuffer(input, dtype=dtype, count=count)

        # _handle_pad_byte(fid, size)
        return data


    '''
    Low Pass Filter
    '''
    


    def running_mean(self, x, windowSize):
        cumsum = np.cumsum(np.insert(x, 0, 0)) 
        return (cumsum[windowSize:] - cumsum[:-windowSize]) / windowSize
    
    # wavedata = _read_data_chunk(wavedata, 1, 1, 16, False, 2, False)
    # print(wavedata)
    # filtered = running_mean(wavedata, N)
    # print(filtered)


    '''
    Rectify Data
    '''
    def count_bias(self,clientsocket, addr):
        for t in range(3):
            data_cnt = 0
            acc_data = [[] for i in range(6)]
            ok = 1
            while ok:
                buffer = clientsocket.recv(1024).decode('utf-8')
                chunk = buffer.split('\n')
                for data in chunk:
                    raw = data.split(' ')
                    if (len(raw) == 7):
                        print(raw)
                        raw = [int(x) for x in raw]
                        for i in range(6):
                            if (data_cnt > 0 and raw[i] - mean(acc_data[i]) > 200):
                                print("Do not move!")
                                
                                ok = 0
                                break
                            acc_data[i].append(raw[i])
                        data_cnt += 1
                    if (data_cnt >= 100):
                        print("Bias counted")
                        for i in range(6):
                            self.bias[i] = mean(acc_data[i])
                        return True
        return False

    def RectifyData(self,data):
        if (len(data) < 6):
            print("Data length error")
            return data
        for i in range(6):
            data[i] -= self.bias[i]

        data[5] += 8192
        for i in range(3):
            data[i] /= 16.384
            data[i+3] /= 8192.0
        return data



    def CalculateAngle_Complementary(self, data):

        temp = []
        temp.append(sqrt(data[1]*data[1]+data[2]*data[2]))
        temp.append(sqrt(data[0]*data[0]+data[2]*data[2]))

        for i in range(2):
            self.angle[i] = self.R*(self.angle_last[i]+data[3+i]*self.dt_1) + (1-self.R)*self.fRad2Deg*atan(data[i]/temp[i])
            self.angle_last[i] = self.angle[i]
        self.angle[2] = self.angle_last[2]+data[5]*self.dt_1
        self.angle_last[2] = self.angle[2]



    def kalman_filter(self, angle_m, gyro_m):
        angle = 0
        angle_dot = 0
        q_bias = 0
        P = [[1, 0], [0, 1]]
        Pdot = [0 for i in range(4)]
        Q_angle = 0.000001
        Q_gyro = 0.0001
        C_0 = 1
        R_angle = 0.5
        dt_2 = 0.002


        angle += (gyro_m - q_bias) * dt_2

        Pdot[0] = Q_angle - P[0][1] - P[1][0]
        Pdot[1] = -P[1][1]
        Pdot[2] = -P[1][1]
        Pdot[3] = Q_gyro

        P[0][0] += Pdot[0] * dt_2
        P[0][1] += Pdot[1] * dt_2
        P[1][0] += Pdot[2] * dt_2
        P[1][1] += Pdot[3] * dt_2

        angle_err = angle_m - angle

        PCt_0 = C_0 * P[0][0]
        PCt_1 = C_0 * P[1][0]

        E = R_angle + C_0 * PCt_0

        K_0 = PCt_0 / E
        K_1 = PCt_1 / E

        t_0 = PCt_0
        t_1 = C_0 * P[0][1]

        P[0][0] -= K_0 * t_0
        P[0][1] -= K_0 * t_1
        P[1][0] -= K_1 * t_0
        P[1][1] -= K_1 * t_1
            
        angle	+= K_0 * angle_err
        q_bias += K_1 * angle_err
        angle_dot = gyro_m - q_bias

        return angle, angle_dot



    def get_data(self):
        try:
            buffer = self.client_socket.recv(1024).decode('utf-8')
        except:
            # self.connected = 0
            return
        #     print("unconnected")
        #     return
            # print('Received from socket server : ', data)
        # if (len(buffer) == 0):
        #     self.idle_time += 1
        #     print("idle")
        # if self.idle_time >= 5:
        #     self.connected = 0
        #     self.idle_time = 0
        #     return
        chunk = buffer.split('\n')
        for data in chunk:
            # print(data) 
            if (len(data) and data[0] == 'W'):
                # print(data)
                # try:
                wavedata = np.array(bytearray.fromhex(data[2:162]))
                wavedata = self._read_data_chunk(wavedata, 1, 1, 16, False, 2, False)
                # if (len(wavedata) == 0):
                #     continue
                filtered = self.running_mean(wavedata, self.N)
                db = 20 * log10(sqrt(mean(filtered.astype('int64') ** 2)))
                print(db)
                self.loudness = db
                continue
                # except:
                #     continue
                
            # print(data)
            
            # # print(raw)
            # # print(len(raw))
            raw = data.split(' ')
            if (len(raw) == 7):
                # print(raw)
                raw = [int(x) for x in raw]
                if (raw[6] == 1 and self.button_last == 0):
                    print("Pressed!")
                    self.pressed = 1
                else:
                    self.pressed = 0
                
                self.button_last = raw[6]
                

                rectified = self.RectifyData(raw)

                # print(rectified[3:])

                if (rectified[0] < -30):
                    print("Left")
                    self.keyDirection = "Left"
                elif (rectified[0] > 30):
                    print("Right")
                    self.keyDirection = "Right"
                elif (rectified[1] > 20):
                    print("Up")
                    self.keyDirection = "Up"
                elif (rectified[1] < -20):
                    print("Down")
                    self.keyDirection = "Down"
                else:
                    self.keyDirection = "No"

                if (self.last_data != 'NULL' and rectified[2] - self.last_data > 100):
                    print("Attack")
                    self.attack = 1
                else:
                    self.attack = 0
                #     cnt_shake += rectified[2] - last_data
                #     t_shake += 1
                # else:
                #     cnt_shake = 0
                #     t_shake = 0

                # if cnt_shake > 300 and t_shake < 10:
                #     print("Attack")
                #     cnt_shake = 0
                #     t_shake = 0
                # print(rectified)

                self.last_data = rectified[2]

                # self.CalculateAngle_Complementary(rectified)
                # print("angle: ", self.angle)

    def get_data2(self):
        try:
            buffer = self.client_socket2.recv(1024).decode('utf-8')
        except:
            # self.connected2 = 0
            return
            # print('Received from socket server : ', data)
        chunk = buffer.split('\n')
        for data in chunk:
            # print(data) 
            if (len(data) and data[0] == 'W'):
                # print(data)
                # try:
                wavedata = np.array(bytearray.fromhex(data[2:162]))
                wavedata = self._read_data_chunk(wavedata, 1, 1, 16, False, 2, False)
                # if (len(wavedata) == 0):
                #     continue
                filtered = self.running_mean(wavedata, self.N)
                db = 20 * log10(sqrt(mean(filtered.astype('int64') ** 2)))
                print(db)
                self.loudness2 = db
                continue
                # except:
                #     continue
                
            # print(data)
            
            # # print(raw)
            # # print(len(raw))
            raw = data.split(' ')
            if (len(raw) == 7):
                # print(raw)
                raw = [int(x) for x in raw]
                if (raw[6] == 1 and self.button_last2 == 0):
                    print("Pressed!2")
                    self.pressed2 = 1
                else:
                    self.pressed2 = 0
                
                self.button_last2 = raw[6]
                

                rectified = self.RectifyData(raw)

                # print(rectified[3:])

                if (rectified[0] < -30):
                    print("Left2")
                    self.keyDirection2 = "Left"
                elif (rectified[0] > 30):
                    print("Right2")
                    self.keyDirection2 = "Right"
                elif (rectified[1] > 20):
                    print("Up2")
                    self.keyDirection2 = "Up"
                elif (rectified[1] < -20):
                    print("Down2")
                    self.keyDirection2 = "Down"
                else:
                    self.keyDirection2 = "No"

                if (self.last_data2 != 'NULL' and rectified[2] - self.last_data2 > 100):
                    print("Attack2")
                    self.attack2 = 1
                else:
                    self.attack2 = 0
                #     cnt_shake += rectified[2] - last_data
                #     t_shake += 1
                # else:
                #     cnt_shake = 0
                #     t_shake = 0

                # if cnt_shake > 300 and t_shake < 10:
                #     print("Attack")
                #     cnt_shake = 0
                #     t_shake = 0
                # print(rectified)

                self.last_data2 = rectified[2]

                # self.CalculateAngle_Complementary(rectified)
                # print("angle: ", self.angle)

    # def on_new_client(self, clientsocket, addr):
    #     print("connected from", addr)
    #     self.count_bias(clientsocket, addr)

    #     last_data = 0
    #     cnt_shake = 0
    #     t_shake = 0
    #     # return
    #     while True:
    #         self.get_data()
                    
    def _connect(self):
        
        print("connecting ... ")
        self.s.listen()
        conn, addr = self.s.accept()
        print("connected")
        # t = threading.Thread(target=self.on_new_client, args=(conn, addr))
        # t.start()

        self.client_socket = conn
        self.addr = addr
                # break
        # clientsocket.close()
        self.connected = True
    
    def _connect2(self):
        
        print("connecting2 ... ")
        self.s.listen()
        conn, addr = self.s.accept()
        print("connected2")
        # t = threading.Thread(target=self.on_new_client, args=(conn, addr))
        # t.start()

        self.client_socket2 = conn
        self.addr2 = addr
                # break
        # clientsocket.close()
        self.connected2 = True

    def _setmode(self, x):
        encodedMessage = bytes(str(x), 'utf-8')
        self.client_socket.sendall(encodedMessage)
    def _setmode2(self, x):
        encodedMessage = bytes(str(x), 'utf-8')
        self.client_socket2.sendall(encodedMessage)

    
            

                








