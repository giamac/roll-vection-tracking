#!/usr/bin/env python

"""
This script shows moving cirecles made of dots and measures the
participants' sway
"""

import viz, viztask, vizact, vizinput, vizshape
import math
import random
import oculus
import time
import datetime
from datetime import date
from string import maketrans
import itertools, csv, time

#Ask for mode
presentations = ['oculus','normal']
presentationMode = vizinput.choose('Presentation Mode', presentations)

#Prompt for the participant's demographic
def participantInfo():

	subject = vizinput.input('What is the participant number?')
	age = vizinput.input('age?')
	sex = ['male','female']
	sex_choice = vizinput.choose('Sex',sex)
	handedness = ['right','left','both']
	handedness_choice = vizinput.choose('Handedness',handedness)
	ts = time.time()

	##create demographic data file
	demographic_data = open('demographic_data_rod_frame.csv','w')
	with open('data/demographic_data_rod_frame.csv', 'a') as f:
		wr = csv.writer(f, delimiter=';', lineterminator='\n', quoting=csv.QUOTE_ALL)
		row_demo = [subject, age, sex[sex_choice] ,handedness[handedness_choice] , datetime.datetime.fromtimestamp(ts).strftime('%Y-%d-%m %H:%M:%S')]
		wr.writerow(row_demo)

#-----------------------------------------------------

# Set the viewpoint

if presentations[presentationMode] == 'oculus':
	hmd = oculus.Rift()
	if not hmd.getSensor():
		sys.exit('Oculus Rift not detected')
else:
	pass

viz.setMultiSample(8)
viz.go()

viz.fov(90)

def trial():

	position = []

	def createFrame(direction):

		viz.startLayer(viz.LINES)
		viz.vertex(-.2,1.6,1)
		viz.vertex(-.2,2,1)

		viz.vertex(.2,1.6,1)
		viz.vertex(.2,2,1)

		viz.vertex(-.2,1.6,1)
		viz.vertex(.2,1.6,1)

		viz.vertex(-.2,2,1)
		viz.vertex(.2,2,1)

		poly = viz.endLayer()

		poly.center(0,1.8,1)
		if direction == 'left':
			poly.setEuler([0,0,20])
		elif direction == 'right':
			poly.setEuler([0,0,-20])


	def createRod():
		viz.startLayer(viz.POINTS)
		viz.pointSize(4)
		viz.vertex(0,1.65,1)
		viz.vertex(0,1.70,1)
		viz.vertex(0,1.75,1)
		viz.vertex(0,1.80,1)
		viz.vertex(0,1.85,1)
		viz.vertex(0,1.90,1)
		viz.vertex(0,1.95,1)
		line = viz.endLayer()

		line.center(0,1.8,1)
		initLinePos = 0 + 20 * random.uniform(-1,1)
		line.setEuler([0,0,initLinePos])
		class LineRotation(viz.EventClass):
			def __init__(self):
				viz.EventClass.__init__(self)

				self.callback(viz.KEYDOWN_EVENT, self.keyboardAction)

			def keyboardAction(self,key):
				currentPosition = line.getEuler()
				currentRoll = currentPosition[2]
				if viz.key.isDown(viz.KEY_LEFT):
					line.setEuler([0,0,currentRoll + 1])
				elif viz.key.isDown(viz.KEY_RIGHT):
					line.setEuler([0,0,currentRoll -1])
		return position
		LineRotation()

	createFrame('right')
	createRod()

trial()
