'''
This code computes analytical solution for magnetic forces under different conditions given in Okress paper
It reproduces Fig. 5,6 and 7 from Okress paper.
'''

import math
import matplotlib.pyplot as plt

    
loopType = 'twocoils'           # 'singlecoil'/'twocoils'
directionCurrent = 'reverse'    # only applicable for 'twocoils' case. 'same'/'reverse'
# ---------------- UNCERTAIN PARAMETERS
densityBronze_kgm3 = 8550   # NOTE: This is assumed. So the plots may give some error
                            # 8350 gives good result for Fig. 5 in paper
                            # 8550 gives good result for Fig. 6 in paper

# ---------------- PARAMETERS FROM OKRESS PAPER
permeability_freeSpace_SI = 1.25714e-06
permeability_freeSpace_muOhmSperCm = permeability_freeSpace_SI*1E4
newtonToDyne = 1E5
cmToMeter = 1E-2           
listVerticalDistancesFromLoopCenter_cm = [0.05*ii for ii in range(-241,241)]
radiusSphere_cm = 0.5*2.54
radiusLoop_cm = 0.5*4.85*2.54
resistivity_muOhmCm = 6 
currentCoil1RMS_amp = 600
frequency_Hz = 9600
accDueToGravity = 9.81
distanceBetweenPlanesOfLoops_cm = 5

listForceToWeightRatios = []
listForceToWeightRatios_Rony = []
for iDistance in range(0,len(listVerticalDistancesFromLoopCenter_cm)):
    verticalDistanceFromLoopCenter_cm = listVerticalDistancesFromLoopCenter_cm[iDistance]
    x = 2*math.pi*radiusSphere_cm*(frequency_Hz/(1000*resistivity_muOhmCm))**0.5    # See ur notes for this derivation
    x_Rony = math.sqrt(math.pi)*radiusSphere_cm*(frequency_Hz*permeability_freeSpace_muOhmSperCm/(resistivity_muOhmCm))**0.5 # <--- becomes dimensionless. equivalently, SI units can be used for all the quantities
    if x <= 4:
        G_x = 1 - (3/(4*x))*((math.sinh(2*x)-math.sin(2*x))/((math.sinh(x))**2+(math.sin(x))**2))
        G_Rony = 1 - (3/(4*x_Rony))*((math.sinh(2*x_Rony)-math.sin(2*x_Rony))/((math.sinh(x_Rony))**2+(math.sin(x_Rony))**2))
    else:
        G_x = 1 - (3/(2*x))
        G_x_Rony = 1 - (3/(2*x_Rony))
     
    print('x,x_Rony:',x,x_Rony)
    print('G_x,G_x_Rony:',G_x,G_x_Rony)
    y = verticalDistanceFromLoopCenter_cm/radiusLoop_cm
    A_y = y/((1+y**2)**4)    
    y1 = y - (distanceBetweenPlanesOfLoops_cm/radiusLoop_cm)
    if directionCurrent.lower() == "same":
        B_y = ((1/((1+y**2)**1.5)) + (1/((1+y1**2)**1.5)))*((y/((1+y**2)**2.5)) + (y1/((1+y1**2)**2.5)))
    elif directionCurrent.lower() == "reverse":
        B_y = ((1/((1+y**2)**1.5)) - (1/((1+y1**2)**1.5)))*((y/((1+y**2)**2.5)) - (y1/((1+y1**2)**2.5)))
        
    sphereWeight = ((4/3)*math.pi*(radiusSphere_cm*cmToMeter)**3)*densityBronze_kgm3*accDueToGravity*newtonToDyne
    
    if loopType.lower() == "singlecoil":
        Force = (3/50)*((math.pi)**2)*(currentCoil1RMS_amp**2)*G_x*A_y*((radiusSphere_cm/radiusLoop_cm)**3) # <----- dynes
        listForceToWeightRatios.append(100*Force/sphereWeight)
    elif loopType.lower() == "twocoils":    
        Force = (3/50)*((math.pi)**2)*(currentCoil1RMS_amp**2)*G_x*B_y*((radiusSphere_cm/radiusLoop_cm)**3) # <----- dynes
        listForceToWeightRatios.append(100*Force/sphereWeight)
        Force_Rony = (3/2)*((math.pi))*permeability_freeSpace_muOhmSperCm*(currentCoil1RMS_amp**2)*G_x*B_y*((radiusSphere_cm/radiusLoop_cm)**3)*10 # <----- dynes (factor 10 is convert the muOhmSperCm*Amp^2=1E-4Newtons units to dynes (1N=1E5dynes))
        listForceToWeightRatios_Rony.append(100*Force_Rony/sphereWeight)
                
    print('verticalDistance,Force,weight,Force/Weight:',verticalDistanceFromLoopCenter_cm,Force,sphereWeight,Force/sphereWeight)    
plt.plot(listVerticalDistancesFromLoopCenter_cm,listForceToWeightRatios,'-',c='black',label="Okress")
if loopType.lower() == "twocoils":
    plt.plot(listVerticalDistancesFromLoopCenter_cm,listForceToWeightRatios_Rony,'--',c='red',marker="o",markersize=1,label="Rony")

plt.xlabel('distanceZ (cm)')
plt.ylabel('Force/Weight (%)')
plt.legend(loc='upper center',ncol=2,borderpad=0.2,columnspacing=0.5,handletextpad=0.05)
plt.show()