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

#start vrpn
## Is this need here?
vrpn = viz.addExtension('vrpn7.dle')

#Ask for mode
presentations = ['oculus','normal']
presentationMode = vizinput.choose('Presentation Mode', presentations)

#Prompt for the participant's demographic

subject = vizinput.input('What is the participant number?')
age = vizinput.input('age?')
sex = ['male','female']
sex_choice = vizinput.choose('Sex',sex)
handedness = ['right','left','both']
handedness_choice = vizinput.choose('Handedness',handedness)
run = vizinput.input('Which run?')
ts = time.time()

##create demographic data file
demographic_data = open('demographic_data.csv','w')
with open('data/demographic_data.csv', 'a') as f:
	wr = csv.writer(f, delimiter=';', lineterminator='\n', quoting=csv.QUOTE_ALL)
	row_demo = [subject, age, sex[sex_choice] ,handedness[handedness_choice] , run , datetime.datetime.fromtimestamp(ts).strftime('%Y-%d-%m %H:%M:%S')]
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
viz.go(viz.FULLSCREEN)

viz.fov(90)

HEAD = 0
NECK = 1
#TORSO = 2
WAIST = 3
LEFTCOLLOR = 4
LEFTSHOULDER = 5
LEFTELBOW = 6
LEFTWRIST = 7
LEFTHAND = 8
LEFTFINGERTIP = 9
RIGHTCOLLAR = 10
RIGHTSHOULDER = 11
RIGHTELBOW = 12
RIGHTWRIST = 13
RIGHTHAND = 14
RIGHTFINGERTIP = 15
LEFTHIP = 16
LEFTKNEE = 17
LEFTANGLE = 18
LEFTFOOT = 19
RIGHTHIP = 20
RIGHTKNEE = 21
RIGHTANKLE = 22
RIGHTFOOT = 23

#start vrpn
vrpn = viz.addExtension('vrpn7.dle')

#store trackers, links, and vizshape objects
trackers = []
links = []
shapes = []
tracker_coordinates = []

#now add all trackers and link a shape to it
for i in range(0, 24):
	t = vrpn.addTracker('Tracker0@localhost',i)
	s = vizshape.addSphere(radius=0.01)
	s.color(viz.GREEN)
	s.visible(viz.OFF)
	l = viz.link(t,s)
	pos = t.getPosition()
	trackers.append(t)
	print()


'''EDIT: all segments (proximal, distal) with each x, y, z coodrinates as headers

['Head-Neck', self.HEAD, self.SHOULDER_CENTER], ['Trunk', self.SHOULDER_CENTER, self.HIP_CENTER], ['UpperArm_Left', self.SHOULDER_LEFT, self.ELBOW_LEFT], ['UpperArm_Right', self.SHOULDER_RIGHT, self.ELBOW_RIGHT],
						['Forearm_Left', self.ELBOW_LEFT, self.WRIST_LEFT], ['Forearm_Right', self.ELBOW_RIGHT, self.WRIST_RIGHT],
						['Hand_Left', self.WRIST_LEFT, self.HAND_LEFT], ['Hand_Right', self.WRIST_RIGHT, self.HAND_RIGHT],
						['Pelvis', self.HIP_CENTER,self.HIP_MIDPOINT], ['Thigh_Left', self.HIP_LEFT, self.KNEE_LEFT], ['Thigh_Right', self.HIP_RIGHT, self.KNEE_RIGHT],
						['Leg_Left', self.KNEE_LEFT, self.ANKLE_LEFT], ['Leg_Right', self.KNEE_RIGHT, self.ANKLE_RIGHT], ['Foot_Left', self.ANKLE_LEFT, self.FOOT_LEFT],
						['Foot_Right', self.ANKLE_RIGHT, self.FOOT_RIGHT] + str(time.strftime("%A, %d %B %Y %H:%M:%S"  )
'''

### Carefully consider what to write into the header
#with open(file, 'a') as f:
#	writer = csv.DictWriter(f, fieldnames = ['Subject ID', 'Age', 'Sex', 'Stimulus_Name', 'Stimulus_Ori_Yaw', 'Stimulus_Ori_Roll', 'Trial_State',
#	'Global_Time', 'Frame_No.','Frame_Elapsed', 'Frame_Time'], delimiter = ';')
#	writer.writeheader()

class RollVection():

	def __init__(self):
		#ROLL VECTION DATA
		##ONLY KEY PRESS AND TIME?
		self.RV_DATA = []
		#Tracking Data?
		self.COM_DATA = []
		#Tracking data?
		self.TCBOM = []
		#Size of the dots in the circles
		self.POINTSIZE = 22
		#Duration of a run is 30 seconds
		self.DURATION = 30
		#--- Other VARIABLES MIT WHILE SCHLAUFE?
		self.response = None
		self.current_State = None
		self.keyPressTime = None;
		self.STATE = None
		# Opens file 'response.txt' in write mode
	# Create a function for the circles

	def createCircles(self,NUM_DOTS,RADIUS,POINTSIZE,VELOCITYDIRECTION):

			#Build sphere
		viz.startLayer(viz.POINTS)
		viz.vertexColor(viz.WHITE)
		viz.pointSize(self.POINTSIZE)

		for i in range(0, NUM_DOTS):
			x = RADIUS*math.cos((i*2*math.pi)/NUM_DOTS)
			y = RADIUS*math.sin((i*2*math.pi)/NUM_DOTS)
			viz.vertex([x,y,0])

		sphere = viz.endLayer()
		sphere.setPosition([0,1.8,4])
		sphere.addAction(vizact.spin(0,0,1,VELOCITYDIRECTION))
		return sphere

	# Define the Block

	def BlockProcedure(self):
		yield viztask.waitKeyDown(' ')
		yield self.experimentProcedure()
		with open('data/subject' + subject + '_run_jj' + run + '.csv', 'a') as f:
			wr = csv.writer(f, delimiter=';', lineterminator='\n', quoting=csv.QUOTE_ALL)

			import itertools
			flattened = flattened = [[item for sublist in list for item in sublist] for list in self.COM_DATA]

			#[framelist for segment in self.COM_DATA for segment in framelist in self.COM_DATA]

			print(flattened)

			for rv_data, coord_data, tcbom in zip(self.RV_DATA, flattened, self.TCBOM):

				row = rv_data + coord_data + tcbom

				wr.writerow(row)

			print(self.RV_DATA)
			print(self.COM_DATA)

		# Define the Procedure of the experiment
	def experimentProcedure(self):
		self.response = None
		self.STARTTIME = viz.tick()
		self.STATE = 'Start Vection'
				#Define the Vection
		def motion():
					# Create Fixation Dot
					viz.startLayer(viz.POINTS)
					viz.pointSize(self.POINTSIZE)
					viz.vertexColor(viz.GRAY)
					viz.vertex(0,1.8,4)
					points = viz.endLayer()
					points.disable(viz.CULLING)
					# Create the circles
					sphere = self.createCircles(26,1,30,-26)
					sphere2 = self.createCircles(22,0.8,30,-26)
					sphere3 = self.createCircles(18,0.6,30,-26)
					sphere4 = self.createCircles(14,0.4,30,-26)
					sphere5 = self.createCircles(10,0.2,30,-26)
					viz.MainView.move([0,0,3])
					def keydown( key ):

						if 	key == 'f':
							self.response = 'self motion'
							self.keyPressTime = viz.tick() # get time for keypress
							print(self.response, self.keyPressTime)
							self.STATE = 'State - self Motion'

						if key == 'j':
							self.response = 'object motion'
							self.keyPressTime = viz.tick() # get time for keypress
							print(self.response, self.keyPressTime)
							self.STATE = 'State - Object Motion'
					viz.callback(viz.KEYDOWN_EVENT, keydown)


		# A function to record thfe responses
		yield motion()
		
		yield viztask.waitTime(10)
		viz.quit()

				#go to the experiment


class CenterOfMass(viz.EventClass):

	def __init__(self):

		# initialize base class
		viz.EventClass.__init__(self)
		#self.total_M = viz.input('Please enter total body mass [kg]')

		self.exp = RollVection()
		viztask.schedule(self.exp.BlockProcedure)

		self.TEMP_RV_DATA = []
		self.TEMP_COM_DATA = []
		self.TEMP_TCBOM = []

		self.exp.COM_DATA = self.TEMP_COM_DATA
		self.exp.RV_DATA = self.TEMP_RV_DATA
		self.exp.TCBOM = self.TEMP_TCBOM

		# body segments
		self.HEAD = vrpn.addTracker('Tracker0@localhost', 0)
		self.SHOULDER_CENTER = vrpn.addTracker('Tracker0@localhost', 1)
		self.HIP_CENTER = vrpn.addTracker('Tracker0@localhost', 3)

		self.SHOULDER_LEFT = vrpn.addTracker('Tracker0@localhost', 5)
		self.ELBOW_LEFT = vrpn.addTracker('Tracker0@localhost', 6)
		self.WRIST_LEFT = vrpn.addTracker('Tracker0@localhost', 7)
		self.HAND_LEFT = vrpn.addTracker('Tracker0@localhost', 8)

		self.SHOULDER_RIGHT = vrpn.addTracker('Tracker0@localhost', 11)
		self.ELBOW_RIGHT = vrpn.addTracker('Tracker0@localhost', 12)
		self.WRIST_RIGHT = vrpn.addTracker('Tracker0@localhost', 13)
		self.HAND_RIGHT = vrpn.addTracker('Tracker0@localhost', 14)

		self.HIP_LEFT = vrpn.addTracker('Tracker0@localhost', 16)
		self.KNEE_LEFT = vrpn.addTracker('Tracker0@localhost', 17)
		self.ANKLE_LEFT = vrpn.addTracker('Tracker0@localhost', 18)
		self.FOOT_LEFT = vrpn.addTracker('Tracker0@localhost', 19)

		self.HIP_RIGHT = vrpn.addTracker('Tracker0@localhost', 20)
		self.KNEE_RIGHT= vrpn.addTracker('Tracker0@localhost', 21)
		self.ANKLE_RIGHT = vrpn.addTracker('Tracker0@localhost', 22)
		self.FOOT_RIGHT = vrpn.addTracker('Tracker0@localhost', 23)

		# calculate midpoint between left and right hip
		#self.HIP_MIDPOINT = vrpn.addTracker('Tracker0@localhost', 2)
		self.HIP_MIDPOINT = None


		# list of body segments for 15-segment body model
		self.body_segments = [['Head-Neck', self.HEAD, self.SHOULDER_CENTER], ['Trunk', self.SHOULDER_CENTER, self.HIP_CENTER],
						['UpperArm_Left', self.SHOULDER_LEFT, self.ELBOW_LEFT], ['UpperArm_Right', self.SHOULDER_RIGHT, self.ELBOW_RIGHT],
						['Forearm_Left', self.ELBOW_LEFT, self.WRIST_LEFT], ['Forearm_Right', self.ELBOW_RIGHT, self.WRIST_RIGHT],
						['Hand_Left', self.WRIST_LEFT, self.HAND_LEFT], ['Hand_Right', self.WRIST_RIGHT, self.HAND_RIGHT],
						['Pelvis', self.HIP_CENTER,self.HIP_MIDPOINT], ['Thigh_Left', self.HIP_LEFT, self.KNEE_LEFT], ['Thigh_Right', self.HIP_RIGHT, self.KNEE_RIGHT],
						['Leg_Left', self.KNEE_LEFT, self.ANKLE_LEFT], ['Leg_Right', self.KNEE_RIGHT, self.ANKLE_RIGHT], ['Foot_Left', self.ANKLE_LEFT, self.FOOT_LEFT],
						['Foot_Right', self.ANKLE_RIGHT, self.FOOT_RIGHT]]

		self.test_segment_list = []

		#list of center of mass / segmental length (proximal, distal) and segment weight / total body weight
		# ->>> TRUNK OR THORAX-ABDOMEN ????
		self.perc_of_segm_length = {'Head-Neck': (1.0, 0.0, 0.081), 'Trunk': (0.5, 0.5, 0.497),
						'UpperArm_Left': (0.436, 0.564, 0.028),'UpperArm_Right': (0.436, 0.564, 0.028),
						'Forearm_Left': (0.47, 0.57, 0.016), 'Forearm_Right': (0.47, 0.57, 0.016),
						'Hand_Left': (0.506, 0.494, 0.006), 'Hand_Right': (0.506, 0.494, 0.006),
						'Pelvis': (0.105, 0.895, 0.142), 'Thigh_Left': (0.433, 0.567, 0.100), 'Thigh_Right': (0.433, 0.567, 0.100),
						'Leg_Left': (0.433, 0.567, 0.0465), 'Leg_Right': (0.433, 0.567, 0.0465),
						'Foot_Left': (0.5, 0.5, 0.0145), 'Foot_Right':(0.5, 0.5, 0.0145)}

		# preload spheres for body segment CoM and TBCoM
		self.com_spheres = {}
		for segment in self.perc_of_segm_length:
			self.com_spheres[segment] = vizshape.addSphere(radius=0.02, color=viz.BLUE)
			#.com_spheres.visible(viz.OFF)
		#print(self.com_spheres)

		self.TBCoM_sphere = vizshape.addSphere(radius=0.04, color=viz.RED)

		self.s = vizshape.addSphere(radius=0.01)
		self.s.color(viz.YELLOW_ORANGE)
		self.s.visible(viz.OFF)

	def calculate_segment_CoM(self):

		x_TBCoM = {}
		y_TBCoM = {}
		z_TBCoM = {}

		self.test_segment_list = []

		for segment in self.body_segments:

			if segment[0] is 'Pelvis':
				# for body segment pelvis distal end (hip midpoint) equals the midpoint between r and l hip
				# get tracker of r and l hip
				lhip, rhip = trackers[16], trackers[20]
				# use list comprehension to calculate midpoint (using getPosition for coordinates)
				self.HIP_MIDPOINT = [((a+b/2))for a, b in zip(lhip.getPosition(), rhip.getPosition())]
				#print(self.HIP_MIDPOINT)
				# apply hip midpoint coordinates to sphere
				self.s.setPosition(self.HIP_MIDPOINT)

				# get position of prox / dist segment ends
				prox_pos = self.HIP_CENTER
				prox_pos = prox_pos.getPosition()
				dist_pos = self.HIP_MIDPOINT

			else:
				# link green/red spheres to prox/dist segment
				prox = segment[1]
				dist = segment[2]

				# get position of prox / dist segment ends
				prox_pos = prox.getPosition()
				dist_pos = dist.getPosition()

			#print(segment, prox_pos, dist_pos)
			seg = [segment[0]+'_prox', prox_pos[0], prox_pos[1], prox_pos[2], segment[0]+'_dist', dist_pos[0], dist_pos[1], dist_pos[2]]
			#data = map(lambda x: str(x).translate(None, ['[',']']), seg)
			self.test_segment_list.append(seg)#[segment, dist_pos, prox_pos])

			x_prox, y_prox, x_dist, y_dist = prox_pos[0], prox_pos[1], dist_pos[0], dist_pos[1]
			z_prox, z_dist = prox_pos[2], prox_pos[2]

			segment = segment[0]

			l_prox, l_dist = self.perc_of_segm_length[segment][0], self.perc_of_segm_length[segment][1]

			#
			x_COM = x_prox*l_dist + x_dist*l_prox
			y_COM = y_prox*l_dist + y_dist*l_prox
			z_COM = z_prox*l_dist + z_dist*l_prox

			# apply body segment COM to according sphere
			self.com_spheres[segment].setPosition(x_COM, y_COM, z_COM)
			self.com_spheres[segment].visible(viz.OFF)
			segment_fraction = self.perc_of_segm_length[segment][2]

			x_TBCoM[segment] = (x_COM * segment_fraction)
			y_TBCoM[segment] = (y_COM * segment_fraction)
			z_TBCoM[segment] = (z_COM * segment_fraction)

			X = sum(x_TBCoM.values())
			Y = sum(y_TBCoM.values())
			Z = sum(z_TBCoM.values())

			# apply TBCoM coordinates to TBCoM sphere
			self.TBCoM_sphere.setPosition(X, Y, Z)
			self.TBCoM_sphere.visible(viz.OFF)
			#print(self.TBCoM_sphere.getPosition()[0])


		#print(self.TBCoM_sphere.getEuler())
		# print out data in console
		#print(self.test_segment_list)
		#print(self.exp.TRIAL_NO, self.exp.current_stimulus_name, self.exp.current_stimulus_yaw, self.exp.current_stimulus_roll,self.exp.STATE,
		#			viz.tick(), (viz.tick() - self.exp.TRIAL_START_TIME), viz.getFrameNumber(), viz.getFrameElapsed(), viz.getFrameTime(), [X, Y, Z], tracker_coordinates)#self.segment_coordinates)

		# temporarily save framewise data into empty list


		self.TEMP_RV_DATA.append([self.exp.STATE, self.exp.response,self.exp.keyPressTime,viz.tick(),viz.getFrameNumber(), viz.getFrameElapsed(), viz.getFrameTime()])

		self.TEMP_COM_DATA.append(self.test_segment_list) # self.segment_coordinates

		self.TEMP_TCBOM.append(['TCBOM',X, Y, Z])


def main():

	# create instance of class
	com = CenterOfMass()
	# call method in event class
	vizact.ontimer(0, com.calculate_segment_CoM)

if __name__ == '__main__': main()
