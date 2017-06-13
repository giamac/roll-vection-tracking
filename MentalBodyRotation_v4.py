############################################
import viz, viztask, vizact, vizinput, vizshape
import random
random.seed() # initialize the random functions
from string import maketrans
import itertools, csv, time

#viz.go()

#start vrpn
## Is this need here?
vrpn = viz.addExtension('vrpn7.dle')

#GUI to enter participant data
#Demographic data are entered: similar to my script
myID = viz.input('Bitte ID der Versuchsperson eingeben')
myAge = viz.input('Alter')
mySex = vizinput.choose('Geschlecht',['female','male'])
if mySex == 0:
	mySex = 'female'
else:
	mySex = 'male'

myBlock = vizinput.choose('Block',['Block_1','Block_2','Block_3','Block_4'])

#------------------------------------------------------------------------------------
# set the viewpoint
viz.MainView.setPosition([0,2, 1])
viz.MainView.setEuler([0,0,0])
#Increase the Field of View
viz.MainWindow.fov(90)
#Enable full screen anti-aliasing (FSAA) to smooth edges
viz.setMultiSample(8)

import oculus
hmd = oculus.Rift()
link = viz.link(hmd.getSensor(), viz.MainView)
viz.go(viz.FULLSCREEN)
viz.go()

viz.MainView.setPosition(0, 0, 0)

### Why here? Kinect Tracking Stuff
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
	t = vrpn.addTracker( 'Tracker0@localhost',i )
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

# Create a Header for the CSV file for each participant
with open('DATEN/'+str(myID)+'_'+str(mySex)+'_'+str(myAge)+'_'+str(myBlock)+'_'+'MentalBodyRotationTask.csv', 'a') as f:
	writer = csv.DictWriter(f, fieldnames = ['Subject ID', 'Age', 'Sex', 'Trial_No.', 'Stimulus_Name', 'Stimulus_Ori_Yaw', 'Stimulus_Ori_Roll', 'Trial_State',
	'Global_Time', 'Trial_Time', 'Frame_No.','Frame_Elapsed', 'Frame_Time'], delimiter = ';')
	writer.writeheader()

# Create a class for the MentalBodyRotation Task: Including all
# kinds of methods
class MentalBodyRotation():

	# Define some variables necessary for the Experiment
	def __init__(self):
		#Mental Body Rotation Data?
		self.MBR_DATA = []
		#Tracking Data?
		self.COM_DATA = []
		#Tracking data?
		self.TCBOM = []

		#The
		self.stimulus_path = 'models'#'l1etters'
		# three types of stimuli both left and right
		self.stimuli = ('LeftArmUp', 'RightArmUp','LeftArmOut', 'RightArmOut')
		#('E', 'F', 'L', 'P', 'R')

		# stimulus orientation in the picture plane = ROLL
		self.stimulus_orientations = (0, 90, 120, 140, 160, 200, 220, 240, 270)#(0, 90, 180, 270)
		# front and back view = YAW
		self.stimulus_view = (0, 180,0,180)
		# set number of repetitions of the 48 body stimuli if needed; 48 x self.NO_REPETITIONS = total number of trials
		self.NO_REPETITIONS = 5
		# set inter stimulus interval (ISI)in seconds
		self.ISI = 0.5
		# create the experimental trials (stimulus type x orientation x back or front)
		self.trials = self.comb(self.stimuli, self.stimulus_orientations, self.stimulus_view)
		print('TRIALS: ', len(self.trials),  self.trials)

		self.TRIAL_NO = 0
		self.TRIAL_START_TIME = 0
		self.reactionTime = None
		self.response = None
		self.correct_response = None

		self.current_stimulus_name = None
		self.current_stimulus_yaw = None
		self.current_stimulus_roll = None

		# create empty lists for the stimuli, stimulus names, and orientations
		self.myStimuli = viz.cycle([])
		self.myStimulusNames = viz.cycle([])
		self.myAnglesRoll = viz.cycle([])
		self.myAnglesYaw = viz.cycle([])

		# randomly shuffle the list of trials
		random.shuffle(self.trials)
		print('TRIALS shuffled: ', self.trials)

		self.STATE = None

		# call generate trials function first of all
		self.generate_stimuli()

		self.STIMULUS_DURATION = 2 # in seconds

		self.state = {"keypress" : True}

	def comb(self, *sequences):
		#code from http://code.activestate.com/recipes/502199/
		combinations = [[seq] for seq in sequences[0]]
		for seq in sequences[1:]:
			combinations = [comb+[item]
							for comb in combinations
							for item in seq ]
		return combinations

	def generate_stimuli(self):
		for trial in self.trials:
			print(trial)
			model = self.stimulus_path+'/'+ (trial[0]) + '.obj'
			temp = viz.addChild(model, cache=viz.CACHE_CLONE) # load the stimuli from cache -> runs faster
			temp.visible(viz.OFF) # make the preloaded stimuli invisible
			self.myStimuli.append(temp)

			name, roll_deg, yaw_deg = trial[0], trial[1], trial[2]
			self.myStimulusNames.append(name), self.myAnglesRoll.append(roll_deg), self.myAnglesYaw.append(yaw_deg)

		print(self.myStimuli)

	def SessionProcedure(self):
		yield viztask.waitKeyDown(' ')
		# execute Block Procedure
		yield self.BlockProcedure()

	def BlockProcedure(self):
		for t in range(len(self.trials)):
			# execute Trial Procedure
			yield self.TrialProcedure()

		# 'Subject ID', 'Age', 'Sex', 'Trial_No.', 'Stimulus_Name', 'Stimulus_Ori_Yaw', 'Stimulus_Ori_Roll', 'Trial_State', 'Global_Time', 'Trial_Time', 'Frame_No.','Frame_Elapsed', 'Frame_Time'
		if self.TRIAL_NO == len(self.trials):

			print('*STORING DATA TO CSV...')

			# save data from list to csv file
			with open('DATEN/'+str(myID)+'_'+str(mySex)+'_'+str(myAge)+'_'+'MentalBodyRotationTask.csv', 'a') as f:
				wr = csv.writer(f, delimiter=';', lineterminator='\n', quoting=csv.QUOTE_ALL)

				import itertools
				flattened = flattened = [[item for sublist in list for item in sublist] for list in self.COM_DATA]

				#[framelist for segment in self.COM_DATA for segment in framelist in self.COM_DATA]

				print(flattened)

				for mrb_data, coord_data, tcbom in zip(self.MBR_DATA, flattened, self.TCBOM):

					row = mrb_data + coord_data + tcbom

					wr.writerow(row)

			print(self.MBR_DATA)
			print(self.COM_DATA)


	def TrialProcedure(self):

		self.response, self.correct_response, self.reactionTime = 'None', 'None', 'None'

		self.TRIAL_NO += 1
		print(self.TRIAL_NO)

		self.TRIAL_START_TIME = viz.tick()

		self.STATE = 'inter-stimulus intervall'

		yield viztask.waitTime(self.ISI) # INTERSTIMULUS-INTERVALL
		# get cycle through preloaded stimuli one at a time using next function
		body = self.myStimuli.next()

		# make the stimulus visible again (preloaded invisibly)
		body.visible(viz.ON)
		self.STATE = 'stimulus - no response'

		body.disable(viz.LIGHTING)
		# adapt size of stimuli if needed
		size = 0.05
		body.setScale(size, size, size)
		# set position (x, y, z) of the stimulus
		body.setPosition(0, 0.2, -0.5)

		self.current_stimulus_name = self.myStimulusNames.next()
		self.current_stimulus_yaw  = self.myAnglesYaw.next()
		self.current_stimulus_roll = self.myAnglesRoll.next()

		# get left or right from stimulus name

		if self.current_stimulus_name.startswith('Left'):
			self.correct_response = 'left'
		else:
			self.correct_response = 'right'

		# set euler of stimulus (yaw, pitch, roll)
		body.setEuler(float(self.current_stimulus_yaw), 0, float(self.current_stimulus_roll))
		body.visible(viz.ON) # make the 3d stimulus visible again

		self.state = {"keypress" : True}

		startTime = viz.tick() # get time for stimulus onset

		#data = yield viztask.waitKeyDown(['f', 'j']) # keyboard answers allowed: f=leftArm and j=rightArm

		self.state = {"keypress" : False}

		def keydown( key ):

			if not self.state["keypress"] and key == 'f':
				self.response = 'left'
				keyPressTime = viz.tick() # get time for keypress
				self.reactionTime = keyPressTime - startTime # calculate reation time
				self.state = {"keypress" : True}
				print(self.response)
				self.STATE = 'stimulus - response'

			if not self.state["keypress"] and key == 'j':
				self.response = 'right'
				keyPressTime = viz.tick() # get time for keypress
				self.reactionTime = keyPressTime - startTime # calculate reation time
				self.state = {"keypress" : True}
				print(self.response)
				self.STATE = 'stimulus - response'

		viz.callback(viz.KEYDOWN_EVENT, keydown)

		yield viztask.waitTime(self.STIMULUS_DURATION) # wait

		body.visible(viz.OFF) # make stimulus invisible after keyboard response

		self.STATE = 'post-stimulus - response'

		print(self.TRIAL_NO, self.current_stimulus_name, self.current_stimulus_yaw, self.current_stimulus_roll, self.reactionTime)
		#yield viztask.waitTime(0.5) # wait 0,5 sec for next trial

class CenterOfMass(viz.EventClass):

	def __init__(self):

		# initialize base class
		viz.EventClass.__init__(self)
		#self.total_M = viz.input('Please enter total body mass [kg]')

		self.exp = MentalBodyRotation()
		viztask.schedule(self.exp.SessionProcedure)

		self.TEMP_MBR_DATA = []
		self.TEMP_COM_DATA = []
		self.TEMP_TCBOM = []

		self.exp.COM_DATA = self.TEMP_COM_DATA
		self.exp.MBR_DATA = self.TEMP_MBR_DATA
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

		self.TEMP_MBR_DATA.append([self.exp.TRIAL_NO, self.exp.current_stimulus_name, self.exp.current_stimulus_yaw, self.exp.current_stimulus_roll,self.exp.STATE, self.exp.correct_response,
					self.exp.response, self.exp.reactionTime, viz.tick(), (viz.tick() - self.exp.TRIAL_START_TIME), viz.getFrameNumber(), viz.getFrameElapsed(), viz.getFrameTime()])

		self.TEMP_COM_DATA.append(self.test_segment_list) # self.segment_coordinates

		self.TEMP_TCBOM.append(['TCBOM',X, Y, Z])


def main():

	# create instance of class
	com = CenterOfMass()
	# call method in event class
	vizact.ontimer(0, com.calculate_segment_CoM)

if __name__ == '__main__': main()
