import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty, StringProperty

## Can import from kivy file

kivy.require('1.10.0')

import ProtocolController
sendPort = 4020
recievePort = 4021

#Handlers
def sendPortInputHandler(instance, value):
	try:
		global sendPort
		sendPort = int(value)
	except:
		pass
def recievePortInputHandler(instance, value):
	try:
		global recievePort
		recievePort = int(value)
	except:
		pass

def connectButtonHandler(instance):
	ProtocolController.listen(recievePort)
	ProtocolController.connectToLabView(sendPort)


def updateParametersButtonHandler(args):
	print(args)


guiString = """
<ConnectScreen>:
	BoxLayout:
		orientation: 'vertical'
		Label:
			text: 'Band Excitation Mediator V0.2'
		BoxLayout:
			orientation: 'horizontal'
			Label:
				text: 'Send Port'
			TextInput:
				text: '4020'
		BoxLayout:
			orientation: 'horizontal'
			Label:
				text: 'Recieve Port'
			TextInput:
				text: '4021'
		Button
			text: 'Connect'
			on_press:
				root.manager.transition.direction = 'left'
				root.manager.current = 'parameterScreen'
<ParameterScreen>:
	chirpAmplitude: chirpAmplitude
	inputVoltage: inputVoltage
	upperFrequency: upperFrequency
	lowerFrequency: lowerFrequency
	sampleRate: sampleRate
	chirpDuration: chirpDuration
	chirpWindowing: chirpWindowing
	signalType: signalType
	numberOfAcquisitions: numberOfAcquisitions

	BoxLayout:
		orientation: 'vertical'
		Label:
			text: 'Parameters'
		BoxLayout:
			Label:
				text: 'Chirp Amplitude'
			TextInput:
				id: chirpAmplitude
		BoxLayout:
			Label:
				text: 'Input Voltage'
			TextInput:
				id: inputVoltage
		BoxLayout:
			Label:
				text: 'Upper Frequency'
			TextInput:
				id: upperFrequency
		BoxLayout:
			Label:
				text: 'Lower Frequency'
			TextInput:
				id: lowerFrequency
		BoxLayout:
			Label:
				text: 'Sample Rate'
			TextInput:
				id: sampleRate
		BoxLayout:
			Label:
				text: 'Chirp Duration'
			TextInput:
				id: chirpDuration
		BoxLayout:
			Label:
				text: 'Chirp Windowing'
			TextInput:
				id: chirpWindowing
		BoxLayout:
			Label:
				text: 'Signal Type'
			TextInput:
				id: signalType
		BoxLayout:
			Label:
				text: 'Number of Acquisitions'
			TextInput:
				id: numberOfAcquisitions
		Button:
			text: 'Update Parameters'
			on_press: root.updateParams([chirpAmplitude, inputVoltage, upperFrequency, lowerFrequency, sampleRate, chirpDuration, chirpWindowing, signalType, numberOfAcquisitions])
"""

Builder.load_string(guiString)

class ConnectScreen(Screen):
	pass

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


	def updateParams(self, textFields):
		for field in textFields:
			field.text = ''



sm = ScreenManager()
sm.add_widget(ConnectScreen(name='connectScreen'))
sm.add_widget(ParameterScreen(name='parameterScreen'))


	
class MediatorApp(App):

	def build(self):

		# # GUI setup
		# rootLayout = BoxLayout(orientation='vertical')

		# titleText = Label(text='Band Excitation Mediator V0.2')
		# rootLayout.add_widget(titleText)

		# sendLayout = BoxLayout(orientation='horizontal')
		# rootLayout.add_widget(sendLayout)

		# sendPortInputLabel = Label(text="Send Port")
		# sendLayout.add_widget(sendPortInputLabel)

		# sendPortInput = TextInput(text='4020')
		# sendPortInput.bind(text=sendPortInputHandler)
		# sendLayout.add_widget(sendPortInput)

		# recieveLayout = BoxLayout(orientation='horizontal')
		# rootLayout.add_widget(recieveLayout)

		# recievePortInputLabel = Label(text="Recieve Port")
		# recieveLayout.add_widget(recievePortInputLabel)

		# recievePortInput = TextInput(text='4021')
		# recievePortInput.bind(text=recievePortInputHandler)
		# recieveLayout.add_widget(recievePortInput)
		
		# connectButton = Button(text='Connect')
		# connectButton.bind(on_press=connectButtonHandler)
		# rootLayout.add_widget(connectButton)

		return sm

if __name__ == '__main__':
    MediatorApp().run()