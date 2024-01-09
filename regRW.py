import sys
# import time, datetime
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import  QTime
from PyQt5.QtNetwork import QTcpSocket
from streamConv import *

gTagNo = 0

def sendCommand(clientCmd, packet):
    # print("sendCommand")
    rcvBytes = bytearray()

    sendLen = len(packet)
    print("send length: " + str(sendLen) + " data: " + str(packet))
    try:
        clientCmd.write(packet)
    except Exception as e:
        print(e)
        #messagebox.showwarning(title="send warning", message=e)
        return rcvBytes
    
    timeA = QTime()
    timeA.start()
    rcvLen = 0
    printRcvErr = True 
    #QThread.msleep(100);       
    while( timeA.elapsed() < 1000 and rcvLen == 0): 
        try:
            QApplication.processEvents()
            if clientCmd.bytesAvailable() > 0:
                rcv = clientCmd.readAll()
                if(len(rcv) > 0):
                    rcvBytes += rcv
                    rcvLen = len(rcvBytes)
        except Exception as e:
            print(e)
            #messagebox.showwarning(title="send warning", message=e)
            return rcvBytes    

    # rcvBytes = clientCmd.recv(1024)
    # for i in range(len(rcvBytes)):
    #     print("0x%x "% rcvBytes[i], end='')
    # print()    
    print("use " + str(timeA.elapsed()) + "ms")
    print("rcv length: " + str(rcvLen) + " data: " + str(rcvBytes))
    return rcvBytes

def command_writeReg(tcpSocket_cmd: QTcpSocket, reg: int, val: int):  
    global gTagNo      
    reg_str = '{:04x}'.format(reg)
    data_str = '{:04x}'.format(val)
    pkt_str = f"DEBUG REG 0 \"SlotFPGA 0 w {reg_str} 4 1 {data_str}\";\r\n"

    strlen = len(pkt_str) + 2
    pkt_data = bytearray([0xAB, (gTagNo & 0xFF)]) + u16_to_bytesLE(strlen) + u16_to_bytesLE(0xFF00) + bytes(pkt_str, 'ascii') 
    gTagNo += 1
    pkt_data += bytearray([packetCheckSum(pkt_data)]) + bytearray([0])
    print(pkt_data) 
    rcvBytes = sendCommand(tcpSocket_cmd, pkt_data)
    if(len(rcvBytes) > 15):
        dataBytes = bytearray(rcvBytes[8: (len(rcvBytes) - 4)])
        dataStr = dataBytes.decode()
        if(dataStr == "^OK;"):     
            return True
        else:
            return False
    else:
        return False

def  command_readReg(tcpSocket_cmd: QTcpSocket, reg: int):        
    global gTagNo
    reg_str = '{:04x}'.format(reg)
    pkt_str = f"DEBUG REG 0 \"SlotFPGA 0 r {reg_str} 4 1 0\";\r\n"

    strlen = len(pkt_str) + 2
    pkt_data = bytearray([0xAB, (gTagNo & 0xFF)]) + u16_to_bytesLE(strlen) + u16_to_bytesLE(0xFF00) + bytes(pkt_str, 'ascii') 
    gTagNo += 1
    pkt_data += bytearray([packetCheckSum(pkt_data)]) + bytearray([0])
    print(pkt_data) 
    rcvBytes = sendCommand(tcpSocket_cmd, pkt_data)
    if(len(rcvBytes) >= 18):
        dataBytes = rcvBytes[8: (len(rcvBytes) - 4)]
        dataStr = bytearray(dataBytes).decode()
        dataStrList = dataStr.split(' ')
        if(len(dataStrList) == 2):
            readData = int(dataStrList[1], 16)
            return readData
        else:
            return 0
    else:
        return 0
    
def command_write(tcpSocket_cmd: QTcpSocket, subCmd: int, data: bytearray):  
    global gTagNo      
    # reg_str = '{:04x}'.format(reg)
    # data_str = '{:04x}'.format(val)
    # pkt_str = f"DEBUG REG 0 \"SlotFPGA 0 w {reg_str} 4 1 {data_str}\";\r\n"

    strlen = len(data) + 4
    pkt_data = bytearray([0xAB, (gTagNo & 0xFF)]) + u16_to_bytesLE(strlen) + u16_to_bytesLE(0xFF03) + u16_to_bytesLE(subCmd) + data 
    gTagNo += 1
    pkt_data += bytearray([packetCheckSum(pkt_data)]) + bytearray([0])
    print(pkt_data) 
    rcvBytes = sendCommand(tcpSocket_cmd, pkt_data)
    if(len(rcvBytes) > 15):
        return True
    else:
        return False