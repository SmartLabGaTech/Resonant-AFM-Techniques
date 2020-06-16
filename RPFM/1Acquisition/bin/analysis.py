##########################################################
# analysis.py                                         #
#                                                        #
# Description: This file contains functions that are     #
#    used during the measurement.                        #
#                                                        #
# History:                                               #
#           - 12/28/2017: First created                  #
##########################################################


import numpy as np                #for numerical operations
import pandas as pd               #for data reading/structure
from math import factorial
from scipy.optimize import leastsq
import scipy.signal as signal
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt          #Used for plotting
from datamanagement import chopper, readTDMS

import pyfftw

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


#############################################################
#                      SHO Analysis		                    #
# This section contains functions that perform analysis     #
# necessary for SHO fitting									#
#############################################################

#quickFFT:
#
#This function takes the raw result from a single chirp and
#does a quick fft to extract the frequency response. 
#
#Inputs:
#		rawResult: The raw time domain data returned from
#				   a single chirp
#		lowerFreq: The lower frequency used in the chirp
#		upperFreq: The upper frequency used in the chirp
#		samplingFreq: The sampling frequency
#
#Returns:
#		limfreq: the frequency values (i.e. the x-axis)
#		limfreqDomain: the FFT data (i.e. the y-axis)

def quickFFT(rawResult,samplingFreq):

    #First take the fft of the data
    #freqDomain=np.fft.fft(rawResult)
    freqDomain=pyfftw.interfaces.numpy_fft.fft(rawResult)
	
    #Use the numpy function fftfreq to determine the frequency
    #array
    timeStep=1/samplingFreq
    freq=np.fft.fftfreq(freqDomain.size, timeStep)
    
    return freq,freqDomain

#getSpecWaveform:
#
#Calls quickFFT and does some converting to extract amp and phase 
#as a pandas datafram 
#
#Inputs:
#		response: The raw time domain data returned from
#				   a single chirp
#		app_chirp: the applied chirp
#		lowerFreq: The lower frequency used in the chirp
#		upperFreq: The upper frequency used in the chirp
#		samplingFreq: The sampling frequency
#
#Returns:
#		specData: Dataframe containing the amplitude and phase
	
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

#getAcqusitionSpectrum:
#
#Calls getSpecWaveform for each chirp in an acquisition
#Results in a dataframe with the spectrum for each of the
#shirps 
#
#Inputs:
#		allData: The entire data set for the acquisition
#		lowerFreq: The lower frequency used in the chirp
#		upperFreq: The upper frequency used in the chirp
#		samplingFreq: The sampling frequency
#		numAcq: the acquisition number
#
#Returns:
#		limfreq: the frequency values (i.e. the x-axis)
#		limfreqDomain: the FFT data (i.e. the y-axis)
	
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
		else:
			info=chirpMap.loc[i,:]
			harmonic=info['Harmonic']
		
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

def generateChirpMap(waveformSpecPath):

	#Read in the waveform specification file
	waveSpec=pd.read_csv(waveformSpecPath)

	#Get the column labels
	cols=waveSpec.columns.values
	
	#Get the number of chirps and packets
	numChirps=int(np.sum(waveSpec.loc[:,cols[0]].values))
	numPackets=waveSpec.shape[0]
	
	#initialize the chirp map
	chirpMap=np.empty([numChirps,6])
	
	#chirp couter
	chirpCount=0
	prevDC=0
	
	for i in np.arange(0,numPackets):
		
		#Get the info on the packet and the 
		packInfo=waveSpec.loc[i,:]
		packetSize=packInfo[cols[0]]
		dcField=packInfo[cols[1]]
		multiplier=packInfo[cols[2]]
		harmonic=packInfo[cols[3]]
		plotGroup=packInfo[cols[4]]
		
		#For each chirp in the packet
		for j in np.arange(0,packetSize):
			
			currentRow=int(j+chirpCount)
			
			chirpMap[currentRow,0]=i
			chirpMap[currentRow,1]=plotGroup
			chirpMap[currentRow,2]=harmonic
			chirpMap[currentRow,5]=multiplier

			#If out of field
			if dcField == 0:
				chirpMap[currentRow,3]=0
				chirpMap[currentRow,4]=prevDC
			else:
				chirpMap[currentRow,3]=1
				chirpMap[currentRow,4]=dcField
				prevDC=dcField

		
		
		#Keep track of the number of chirps
		chirpCount=chirpCount+packetSize

	#Then get the row labels
	chirps=np.repeat('Chirp',numChirps)
	numbers=np.arange(1,numChirps+1)
	numbers = list(map(str,numbers))
	comb=list(zip(chirps,numbers))
	joined_data = (''.join(w) for w in comb)
	rows=list(joined_data)
		
	finalMap = pd.DataFrame(chirpMap, index=np.arange(0,numChirps), columns=['Packet','PlotGroup', 'Harmonic', 'InOut', 'DC', 'Multiplier'])
	
	return finalMap
	
#getSHOguess:
#
#Get a good SHO fit for the given chirp data
#
#Inputs:
#		chirpData: the complex data for the chirp
#
#Returns:
#		xGuess: contains good guess for the amp, phase, resonance and Q
	
def getSHOguess(chirpData, freq):
    
    #Get amplitude and phase
    amp=np.abs(chirpData)
    phase=np.angle(chirpData)

    #-----------------Get some guesses for the fitting-----------------
    resGuess=np.argmax(amp)
    ampGuess=amp[resGuess]

    #Start by estimating the full width half max
    ampHalfMax=ampGuess/2

    #First find the inidices (left and right) where the value is half the maximum
    #An error is thrown is these indicies or outside the range of the data
    try:
        leftInd=next(x[0] for x in enumerate(amp) if x[1] > ampHalfMax)
    except:
        leftInd=0
    try:
        rightInd=next(x[0] for x in enumerate(amp[argAmpMax:]) if x[1] < ampHalfMax)+argAmpMax
    except:
        rightInd=len(freq)-1
		
    FWHM=freq[rightInd]-freq[leftInd]

    phi=phase[resGuess]-np.pi/2
    res=freq[resGuess]
    Q=res/FWHM
    a=ampGuess

    xGuess=[a,phi,res,Q]
    
    return xGuess
	
#savitzky_golay:
#
#This function is a smoothing function 
#
"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """

def savitzky_golay(y, window_size, order, deriv=0, rate=1):
        
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')
	
#complexGaus:
#
#Define a gaussian for fitting
#
#Inputs:
#		x: the x-axis data, in our case frequencies
#		a: amplitude of the gaussian
#		phi: phase of the gaussian
#		res: resonance of the gaussian
#		Q: quality factor of the gaussian
#
#Returns:
#		the gaussian function
	
def complexGaus(x,a,phi,res,Q):
	func=a*np.exp(1j*phi)*res**2 / (x**2-1j*x*res/Q-res**2)
	return np.real(func)-1j*np.imag(func)

#residuals:
#
#Used to calculate the error of a fit to complex gaussian
#
#Inputs:
#		p: coefficient of the complex gaussian defined above
#		y: actual data
#		x: x axis values, or here typically frequency
#
#Returns:
#		the error of the fit
	
def residuals(p,y,x):
    a,phi,res,Q=p
    fit=complexGaus(x,a,phi,res,Q)
    error=y-fit
    res=error.real**2+error.imag**2
    return res

#shoFit:
#
#Used to fit a single acquisition
#
#Inputs:
#
#Returns:
	
	
def shoFit(responseFFT, numAcq):

	#Get the names of the chirps
	chirps=responseFFT.index.get_level_values(0)
	chirpNames=chirps.unique()
	numChirps=len(chirpNames)
	
	#Extract Acquisition
	acqData=responseFFT
	
	outData=[]
	
	for chirp in chirpNames:
	
		#Extract chirp and freq axis
		chirpData=acqData.xs(chirp)
		freq=chirpData.index.values
		chirpData=chirpData.values
		
		#Check that the phase is continually increasing
		phase=np.angle(chirpData)
		averageSlop=np.mean(np.diff(phase))
		
		#if not fix the data so that it is continually increasing
		if averageSlop<0:
			chirpData=np.real(chirpData)-1j*np.imag(chirpData)
			
		#Get a guess for the SHO fit
		xGuess=getSHOguess(chirpData, freq)
		xGuess=np.array(xGuess,dtype='float64')
		
		#Smooth
		chirpData=savitzky_golay(chirpData,53,3)
		
		#Fit it
		result=leastsq(residuals,xGuess,args=(chirpData,freq),maxfev=3000)
		pfit, pcov, infodict, errmsg, success = leastsq(residuals, xGuess, args=(chirpData,freq),full_output=1)
		
		try:
			flag=0
			msg=0
			
			#Get confidence values
			finalFit=complexGaus(freq,pfit[0],pfit[1],pfit[2],pfit[3])
			s_sq = ((finalFit.real**2+finalFit.imag**2)**2).sum()/(len(chirpData)-len(xGuess))
			pcov = pcov * s_sq
			perr = np.sqrt(np.diag(pcov))
		except:
			flag=1
			msg=errmsg
			perr=[np.inf,np.inf,np.inf,np.inf]
		
		#Set up the data entry for this chirp/acq
		#See the ppt for the analysis overview for more
		#info on each entry
		data=[1,pfit[0],pfit[1],pfit[2],pfit[3],perr[0],perr[1],perr[2],perr[3],0,flag,msg]
		
		try:
			outData=np.vstack([outData,data])
		except:
			outData=data
			
	#Then get the column labels
	indexChirps=chirpNames.values
	
	#Get the multi index from the products of these two
	index=pd.Index(indexChirps, names=['ChirpNum'])
	
	#Get the multi columns from the products of these two
	multiCol=pd.MultiIndex.from_product([[numAcq],['PlotGroup','Amp','Phase','Res','Q','errA','errP','errRes','errQ','R','Flag','Msg']], names=['Acq', 'Value'])
	
	#Create the total output data
	extractedData=pd.DataFrame(outData,index=index, columns=multiCol)
	
	return extractedData

#fftAnalysis:
#
#Convert the raw acquisitions to the frequency domain
#
#Inputs:
#		response: the data from a single acquisition to be fitted
#		numAcq: the acquisition number
#
#Returns:
#		popt: The fitted coefficients
#		perr: the error/uncertainty in these coefficients
#		rSq: the r squared fit value
	
def fftAnalysis(acqNum,file,samplingFreq, chirpDuration, lowerFreq, upperFreq, freqApplied, tdmsFile, chirpMap=None):
	
	#Pull out the data
	acqData=readTDMS(file, acqNum, tdms_file=tdmsFile)
	
	#Chop it up into individual chirps
	#chop=chopper(acqData,samplingFreq,chirpDuration,acqNum)
	
	#Get the specturm for each chirp
	spec=getAcqusitionSpectrum(acqData,freqApplied,lowerFreq,upperFreq,samplingFreq,acqNum,chirpDuration,chirpMap)
	
	return spec

#fftAnalysis:
#
#Convert the raw acquisitions to the frequency domain
#
#Inputs:
#		response: the data from a single acquisition to be fitted
#		numAcq: the acquisition number
#
#Returns:
#		popt: The fitted coefficients
#		perr: the error/uncertainty in these coefficients
#		rSq: the r squared fit value
	
def quickerFftAnalysis(acqNum,file,samplingFreq, chirpDuration, lowerFreq, upperFreq, freqApplied, tdmsFile=None):
	
	if tdms_file == None:
		#Load the file
		tdms_file=TdmsFile(file)
    
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
	
    #First, we need to find the number of samples per chirp
	sampPerChirp=np.ceil(samplingFreq*chirpDuration)
    
    #Then find the total number of samples in the data
	totalSamp=len(data)
    
    #Then we can find the total number of chirps present
	numChirps=int(totalSamp/sampPerChirp)
	
	#For each chirp get the FFT
	for chirp in chirpNames:
	
		#Extract chirp
		chirpData=acqData.xs(chirp)
		
		#Get the spectrum data (i.e. fft)
		freq,response=getSpecWaveform(chirpData,freqApplied,lowerFreq,upperFreq,samplingFreq)
		
		#Transpose it because I didn't think ahead
		#response=response.transpose()
		
		#Stack the results for each chirp on top of each other.
		#This will fail if it is the first chirp
		try:
			outData=np.vstack([outData,response])
		except:
			outData=response
	
	return spec
	
def storeFFT(acqNum,data,fftFileName):
	store=pd.HDFStore(fftFileName)
	store['Acq'+str(acqNum)]=data
	store.close()
	
	
#shoFitAcq:
#
#Perform the SHO fit an acquisition
#
#Inputs:
#		response: the data from a single acquisition to be fitted
#		numAcq: the acquisition number
#
#Returns:
#		popt: The fitted coefficients
#		perr: the error/uncertainty in these coefficients
#		rSq: the r squared fit value
	
def shoFitAcq(acqNum,fftFileName):

	#Get a path to the fft information
	store=pd.HDFStore(fftFileName)
	
	#extract the data for this acquisition
	spec=store['Acq'+str(acqNum)]
	
	#Call the SHO fitter for each chirp
	extracted=shoFit(spec,acqNum)
	
	return extracted