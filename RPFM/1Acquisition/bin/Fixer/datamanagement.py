##########################################################
# datamanager.py                                         #
#                                                        #
# Description: This file contains functions that         #
#    perform general operations on the data              #
#                                                        #
# History:                                               #
#           - 12/28/2017: First created                  #
##########################################################

import numpy as np                #for numerical operations
import pandas as pd               #for data reading/structure
from nptdms import TdmsFile		  #For reading LabView files

##############################################################
#chopper:
#
#This function takes data generated from a multiple chirp
#application and seperates out the response due to each chirp 
#
#Inputs:
#		rawResult: The raw time domain data returned a single
#			application of the waveform
#		samplingFreq: The sampling frequency
#		chirpDuration: The duration of a single chirp
#		acqNum: number of the acquisition you want analyzed
#
#Returns:
#		chopped: a dataframe that has the response to the 
#			individual chirps 

def chopper(rawResult,samplingFreq,chirpDuration,acqNum):

    #Get the data and the time
	data=rawResult
   
    #First, we need to find the number of samples per chirp
	sampPerChirp=np.ceil(samplingFreq*chirpDuration)
    
    #Then find the total number of samples in the data
	totalSamp=len(data)
    
    #Then we can find the total number of chirps present
	numChirps=int(totalSamp/sampPerChirp)
    
    #Initalize output data
    
    #First get the index values, in our case just the time
	#axis
	timeStep=1/samplingFreq
	totalTime=chirpDuration
	times=np.linspace(0,totalTime-timeStep,sampPerChirp)
	
	#Then get the column labels
	chirps=np.repeat('Chirp',numChirps)
	numbers=np.arange(1,numChirps+1)
	numbers = list(map(str,numbers))
	comb=list(zip(chirps,numbers))
	joined_data = (''.join(w) for w in comb)
	columns=list(joined_data)
	
	multiInd=pd.MultiIndex.from_product([columns,times], names=['ChirpNum', 'Time'])
	
	colName=pd.Index([acqNum],name='Acq') 
    #Initalize the output data
	choppedData=pd.DataFrame(data.values,index=multiInd, columns=colName)
	
	return choppedData


#########################################################	
#readTDMS:
#
#This function reads the tdms files that labview saves the 
#data as
#
#Inputs:
#		path: Path to the file
#		acqNum: number of the acquisition you want analyzed
#		channelName: name of the channel where the data is
#
#Returns:
#		newData: a dataframe containing all of the info
#			from the tdms file 
	
def readTDMS(path, acqNum, channelName='PXI1Slot7/ai0',tdms_file=None):

	dataOut={}
    
	if tdms_file == None:
		#Load the file
		tdms_file=TdmsFile(path)
    
    #Get the number of groups (or entries)
	groups=tdms_file.groups()
	
	GroupName=str(acqNum)

	#Extract the data
	channel=tdms_file.object(GroupName,channelName)
	
	#Get the data
	data=channel.data
	data=data.astype(np.float)
	
	#Get the meta data
	timeStep=channel.property('wf_increment')
	numSamples=channel.property('wf_samples')
	
	#Store data
	#dataOut['Acq'+str(acqNum)]=data
	#dataOut['Time']=np.arange(0,numSamples*timeStep,timeStep)
	
	#Convert to dataframe, cause it IS better
	newData=data
	
	return newData

#convertTDMS:
#
#This converts the tdms files that labview saves to an HDF5 format 
#
#Inputs:
#		path: Path to the file
#		pathHDF5: Path to save the hdf5 too
#
#Returns:
#		newData: a dataframe containing all of the info
#			from the tdms file 
	
def convertTDMS(path, pathHDF5):
    
    #Load the file
	tdms_file=TdmsFile(path)
	tdms_file.as_hdf(pathHDF5)
	