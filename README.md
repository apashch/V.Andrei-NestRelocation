# V.Andrei-NestRelocation
Simulation source code and data files for the harvester ants nest relocation paper ***(DOI link)***

TL;DR: [here](Poster.pdf) is a poster about our research and the simulation and [here](Presentation.pptx) are some slides

## What are we doing here?
This is an agent-based simulation of the experiment where *Veromessor Andrei* ants are moving between artifical ant nests. One of the nests is heated up, which creates the incentive for the ants (agents) to move out of it and occupy the second (cooler) nest.

<img src="./Graphics for README/relocation.png" width=450px >

Even though there is incentive for the ants to evetually relocate to the cooler structure, we assume independent and stochastic decision making meachanism for individual ants at every time step. The heat influence is incorporated as a factor that makes agents' random movements more biased towards one of the directions. Below is a schematic of the step generation process

<img src="./Graphics for README/Step_Generation4.png" width=450px >

And here is an intuitive visual represnetation of how the bias works:

<img src="./Graphics for README/movement.png" width=450px>

## Structure of the code

Simulation source code is split into multiple files.

#### Main files containing the simulation logic

* [AntSim.py](./Simulation%20code/AntSim.py) - contains the main loop

* [Arena.py](./Simulation%20code/Arena.py) - contains the Arena class describing the state of the simulated nest (field)
* [Ant.py](./Simulation%20code/Ant.py) - contains the Ant class describing simulated agents

#### Additional files with the simulation logic

* [misc.py](./Simulation%20code/misc.py) - small helper functions that dont fit into any of the tree components above

#### Resources

* [raw_fields](./Simulation%20resources/fields_raw/) - folder with b/w contours of the used arenas (to add new arenas you need to put your file into the raw_fields folder and then run 'generate()' function from the Arena.py file on it. More instructions inside Arena.py as comments)
* [const_dict.py](./Simulation%20code/consts_dict.py) - a dictionary with default values of simulation parameters

#### Graphical output

* [PostProcessor.py](./Simulation%20code/PostProcessor.py) - contains several functions for converting raw simulation results into meaningful plots

#### Usability

* [MultiThreads.py](./Simulation%20code/MultiThreads.py) - contains routines for parallelizing multi-simulatuons runs between multiple cores (still in beta)
* [Example.py](./Simulation%20code/Example.py) and [Example_minimal.py](./Simulation%20code/Example_minimal.py) - show some of the simulation API in actions

## Output

#### Below are some examples of what can be obtained as immideate results of the simulation run:

* trajectrories data file

  * turned ON by default, to turn OFF, set flag *recordcsv = False* when calling AntSim.run()

* trajectories visualisation 

  * producing this slows down the simulation significantly

  * turned OFF by default, to turn ON, set flag *drawing = True* when calling AntSim.run()

  <img src="./Graphics for README/trajectories.png" width=450px >

* initial positions visualisation + PDF of the used x-axis distrubution of initial positions

  * turned OFF by default, to turn ON, set flag *saveinitialdist = True* when calling AntSim.run()

  <img src="./Graphics for README/initial.png" width=450px >

#### And here are some examples of what can be obtained using the PostProcessor module on top of the simulation:

* Density estimate of the trajectories

  <img src="./Graphics for README/trajectories_kde.png" width=450px >

* Timed counts of agents in hot and cold nests respectively (also known as *crossings plot*)

  <img src="./Graphics for README/crossings.png" width=450px >

## Running simulations in bulk

*Instructions on using the bulk mode and obtaining the correponding plots can be found in the block comment on the lines 68-74 of the [PostProcesor module](./Simulation%20code/PostProcesor.py). A complete example of the corresponding API commands lives [here](./Simulation%20code/Exmaple.py). There are two levels of bulk mode:*

### 1. Many trials

Due to a stochastic nature of the simulation, results of the two indeendent runs under the same set of parameter values will be different. To get a good idea of how the system behaves with given values, one  might want to run many instances (trials) of the simulation and look at the summary statistics of the obtained metrics. The PostProcessor module can collect these metrics automatically. If multiple trials are added to the PostProcessor, it can produce the following plots:

* Boxplot of the first crossing time (the first time when half of the agents is in the heated nest and half is in the cold)

  <img src="./Graphics for README/first_trials.png" width=450px >
  
* Boxplot of the last crossing time (the last time when half of the agents is in the heated nest and half is in the cold)

  <img src="./Graphics for README/last_trials.png" width=450px >
  
* Boxplot of the total number of crossings (how many times during the simulation there was a 50/50 split between agents in the cold and the heated nests)

  <img src="./Graphics for README/numcrossings_trials.png" width=450px >
  
* Boxplot of how many agents were located in the cold nest at the end of the simulation

  <img src="./Graphics for README/finalnum_trials.png" width=450px >
  
* Trajectories of the geometrical center of mass for all agents in the x-direction 

  <img src="./Graphics for README/cm.png" width=450px >

* Averaged density estimate of trajectories

  <img src="./Graphics for README/trajectories_kde.png" width=450px >

### 2. Exploring a parameter space

Perhaps, for research purposes the most interesting application of this model would be to compare the behavior of the system under different values of a parameter drawn from a certain space. To fascilitate such observations, PostProcessing module is also capable of stroing results for multiple sets of multi-trial runs (with the idea that each set of simulations is ran with a new value of the parameter). 

Each of the four boxplot types described above, can be produced for more than one set of simulations simultaneously.

* For example, here we explored the final number of ants in the cold nest as a function of the architecture of the arena

  <img src="./Graphics for README/final_num_pars.png" width=450px >

* And here, how the heat implementation affects the final number of the relocated agents (spoiler: it does not)

  <img src="./Graphics for README/final_num_pars2.png" width=450px >

Such large-scale experiments can take significant amount of time, so we suggest using [our parallelization tool](./Simulation%20code/MultiThreads.py) to simulate each of the parameter values on a separate core.







