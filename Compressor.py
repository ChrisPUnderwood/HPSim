def Compressor(PropsSI,Fluid,HI,PE,PC,EtaIsen):
    #Get entropy and enthalpy  at compressor inlet using CoolProp...
    s = PropsSI('S','H',HI*1000,'P',PE*100000,Fluid)  
    H_isen_out = PropsSI('H','S',s,'P',PC*1E+05,Fluid) / 1000
    H_out = HI + (H_isen_out - HI) / EtaIsen
    #Get discharge gas temperature:
    Tgd = PropsSI('T','P',PC*100000,'H',H_out*1000,Fluid)
    return H_out,Tgd-273.15                           