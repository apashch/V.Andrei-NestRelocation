import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st
import os
import csv
import glob
import shutil
import misc
from statistics import mean, stdev
from math import sqrt
import time



class PostProcessor:

	def __init__(self, parent, name = None):
		self.parentSim = parent
		self.timestamp = self.parentSim.getID()
		self.num_sets = 0

		self.first_crossing_data = list()
		self.last_crossing_data = list()
		self.num_crossings = list()
		self.final_num = list()

		if name == None:
			self.foldername = 'results/{}'.format(self.timestamp)
		else:
			self.foldername = 'results/{}/{}'.format(name[0], name[1])

		if not os.path.exists(self.foldername):
			os.makedirs(self.foldername)

		self.first_crossing_fig, self.fca = plt.subplots(1, 1)
		self.first_crossing_fig.suptitle('First crossing time')
		self.fca.set_ylim(0, self.parentSim.pars['ITER'])
		

		self.last_crossing_fig, self.lca = plt.subplots(1, 1)
		self.last_crossing_fig.suptitle('Last crossing time')
		self.lca.set_ylim(0, self.parentSim.pars['ITER'])
		

		self.num_crossings_fig, self.nca = plt.subplots(1, 1)
		self.num_crossings_fig.suptitle('Nest transfer crossings count')
		
		self.final_num_fig, self.fna = plt.subplots(1, 1)
		self.final_num_fig.suptitle('Final number of ants on the cooler side')
		self.fna.set_ylim(0, self.parentSim.pars['NUM'])
	



	def add_subplot(self, fig):
		if self.num_sets == 0:
			return fig.axes[0]
		else:
			n = len(fig.axes)
			for i in range(n):
				fig.axes[i].change_geometry(1, n+1, i+1)
			ax = fig.add_subplot(1, n+1, n+1)
			return ax


	def nest_transfer(self, nest_transfer_data, mode = 'one', name = "test", numtrials = 1):
		trials_name = [name]
		left = nest_transfer_data[:, :2]
		right = nest_transfer_data[:, 2:]

		if mode == 'one':
			# show nest transfer data
			plt.close()
			plt.plot(left[:, 0],left[:, 1],'r') # plotting t,a separately 
			plt.plot(right[:, 0], right[:, 1],'b') # plotting t,b separately
			plt.savefig(self.foldername + "/nest_transfer_fig.png")
			plt.close()


		elif mode == 'add':

			crossings = np.where(left[:, 1]==right[:, 1])[0]
			crossings_counter = 0
			crossings2 = np.append([0], crossings)
			for i in range(1, crossings2.size):
				if crossings2[i] - crossings2[i-1] > 1:
					crossings_counter += 1

			if crossings.size == 0:
				crossings = [left[:, 0][-1]]

			self.first_crossing_data.append(crossings[0])
			self.last_crossing_data.append(crossings[-1])
			self.final_num.append(left[:, 1][-1])
			self.num_crossings.append(crossings_counter)

		elif mode == 'process':
			ax = self.add_subplot(self.num_crossings_fig)
			ax.boxplot(self.num_crossings, labels = trials_name)
			with open (self.foldername+"/crossings_count_file.csv", 'a') as ncf:
				ncf.write(trials_name[0]+",")
				ncf.write(get_writable_data(self.num_crossings, numtrials))
				

			ax = self.add_subplot(self.first_crossing_fig)
			ax.set_ylim(0, self.parentSim.pars['ITER'])
			ax.boxplot(self.first_crossing_data, labels = trials_name)
			with open (self.foldername+"/first_crossing_file.csv", 'a') as fcf:
				fcf.write(trials_name[0]+",")
				fcf.write(get_writable_data(self.first_crossing_data, numtrials))

			ax = self.add_subplot(self.last_crossing_fig)
			ax.set_ylim(0, self.parentSim.pars['ITER'])
			ax.boxplot(self.last_crossing_data, labels = trials_name)
			with open (self.foldername+"/last_crossing_file.csv", 'a') as lcf:
				lcf.write(trials_name[0]+",")
				lcf.write(get_writable_data(self.last_crossing_data, numtrials))

			ax = self.add_subplot(self.final_num_fig)
			ax.set_ylim(0, self.parentSim.pars['NUM'])
			ax.boxplot(self.final_num, labels = trials_name)
			with open (self.foldername+"/final_number_file.csv", 'a') as fnf:
				fnf.write(trials_name[0]+",")
				fnf.write(get_writable_data(self.final_num, numtrials))

			#tm = time.time()
			self.parameters_dump(self.parentSim.pars, trials_name[0])
			#tM = time.time()
			#print("Par dump = "+str(tM - tm)+" seconds")
			#tm = time.time()
			self.relocate_traj(self.foldername, trials_name[0])
			#tM = time.time()
			#print("Rel traj = "+str(tM - tm)+" seconds")
			#tm = time.time()
			misc.bulk_center_mass(self.foldername, trials_name[0], self.parentSim.pars['ITER'], self.parentSim.arena.minX, self.parentSim.arena.maxX)
			#tM = time.time()
			#print("BCM = "+str(tM - tm)+" seconds")
			self.parentSim.runcount = 0


			self.num_sets += 1

		elif mode == 'save':
			# when dynamically adding subplots the default one never gets filled so we don't need it
			# self.num_crossings_fig.delaxes(self.num_crossings_fig.axes[0])
			# self.first_crossing_fig.delaxes(self.first_crossing_fig.axes[0])
			# self.last_crossing_fig.delaxes(self.last_crossing_fig.axes[0])
			# self.final_num_fig.delaxes(self.final_num_fig.axes[0])

			np.save(self.foldername + "/num_crossings.npy", self.num_crossings)
			np.save(self.foldername + "/first_cross.npy", self.first_crossing_data)
			np.save(self.foldername + "/last_cross.npy", self.last_crossing_data)
			np.save(self.foldername + "/final_num.npy", self.final_num)
			
			self.num_crossings_fig.savefig(self.foldername + "/num_crossings.png")
			self.first_crossing_fig.savefig(self.foldername + "/first_cross.png")
			self.last_crossing_fig.savefig(self.foldername + "/last_cross.png")
			self.final_num_fig.savefig(self.foldername + "/final_num.png")
			plt.close()

			# self.fnf.close()
			# self.ncf.close()
			# self.lcf.close()
			# self.fcf.close()
			#misc.bulk_nest_transfer(self.foldername)




	def plot2dkernel(self, interactions_data = None, mode = 'inter'):
		if mode == "inter":
			x = np.array(interactions_data[0])
			y = np.array(interactions_data[1])

		elif mode == "traj":
			x = np.zeros(1)
			y = np.zeros(1)
			for f in glob.glob(self.foldername + "/trajectories*.csv"):
				x_f = np.genfromtxt(f, usecols = (2), dtype = int, delimiter = ',')
				y_f = np.genfromtxt(f, usecols = (3), dtype = int, delimiter = ',')
				x = np.hstack((x, x_f))
				y = np.hstack((y, y_f))
			x = x[1:]
			y = y[1:]

		#xmin, xmax = self.parentSim.arena.minX, self.parentSim.arena.maxX
		#ymin, ymax = self.parentSim.arena.minY, self.parentSim.arena.maxY

		xmin, xmax = 0, self.parentSim.arena.dimX
		ymin, ymax = 0, self.parentSim.arena.dimY


		# Peform the kernel density estimate
		xx, yy = np.mgrid[xmin:xmax:50j, ymin:ymax:50j]
		positions = np.vstack([xx.ravel(), yy.ravel()])
		values = np.vstack([x, y])

		kernel = st.gaussian_kde(values)

		kernel.set_bandwidth(0.15)

		f = np.reshape(kernel(positions).T, xx.shape)

		fig = plt.figure()
		ax = fig.gca()
		ax.set_xlim(xmin, xmax)
		ax.set_ylim(ymin, ymax)

		# Contourf plot
		cfset = ax.contourf(xx, yy, f, cmap='Blues', alpha=0.9)
		## Or kernel density estimate plot instead of the contourf plot
		#ax.imshow(np.rot90(f), cmap='Blues', extent=[xmin, xmax, ymin, ymax])

		# Contour plot
		cset = ax.contour(xx, yy, f, colors='k')

		# Label plot
		# ax.clabel(cset, inline=1, fontsize=10)
		# ax.set_xlabel('Y1')
		# ax.set_ylabel('Y0')

		arenaIm = plt.imread(self.parentSim.arena.arFile.replace(".npy", ".gif"))
		ax.imshow(arenaIm)


		# making plots looks pretty
		ax.invert_yaxis()
		ax.set_yticklabels([])
		ax.set_xticklabels([])
		
		if mode == 'inter':
			plt.title("Interactctions kernel density estimation")
			plt.savefig(self.foldername + "/interactions_kernel_density_{}.png".format(self.parentSim.runcount))
			interactions_data2 = np.transpose(np.array(interactions_data))
			np.savetxt(self.foldername + "/interactions_{}.csv".format(self.parentSim.runcount), interactions_data2, delimiter = ',', fmt = '%s')
		elif mode == 'traj':
			plt.title("Trajectories kernel density estimation")
			plt.savefig(self.foldername + "/traj_kernel_density_{}.png".format(self.parentSim.runcount))
		plt.close()

	def simple_interactions(self, interactions_data, mode = 'run'):
		plt.figure("simple_interactions")
		plt.imshow(plt.imread(self.parentSim.arena.arFile.split('.')[0]+".gif"))
		plt.scatter(interactions_data[0], interactions_data[1], c = 'Red', alpha = 0.3)
		plt.savefig(self.foldername + "/simple_interactions{}.png".format(self.parentSim.runcount))
		plt.close()

	def parameters_dump(self, pars_dict, name = ''):
		with open(self.foldername + "/" + name + "_pars.csv", "w") as csvfile:
			w = csv.writer(csvfile)
			for key, val in pars_dict.items():
				w.writerow([key, val])
			#TODO: record bias type, activation value and other things from sim.run() paramters

	def relocate_traj(self, foldername, name):
		newfolder = '{}/{}'.format(foldername, name)
		if not os.path.exists(newfolder):
			os.makedirs(newfolder)

		for f in glob.glob('{}/trajectories*.csv'.format(foldername)):
			shutil.move(f, newfolder)

# compute mean, stddev, and stderr of the data and return it in the string
def get_writable_data(data, numtrials):
	mean_str = str(mean(data))[:8]
	try:
		stdev_str = str(stdev(data))[:8]
		stdev_num = stdev(data)
	#if not enough data to compute stdev
	except statistics.StatisticsError:
		stdev_str = '0'
		stdev_num = 0
	stderr_str =  str(stdev_num/sqrt(numtrials))[:8]

	return(mean_str + ',' + stdev_str + ',' + stderr_str + '\n')
		
		
