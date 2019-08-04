#########################################
##  A minimal working exmaple of the   ##
## nest transfer experiment simulation ##
## (c) Artem Pashchinskiy, UCLA, 2019  ##
#########################################

from AntSim import *
from misc import *

# create a simulation with parameters described in the dict file
MySim = AntSim(parameters = 'consts_dict.py') 
PP = PostProcessor(MySim)

#number of trials for each set of parameters
trials = 3

# A minimal example of iteration with deafult parameters
for k in range(trials):
	MySim.run() 
	PP.nest_transfer(MySim.nest_transfer_data, mode = 'add')
PP.nest_transfer(MySim.nest_transfer_data, mode = 'process', name = 'test_minimal')
PP.nest_transfer(MySim.nest_transfer_data, mode = 'save')