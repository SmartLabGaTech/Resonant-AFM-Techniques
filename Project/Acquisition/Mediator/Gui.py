import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.clock import Clock
import signal
import sys
import ProtocolController
import GuiViews
import globalVariables as Global
import analysisController
import os
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt
#matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')


from kivy.uix.boxlayout import BoxLayout
from kivy.garden.matplotlib import FigureCanvasKivyAgg

kivy.require('1.10.0')

#Define the signal so a control-c cleans up the connection
def signal_handler(signal, frame):
        print("Got termination signal, attempting to exit cleanly")
        try:
        	ProtocolController.sendDisconnectMessage()
        except:
        	pass
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

#Constants
sendPort = 4020
recievePort = 4021

#Import and use kivy definition string
guiString = GuiViews.getGuiString()
Builder.load_string(guiString)

class ConnectScreen(Screen):
	receivePort = ObjectProperty(None)
	sendPort = ObjectProperty(None)

	def connect(self, sendPort, receivePort):
		popup = Popup(title="Connecting", content=Label(text='Connecting...'), auto_dismiss=False)
		popup.open()

		if(ProtocolController.runProtocol(int(sendPort.text), int(receivePort.text))):
			popup.dismiss()
		else:
			popup.dismiss()
			#TODO: handle error messages
		return
class ParameterScreen(Screen):

	chirpAmplitude = ObjectProperty(None)
	inputVoltage = ObjectProperty(None)
	upperFrequency = ObjectProperty(None)
	lowerFrequency = ObjectProperty(None)
	sampleRate = ObjectProperty(None)
	chirpDuration = ObjectProperty(None)
	chirpWindowing = ObjectProperty(None)
	signalType = ObjectProperty(None)
	numberOfAcquisitions = ObjectProperty(None)
	waveformSpecificationFile = ObjectProperty(None)
	saveLocation = ObjectProperty(None)

	def updateParams(self):
		if(len(self.chirpAmplitude.text) > 0):
			ProtocolController.sendSetParamMessage("chirpAmplitude", self.chirpAmplitude.text)
			Global.AMPLITUDE=float(self.chirpAmplitude.text)
			
		if(len(self.inputVoltage.text) > 0):
			ProtocolController.sendSetParamMessage("inputVoltage", self.inputVoltage.text)
			Global.VOLT_LIMIT=float(self.inputVoltage.text)
			
		if(len(self.upperFrequency.text) > 0):
			ProtocolController.sendSetParamMessage("upperFrequency", self.upperFrequency.text)
			Global.UPPER_FREQ=float(self.upperFrequency.text)
			
		if(len(self.lowerFrequency.text) > 0):
			ProtocolController.sendSetParamMessage("lowerFrequency", self.lowerFrequency.text)
			Global.LOWER_FREQ=float(self.lowerFrequency.text)
			
		if(len(self.sampleRate.text) > 0):
			ProtocolController.sendSetParamMessage("sampleRate", self.sampleRate.text)
			Global.SAMPLE_RATE=float(self.sampleRate.text)

		if(len(self.chirpDuration.text) > 0):
			ProtocolController.sendSetParamMessage("chirpDuration", self.chirpDuration.text)
			Global.CHIRP_DURATION=float(self.chirpDuration.text)
			
		if(len(self.chirpWindowing.text) > 0):
			ProtocolController.sendSetParamMessage("chirpWindowing", self.chirpWindowing.text)
			Global.CHIRP_WINDOW=int(self.chirpWindowing.text)
			
		if(len(self.signalType.text) > 0):
			ProtocolController.sendSetParamMessage("signalType", self.signalType.text)
			Global.SIGNAL_TYPE=float(self.signalType.text)

		if(len(self.numberOfAcquisitions.text) > 0):
			ProtocolController.sendSetParamMessage("numberOfAcquisitions", self.numberOfAcquisitions.text)
			Global.TOTAL_NUM_ACQS=float(self.numberOfAcquisitions.text)
			
		if(len(self.waveformSpecificationFile.text) > 0):
			ProtocolController.sendSetParamMessage("waveformSpecificationFile", self.waveformSpecificationFile.text)
			Global.WAVEFORM_FILE_PATH=self.waveformSpecificationFile.text
			
		if(len(self.saveLocation.text) > 0):
			temp=self.saveLocation.text
			lastBackSlash=temp.rfind('\\')
			Global.SAVE_FOLDER=self.saveLocation.text[:lastBackSlash+1]
			Global.SAVE_NAME=self.saveLocation.text[(lastBackSlash+1):]
			ProtocolController.sendSetParamMessage("saveLocation", Global.SAVE_FOLDER)
			
			

			
	def startExperiment(self):
		if not os.path.exists(Global.SAVE_FOLDER):
			os.makedirs(Global.SAVE_FOLDER)
		if not os.path.exists(Global.SAVE_FOLDER+'RawData\\'):
			os.makedirs(Global.SAVE_FOLDER+'RawData\\')
		ProtocolController.sendStartExperimentMessage()
		analysisController.generateSupplementaryInfo()
		analysisController.startPathMonitor()
		analysisController.startStoreProcess()

		
		#Initalize plot data
		#Global.PLOT_AMP=np.full((TOTAL_NUM_ACQS),np.inf)
		#Global.PLOT_PHASE=np.full((TOTAL_NUM_ACQS),np.inf)
		#Global.PLOT_Q=np.full((TOTAL_NUM_ACQS),np.inf)
		#Global.PLOT_RES=np.full((TOTAL_NUM_ACQS),np.inf)

fig, ax = plt.subplots()
plot_canvas=FigureCanvasKivyAgg(fig)
	
class PlotBox(BoxLayout):

	def plot(self, dt):
		ax.plot([1,2,3,4],[5,5,5,6])
		plot_canvas.draw()
		
	def update(self):
		Clock.schedule_interval(self.plot,1)
	
class PlotScreen(Screen):
	
	def __init__(self,**kwargs):
		self.build()
		super(Screen,self).__init__(**kwargs)
	
	def build(self):
		res=PlotBox()
		res.add_widget(plot_canvas)
		res.update()
		return res
		
#Define the screens
sm = ScreenManager()
sm.add_widget(ConnectScreen(name='connectScreen'))
sm.add_widget(ParameterScreen(name='parameterScreen'))
sm.add_widget(PlotScreen(name='plotScreen'))

class MediatorApp(App):

	def build(self):
		return sm

	def on_stop(self):
		ProtocolController.sendDisconnectMessage()


if __name__ == '__main__':
    MediatorApp().run()