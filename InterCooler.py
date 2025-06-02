def InterCooler(PropsSI,Fluid,P,EC,THWI,TRI,HRI):
    #Allowable outlet gas temperature assuming 5K superheat at HP compressor inlet
    TRO_min = 5 + PropsSI('T','P',P*1E+05,'Q',1,Fluid) - 273.15
    HIC_out = PropsSI('H','T',TRO_min + 273.15,'P',P*1E+05,Fluid) / 1000
    TRO = TRI - EC * (TRI - THWI)
    if TRI <= THWI:
        TRO = TRO_min
        qH = 0
        qS = HRI - HIC_out
    else:
        HIC0 = PropsSI('H','T',TRO + 273.15,'P',P*1E+05,Fluid) / 1000 
        qH = HRI - HIC0
        qS = HRI - qH - HIC_out 
        TRO = TRO_min
    return HIC_out, TRO, qH, qS