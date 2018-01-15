import sys
import pyqtgraph as pg
from PySide import QtGui, QtCore

import numpy as np

class tabdemo ( QtGui.QTabWidget ):
    def __init__(self, parent=None):
        super(tabdemo, self).__init__(parent)

        self.electrodes = (('AF3', (15, 150, 255)), ('AF4', (150, 255, 15)), ('F3', (255, 15, 150)), ('F4', (15, 150, 255)),
                            ('F7', (150, 255, 15)), ('F8', (255, 15, 150)),
                            ('FC5', (15, 150, 255)), ('FC6', (150, 255, 15)), ('T7', (255, 15, 150)), ('T8', (15, 150, 255)),
                            ('P7', (150, 255, 15)), ('P8', (255, 15, 150)),
                            ('O1', (15, 150, 255)), ('O2', (150, 255, 15))
                            )

        # Plot in chunks, adding one new plot curve for every 100 samples
        self.chunkSize = 100
        # Remove chunks after we have 10
        self.maxChunks = 10
        self.startTime = pg.ptime.time()

        self.tab1 = QtGui.QWidget()
        self.tab2 = QtGui.QWidget()

        self.addTab(self.tab1, "Tab 1")
        self.addTab(self.tab2, "Tab 2")

        self.tab1UI()
        self.tab2UI()
        self.setWindowTitle("Emokit Visualizer")
        self.showMaximized()

    def update3( self, p, data, ptr, i_curves, startTime, emo_data, color ):
        now = pg.ptime.time()
        for c in i_curves:
            c.setPos(-(now - startTime), 0)

        i = ptr % self.chunkSize
        if i == 0:
            curve = p.plot()
            curve.setPen(color)  # (255, 125, 123))
            i_curves.append(curve)
            last = data[-1]
            data = np.empty((self.chunkSize + 1, 2))
            data[0] = last
            while len(i_curves) > self.maxChunks:
                c = i_curves.pop(0)
                p.removeItem(c)
        else:
            curve = i_curves[-1]
        data[i + 1, 0] = now - startTime
        data[i + 1, 1] = emo_data / 4000  # np.random.normal()  # dummy data  #
        # print emo_data
        # data[i + 1, 1] = ef.process_decrypted_packet_queue(raw_decrypted_packet, processed_packets)
        curve.setData(x=data[:i + 2, 0], y=data[:i + 2, 1])
        ptr += 1
        return [p, data, ptr, i_curves]

    # update all plots
    def update( self ):
        global allWaves
        global startTime
        global headset
        packet = headset.dequeue()
        # print packet
        # packet = 1
        if packet is not None:
            for i, wave in enumerate(allWaves):
                wave = self.update3(*wave, startTime=startTime, emo_data=packet.sensors[ self.electrodes[i][0]]['value'],
                               color = self.electrodes[i][1])
                # wave = update3(*wave, emo_data=1, color=electrodes[i][1])
                allWaves[i] = wave

    def tab1UI(self):
        # Left sided box for controls
        leftBox = QtGui.QFormLayout()

        record = QtGui.QPushButton("Grabar")
        stop = QtGui.QPushButton("Detener")
        recordButtons = QtGui.QGridLayout()
        recordButtons.addWidget( record, 0, 0 )
        recordButtons.addWidget( stop, 0, 1 )
        leftBox.addRow(QtGui.QLabel("Controles de grabacion"))
        leftBox.addRow(recordButtons)

        route = QtGui.QLineEdit()
        route.setReadOnly(True)
        examine = QtGui.QPushButton("Examinar")
        folderButtons = QtGui.QGridLayout()
        folderButtons.addWidget(route, 0, 0)
        folderButtons.addWidget(examine, 0, 1)
        leftBox.addRow(QtGui.QLabel("Carpeta de guardado"))
        leftBox.addRow(folderButtons)

        # Sensors status
        '''headsetState = QtGui.QLabel()
        headsetState.setPixmap(QtGui.QPixmap("../assets/headset.png"))'''
        painter = QtGui.QPainter()
        painter.begin(self)
        # leftBox.addRow( headsetState )

        # Center sided box for signals
        centerBox = QtGui.QFormLayout()
        plots = pg.GraphicsWindow()
        centerBox.addRow( QtGui.QLabel("Estado de las senales") )
        centerBox.addRow(plots)

        allWaves = []
        for i in xrange(14):
            if i:
                plots.nextRow()
            p = plots.addPlot()
            # p.setPen((255, 125, 123))
            if i == 13:
                p.setLabel('bottom', 'Time', 's')
            else:
                p.showAxis('bottom', False)
            # p.setXRange(-10, 0)
            curves = []
            data = np.empty( (self.chunkSize + 1, 2 ))
            ptr = 0
            allWaves.append([p, data, ptr, curves])

        timer = pg.QtCore.QTimer()
        timer.timeout.connect( self.update )
        timer.start(10)

        # Bottom sided box
        textEdit2 = QtGui.QTextEdit("Bottom rectangle")

        # Main grid layout
        gridLayout = QtGui.QGridLayout()
        gridLayout.addLayout(leftBox, 0, 0)
        gridLayout.addLayout(centerBox, 0, 1)
        gridLayout.addWidget(textEdit2, 1, 1)

        gridLayout.setColumnStretch(0, 1)
        gridLayout.setColumnStretch(1, 3)

        gridLayout.setRowStretch(0, 3)
        gridLayout.setRowStretch(1, 1)

        self.setTabText(0, "Grabar")
        self.tab1.setLayout(gridLayout)

    def tab2UI(self):
        layout = QtGui.QFormLayout()
        sex = QtGui.QHBoxLayout()
        sex.addWidget(QtGui.QRadioButton("Male"))
        sex.addWidget(QtGui.QRadioButton("Female"))
        layout.addRow(QtGui.QLabel("Sex"), sex)
        layout.addRow("Date of Birth", QtGui.QLineEdit())
        self.setTabText(1, "Personal Details")
        self.tab2.setLayout(layout)

    def b1_clicked(self):
        print "Button 1 clicked"

    def b2_clicked(self):
        print "Button 2 clicked"


def main():
    app = QtGui.QApplication(sys.argv)
    ex = tabdemo()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()