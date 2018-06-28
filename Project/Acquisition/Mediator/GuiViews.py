_guiString = """
<ConnectScreen>:
	receivePort: receivePort
	sendPort: sendPort
	BoxLayout:
		orientation: 'vertical'
		Label:
			text: 'Band Excitation Mediator V0.2'
		BoxLayout:
			orientation: 'horizontal'
			Label:
				text: 'Send Port'
			TextInput:
				id: sendPort
				text: '4020'
		BoxLayout:
			orientation: 'horizontal'
			Label:
				text: 'Receive Port'
			TextInput:
				id: receivePort
				text: '4021'
		Button
			text: 'Connect'
			on_press:
				root.connect(sendPort, receivePort)
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
	waveformSpecificationFile: waveformSpecificationFile
	saveLocation: saveLocation

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
		BoxLayout:
			Label:
				text: 'Waveform Specification File'
			TextInput:
				id: waveformSpecificationFile
		BoxLayout:
			Label:
				text: 'Save Location'
			TextInput:
				id: saveLocation
		Button:
			text: 'Update Parameters'
			on_press: root.updateParams()
		Button:
			text: 'Start Experiment'
			on_press: 
				root.startExperiment()
				root.manager.transition.direction = 'right'
				root.manager.current = 'plotScreen'
		Button:
			text: 'Back To Connection'
			on_press:
				root.manager.transition.direction = 'right'
				root.manager.current = 'connectScreen'
<PlotScreen>:
	
	BoxLayout:
		orientation: 'vertical'

		PlotBox:
			id: plot
			orientation: 'vertical'
		
		BoxLayout:
			orientation: 'vertical'
			Button
				text: 'Back to Parameters'
				on_press:
					root.manager.transition.direction = 'left'
					root.manager.current = 'parameterScreen'
"""


def getGuiString():
	return _guiString