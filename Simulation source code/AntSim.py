from Arena import *
from Ant import *
from PostProcessor import *
from importlib import import_module
from random import normalvariate, expovariate, randint, sample
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
matplotlib.use('agg')
import math
import time, datetime
import os

class AntSim:
	
	def __init__(self, fieldType = 'c0d0', parameters = None, name = None):
		self.simID = datetime.datetime.fromtimestamp(time.time()).strftime('%m%d%Y_%H%M%S')+'_'+str(randint(0,10000))
		self.parfilename = parameters
		self.pars = self.loadPars(parameters)
		self.arena = Arena(self.pars["ARENA"])
		self.arena.getNestDim()
		self.cm = Ant('cm', self)
		self.runcount = 0
		self.name = name
		self.allInter_x = list()
		self.allInter_y = list()
		self.allInter_actor = list()
		self.allInter_reciever = list()
		self.allInter_actstate =  list()
		self.allInter_recstate = list()
		self.allInter = (self.allInter_x, self.allInter_y, self.allInter_actor, self.allInter_reciever,  self.allInter_actstate, self.allInter_recstate)

		# set up for saving data
		self.nest_transfer_data = None;
		self.interactions_data = None;


	def getID(self):
		return self.simID

	def loadPars(self, filename = None, key = None, val = None):
		pars = dict()

		if filename:
			consts_dict = import_module(filename[:-3])
			pars = consts_dict.pars
			self.pars = pars
		elif key:
			self.pars[key] = val
			if key == "ARENA":
				self.arena.reset(field = self.pars["ARENA"])

		return pars

	def run(self, drawing = False, recordcsv = True, recordinter = True, activation = True, bulk = True, saveinitialdist = False):


		self.arena.reset(field = self.pars["ARENA"])
		self.ants = [Ant(i, self, dir = math.radians(randint(0, 360))) for i in range(1, self.pars['NUM'] + 1)]
		self.runcount += 1
		bias_type = self.pars["BIAS_C"]
		wallreact =  self.pars["WALL"]
		maxiter = self.pars["MAXTRY"]	

		# set up full-body mode
		ant_length = self.pars["ANT_SIZE_X"]
		ant_width = self.pars["ANT_SIZE_Y"]


		#### Setting up unitial configuration

		# For ant transfer data
		left_array = list()
		right_array = list()

		# for csv recording
		if self.name == None:
			csvpath = "results/{}".format(self.simID)
		else:
			csvpath = 'results/{}/{}'.format(self.name[0], self.name[1])

		if recordcsv:
			if not os.path.exists(csvpath):
				os.makedirs(csvpath)
			csv = open("{}/trajectories_{}.csv".format(csvpath, self.runcount), 'w')

		#for drawing:
		if drawing:
			tr_fig, tr_ax = plt.subplots(1,1, figsize=(18, 12))
			tr_ax.imshow(plt.imread(self.arena.arFile.split('.')[0]+".gif"))
			tr_ax.set_yticklabels([])
			tr_ax.set_xticklabels([])
			self.xs =[[] for _ in range(self.pars["NUM"])]
			self.ys =[[] for _ in range(self.pars["NUM"])]
			self.colors = list()

		# for activation
		leftend = self.arena.minX
		rightend = self.arena.maxX
		par_zeroX = leftend + (rightend - leftend)//self.pars["PARAB_ZERO"]

		# calculate starting positions
		starting_pos, starting_distr = self.arena.getStartPos(self.pars)

		# initial set-up loop through all ants
		for a in self.ants:
			a.goto(starting_pos[a.getID()-1])
			a.setTort(expovariate(self.pars['ANGLEEXPMEAN']))
			if drawing:
				self.xs[a.getID()-1].append(a.Xcor())
				self.ys[a.getID()-1].append(a.Ycor())

				RGB = tuple(sample((randint(150, 255), randint(0, 105), randint(0, 255)), 3))
				RGB_scaled = [x/255 for x in RGB]
				self.colors.append(RGB_scaled)

		# save initial positions plot if needed
		if saveinitialdist:

			plt.figure('initial_dist_fig', figsize=(18,12))
			gs = gridspec.GridSpec(2, 1, height_ratios=[4,1])
			ax0 = plt.subplot(gs[0, 0])
			ax1 = plt.subplot(gs[1, 0])

			ax0.set_xlim(0, self.arena.dimX)
			ax0.scatter(self.xs, self.ys, c = self.colors, s = 120)
			ax0.imshow(plt.imread(self.arena.arFile.split('.')[0]+".gif"), alpha = 0.7)
			ax0.set_yticklabels([])
			ax0.set_xticklabels([])

			x = np.linspace(0, self.arena.dimX, self.arena.dimX*10)
			ax1.set_xlim(0, self.arena.dimX)
			ax1.plot(x, starting_distr(x), color = 'r')
			ax1.set_aspect(1/ax1.get_data_ratio()*0.14)
			#ax1.set_yticklabels([0,'','','','', 0.000001]) #- for rs
			#ax1.set_yticklabels([0,'','','','','','', 0.007]) #- for ls
			ax1.set_yticklabels([0,'','','','','','', '', 0.0016]) #- for u
			ax1.set_xticklabels([])
			
			
			if not os.path.exists("results/{}/initial_dist/".format(self.getID())):
				os.makedirs("results/{}/initial_dist/".format(self.getID()))
			plt.savefig("results/{}/initial_dist/{}.png".format(self.getID(), self.runcount))
			plt.close()


		### main loop through iterations
		for i in range(self.pars['ITER']):
			left_ants = 0
			right_ants = 0

			### main loop through ants inside iteration
			for a in self.ants:

				# record the position
				if recordcsv:
					# format: time, antID, X, Y, state, excitment
					csv.write("{0!s}, {1!s}, {2!s}, {3!s}, {4!s}, {5!s}\n".format(i, a.getID(), a.Xcor(), a.Ycor(), a.getstate(), a.getExcitment()))

				# get step
				if activation:
					if a.activated():
						computed_step = a.get_step_with_bias('a', basicBias = self.pars["ACTIVATED_BIAS_PAR"])
					else:
						eb = self.pars["EXCITED_BIAS_PAR"] * int(a.getExcitment() >= self.pars["EXCITMENT_TRESHOLD"])
						# record whether the ant was activated or not
						a.setstate('e') if eb else a.setstate('n')
						#compute the actual step
						computed_step = a.get_step_with_bias(bias_type, extraBias = eb)

				else:
					computed_step = a.get_step_with_bias(bias_type)

				# get turning angle
				delTeta = normalvariate(0,a.getTort())
				NewDir = a.heading() + delTeta
				a.turn(delTeta)

				# calculate new coordnates
				curX = a.Xcor()
				curY = a.Ycor()
				delX = int(round(computed_step*math.cos(NewDir)))
				delY = int(round(computed_step*math.sin(NewDir)))

				# adjust coordinate to prevent leaving the nest area by either changing length or the direction
				if wallreact == 'delstep':
					while ((self.arena.getFieldVal(curX + delX, curY + delY) != 255) and (abs(delX) > 0 or abs(delY) > 0)):
						if abs(delX) > 0:
							delX = np.sign(delX)*(abs(delX) - 1)
						if abs(delY) > 0:
							delY = np.sign(delY)*(abs(delY) - 1)

				elif wallreact == 'deldir':
					counter =  0
					while self.arena.getFieldVal(curX + delX, curY + delY) != 255 and counter < maxiter:
						# get turning angle
						delTeta = normalvariate(0,a.getTort())
						NewDir = a.heading() + delTeta
						a.turn(delTeta)

						# calculate new coordnates
						curX = a.Xcor()
						curY = a.Ycor()
						delX = int(round(computed_step*math.cos(NewDir)))
						delY = int(round(computed_step*math.sin(NewDir)))

						counter +=  1
						if counter == maxiter:
							delX  = 0
							delY  = 0

				# move the ant center 
				a.goto(curX + delX, curY + delY)
				self.arena.setFieldVal(255, curX, curY)
				self.arena.setFieldVal(a.getID(), curX + delX, curY + delY)

				# move the full ant
				body = self.arena.fillbodyspace(a.getID(), curX + delX, curY + delY, a.heading(), ant_length, ant_width)
				self.arena.fillbodyspace(255, curX, curY, a.heading() - delTeta, ant_length, ant_width)


				# collect nest transfer information
				if self.arena.Xmin() <= a.Xcor() <= self.arena.Xmid():
					left_ants += 1
				else:
					right_ants += 1

				# collect interactions information
				allNeib = self.arena.getInter(a.Xcor(), a.Ycor(), self.pars["INTER_RAD"])
				newNeib = allNeib - (a.getNeib() | {0, 255, a.getID()})
				a.setNeib(allNeib)
				if recordinter and newNeib:
					for r in newNeib:
						self.allInter_x.append(int(a.Xcor()))
						self.allInter_y.append(int(a.Ycor()))
						self.allInter_actor.append(int(a.getID()))
						self.allInter_reciever.append(int(r))
						self.allInter_actstate.append(a.getstate())
						self.allInter_recstate.append(self.ants[r-1].getstate())

				# active/excited ants porcessing
				if activation:
					if a.activated():
						# excite all new neighbors
						for nn in newNeib:
							self.ants[nn - 1].excite(self.pars['ONE_INTER_INCR'])

						# deactivate if needed
						a.incrDeactivationDelay(-1)
						if a.getDeactivationDelay() <= 0:
							a.deactivate()
					
					else:
						# reduce excitment if not 0
						a.deexcite()
						# activate if needed
						if abs(a.Xcor() - par_zeroX) < ((rightend-leftend) // self.pars["ACTIVATION_ZONE"]):
							activation_chance = randint(1, self.pars["ACTIVATION_CHANCE"] + 1) #TODO : make it ant-specific (?)
							if activation_chance == 1:
								a.activate(delay = self.pars["DEACTIVATION_DELAY"])

				# draw trajectories
				if drawing:	
					self.xs[a.getID()-1].append(a.Xcor())
					self.ys[a.getID()-1].append(a.Ycor())
					if i % self.pars['SIMSPEED'] == 0:
						plt.figure(tr_fig.number)
						tr_ax.plot(self.xs[a.getID()-1], self.ys[a.getID()-1], c = self.colors[a.getID()-1], marker='.')
						try:
							tr_ax.plot(body[0], body[1], c = self.colors[a.getID()-1], marker='.')
						except:
							pass
						#plt.show()

				### END OF ANTS LOOP

			# process nest tranfer info
			left_array.append((i, left_ants))
			right_array.append((i, right_ants))

			# things you do once in a while (with certain frequency)
			if i % self.pars['SIMSPEED'] == 0:
				if not bulk:
					print("{0:.0f}% completed".format(i/self.pars['ITER']*100))

			### END OF ITERATONS LOOP




		# reset arena for next run. Note: interactions are still saved if the bulk mode is ON
		self.arena.reset(field = self.pars["ARENA"])
		for a in self.ants:
			del a

		# save trajectories file
		if recordcsv:
			csv.close()

		# save nest transfer data
		left_array = np.array(left_array)
		right_array = np.array(right_array)
		self.nest_transfer_data = np.hstack((left_array, right_array))

		# save the trajectories image
		if drawing:
			plt.figure(tr_fig.number)
			plt.savefig("results/{}/trajectories_{}.png".format(self.getID(), self.runcount))
			plt.close()




if __name__ == "__main__":
	MySim = AntSim(parameters = 'consts_dict.py')
	#MySim.loadPars(key = 'BIAS_PAR', val = 2.0)
	MySim.loadPars(key = 'ARENA', val = '2tun')
	MySim.loadPars(key = 'INIT_DISTR', val = 'rs')
	MySim.loadPars(key = 'ITER', val = 10000)
	#MySim.loadPars(key = 'BIAS_C', val = 'h1')
	PP = PostProcessor(MySim)


	MySim.run(activation = False, recordinter = True, drawing = True, saveinitialdist = True, bulk = False)


	PP.nest_transfer(MySim.nest_transfer_data, mode = 'one')
	#PP.nest_transfer(MySim.nest_transfer_data, mode = 'process')
	PP.simple_interactions(MySim.allInter)
	PP.plot2dkernel(MySim.allInter)
	PP.plot2dkernel(mode = 'traj')
	PP.parameters_dump(MySim.pars)
