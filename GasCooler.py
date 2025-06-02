def GasCooler(PropsSI,Fluid,PRI,DP,EC,THWI,TRI):
    #THWI = gas cooler water inlet temperature; THWO = gas cooler water outlet temperature
    TRO = TRI - EC * (TRI - THWI) 
    PRO = PRI - DP  #Adjust for gas cooler pressure loss
    HGC_out = PropsSI('H','T',TRO + 273.15,'P',PRO*100000,Fluid) / 1000   
    return PRO, HGC_out, TRO