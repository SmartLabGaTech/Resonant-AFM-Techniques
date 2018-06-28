## Written by Lee Griffin
## 

from multiprocessing import Process, Queue
import numpy as np                #for numerical operations
import pandas as pd               #for data reading/structure
from nptdms import TdmsFile		  #For reading LabView files
from analysis import fftAnalysis, quickFFT, getSHOguess, storeFFT, generateChirpMap
import globalVariables as Global
import scipy.signal as signal
import time
import traceback

fftQ=Queue()
acqQ=Queue()		
			
def startPathMonitor():
	fileMonitor0=Process(target=updateData, args=(0,Global.SAVE_FOLDER,Global.SAMPLE_RATE, Global.CHIRP_DURATION, Global.LOWER_FREQ, Global.UPPER_FREQ, Global.APP_FFT, Global.CHIRP_MAP,fftQ, acqQ))
	fileMonitor0.daemon=True
	fileMonitor0.start()
	
	fileMonitor1=Process(target=updateData, args=(1,Global.SAVE_FOLDER,Global.SAMPLE_RATE, Global.CHIRP_DURATION, Global.LOWER_FREQ, Global.UPPER_FREQ, Global.APP_FFT,  Global.CHIRP_MAP,fftQ, acqQ))
	fileMonitor1.daemon=True
	fileMonitor1.start()
	
	fileMonitor2=Process(target=updateData, args=(2,Global.SAVE_FOLDER,Global.SAMPLE_RATE, Global.CHIRP_DURATION, Global.LOWER_FREQ, Global.UPPER_FREQ, Global.APP_FFT,  Global.CHIRP_MAP,fftQ, acqQ))
	fileMonitor2.daemon=True
	fileMonitor2.start()
	
	fileMonitor3=Process(target=updateData, args=(3,Global.SAVE_FOLDER,Global.SAMPLE_RATE, Global.CHIRP_DURATION, Global.LOWER_FREQ, Global.UPPER_FREQ, Global.APP_FFT,  Global.CHIRP_MAP,fftQ, acqQ))
	fileMonitor3.daemon=True
	fileMonitor3.start()


def updateData(fileNum, folder, fs, chirp_duration, lowerFreq, upperFreq, applied, chirpMap,  fftQ, acqQ):
	
	print('Process '+str(fileNum)+': Starting')

	while True:
		counter=Global.THREAD_COUNTERS[fileNum]*4+fileNum
		path=folder+'RawData\\Acq'+str(counter)+'.tdms'
		
		try:
			tdmsFile=TdmsFile(path)
			try:
				#Perform FFT and store it
				spec=fftAnalysis(counter,path, fs, chirp_duration, lowerFreq, upperFreq, applied, tdmsFile, chirpMap)
				fftQ.put(spec)
				acqQ.put(counter)
				print('Process '+str(fileNum)+': Acq '+str(counter)+' FFT Complete')
				Global.THREAD_COUNTERS[fileNum]=Global.THREAD_COUNTERS[fileNum]+1
			except Exception as e:
				tb=traceback.format_exc()
			finally:
				pass
				#print(tb)
		except Exception as e:
			time.sleep(.1)

def startStoreProcess():
	storeProcess = Process(target=storeAnalysisProcessFunc, args=(Global.SAVE_FOLDER,Global.SAVE_NAME, fftQ, acqQ))
	storeProcess.daemon=True
	storeProcess.start()
		
def storeAnalysisProcessFunc(folder,name, fftQ, acqQ):	
	while True:
		try:
			data=fftQ.get()
			acqNum=acqQ.get()
		except Queue.Empty:
			pass
		else:
			storeFFT(acqNum,data,folder+name+'.h5')
			print('   Acq '+str(acqNum)+' Stored')

		
def storeNewData(spec):
	dataShape=spec.shape
	numRows=dataShape[0]
	a,phi,res,Q=getSHOguess(spec[1,:], freq)
	
	
def generateSupplementaryInfo():
	
	#Generate the applied chirp for Info
	#
	#Time axis
	t=np.arange(0,Global.CHIRP_DURATION,1/Global.SAMPLE_RATE)
	
	#Applied Chirp in the time domain
	app_chirp=signal.chirp(t,Global.LOWER_FREQ*0.985,Global.CHIRP_DURATION,Global.UPPER_FREQ*1.015)
	
	#Window
	window=signal.tukey(len(app_chirp),alpha=0.2)
	
	#Apply the window
	app_chirp=np.multiply(window,app_chirp)
	
	#Convert to the freq domain
	freq,freqApplied=quickFFT(app_chirp,Global.SAMPLE_RATE)
	
	#Store the info in the global data
	Global.APP_FREQS=freq
	Global.APP_FFT=freqApplied
	
	#Generate the chirp map
	chirpmap=generateChirpMap(Global.WAVEFORM_FILE_PATH)
	Global.CHIRP_MAP=chirpmap
	
	#Save the general chirp info
	parameters=pd.Series([Global.AMPLITUDE,Global.VOLT_LIMIT,Global.UPPER_FREQ,Global.LOWER_FREQ,Global.SAMPLE_RATE,Global.CHIRP_DURATION,Global.CHIRP_WINDOW,Global.TOTAL_NUM_ACQS,Global.WAVEFORM_FILE_PATH],index=['Amp','Volt Lim','Upper Freq','Lower Freq','Sample Rate','Chirp Duration','Window Type','Num Acqusitions','WaveSpec Path'])
	parameters.to_csv(Global.SAVE_FOLDER+'parameters.csv')
	
	chirpmap.to_csv(Global.SAVE_FOLDER+'ChirpMap.csv')
	np.savetxt(Global.SAVE_FOLDER+'AppliedChirp.csv',app_chirp)
	np.savetxt(Global.SAVE_FOLDER+'FreqRange.csv',freq)
	np.savetxt(Global.SAVE_FOLDER+'AppChirpFFT.csv',freqApplied)
	
	Global.ERROR_FILE=Global.SAVE_FOLDER+'ERRORLOG.txt'