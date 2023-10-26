'''
This code creates the simulation directories and input files to compute effective specific capacity at different temperatures
'''
import sys
import os
import shutil
from replaceAstringInAFile import replaceAstringInAFile

def main():
    if len(sys.argv) != 7:
        text = """Six command line arguments are expected: \
                    \n\t(1) directory to look for reference input files \
                    \n\t(2) reference input file name \
                    \n\t(3) starting temperature for simulations\
                    \n\t(4) ending temperature for simulations \
                    \n\t(5) temperature increment \
                    \n\t(6) volumetric heat flux"""
        raise RuntimeError(text)
    
    source_dir_name = str(sys.argv[1])
    ref_inp_file_name = str(sys.argv[2])
    temperatureStart = float(sys.argv[3])
    temperatureEnd = float(sys.argv[4])
    incrementTemperature = float(sys.argv[5])
    volumetricHeatFlux = float(sys.argv[6])
    pwd = os.getcwd()
    
    tolerance = 1E-3
    listTemperatures = []
    temperature = temperatureStart
    while temperature <= temperatureEnd:
        listTemperatures.append(temperature)
        temperature = temperature + incrementTemperature
    
    if abs(temperature-incrementTemperature-temperatureEnd) >= tolerance*incrementTemperature:
        listTemperatures.append(temperatureEnd)
    
    logFile = open('simulationInformation.log','w')
    for iTemperature in range(0,len(listTemperatures)):
        print('Creating inputs at temperature : ', listTemperatures[iTemperature])
        source_dir_path = str(source_dir_name)
        dest_dir_name = 'temperature_' + str(iTemperature+1)
        dest_dir_path = str(pwd) + '\\' + str(dest_dir_name) + "\\"
        if not os.path.exists(dest_dir_path):
            os.makedirs(dest_dir_path)
        
        shutil.copytree(source_dir_path, dest_dir_path, dirs_exist_ok=True)        
        nameFile = dest_dir_path + '\\' + str(ref_inp_file_name)
        
        refDomainTemperature = listTemperatures[iTemperature]
        logFile.write("{0:50s}{1:30.15f}\n".format(dest_dir_name,refDomainTemperature))
        
        success = replaceAstringInAFile(nameFile,"__initialTempDomain__",str(refDomainTemperature))
        success = replaceAstringInAFile(nameFile,"__volumetricHeatFlux__",str(volumetricHeatFlux))
        
    logFile.close()
    
if __name__ == "__main__":
    main()