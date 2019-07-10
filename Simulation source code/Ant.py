import math
from random import randint
import numpy as np
from math import sqrt

class Ant:
	def __init__(self, id, parent, posX = 0, posY = 0, dir = 0):
		self.id = id
		self.coords = (posX, posY)
		self.dir = dir
		self.active = False
		self.parentSim = parent
		self.neib = set()
		self.excitment = 0
		self.state = 'n'


	def __repr__(self):
		return "AntID="+str(self.id)

	def goto(self, x_or_tuple, y = None):
		if y == None:
			self.coords = x_or_tuple
		else:
			self.coords = (x_or_tuple, y)
		
	def Xcor(self):
		return self.coords[0]

	def Ycor(self):
		return self.coords[1]

	def move(self, dx, dy):
		newX = self.Xcor()+dx
		newY = self.Ycor()+dy
		self.coords = (newX, newY)

	def setheading(self, alpha):
		self.dir = alpha

	def heading(self):
		return self.dir

	def turn(self, alpha):
		self.dir += alpha
		self.dir %= (2*math.pi)

	def getID(self):
		return self.id

	def position(self):
		return (self.coords, self.dir)

	# TURTLE LEGACY
	def getTort(self):
		return self.tort
	def setTort(self, val):
		self.tort = val
	def activated(self):
		return self.active
	def activate(self, delay = None):
		self.active = True
		self.setstate('a')
		if delay:
			self.setDeactivationDelay(delay)
	def setstate(self, s):
		self.state = s
	def getstate(self):
		return self.state
	def deactivate(self):
		self.active = False
		self.setstate('n')
	def excite(self, val):
		self.excitment += val;
	def getExcitment(self):
		return self.excitment
	def setExcitment(self, val):
		self.excitment = val;
	def deexcite(self, incr = 1):
		self.excitment = max(0, self.excitment - incr)
	def getNeib(self):
		return self.neib
	def setNeib(self, li):
		self.neib = li
	def getDeactivationDelay(self):
		return self.deactivationDelay
	def setDeactivationDelay(self, val):
		self.deactivationDelay = val
	def incrDeactivationDelay(self, incr = -1):
		self.deactivationDelay = max(0, self.deactivationDelay + incr)


	def get_step_with_bias(self, biasType, basicBias = None, extraBias = 0):

		leftend = self.parentSim.arena.minX
		rightend = self.parentSim.arena.maxX
		mid = (rightend + leftend) // 2
		#originX = self.parentSim.pars["ORIGIN"][0]
		originX = self.parentSim.arena.origin[0]
		par_zeroX = leftend + (rightend - leftend)//self.parentSim.pars["PARAB_ZERO"]

		if basicBias == None:
			basicBias = self.parentSim.pars["BIAS_PAR"]
		biasVal = basicBias + extraBias

		step_mean = self.parentSim.pars["ANT_STEP"]
		step_var = self.parentSim.pars["ANT_STEP_VAR"]
		step_max = self.parentSim.pars["ANT_STEP_MAX"]

		#transformations for gamma-dist
		theta = step_var/step_mean   #scale
		k = step_mean / theta		 #shape

		step = np.random.gamma(shape = k, scale = theta)
		bias_influence = np.random.uniform(0, step * biasVal)


		if biasType == 'h1':
			computed_step = step + bias_influence*self.heat_coefficent_calculation(self.Xcor(), self.Ycor(), 1.2*(originX-mid))

		# this option gets rid of extra bias_influence parameter but requires some more thinking
		elif biasType == 'h2':
			computed_step = step*self.heat_coefficent_calculation(self.Xcor(), self.Ycor(), originX-mid)


		# constant bias
		elif biasType == 'c':
			if (0 < self.heading() < math.pi/2) or (3 * math.pi / 2 < self.heading() <  2 * math.pi): 
				# when oriented to the right 
				computed_step = step - bias_influence
			else:
				# when oriented to the left 
				computed_step = step + bias_influence

		# straight-line declining bias
		elif biasType == 'l':
			if (0 < self.heading() < math.pi/2) or (3 * math.pi / 2 < self.heading() <  2 * math.pi): # when oriented to the right 
				computed_step = step - (bias_influence * ((self.Xcor() - leftend) / (mid - leftend)))
			else:
				computed_step = step + (bias_influence * ((self.Xcor() - leftend) / (mid - leftend)))
		
		# parabolic bias
		elif biasType == 'p':
			#delta = bias_influence * (((self.Xcor() - par_zeroX)/(originX - par_zeroX)) ** 2)
			par_zeroX = leftend # (*)
			delta = bias_influence * (((self.Xcor() - leftend)/(originX - leftend)) ** 2)
			#if (self.Xcor() > par_zeroX):
			if (0 < self.heading() < math.pi/2) or (3 * math.pi / 2 < self.heading() <  2 * math.pi): 
			# when oriented to the right 
				computed_step = step - delta
			else:
			# when oriented to the left 
				computed_step = step + delta

			# irreleant if (*) is activated
			# else:
			# 	if (0 < self.heading() < math.pi/2) or (3 * math.pi / 2 < self.heading() <  2 * math.pi): # when oriented to the right 
			# 		computed_step = step + delta
			# 	else:
			# 		computed_step = step - delta

		elif biasType == 'a':
		# constant preference towards right side
			if (0 < self.heading() < math.pi/2) or (3 * math.pi / 2 < self.heading() <  2 * math.pi): 
			# when oriented to the right 
				computed_step = step + bias_influence
			else:
			# when oriented to the left 
				computed_step = step - bias_influence

		# if a "jump" is generated, reduce it to max possible step
		if abs(computed_step) > step_max:
			computed_step = math.copysign(step_max, computed_step)

		return computed_step


	def heat_coefficent_calculation(self, x, y, rad = 0):
		if not rad:
			rad = (self.parentSim.arena.minX + self.parentSim.arena.maxX) // 3


		origin = self.parentSim.arena.origin
		oX, oY = origin[0], origin[1]
		dist = sqrt((x-oX)**2 + (y-oY)**2)
		if dist < rad:
			return 1
		else:
			return 0




