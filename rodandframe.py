import viz
import vizact
import random

viz.go()

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
poly.setEuler([0,0,20])


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
		elif viz.key.isDown(viz.KEY_BACKSPACE):
			self.callback(viz.KEYDOWN_EVENT,0)
		print line.getEuler()

LineRotation()



