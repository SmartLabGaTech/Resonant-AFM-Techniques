import numpy as np                #for numerical operations
import pandas as pd               #for data reading/structure
#from analysis import *
from datamanagement import *
import traceback
import scipy.signal as signal

from math import factorial
from scipy.optimize import leastsq
import scipy.signal as signal
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt          #Used for plotting
from nptdms import TdmsFile		  #For reading LabView files

from scipy.fftpack import fft, fftfreq, fftshift

import pyfftw

amp = 0.1
low = 375000
high = 425000
dur = 0.025
sr = 2000000
numAcq = 900

chirp_path = 'E:\\Data\\Lee\\pt27_007\\05-10-2019\\B\\Relax\\chirpMap.csv'

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

def getfreqapp():
	t=np.arange(0,dur,1/sr)

	############# Generate Fundamental ########################################
	#Applied Chirp in the time domain
	app_chirp=amp*signal.chirp(t,low*0.985,dur,high*1.015)

	#Window
	window=signal.tukey(len(app_chirp),alpha=0.2)

	#Apply the window
	app_chirpFun=np.multiply(window,app_chirp)

	#Convert to the freq domain
	freq,freqAppliedFun=quickFFT(app_chirp,sr)


	############# Generate 2nd Harmonic ########################################
	#Applied Chirp in the time domain
	app_chirp=amp*signal.chirp(t,2*low*0.985,dur,2*high*1.015)

	#Window
	window=signal.tukey(len(app_chirp),alpha=0.2)

	#Apply the window
	app_chirpFun=np.multiply(window,app_chirp)

	#Convert to the freq domain
	freq,freqApplied2nd=quickFFT(app_chirp,sr)

	############# Generate 3rd Harmonic ########################################
	#Applied Chirp in the time domain
	app_chirp=amp*signal.chirp(t,3*low*0.985,dur,3*high*1.015)

	#Window
	window=signal.tukey(len(app_chirp),alpha=0.2)

	#Apply the window
	app_chirpFun=np.multiply(window,app_chirp)

	#Convert to the freq domain
	freq,freqApplied3rd=quickFFT(app_chirp,sr)

	return np.squeeze([[freqAppliedFun],[freqApplied2nd],[freqApplied3rd]])

def getAcqusitionSpectrum(rawResult,freqApplied,lowerFreq,upperFreq,samplingFreq,acqNum,chirpDuration,chirpMap=None):

	#Get the data and the time
	data=rawResult
   
    #First, we need to find the number of samples per chirp
	sampPerChirp=np.ceil(samplingFreq*chirpDuration)

    #Then find the total number of samples in the data
	totalSamp=len(data)
	
    #Then we can find the total number of chirps present
	numChirps=int(totalSamp/sampPerChirp)
	
	temp=freqApplied[0,:]
	
	fres=np.ceil(1/(temp.size*(1/samplingFreq)))
	
	#Check to see if we are interested in higher harmonics	
	fund=np.where(chirpMap['Harmonic']==3)
	numChirps3rd=np.shape(fund)[1]
	
	fund=np.where(chirpMap['Harmonic']==2)
	numChirps2nd=np.shape(fund)[1]
	
	if numChirps3rd > 0:
		fftLen=np.ceil(((3*upperFreq-3*lowerFreq)/fres)-1)
	elif numChirps2nd > 0:
		fftLen=np.ceil(((2*upperFreq-2*lowerFreq)/fres)-1)
	else:
		fftLen=np.ceil(((upperFreq-lowerFreq)/fres)-1)

	outData=np.empty([numChirps,int(fftLen)], dtype=np.complex)

	chirpIterator=np.arange(0,numChirps)
	
	#For each chirp get the FFT
	for i in chirpIterator:

		lowInd=int(i*sampPerChirp)
		highInd=int((i+1)*(sampPerChirp)-1)
	
		#Extract chirp
		chirpData=data[lowInd:highInd]
		
		#Extract chirp 
		if chirpMap is None:
			harmonic=1
			plotgroup = 0
		else:
			info=chirpMap.loc[i,:]
			harmonic=info['Harmonic']
			plotgroup = info['PlotGroup']
		
		if harmonic == 1:
			low=lowerFreq
			upper=upperFreq
		else:
			low=lowerFreq*harmonic
			upper=upperFreq*harmonic
		
		freqApp=freqApplied[int(harmonic-1),:]
		
		#Get the spectrum data (i.e. fft)
		freq,response=getSpecWaveform(chirpData,freqApp,low,upper,samplingFreq)
				
		#response=savitzky_golay(response, 53, 3)

		resLen=np.shape(response)
		
		if resLen < fftLen:
			differ=fftLen-resLen
			adjust=np.zeros(int(differ),dtype=np.complex)
			response=np.hstack([response,adjust])
		elif resLen > fftLen:
			differ=resLen-fftLen
			fftLen=fftLen+differ
			outData=np.empty([numChirps,int(fftLen)], dtype=np.complex) 

		outData[i,:]=response
		
	#Get the indicies
	ind=np.arange(1,numChirps+1)

	#Create the total output data
	allResponse=pd.DataFrame(outData.transpose(),index=freq, columns=ind)

	return allResponse.transpose()

def getSpecWaveform(response,freqApplied,lowerFreq,upperFreq,samplingFreq):

	#Take the fft of the response and the applied chirp
	freq,freqResponse=quickFFT(response,samplingFreq)

	#We only care about the frequency range applied
	#Find the indicies of the chirp bandwidth (lower and upper)
	indicies=np.where(np.logical_and(freq>lowerFreq,freq<upperFreq))

	#Apply this range
	limfreq=freq[indicies]
	limfreqDomain=freqResponse[indicies]
	limApplied=freqApplied[indicies]

	#Deconvolve
	deconResponse=np.divide(limfreqDomain,limApplied)
	
	#filter
	#deconResponse=butter_lowpass_filter(deconResponse, 0.1, 1, order=5)
	
	return limfreq,deconResponse

def quickFFT(rawResult,samplingFreq):

	#First take the fft of the data
	#freqDomain=np.fft.fft(rawResult)
	freqDomain=pyfftw.interfaces.numpy_fft.fft(rawResult)
	
	#Use the numpy function fftfreq to determine the frequency
	#array
	timeStep=1/samplingFreq
	#freq=np.fft.fftfreq(freqDomain.size, timeStep)
	freq=fftfreq(freqDomain.size, timeStep)
	
	return freq,freqDomain
	
if __name__ == "__main__":
	
	for i in np.arange(0,numAcq):
		print('Starting Acq '+str(i))
		data = readTDMS('RawData\\Acq'+str(i)+'.tdms', i)
		chirpMap = pd.read_csv(chirp_path, index_col=0, header=0)
		freqApplied = getfreqapp()
		try:
			spec=getAcqusitionSpectrum(data,freqApplied,low,high,sr,i,dur,chirpMap)
		except Exception as e:
			traceback.print_exc()
		store=pd.HDFStore('fft_data.h5')
		store['Acq'+str(i)]=spec
		store.close()
		print('     Acq '+str(i)+' Stored')
	garbage = input('Press Enter')