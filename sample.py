import serial
import time

while True:
    temperature = 0.0
    probe = 0
    batchtemps = [0.0] * 9
    ser=serial.Serial('COM9',baudrate=230400,timeout=0)
    time.sleep(3)
    bytesToRead = ser.in_waiting
    print bytesToRead
    msg=ser.read(1000)
    ser.close()
    print msg
    print msg[5:10]

    i = 0
    while i <= (len(msg)-10):
        if msg[i] == 'e':
            print msg[i]
            temperature = float(msg[(i+5):(i+10)])
            probe = int(msg[i+2])
            batchtemps[probe-1] = temperature
            print temperature
            print probe
        i=i+1

    print batchtemps


