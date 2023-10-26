'''
 This code is written to extract output variables for a given element set in electromagnetic analysis.
 In electromagnetic analysis, the variables are given for the whole element and no integration point data is used.
 Therefore, the quantities over the entire element are extract
'''
from odbAccess import *
from abaqusConstants import *
from odbMaterial import *
from odbSection import *
from textRepr import *
import time as wallTime

if len(sys.argv) != 5:
   text = """ Four arguments must be supplied : \
            \n\t (1) odbName with extension \
            \n\t (2) element set name \
            \n\t (3) variable Name (no quotations) \
            \n\t (4) frameNoInc """ 
   raise RuntimeError(text)
    
# Settings
odbName = str(sys.argv[1])
nameElementSet= str(sys.argv[2])
variableName = str(sys.argv[3])
frameNoInc = int(sys.argv[4])

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

outputFileName = 'outputData_elID_eVol_' + str(variableName) + '_ElSet_' + str(nameElementSet) + '.dat'
file_output = open(outputFileName,'w')
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
        file_output.write('Time: %20.8E\n' %timeTotal)
        print 'step: ',iStep+1, '/',len(stepNames),' stepName: ', stepNames[iStep], ' stepTime=',stepTime, ' totalTime: ',timeTotal

        fieldVariableObject = frameData.fieldOutputs[variableName].getSubset(region=elementSetObjectRequired)
        fieldVariableFieldValues = fieldVariableObject.values  
        elementVolumeObject = frameData.fieldOutputs['EVOL'].getSubset(region=elementSetObjectRequired)
        elementVolumeFieldValues = elementVolumeObject.values
        
        # Write field variable components
        totalVolume = 0
        for iVol,ifieldVariableField in zip(elementVolumeFieldValues,fieldVariableFieldValues):
            idElement = int(ifieldVariableField.elementLabel)
            file_output.write('%20d\t' %idElement)
            volumeElement = iVol.data            
            totalVolume = totalVolume + volumeElement
            file_output.write('%20.8E\t' %volumeElement)
            if str(ifieldVariableField.type) == 'SCALAR':
                nComponentsVariable = 1
            elif str(ifieldVariableField.type) == 'VECTOR':
                nComponentsVariable = ifieldVariableField.data.size
            
            if nComponentsVariable == 1:
                data_to_write = ifieldVariableField.data
                file_output.write('%20.8E\t' %data_to_write)
            else:
                for iComponent in range(0,nComponentsVariable):
                    data_to_write = ifieldVariableField.data[iComponent]
                    file_output.write('%20.8E\t' %data_to_write)
            file_output.write('\n')
            
        #print('totalVolume:',totalVolume)
    timeTotal_prevStep = timeTotal_prevStep + stepTime
   
file_output.close()       
odb.close()   
end = wallTime.clock()     

print "Time Taken for writing: ",(end-start), "s"
