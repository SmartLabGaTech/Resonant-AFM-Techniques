import kivy
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

kivy.require('1.10.0')

from kivy.app import App
from kivy.uix.label import Label

class MyApp(App):

	def build(self):
		layout = BoxLayout(orientation='vertical')
		btn1 = Button(text='Hello')
		btn2 = Button(text='World')
		layout.add_widget(btn1)
		layout.add_widget(btn2)

		return layout

if __name__ == '__main__':
    MyApp().run()