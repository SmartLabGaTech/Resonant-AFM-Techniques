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
import signal
import sys
import ProtocolController
import GuiViews
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

	def updateParams(self):
		if(len(self.chirpAmplitude.text) > 0):
			ProtocolController.sendSetParamMessage("chirpAmplitude", self.chirpAmplitude.text)

		if(len(self.inputVoltage.text) > 0):
			ProtocolController.sendSetParamMessage("inputVoltage", self.inputVoltage.text)

		if(len(self.upperFrequency.text) > 0):
			ProtocolController.sendSetParamMessage("upperFrequency", self.upperFrequency.text)

		if(len(self.lowerFrequency.text) > 0):
			ProtocolController.sendSetParamMessage("lowerFrequency", self.lowerFrequency.text)

		if(len(self.sampleRate.text) > 0):
			ProtocolController.sendSetParamMessage("sampleRate", self.sampleRate.text)

		if(len(self.chirpDuration.text) > 0):
			ProtocolController.sendSetParamMessage("chirpDuration", self.chirpDuration.text)

		if(len(self.chirpWindowing.text) > 0):
			ProtocolController.sendSetParamMessage("chirpWindowing", self.chirpWindowing.text)

		if(len(self.signalType.text) > 0):
			ProtocolController.sendSetParamMessage("signalType", self.signalType.text)

		if(len(self.numberOfAcquisitions.text) > 0):
			ProtocolController.sendSetParamMessage("numberOfAcquisitions", self.numberOfAcquisitions.text)

		if(len(self.waveformSpecificationFile.text) > 0):
			ProtocolController.sendSetParamMessage("waveformSpecificationFile", self.waveformSpecificationFile.text)

	def startExperiment(self):
		ProtocolController.sendStartExperimentMessage()

#Define the screens
sm = ScreenManager()
sm.add_widget(ConnectScreen(name='connectScreen'))
sm.add_widget(ParameterScreen(name='parameterScreen'))

class MediatorApp(App):

	def build(self):
		return sm

	def on_stop(self):
		ProtocolController.sendDisconnectMessage()

if __name__ == '__main__':
    MediatorApp().run()