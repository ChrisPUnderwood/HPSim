def Recuperator(PropsSI,Fluid,RDoSH,HEI,PE):
    #HEI = LP gas inlet enthalpy; HCI = HP fluid inlet enthalpy
    #Get specific heats using CoolProp...
    qRecup = RDoSH*PropsSI('C','H',1000*HEI,'P',100000*PE,Fluid) / 1000
    rhosuc = PropsSI('D','H',1000*(HEI+qRecup),'P',100000*PE,Fluid)
    return qRecup,rhosuc