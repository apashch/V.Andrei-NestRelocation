#########################################
## An extended working exmaple of the  ##
## nest transfer experiment simulation ##
## (c) Artem Pashchinskiy, UCLA, 2019  ##
#########################################

from AntSim import *
from misc import *
from Arena import generate

# Before running on a new field a mask should be created from the image file 
# Comment out if your folder already has .npy mask of the field
# generate('4ch_2_4ch_raw.gif')

# create a simulation with parameters described in the dict file
MySim = AntSim(parameters = 'consts_dict.py') 
PP = PostProcessor(MySim)

# you can manually override parameters if needed
# speific describtions of avaliable parameters are in the dict file
MySim.loadPars(key = 'ITER', val = 3000)

#number of trials for each set of parameters
trials = 5

# A minimal example of iteration
for k in range(trials):
	# a type of bias needs to be passed to each iteration
	# otherwise a default value of 'c' will be used
	# 'c' - constant bias
	# 'l' - linearly decreasing bias
	# 'p' - parabolically decreasing bias
	MySim.run('c') 
	PP.nest_transfer(MySim.nest_transfer_data, mode = 'add')
PP.nest_transfer(MySim.nest_transfer_data, mode = 'process', name = 'test1')
PP.nest_transfer(MySim.nest_transfer_data, mode = 'save')


# More than one set of parameters can be ran at the same time
# Below is an exmaple of how to run three sets of experments 
# with increasing values of bias strength from 1.0 to 3.0

# this time there will be output to track the progress of the simulation

MySim.loadPars(key = 'BIAS_PAR', val = 1) 
for i in range(trials):
	MySim.run()
	PP.nest_transfer(MySim.nest_transfer_data, mode = 'add')
	print("In batch 1 finished {} / {}".format(i+1, trials))
PP.nest_transfer(MySim.nest_transfer_data, mode = 'process', name = 'bias_1')


MySim.loadPars(key = 'BIAS_PAR', val = 2) 
for u in range(trials):
	MySim.run()
	PP.nest_transfer(MySim.nest_transfer_data, mode = 'add')
	print("In batch 2 finished {} / {}".format(i+1, trials))
PP.nest_transfer(MySim.nest_transfer_data, mode = 'process', name = 'bias_2')

MySim.loadPars(key = 'BIAS_PAR', val = 3)
for j in range(trials):
	MySim.run()
	PP.nest_transfer(MySim.nest_transfer_data, mode = 'add')
	print("In batch 3 finished {} / {}".format(j+1, trials))
PP.nest_transfer(MySim.nest_transfer_data, mode = 'process', name = 'bias_3')

# to get output files need to have the save line in the end
PP.nest_transfer(MySim.nest_transfer_data, mode = 'save')


