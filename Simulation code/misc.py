########################################
##   A variety of helper functions    ##
## making possible the collection of  ##
##    simple simulation statistics    ##
## (c) Artem Pashchinskiy, UCLA, 2019 ##
########################################

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import glob
import numpy as np
from math import sqrt
import os
import csv
import shutil
import operator


# compute center of masses movement for multiple data files in a folder
def bulk_center_mass(folder, name, iters, ymin = 0, ymax = 1800):
	foldername = '{}/{}'.format(folder, name)
	bulk_cm = np.zeros((iters, 1))

	# to calculate num of trials processed
	trial_counter = 0

	for f in glob.glob('{}/trajectories_*.csv'.format(foldername)):
		trial_counter += 1
		traj = np.genfromtxt(f, delimiter=',', dtype = int)
		cm = np.zeros((len(np.unique(traj[:, 0])), 1))
		for t in np.unique(traj[:, 0]):
			cm[t] = traj[traj[:, 0] == t][:, 2].mean()
		bulk_cm = np.hstack((bulk_cm, cm))
	bulk_cm = bulk_cm[:, 1:]

	results_mean = np.zeros(len(bulk_cm))
	results_std = np.zeros(len(bulk_cm))

	for i in range(len(results_mean)):
		results_mean[i] = bulk_cm[i].mean()
		results_std[i] = bulk_cm[i].std()

	#np.savetxt('{}/res_mean.csv'.format(foldername), results_mean, delimiter=',')
	#np.savetxt('{}/res_stdev.csv'.format(foldername), results_std, delimiter=',')

	nf = plt.figure()
	na = nf.add_subplot(111)
	na.set_ylim(ymin, ymax)
	na.plot(results_mean)
	ymid = (ymax+ymin)/2

	#plot cm curves for every trial
	for trialnum in range(len(bulk_cm[1])):
		na.plot(bulk_cm[:, trialnum], alpha = 0.12, color = 'gray')
	
	# plot averaged cm curve
	plt.axhline(y=ymid, color='r', linestyle='-')
	na.fill_between(np.arange(len(bulk_cm)), results_mean-results_std, results_mean+results_std, facecolor='blue', alpha=0.5)

	# annotate plot and save
	na.set_title("Center of mass location vs time \n (for n = {} trials)".format(trial_counter))
	na.set_xlabel("Time (iterations)")
	na.set_ylabel("Center of mass x-coordinate")
	plt.savefig('{}/cm.png'.format(foldername))
	plt.clf()

# helper function to automaticaly create plot text attributes 
# based on the data filename
def set_plot_describtion(fig, ax, filename):
		if filename == 'crossings_count_file.csv' or filename == 'num_crossings':
			fig.suptitle("Number of times when same number of ants in cold and hot")
			ax.set_ylabel("Number of events")
			return 1
		elif filename == 'final_number_file.csv' or filename == 'final_num':
			fig.suptitle("Number of ants in the cooler chamber in the end")
			ax.set_ylabel("Number of ants")
			return 1
		elif filename == 'first_crossing_file.csv' or filename == 'first_cross':
			fig.suptitle("First time when same number of ants in cold and hot")
			ax.set_ylabel("Time (iterations)")
			return 1
		elif  filename == 'last_crossing_file.csv' or filename == 'last_cross':
			fig.suptitle("Last time when same number of ants in cold and hot")
			ax.set_ylabel("Time (iterations)")
			return 1
		else:
			return 0

# compute relocation curves for multiple .csv data files in a folder
def fromcsv_bulk_nest_transfer(foldername, numtrials = 1):
	for f in glob.glob('{}/*/*_file.csv'.format(foldername), recursive = True):
		filename = f.split('/')[-1]
		if os.path.isfile('{}/{}'.format(foldername, filename)):
			with open(f) as donor:
				with open('{}/{}'.format(foldername, filename), 'a') as acceptor:
					wrt = csv.writer(acceptor, delimiter=',')
					rdr = csv.reader(donor, delimiter=',')
					for row in rdr:
						wrt.writerow(row)
			os.remove(f)
		else:
			shutil.move(f, foldername)
	for f in glob.glob('{}/*_file.csv'.format(foldername)):
		filename = f.split('/')[-1]
		aux_tdata = np.genfromtxt(f, delimiter=',', usecols = (1,2))
		name = np.genfromtxt(f, delimiter=',', usecols = (0), converters = {0: lambda s: s.decode("utf-8")}, dtype = 'U12')

		aux_tdata[:, 0] = [x for _,x in sorted(zip(name,aux_tdata[:, 0]))]
		name, aux_tdata[:, 1] = zip(*sorted(zip(name, aux_tdata[:, 1]), key=operator.itemgetter(0)))

		print(name)

		fig, ax = plt.subplots(1,1)
		ax.set_xlabel('Value of {} parameter'.format(name[0][:-2]))
		if not set_plot_describtion(fig, ax, filename):
			ax.set_title('{}'.format(filename.split('.')[0]))
		else:
			ax.set_title('(for n = {} trials)'.format(numtrials))
		ax.set_xlim(-1, len(aux_tdata[:, 0]))
		ax.set_ylim(0, np.amax(aux_tdata[:, 0])*1.25)

		# plot with error bars as stdev
		#ax.errorbar(x = np.arange(len(aux_tdata[:, 0])), y = aux_tdata[:, 0], yerr = aux_tdata[:, 1], color = 'red')
		#plot with error bars as sederror (stdev/sqrt(# of trials))
		#ax.errorbar(x = np.arange(len(aux_tdata[:, 0])), y = aux_tdata[:, 0], yerr = aux_tdata[:, 1]/sqrt(numtrials))
		#plot with error bars as sederror, DISCRETE (stdev/sqrt(# of trials))
		ax.errorbar(x = np.arange(len(aux_tdata[:, 0])), y = aux_tdata[:, 0], yerr = aux_tdata[:, 1]/sqrt(numtrials), fmt = 'o')


		# setting ledgible labels for x-axis
		if str(name[0]).isnumeric():
			all_names = [float(i.split('_')[-1][:3]) for i in name]
		else:
			all_names = [str(i) for i in name]

		names_subset = all_names
		plt.xticks(np.arange(len(aux_tdata[:, 0])), names_subset, rotation=45)
		fig.set_size_inches(12, 5)
		plt.savefig('{}/{}.png'.format(foldername, f.split('/')[-1].split('_')[0]))
		plt.clf()

# compute relocation curves for multiple .npy data files in a folder
def bulk_nest_transfer(foldername, numtrials = 1, omode = 'bp', errmode = 'stder'):
	for datatype in ['final_num', 'first_cross', 'last_cross', 'num_crossings']:
		fig, ax = plt.subplots(1, 1)

		set_plot_describtion(fig, ax, datatype)
		ax.set_title('(for n = {} trials)'.format(numtrials))

		dataoftype = list()
		labels = list()

		if omode == 'bp':
			for filename in glob.glob(foldername + "/*/{}.npy".format(datatype)):
				dataoftype.append(np.load(filename))
				labels.append(filename.split('/')[-2])

			# sort according to increasing label name
			labels, dataoftype = zip(*sorted(zip(labels, dataoftype), key=operator.itemgetter(0)))

			ax.boxplot(dataoftype, labels = labels)


		if omode == 'lin':
			for filename in glob.glob(foldername + "/*/{}.npy".format(datatype)):
				datafile = np.load(filename)
				dataoftype.append((np.mean(datafile), np.std(datafile)))
				labels.append(filename.split('/')[-2])

			labels, dataoftype = zip(*sorted(zip(labels, dataoftype), key=operator.itemgetter(0)))

			# create a numpy object of same content as list dataoftype
			aux_tdata = np.array(dataoftype)

			#print(aux_tdata.shape)
			#print(aux_tdata)

			ax.set_xlim(-1, len(dataoftype))
			ax.set_ylim(0, np.amax(aux_tdata[:, 0])*1.25)

			if errmode == 'stdev':
				# plot with error bars as stdev
				ax.errorbar(x = np.arange(len(aux_tdata[:, 0])), y = aux_tdata[:, 0], yerr = aux_tdata[:, 1], color = 'red', fmt = 'o')
			if errmode == 'stder':
				#plot with error bars as sederror (stdev/sqrt(# of trials))
				ax.errorbar(x = np.arange(len(aux_tdata[:, 0])), y = aux_tdata[:, 0], yerr = aux_tdata[:, 1]/sqrt(numtrials), fmt = 'o')

			# setting ledgible labels for x-axis
			if str(labels[0]).isnumeric():
				all_names = [float(i.split('_')[-1][:3]) for i in labels]
			else:
				all_names = [str(i) for i in labels]

			plt.xticks(np.arange(len(dataoftype)), all_names, rotation=45)

		plt.savefig('{}/{}.png'.format(foldername, datatype))
		
#bulk_center_mass('09292017_180559/act_off')