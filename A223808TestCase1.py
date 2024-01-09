import sys, os
import codecs
# import time, datetime
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QTabWidget
from PyQt5.QtWidgets import QFileDialog, QTextBrowser, QTextEdit, QLayout, QSizePolicy
from PyQt5.QtCore import Qt, QThread, QMutex , QMutexLocker, QVariant, QByteArray, QCoreApplication, QThread
from PyQt5.QtCore import QFile, QIODevice, QDataStream, QTextStream
from PyQt5.QtCore import  QDateTime, QTime, QTimer
from PyQt5.QtNetwork import QTcpSocket, QNetworkProxy, QAbstractSocket
from streamConv import *
from regRW import *

class QMain(QWidget) :
    def __init__(self):
        super().__init__()
        self.initUI()        
        self.thread_1 = QThread()
        self.thread_1.run = self.thread1_do
        self.thread_1.start()
        self.timer1 = QTimer()
        self.timer1.timeout.connect(self.on_timer1_timeout)
        self.timer1.start(int(self.edit_timeInterval.text()))
        self.resizeEvent = self.onResize

    def initUI(self):
        self.count = 0
        self.isTcpConnected = False
        self.combox_ip = None
        self.btn_connect = None
        self.label1 = None
        self.cmdPort = 61000
        self.dataPort = 61001
        self.tcpSocket_cmd = QTcpSocket(self)
        self.tcpSocket_cmd.setSocketOption(QTcpSocket.KeepAliveOption, QVariant(1))
        self.tcpSocket_cmd.connected.connect(self.on_TcpConnected)
        self.tcpSocket_cmd.disconnected.connect(self.on_TcpDisconnected)
        # self.tcpSocket_cmd.readyRead.connect(self.on_TcpReadyRead)
        self.tcpSocket_cmd.error.connect(self.on_TcpError)
        self.tcpSocket_data = QTcpSocket(self)
        self.tcpSocket_data.setSocketOption(QTcpSocket.KeepAliveOption, QVariant(1))
        self.textStream = QTextStream()
        self.isLogRecord = False
        self.fileDevice = QFile()        

        #In Qt 5.14, system proxy settings are used by default, set the NO_PROXY settings.
        proxy = QNetworkProxy()
        QNetworkProxy.setApplicationProxy(proxy)
        #e

        #self.resize(640, 480)
        self.setWindowTitle("A223808 Test Case 1")        
                
        #------------------------------------------
        v_layout0 = QVBoxLayout()
        h_layout0_1 = QHBoxLayout() 
        v_layout0_2 = QVBoxLayout() 
        self.combox_ip = QComboBox(self)
        self.tabWg = QTabWidget(self)
        self.tabWg.setMinimumSize(640, 480)
        self.tabWg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        for ipNo in range(1, 5):
            self.combox_ip.addItem(f'192.168.1.10{ipNo}')
        self.combox_ip.setFixedWidth(200)
        self.btn_connect = QPushButton(text = self.connectBtnName(), parent = self)
        self.btn_connect.setFixedWidth(100)
        self.btn_connect.clicked.connect(self.on_connectButtonClick)
        h_layout0_1.addWidget(self.combox_ip, alignment = Qt.AlignCenter, stretch = 1)
        h_layout0_1.addWidget(self.btn_connect, alignment = Qt.AlignCenter, stretch = 1)
        v_layout0.addLayout(h_layout0_1)
        v_layout0.addWidget(self.tabWg)
        v_layout0.setContentsMargins(0,0,0,0)
        v_layout0.setSizeConstraint(QLayout.SetMaximumSize)
        self.setLayout(v_layout0)

        #------------------------------------------
        self.logWg = QWidget()
        self.rs485Wg = QWidget()
        self.lvdsSyncWg = QWidget()
        self.tabWg.addTab(self.logWg, "Log")
        self.tabWg.addTab(self.rs485Wg, "rs485Tx")
        self.tabWg.addTab(self.lvdsSyncWg, "lvdsSync")

        self.createLogWidget(self.logWg)
        self.createRS485Widget(self.rs485Wg)
        self.createLvdsSyncWidget(self.lvdsSyncWg)

        #------------------------------------------
        # placeholder = QWidget()
        # placeholder.setLayout(v_layout0)
        # self.setCentralWidget(placeholder)

        #---logWg---------------------------------------
    def createLogWidget(self, parentWg: QWidget):
        self.qWg = QWidget(parent = parentWg)
        self.qWg.setFixedSize(360, 50)
 
        self.label_unit = QLabel(text = "circle", parent = self.qWg)
        self.label_unit.move(0, 0)
        self.label_unit.setFixedWidth(100)
        
        self.edit_timeInterval = QLineEdit(parent = self.qWg, text = "1000") 
        self.edit_timeInterval.move(70, 0)
        self.edit_timeInterval.setFixedWidth(200)
        self.edit_timeInterval.setAlignment(Qt.AlignCenter)
        self.edit_timeInterval.textChanged.connect(self.on_edit_timeInterval_textChanged)

        self.label_unit = QLabel(text = "(ms)", parent = self.qWg)
        self.label_unit.move(280, 0)
        self.label_unit.setFixedWidth(100)

        self.label1 = QLabel("Info: Empty", parentWg)
        self.label1.setFixedWidth(300)
        self.label1.setAlignment(Qt.AlignCenter)
        self.label1.setWordWrap(True)

        self.logButton = QPushButton("log Start", parentWg)
        self.logButton.setToolTip("Select Log file")
        self.logButton.setFixedWidth(100)
        self.logButton.move(100,100)
        self.logButton.clicked.connect(self.on_logButtonClick)  

        h_layout2 = QHBoxLayout() 
        h_layout2.addWidget(self.qWg, alignment = Qt.AlignCenter, stretch = 1)  

        v_layout1 = QVBoxLayout() 
        v_layout1.addLayout(h_layout2)  
        v_layout1.addWidget(self.label1, alignment = Qt.AlignCenter, stretch = 1)  
        v_layout1.addWidget(self.logButton, alignment = Qt.AlignCenter, stretch = 1)  
        v_layout1.addStretch(5)

        parentWg.setLayout(v_layout1)

    def createRS485Widget(self, parentWg: QWidget):
        self.rs485TextEdit = QTextEdit(self)
        self.rs485TextEdit.setFixedHeight(300)
        self.rs485TextEdit.setText("12EFCD")

        self.rs485SendButton = QPushButton("send", self)
        self.rs485SendButton.setToolTip("send rs485 data")
        self.rs485SendButton.setFixedWidth(100)
        self.rs485SendButton.clicked.connect(self.on_rs485SendButtonClick)  

        v_layout1 = QVBoxLayout() 
        v_layout1.addWidget(self.rs485TextEdit)
        v_layout1.addWidget(self.rs485SendButton, alignment = Qt.AlignCenter)  

        parentWg.setLayout(v_layout1)

    def createLvdsSyncWidget(self, parentWg: QWidget):
        self.lvdsSyncTextEdit = QTextEdit(self)
        self.lvdsSyncTextEdit.setFixedHeight(300)

        self.lvdsSyncSendButton = QPushButton("send", self)
        self.lvdsSyncSendButton.setToolTip("send rs485 data")
        self.lvdsSyncSendButton.setFixedWidth(100)
        self.lvdsSyncSendButton.clicked.connect(self.on_lvdsSyncSendButtonClick)  

        v_layout1 = QVBoxLayout() 
        v_layout1.addWidget(self.lvdsSyncTextEdit, alignment = Qt.AlignCenter, stretch = 1)
        v_layout1.addWidget(self.lvdsSyncSendButton, alignment = Qt.AlignCenter, stretch = 1)  

        parentWg.setLayout(v_layout1)

    def connectBtnName(self):
        return ("disconnect" if self.isTcpConnected == True else "connect")

    def isConnected(self):
        state = self.tcpSocket_cmd.state
        return (state == QAbstractSocket.ConnectedState)

    def onResize(self, event):
        print(f"{self.width()},{self.height()}")
        #self.tabWg.setFixedSize(self.width(), self.height() - 50)
        #self.tabWg.resize(self.size())

    def on_rs485SendButtonClick(self):
        dataBytes = hexStrToByteArray(self.rs485TextEdit.toPlainText())
        command_write(self.tcpSocket_cmd, 0xABCD, dataBytes)
        return
    
    def on_lvdsSyncSendButtonClick(self):
        dataBytes = hexStrToByteArray(self.lvdsSyncTextEdit.toPlainText())
        command_write(self.tcpSocket_cmd, 0xABCD, dataBytes)
        return
    
    def on_testButtonClick(self):    
        print("Test Button Clicked")
        # if( self.command_writeReg(self.tcpSocket_cmd, 0x18100000000000F3, 0xFFFF) ):
        #     print("ok")

    def on_logButtonClick(self):    
        print("Log Button Clicked")
        if(not self.isLogRecord):                
            filePath , filterType = QFileDialog.getSaveFileName()
            if(filePath):
                self.fileDevice = QFile(filePath)
                f = self.fileDevice.open(QIODevice.ReadWrite | QIODevice.Truncate | QIODevice.Text )        
                self.textStream = QTextStream(self.fileDevice)
                self.isLogRecord = True
                self.logButton.setText("log Stop")
                return
            else:
                return
        else:
            self.isLogRecord = False
            self.fileDevice.close()
            self.logButton.setText("log Start")
            return

    def on_connectButtonClick(self):    
        if self.isTcpConnected == False:
            ipStr = self.combox_ip.currentText()
            self.tcpSocket_cmd.connectToHost(ipStr, self.cmdPort) 
            #self.tcpSocket_cmd.waitForConnected(3000)
            self.tcpSocket_data.connectToHost(ipStr, self.dataPort) 
            #self.tcpSocket_data.waitForConnected(3000)
        else:
            self.tcpSocket_cmd.abort()
            self.tcpSocket_data.abort()

    def on_TcpError(self):
        print(self, "The following error occurred: %s." % self.tcpSocket_cmd.errorString())

    def on_TcpConnected(self):
        print('connected!')
        self.isTcpConnected = True
        self.btn_connect.setText(self.connectBtnName())
        
    def on_TcpDisconnected(self):
        print('disconnected!')
        self.isTcpConnected = False
        self.btn_connect.setText(self.connectBtnName())

    def on_TcpReadyRead(self):
        # rxData = self.tcpSocket_cmd.readAll()
        pass
        return

    def thread1_do(self):        
        while(True):
            #print('A:', 1)
            # if( self.command_writeReg(0x18100000000000F3, 0xFFFF) ):
            #     print("ok")
            QThread.sleep(1)

    def on_edit_timeInterval_textChanged(self, text):
        msecond = 0
        try:
            msecond = int(text)
        except Exception as e:
            msecond = 1
        self.timer1.start(msecond)

    def on_timer1_timeout(self):
        if(self.isTcpConnected and self.isLogRecord):
            # test read/write
            # val = command_readReg(self.tcpSocket_cmd, 0x18100000000000F3)
            # if( command_writeReg(self.tcpSocket_cmd, 0x18100000000000F3, val) ):
            #     print("ok")

            # registers read
            aReadDataAdr = [0x18100000000000FB, 0x18100000000000FC, 0x18100000000000F7, 0x18100000000000F6]            
            aReadDataLen = len(aReadDataAdr)
            dt_string = QDateTime.currentDateTime().toString("yyyy-MM-dd,hh:mm:ss.zzz")
            infoStr = f"{dt_string}"
            for i in range(0, aReadDataLen):
                data =  command_readReg(self.tcpSocket_cmd, aReadDataAdr[i])
                infoStr += f",{data}"
            # show info    
            print(infoStr)
            self.label1.setText(infoStr)
            self.textStream << infoStr << "\n"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QMain()
    main.show()
    sys.exit(app.exec())
