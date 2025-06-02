def Condenser(PropsSI,Fluid,DoSC,DT,EC,THWI,THWO):
    #THWI = condenser cooling water inlet temperature; THWO = condenser cooling water outlet temperature
    Tsat = THWI + (THWO - THWI) / EC + DT
    #Get properties from CoolProp...
    cPO = PropsSI('P','T',Tsat+273.15,'Q',1,Fluid)
    TC_out = Tsat - DoSC       
    if DoSC > 0:
        H_out = PropsSI('H','P',cPO,'T',TC_out+273.15,Fluid) / 1000
    else:
        H_out = PropsSI('H','P',cPO,'Q',0,Fluid) / 1000
        
    return cPO/100000,H_out,TC_out