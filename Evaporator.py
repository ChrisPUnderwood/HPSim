def Evaporator(PropsSI, Fluid, DT, EE, DoSH, TSFI, TSFO):
    #TWI = array inlet; TWO = array outlet 
    Tsat = TSFI - (TSFI - TSFO) / EE - DT
    #Outlet pressure from CoolProp...
    ePO = PropsSI('P','T',Tsat + 273.15,'Q',1,Fluid)
    TE_out = Tsat + DoSH
    #Outlet enthalpy from CoolProp...
    if DoSH > 0:
        H_out = PropsSI('H','P',ePO,'T',Tsat + DoSH + 273.15,Fluid) / 1000
        Rho_out = PropsSI('D','T',Tsat + DoSH + 273.15,'P',ePO,Fluid)
    else:
        H_out = PropsSI('H', 'P', ePO, 'Q', 1, Fluid) / 1000
        Rho_out = PropsSI('D','P',ePO,'Q',1,Fluid)
    return ePO/100000, H_out, Rho_out, TE_out