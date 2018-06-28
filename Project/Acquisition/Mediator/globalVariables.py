## Written by Lee Griffin
## Global variables for the GUI

import numpy as np
import pandas as pd

#Count of how many acquisitions have been completed
THREAD_COUNTERS=[0,0,0,0,0]


AMPLITUDE=0				#Chirp amplitude
VOLT_LIMIT=0			#Upper voltage magnitude limit
UPPER_FREQ=0			#Upper frequency (in Hz) of the band
LOWER_FREQ=0			#Lower frequency (in Hz) of the band
SAMPLE_RATE=0			#Sample rate of the signal generation/acquisition
CHIRP_DURATION=0		#Length (in seconds) of a single chirp
CHIRP_WINDOW=1			#Just leave this one
SIGNAL_TYPE=1			#Ditto
TOTAL_NUM_ACQS=0		#Total number of acquisitions to be completed
WAVEFORM_FILE_PATH='t'	#Path pointing to the waveform specification file

CHIRP_MAP=[]

APP_FREQS=[]			#Array of the applied frequencies
APP_FFT=[]				#Frequency domain of the applied signal

SAVE_FOLDER='t'			#Folder where everything is saved
SAVE_NAME='t'			#Name used

ERROR_FILE='t'

PLOT_AMP=np.matrix('1 2; 3 4')
PLOT_PHASE=0
PLOT_Q=0
PLOT_RES=0
