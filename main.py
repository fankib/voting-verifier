import sys
import os
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout

is_linux = sys.platform == 'linux'
is_android = sys.platform == 'linux4'

if is_android:
	from plyer import vibrator
	from jnius import cast
	from jnius import autoclass
	import android
	import android.activity

if is_linux:
	os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-8-openjdk/'

class TutorialApp(App):
	txtInput = TextInput(text='', hint_text='Verification code', padding=23, font_size=20)
	lblResult = Label(text='')
	def build(self):
		# initialize components
		lblInput = Label(text='Verifikation:', size_hint_x=None, width=260)
		btnVerify = Button(text='verify', size_hint_x=None, width=260, on_press=self.verify)
		
		# initialize containers		
		# Head row:
		boxHead = BoxLayout(size_hint_y=None, height=120)
		#boxHead.add_widget(lblInput)
		boxHead.add_widget(self.txtInput)
		boxHead.add_widget(btnVerify)
		# Main Box
		box = BoxLayout(orientation='vertical')
		box.add_widget(boxHead)
		#s = Scatter(do_rotation=False, do_scale=False, do_translation_x=False)
		#s.add_widget(self.lblResult)
		f = FloatLayout()
		f.add_widget(self.lblResult)
		box.add_widget(f)
		return box
	
	def verify(self, event):
		if is_android:			
			vibrator.vibrate(0.1)
		word = 'o:' + self.txtInput.text
		self.lblResult.text += '\n' + word[0:20]

if __name__ == '__main__':
	qrcode = '' #sys.platform + ' - ' + os.name
	
	if is_android:
		# test for an intent passed to us
		PythonActivity = autoclass('org.renpy.android.PythonActivity')
		activity = PythonActivity.mActivity
		#print(activity)
		intent = activity.getIntent()
		print(intent)
		if not intent is None:
			extras = intent.getExtras()
			print(extras)
			strExtra = intent.getStringExtra('android.intent.extra.TEXT')
			print(strExtra)
			if not strExtra is None:
				qrcode = strExtra
		
	app = TutorialApp()
	app.txtInput.text = qrcode
	app.run()
