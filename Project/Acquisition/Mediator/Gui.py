import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.app import App

import ProtocolController

sendPort = 4020
recievePort = 4021

kivy.require('1.10.0')

class MyApp(App):

	def build(self):

		# GUI setup
		rootLayout = BoxLayout(orientation='vertical')

		titleText = Label(text='Band Excitation Mediator V0.2')
		rootLayout.add_widget(titleText)

		sendLayout = BoxLayout(orientation='horizontal')
		rootLayout.add_widget(sendLayout)

		sendPortInputLabel = Label(text="Send Port")
		sendLayout.add_widget(sendPortInputLabel)

		sendPortInput = TextInput(text='4020')
		sendPortInput.bind(text=sendPortInputHandler)
		sendLayout.add_widget(sendPortInput)

		recieveLayout = BoxLayout(orientation='horizontal')
		rootLayout.add_widget(recieveLayout)

		recievePortInputLabel = Label(text="Recieve Port")
		recieveLayout.add_widget(recievePortInputLabel)

		recievePortInput = TextInput(text='4021')
		recievePortInput.bind(text=recievePortInputHandler)
		recieveLayout.add_widget(recievePortInput)
		
		connectButton = Button(text='Connect')
		connectButton.bind(on_press=connectButtonHandler)
		rootLayout.add_widget(connectButton)

		return rootLayout

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

if __name__ == '__main__':
    MyApp().run()