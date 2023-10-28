'''
 This code writes the abaqus amplitude definitions for sine and cosine load forms
'''
import sys
import math

if len(sys.argv) != 5:
   text = """ Four arguments must be supplied : \
            \n\t (1) Frequency in Hz \
            \n\t (2) Type of waveform (sine/cosine) \
            \n\t (3) Number of time points per period ( typically 20) \
            \n\t (3) Total number of cycles """ 
   raise RuntimeError(text)
    
# Settings
frequency = float(sys.argv[1])
typeWaveform = str(sys.argv[2])
numberOfTimePointsPerPeriod = int(sys.argv[3])
nCyclesWaveForm = int(sys.argv[4])

outputFileName = 'amplitudeDefinitions.inp'
file_output = open(outputFileName,'w')
file_output.write('*amplitude, name=' + str(typeWaveform) +'Wave_freq_' + str(int(frequency)) + 'Hz')
file_output.write('\n')

angularVelocity = 2*math.pi*frequency
timePeriod = 2*math.pi/angularVelocity
incrementTime = timePeriod/numberOfTimePointsPerPeriod
totalIncrements = numberOfTimePointsPerPeriod*nCyclesWaveForm

for iIncrement in range(0,totalIncrements+1):
    time = iIncrement*incrementTime
    if typeWaveform.lower() == "sine":
        current = math.sin(angularVelocity*time) # sin and cos should be in radians
    elif typeWaveform.lower() == "cosine":
        current = math.cos(angularVelocity*time)
        
    if iIncrement < totalIncrements:
        file_output.write('%30.15E,\t'%time)
        file_output.write('%30.15E,\n'%current)
    else:
        file_output.write('%30.15E,\t'%time)
        file_output.write('%30.15E'%current)

print('timeIncrement, totalTime: ',incrementTime,'\t',time)   
file_output.close()       

