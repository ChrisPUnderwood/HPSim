def HeatPumpDualStage(Fluid,Pars,PropsSI):

    import numpy as np
    from Evaporator import Evaporator
    from Condenser import Condenser
    from GasCooler import GasCooler
    from Compressor import Compressor
    from Recuperator import Recuperator
    from InterCooler import InterCooler
    from tabulate import tabulate
    import time
    
    #DATA:
    QC = Pars[0]
    Cegs = Pars[1]
    THWO = Pars[2]
    DTHW = Pars[3]
    DoSC = Pars[4]
    DTc = Pars[5]
    EHXc = Pars[6]
    DTe = Pars[7]
    EHXe = Pars[8]
    TSFI = Pars[9]
    DTSF = Pars[10]
    DoSH = Pars[11]
    EtaIsenLP = Pars[12]
    EtaVLP = Pars[13]
    EtaIsenHP = Pars[14]
    EtaVHP = Pars[15]
    RDoSH = Pars[16]  #0 = no recuperator; otherwise this is the additional DoSH imposed by the recuperator
    PRI = Pars[17] #Only used if a transcritical (CO2) cycle 
    DP = Pars[18] #Only used if the above applies
    
    THWI = THWO - DTHW
    
    TsrcRef = TSFI - DTSF / 2 + 273.15 
    PsrcRef = 3 * 1E+05
    Brine = 'INCOMP::MEG-' + str(Cegs) + '%'
    Cp_src = PropsSI('C','T',TsrcRef,'P',PsrcRef,Brine) / 1000
    Msrc = QC * (1-1/3) / (Cp_src * DTSF)  #Estimate source fluid flow rate
    Qsrc = QC #Initial guess Qsrc
    Delt = QC
    FlagN = -1
    FlagP = -1
    TolQ = 0.01
    Q0 = Qsrc + 2*TolQ  #Initialise source load convergence loop
    while (np.absolute(Qsrc-Q0) > TolQ):  #Evaporator (source) load using the bisecton method
        if Qsrc - Q0 < 0:
            if FlagN < 0:
                FlagN = 1
                Q0 = Q0 - Delt
            else: 
                Delt = Delt/2
                Q0 = Q0 - Delt
        else:
                if FlagP < 0:
                    FlagP = 1
                    Q0 = Q0 + Delt
                else: 
                    Delt = Delt/2
                    Q0 = Q0 + Delt

        TSFO = TSFI - Qsrc / (Cp_src * Msrc)   #Evaporator outlet fluid temperature 
        yE = Evaporator(PropsSI,Fluid,DTe,EHXe,DoSH,TSFI,TSFO)   #yE = PE, HEO, RhoEO, TEO

        if (Fluid == 'R744'):
            PC = PRI
        else: 
            yC = Condenser(PropsSI,Fluid,DoSC,DTc,EHXc,THWI,THWO)  #yC = PC, HC_out, TC_out
            PC = yC[0]
 
        if (RDoSH > 0):
            yR = Recuperator(PropsSI,Fluid,RDoSH,yE[1],yE[0])  #yR = RDoSC,qRecup
            rhosuc = yR[1]
        else:
            yR = np.array([0,0])
            rhosuc = yE[2]
            
        Hsuc = yR[0] + yE[1]

        Pinter = yE[0] * np.sqrt(PC / yE[0])  #Assume equal stage compression ratios 
        if (Fluid == 'R744') and Pinter > 73.77:
            Pinter = yE[0] * np.sqrt(73.77 / yE[0])
            
        H_InterV = PropsSI('H','P',Pinter*1E+05,'Q',1,Fluid) / 1000
        H_InterL = PropsSI('H','P',Pinter*1E+05,'Q',0,Fluid) / 1000
        yW_LP = Compressor(PropsSI,Fluid,Hsuc,yE[0],Pinter,EtaIsenLP)  #yW = H_out,Tgd
        yIC = InterCooler(PropsSI,Fluid,Pinter,EHXc,THWI,yW_LP[1],yW_LP[0])  #HIC_out, TRO, qH, qS
        
        if (Fluid == 'R744'):   
            TG0 = 150 #Initial guess TG0
            Delt = 100
            FlagN = -1
            FlagP = -1
            TolT = 0.01
            TGD = TG0 + 2*TolT  #Initialise gas discharge temperature convergence loop
            while (np.absolute(TG0-TGD) > TolT):  #Discharge gas temperature using the bisecton method
                if TGD - TG0 < 0:
                    if FlagN < 0:
                        FlagN = 1
                        TG0 = TG0 - Delt
                    else: 
                        Delt = Delt/2
                        TG0 = TG0 - Delt
                else:
                        if FlagP < 0:
                            FlagP = 1
                            TG0 = TG0 + Delt
                        else: 
                            Delt = Delt/2
                            TG0 = TG0 + Delt   
        
                yC = GasCooler(PropsSI,Fluid,PRI,DP,EHXc,THWI,TG0) #yC = PRO, HC_out, TRO
                fML = (H_InterV - yC[1]) / (H_InterV - H_InterL)
                yW_HP = Compressor(PropsSI,Fluid,yIC[0],Pinter,PC,EtaIsenHP)  #yW = H_out,Tgd
                TGD = yW_HP[1]
        else:
            fML = (H_InterV - yC[1]) / (H_InterV - H_InterL)
            yW_HP = Compressor(PropsSI,Fluid,yIC[0],Pinter,PC,EtaIsenHP)  #yW = H_out,Tgd

        MR = QC / (yW_HP[0] - yC[1] + fML*yIC[2])
        WC = MR * (yW_HP[0] - yIC[0]) + fML * MR * (yW_LP[0] - Hsuc)
        Qsrc = QC - WC - MR*fML*yIC[3]
        QR = MR * fML * yR[1]
    if (WC < 0.1): 
        CoP = 0 
    else: 
        CoP = QC / WC

    #Calculate compressor displacement L/s:
    rhointer = PropsSI('D','P',Pinter*1E+05,'T',yIC[1] + 273.15,Fluid)
    VdisLP =  1000 * MR * fML / (EtaVLP * rhosuc)
    VdisHP =  1000 * MR / (EtaVHP * rhointer)
    QICh = MR * yIC[2]
    QICs = fML * MR * yIC[3]

    TdgHP = yW_HP[1]
    TdgLP = yW_LP[1]
    Tinter = PropsSI('T','P',Pinter*1E+05,'Q',1,Fluid) - 273.15
    Psuc = yE[0]
    Pdis = yC[0]

    #Output results    
    all_data = [["Parameter","Value"],
            ["Refrigerant",Fluid],    
            ["Refrigerant mass flow rate (kg/s)",f"{MR:.3f}"],
            ["Flow split to evaporator",f"{fML:.3f}"],
            ["Compressor power (kW)",f"{WC:.2f}"],
            ["LP discharge gas temperature (dg C)",f"{TdgLP:.2f}"],
            ["HP discharge gas temperature (dg C)",f"{TdgHP:.2f}"],
            ["Flash gas temperature (dg C)",f"{Tinter:.2f}"],
            ["Source heat (kW)",f"{Qsrc:.2f}"],
            ["Intercooler heat to load (kW)",f"{QICh:.2f}"],
            ["Intercooler recovery to source (kW)",f"{QICs:.2f}"],
            ["Recuperator heat (kW)",f"{QR:.2f}"],
            ["CoP",f"{CoP:.3f}"],
            ["Compressor displacement LP stage (L/s)",f"{VdisLP:.2f}"],
            ["Compressor displacement HP stage (L/s)",f"{VdisHP:.2f}"],
            ["Suction pressure (bar)",f"{Psuc:.2f}"],
            ["Discharge pressure (bar)",f"{Pdis:.2f}"],
            ["Outlet source fluid temperature (dg C)",f"{TSFO:.2f}"]]
    
    table = tabulate(all_data,headers='firstrow',tablefmt='grid')
 
    print(table)