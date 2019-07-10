from AntSim import *
from multiprocessing import Pool, cpu_count, current_process
from functools import partial
import time, datetime
import numpy as np
import logging
import misc
import os

def run_trials(trials_num, parameter, name, value, trial_name):
	MySim = AntSim(parameters = 'consts_dict.py', name = (trial_name, name)) # creates a simulation with parameters described in the dict file
	PP = PostProcessor(MySim, (trial_name, name))
	MySim.loadPars(key = parameter, val = value)
	MySim.loadPars(key = 'ITER', val = 10000)
	for i in range(trials_num): 
		MySim.run(activation = True, saveinitialdist =  False)
		PP.nest_transfer(MySim.nest_transfer_data, mode = 'add')
		print("Process {} finished {} / {} for a value of {}".format(current_process().name, i+1, trials_num, value))
	PP.plot2dkernel(MySim.allInter)
	PP.plot2dkernel(mode = 'traj')

	t_proc_start = time.time()
	PP.nest_transfer(MySim.nest_transfer_data, mode = 'process', name = name, numtrials = trials_num)
	PP.nest_transfer(MySim.nest_transfer_data, mode = 'save')
	t_proc_end = time.time()

	#debug lines
	with open ('results/{}/log.txt'.format(trial_name), 'a+') as log:
		log.write('Processing of trial w/val {} took '.format(str(value)))
		log.write(str(t_proc_end - t_proc_start)+"\n")



def auxRunTrials(listParameters): 
	return run_trials(listParameters[0], listParameters[1], listParameters[2], listParameters[3], listParameters[4])

def run_multiple(trials, par, par_vals, trial_name, numJobs = cpu_count()):
	listParameters = [(trials, par, par[:2] + '_' + str(i), i, trial_name) for i in par_vals]
	p = Pool(numJobs)
	p.map(auxRunTrials, listParameters)

def run_multiple_frontend(parname, parval, trials, trial_name = None):
	t_start = time.time()

	if not trial_name:
		#for custom names just pass the name as a parameter trial_name
		trial_name = datetime.datetime.fromtimestamp(time.time()).strftime('%m%d%Y_%H%M%S')+'_'+str(randint(0,10000))
		

	print('Multiprocess Simulations Started for {} values and {} trials each'.format(len(parval), trials))
	run_multiple(trials, parname, parval, trial_name)

	t1 = time.time()
	misc.bulk_nest_transfer('results/{}'.format(trial_name), trials)
	t2 = time.time()
	misc.fromcsv_bulk_nest_transfer('results/{}'.format(trial_name), trials)

	t_end = time.time()
	with open ('results/{}/log.txt'.format(trial_name), 'a+') as log:
		log.write('Executed in {} seconds\n'.format(str(t_end - t_start)))
		log.write('{} values of parameter {} tested for {} trials each\n'.format(len(parval), parname, trials))
		log.write('For the last set it took \n {} seconds for npy processing\n {} deconds for csv processing\n'.format(str(t2 - t1),str(t_end - t2)))
	print('Executed in {}'.format(str(t_end - t_start)))

if __name__ == '__main__':

	parname = 'ARENA'
	#parval  = (2, 5, 10, 15)
	#parval = (3, 2, 2.5, 1.5, 4)
	#parval = np.arange(2, 4, 0.5)
	parval = [
			 	'4o_2_4o',
			 	'3o_2_3o',
			 	'c0d1-m',
			 	'c1d0',
			 	'c1d1',
			 	'2tun',
			 ]


	trials = 50

	t_total_start = time.time()

	#for trials in [2, 5, 25, 100, 500]:
	run_multiple_frontend(parname, parval, trials, 'for_spatial_activ3')
	#run_multiple_frontend(parname, parval, trials)



	print('All trial values executed in {}'.format(str(time.time() - t_total_start)))



	



