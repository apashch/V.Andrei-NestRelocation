#########################################
## The default set of parameters for a ##
## nest transfer experiment simulation ##
## (c) Artem Pashchinskiy, UCLA, 2019  ##
#########################################
from math import pi

pars = {
	#### General parameters
	'ARENA' : 'c0d0',			# which configuration of the arena to use; see getTypeFile in Arena.py for details
	'NUM' : 15, 				# the numer of ants in simulation
	'ITER' : 3000,				# length of simulations in iterations
								# parametrization was based on frames in 30 fps videos
								# which yields a conversion rate of 1800 iterations <-> 1 min real time 
	'SIMSPEED' : 500,			# 1 / frequency of snapshots taken for trajectories - used only if trajectories are recorded

	#### Parameters controlling walking patterns
	'ANT_STEP' : 2.3,			# mean of the step distribution (mu)
	'ANT_STEP_VAR' : 12.4, 		# variance of the step distribution (sigma)
	'ANT_STEP_MAX' : 6.44,		# maximal cut-off for the length of steps (maxstep)
	'RANDANGLE' : (-30, 30),	# DEPRECIATED
	'RANDFREQ' : 1,				# DEPRECIATED
	'ANGLEEXPMEAN':pi/1.5, # variance of normal distribution used in defining turtousity (sigma')
	'WALL' :  'deldir',			# 'deldir' - change direction until avaliable step is found;
								# 'delstep' - decrease step size until can move in the original direction;
	'MAXTRY' : 5, 				# how many attempts at avoiding an obstacle an agent will take in one timestamp
	
	#### Parameters controling bias
	'BIAS_C' : 'p',				# type of bias: 'l' for linerar, 'c' for constant, 'p' for parabolic 
	'BIAS_PAR' : 2,				# multiplier for length of step from general bias (B)
	'PARAB_ZERO' : 4,			# part of the field (1/x) that lies to the left of zero of parabolic bias in x direction 
								# (e.g. 4 stands for the bias vertex being placed at the distance of 25% of the arena length from the left edge)

	#### Parameters controlling initial placement
	'INIT_DISTR' : 'u',			# initial distribution of ants in x-axis. 'u' - uniform
								# 'ls' - right-skewed, 'rs' - left-skewed, 'e' - expontential
	'ORIGIN' : (1470, 540), 	# location of spawning region center
								# usually overwritten automatically when a specific arena is loaded
								# see getFieldType in Arena.py for more details
	'ESCALE' : 125,				# parameter of truncated exponential distr of X-coordinate of initial placement
	'SHIFT' : 300,				# DEPRECIATED


	###################################################################################

	#### Parameters controlling interaction-based activation (not used in the research)
	'ACTIVATED_BIAS_PAR' : 2,	# multiplier for length of step for the activated state
	'EXCITED_BIAS_PAR' : 5,		# multiplier for additional length of step from excited state
	
	#### Parameters controlling interactions (not used in the research)
	'EXCITMENT_TRESHOLD' : 5,   # from what excitment level (in EP - Exitement Points) new bias kicks-in
	'ONE_INTER_INCR' : 50,		# how much EP is added from one interaction with activated ant
	'ACTIVATION_ZONE' : 500,	# part of the field (1/x) around parabola zero X where ants have a chance to be activated
	'ACTIVATION_CHANCE' : 10,   # chance (1/x) ant that is in the activation zone actually gets activated
	'DEACTIVATION_DELAY' : 900, # time (in iterationss) till activated ant gets deactivated again
	'ANT_SIZE_X' : 16,
	'ANT_SIZE_Y' : 8,
	'INTER_RAD' : 8,			# radius of interaction-determining poximity
}

#### Constsnts using other parameters
#DEACTIVATION_DELAY = pars['ITER'] // 30,
								# for how many iterations AFTER reaching the center of mass an actiated ant remains activated
#pars['DEACTIVATION_DELAY'] = DEACTIVATION_DELAY[0]
