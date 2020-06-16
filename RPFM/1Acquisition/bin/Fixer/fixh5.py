from analysis import fftAnalysis, quickFFT, getSHOguess, storeFFT, generateChirpMap
from nptdms import TdmsFile
import numpy as np
import scipy.signal as signal
import pandas as pd

folder='D:\\Data\\Lee\\pt40_024\\01-29-2019\\D\\SSPFM'
chirpmap=generateChirpMap(folder+'\\BESSPFM.csv')
fftFileName='D:\\Data\\Lee\\pt40_024\\01-29-2019\\D\\SSPFM\\pt40_024_5x_ss.h5'

fs = 2000000
chirp_duration = 0.005
lowerFreq = 370000
upperFreq = 420000


#Generate the applied chirp for Info
#
#Time axis
t=np.arange(0,chirp_duration,1/fs)

############# Generate Fundamental ########################################
#Applied Chirp in the time domain
app_chirp=1*signal.chirp(t,lowerFreq*0.985,chirp_duration,upperFreq*1.015)

#Window
window=signal.tukey(len(app_chirp),alpha=0.2)

#Apply the window
app_chirpFun=np.multiply(window,app_chirp)

#Convert to the freq domain
freq,freqAppliedFun=quickFFT(app_chirp,fs)


############# Generate 2nd Harmonic ########################################
#Applied Chirp in the time domain
app_chirp=1*signal.chirp(t,2*lowerFreq*0.985,chirp_duration,2*upperFreq*1.015)

#Window
window=signal.tukey(len(app_chirp),alpha=0.2)

#Apply the window
app_chirpFun=np.multiply(window,app_chirp)

#Convert to the freq domain
freq,freqApplied2nd=quickFFT(app_chirp,fs)

############# Generate 3rd Harmonic ########################################
#Applied Chirp in the time domain
app_chirp=1*signal.chirp(t,3*lowerFreq*0.985,chirp_duration,3*upperFreq*1.015)

#Window
window=signal.tukey(len(app_chirp),alpha=0.2)

#Apply the window
app_chirpFun=np.multiply(window,app_chirp)

#Convert to the freq domain
freq,freqApplied3rd=quickFFT(app_chirp,fs)

freqApplied=np.squeeze([[freqAppliedFun],[freqApplied2nd],[freqApplied3rd]])


for counter in range(900):

	print('Trying: '+str(counter))

	try:
		spec=pd.read_hdf(fftFileName,'Acq45'+str(counter))
		print('   '+str(counter)+' Good')
	except:
		print('   Getting '+str(counter))
		path=folder+'\\RawData\\Acq'+str(counter)+'.tdms'
		tdmsFile=TdmsFile(path,memmap_dir=folder+'\\RawData\\Temp')
		spec=fftAnalysis(counter,path, fs, chirp_duration, lowerFreq, upperFreq, freqApplied, tdmsFile, chirpmap)
		storeFFT(counter,spec,fftFileName)