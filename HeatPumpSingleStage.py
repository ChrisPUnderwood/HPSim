def HeatPumpSingleStage(Fluid,Pars,PropsSI):

    import numpy as np
    from Evaporator import Evaporator
    from Condenser import Condenser
    from GasCooler import GasCooler
    from Compressor import Compressor
    from Recuperator import Recuperator
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
    EtaIsen = Pars[12]
    EtaV = Pars[13]
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
        yE = Evaporator(PropsSI,Fluid,DTe,EHXe,DoSH,TSFI,TSFO)   #yE = PE,H_out,Rho_out,TE_out
        
        if (Fluid == 'R744'):
            PC = PRI
        else:
            yC = Condenser(PropsSI,Fluid,DoSC,DTc,EHXc,THWI,THWO)  #yC = PC, HC_out, TC_out
            PC = yC[0]
 
        if (RDoSH > 0): #Recuperator present
            yR = Recuperator(PropsSI,Fluid,RDoSH,yE[1],yE[0])  #yR = qRecup,Rho_out
            rhosuc = yR[1]
        else:
            yR = np.array([0,0])
            rhosuc = yE[2]
         
        Hsuc = yR[0] + yE[1]
        yW = Compressor(PropsSI,Fluid,Hsuc,yE[0],PC,EtaIsen) #H_out,Tgd    
        
        if (Fluid == 'R744'):
            yC = GasCooler(PropsSI,Fluid,PRI,DP,EHXc,THWI,yW[1]) #yC = PRO, HC_out, TRO
        
        MR = QC / (yW[0] - yC[1])
        WC = MR * (yW[0] - Hsuc)
        Qsrc = QC - WC
        QR = MR * yR[0]
    if (WC < 0.1): 
        CoP = 0 
    else: 
        CoP = QC / WC

    #Calculate compressor displacement L/s:
    Vdisp =  1000 * MR / (EtaV * rhosuc)

    Tdg = yW[1]
    Psuc = yE[0]
    Pdis = yC[0]
    
    all_data = [["Parameter","Value"],
            ["Refrigerant",Fluid],
            ["Refrigerant mass flow rate (kg/s)",f"{MR:.3f}"],
            ["Compressor power (kW)",f"{WC:.2f}"],
            ["Discharge gas temperature (dg C)",f"{Tdg:.1f}"],
            ["Source heat (kW)",f"{Qsrc:.2f}"],
            ["Recuperator heat (kW)",f"{QR:.2f}"],
            ["CoP",f"{CoP:.3f}"],
            ["Compressor displacement (L/s)",f"{Vdisp:.2f}"],
            ["Suction pressure (bar)",f"{Psuc:.2f}"],
            ["Discharge pressure (bar)",f"{Pdis:.2f}"],
            ["Outlet source fluid temperature (dg C)",f"{TSFO:.2f}"]]
    
    table = tabulate(all_data,headers='firstrow',tablefmt='grid')
 
    print(table)