from PyQt5 import QtWidgets, uic
from CoolProp.CoolProp import PropsSI
import sys
import numpy as np

class HPSim(QtWidgets.QMainWindow):
    def __init__(self):
        super(HPSim, self).__init__()
        uic.loadUi('HeatPumpGUI.ui', self)  #Load the main GUI dashboard 
        self.RunPushButton.clicked.connect(self.onChecked)
        
    def onChecked(self):
        if self.r32.isChecked():
            Fluid = 'R32'
        elif self.r1234yf.isChecked():
            Fluid = "R1234yf" 
        elif self.r717.isChecked():
            Fluid = "R717"
        elif self.r290.isChecked():
            Fluid = "R290"
        elif self.r600a.isChecked():
            Fluid = "R600a"
        else:
            Fluid = "R744"  #This option will operate on the transcrit cycle and invoke the gas cooler
 
        QC = float(self.QC.text())
        cEGS = float(self.cEGS.text())
        THWO = float(self.THWO.text())
        if Fluid == "R32" and THWO > 60:
            print("!!!TWHO too high for R32 - it has been reset to 60 dg C!!!")
            THWO = 60
        dTHW = float(self.dTHW.text())
        DoSC = float(self.DoSC.text())
        dTc = float(self.dTc.text())
        EHXc = float(self.EHXc.text())
        dTe = float(self.dTe.text())
        EHXe = float(self.EHXe.text())
        TSFI = float(self.TSFI.text())
        dTSF = float(self.dTSF.text())
        DoSH = float(self.DoSH.text())
        EtaIsenLP = float(self.EtaIsenLP.text())
        EtaVLP = float(self.EtaVLP.text())
        EtaIsenHP = float(self.EtaIsenHP.text())
        EtaVHP = float(self.EtaVHP.text())
        RDoSH = float(self.RDoSH.text())
        GCPI = float(self.GCPI.text())
        GCdP = float(self.GCdP.text())
        HPinputs = np.asarray([QC,cEGS,THWO,dTHW,DoSC,dTc,EHXc,dTe,EHXe,TSFI,dTSF,DoSH,EtaIsenLP,EtaVLP,EtaIsenHP,EtaVHP,RDoSH,GCPI,GCdP,])
        
        if self.SingleCompressor.isChecked():
            from HeatPumpSingleStage import HeatPumpSingleStage
            HeatPumpSingleStage(Fluid,HPinputs,PropsSI)
        else:
            from HeatPumpDualStage import HeatPumpDualStage
            HeatPumpDualStage(Fluid,HPinputs,PropsSI)

app = QtWidgets.QApplication(sys.argv)
win = HPSim()
win.show()
sys.exit(app.exec_())