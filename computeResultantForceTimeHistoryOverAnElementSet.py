'''
 This code is written to compute resultant magnetic force over an given element set in electromagnetic analysis.
 In electromagnetic analysis, the variables are given for the whole element and no integration point data is used.
 Therefore, the quantities over the entire element are multiplied with element volume and summed over the entire set 
 to compute the resultant magnetic force acting on the region
'''
from odbAccess import *
from abaqusConstants import *
from odbMaterial import *
from odbSection import *
from textRepr import *
import time as wallTime
import math

if len(sys.argv) != 4:
   text = """ Three arguments must be supplied : \
            \n\t (1) odbName with extension \
            \n\t (2) element set name \
            \n\t (3) frameNoInc """ 
   raise RuntimeError(text)
    
# Settings
odbName = str(sys.argv[1])
nameElementSet= str(sys.argv[2])
frameNoInc = int(sys.argv[3])
variableName = 'EMBF'   # Magnetic force density from abaqus (N/m^3)

# extract these from the odb
odb = openOdb(path = odbName)
stepNames = odb.steps.keys(0)  # 0 indicates first step (for ex. a static step)
instanceName = odb.rootAssembly.instances.keys(0) # 0 indicates first instance
assembly = odb.rootAssembly
elType = assembly.instances[instanceName[0]].elements[0].type
totalNoNodes = len(odb.rootAssembly.instances[instanceName[0]].nodes)
elementSetObjectRequired = odb.rootAssembly.instances[instanceName[0]].elementSets[nameElementSet.upper()]
totalNoElementsInSet = len(elementSetObjectRequired.elements)
print 'Element Type: ',elType
print 'Total elements in set:',totalNoElementsInSet

outputFileName = 'outputData_ResultantMagneticForceHistory' + '_ElSet_' + str(nameElementSet) + '.dat'
file_output = open(outputFileName,'w')
baseString = '  Time     ' + '  VolumetricForceComponents  ' + '    ResultantForce  ' + '  unitResultantVector  '   +   '  AngleWithAxes(Degrees)'
file_output.write(baseString)
file_output.write('\n')
start = wallTime.clock()
timeTotal_prevStep = 0
for iStep in range(0,len(stepNames)):
    stepObject = odb.steps[stepNames[iStep]]
    totalNoFrames = len(stepObject.frames)
    if iStep == 0:
        frameNosToExport = range(0, totalNoFrames-1, frameNoInc)
    else:
        frameNosToExport = range(1, totalNoFrames-1, frameNoInc)
    frameNosToExport.append(totalNoFrames-1)  # this ensures that the last time step is always exported
    noOfFramesToExport = len(frameNosToExport) 

    for frameNumber in range(len(frameNosToExport)):
        frameData = stepObject.frames[frameNosToExport[frameNumber]]
        stepTime = frameData.frameValue
        timeTotal = timeTotal_prevStep + stepTime
        file_output.write('%20.8E\t' %timeTotal)        

        fieldVariableObject = frameData.fieldOutputs[variableName].getSubset(region=elementSetObjectRequired)
        fieldVariableFieldValues = fieldVariableObject.values  
        elementVolumeObject = frameData.fieldOutputs['EVOL'].getSubset(region=elementSetObjectRequired)
        elementVolumeFieldValues = elementVolumeObject.values
        
        # Write field variable components
        if str(fieldVariableFieldValues[0].type) == 'SCALAR':
            nComponentsVariable = 1
        elif str(fieldVariableFieldValues[0].type) == 'VECTOR':
            nComponentsVariable = fieldVariableFieldValues[0].data.size        
        volumetricTotalFieldComponents = [0 for ii in range(0,nComponentsVariable)]
        
        totalVolume = 0
        for iVol,ifieldVariableField in zip(elementVolumeFieldValues,fieldVariableFieldValues):
            idElement = int(ifieldVariableField.elementLabel)
            volumeElement = iVol.data            
            totalVolume = totalVolume + volumeElement

            for iComponent in range(0,nComponentsVariable):
                fieldData = ifieldVariableField.data[iComponent]
                volumetricTotalFieldComponents[iComponent] = volumetricTotalFieldComponents[iComponent] +  fieldData*volumeElement

        print 'step: ',iStep + 1, '/',len(stepNames),' stepName: ', stepNames[iStep], ' stepTime=',stepTime, ' totalTime: ',timeTotal, ' setVolume: ', totalVolume

        forceResultant = 0
        for iComponent in range(0,nComponentsVariable):
            file_output.write('%20.8E\t' %volumetricTotalFieldComponents[iComponent])
            forceResultant = forceResultant + volumetricTotalFieldComponents[iComponent]**2
        forceResultant = forceResultant**0.5    
        file_output.write('%20.8E\t' %forceResultant)
        unitResultantVector = [volumetricTotalFieldComponents[ii]/forceResultant for ii in range(0,nComponentsVariable)]
        listAnglesWithAxes = [(180/math.pi)*math.acos(unitResultantVector[ii])  for ii in range(0,nComponentsVariable)]
        for iComponent in range(0,nComponentsVariable):
            file_output.write('%20.8E\t' %unitResultantVector[iComponent])
        for iComponent in range(0,nComponentsVariable):
            file_output.write('%20.8E\t' %listAnglesWithAxes[iComponent])            
        file_output.write('\n')
            
    timeTotal_prevStep = timeTotal_prevStep + stepTime
   
file_output.close()       
odb.close()   
end = wallTime.clock()     

print "Time Taken for writing: ",(end-start), "s"
