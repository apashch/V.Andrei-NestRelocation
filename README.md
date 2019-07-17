# V.Andrei-NestRelocation
Simulation source code and data files for the harvester ants nest relocation paper ***(DOI link)***

TL;DR: [here](Poster.pdf) is a poster about our research and the simulation and [here](presentation.pptx) are some slides

## What are we doing here?
This is an agent-based simulation of the experiment where *Veromessor Andrei* ants are moving between artifical ant nests. One of the nests is heated up, which creates the incentive for the ants (agents) to move out of it and occupy the second (cooler) nest.

<img src="./Graphics for README/relocation.png" width=450px >

Even though there is incentive for the ants to evetually relocate to the cooler structure, we assume independent and stochastic decision making meachanism for individual ants at every time step. The heat influence is incorporated as a factor that makes agents' random movements more biased towards one of the directions. Below is a schematic of the step generation process

<img src="./Graphics for README/Step_Generation4.png" width=450px >

And here is an intuitive visual represnetation of how the bias works:

<img src="./Graphics for README/movement.png" width=450px>

## Structure of the code

Simulation source code is split into multiple files.

#### Main files with simulation logic

* AntSim.py - contains the main loop

* Arena.py - contains the Arena class describing the state of the simulated nest (field)
* Ant.py - contains the Ant class describing simulated agents

#### Additional files with simulation logic

* misc.py - small helper functions that dont fit into any of the tree components above

#### Resources

* raw_fields - folder with b/w contours of the used arenas (to add new arenas you need to put your file into the raw_fields folder and then run 'generate()' function from the Arena.py file on it. More instructions inside Arena.py as comments)
* const_dict.py - a dictionary with default values of simulation parameters

####Graphical output

* PostProcessor.py - contains several functions for converting raw simulation results into meaningful plots

#### Usability

* MultiThreads.py - contains routines for parallelizing multi-simulatuons runs between multiple cores (still in beta)
* Example.py and Example_minimal.py - show some of the simulation API in actions

Here is a schematic of how a typical experiment is ran

***image***

## Output

#### Below are some examples of what can be obtained as immideate results of the simulation run:

* trajectrories data file

  * turned ON by default, to turn OFF, set flag *recordcsv = False* when calling AntSim.run()

* trajectories visualisation 

  * producing this slows down the simulation significantly

  * turned OFF by default, to turn ON, set flag *drawing = True* when calling AntSim.run()

  ![trajectories_1](/Users/Artem/Documents/GitHub/AntSimLib/results/06192018_002426_9002/trajectories_1.png)

* initial positions visualisation + PDF of the used x-axis distrubution of initial positions

  * turned OFF by default, to turn ON, set flag *saveinitialdist = True* when calling AntSim.run()

  ![initial](/Users/Artem/Documents/GitHub/V.Andrei-NestRelocation/Graphics for README/initial.png)

#### And here are some examples of what can be obtained using the PostProcessor module on top of the simulation:

* Density estimate of the trajectories

  ![trajectories_kde](/Users/Artem/Documents/GitHub/V.Andrei-NestRelocation/Graphics for README/trajectories_kde.png)

* Timed counts of agents in hot and cold nests respectively (also known as *crossings plot*)

  ![crossings](/Users/Artem/Documents/GitHub/V.Andrei-NestRelocation/Graphics for README/crossings.png)

## Running simulations in bulk

**Instructions on using the bulk mode and obtaining the correponding plots can be found in the block comment on the lines 68-74 of the [PostProcesor module](./Simulation code/PostProcesor.py). A complete example of the corresponding API commands lives [here](./Simulation code/Exmaple.py). There are two levels of bulk mode:**

### 1. Many trials

Due to a stochastic nature of the simulation, results of the two indeendent runs under the same set of parameter values will be different. To get a good idea of how the system behaves with given values, one  might want to run many instances (trials) of the simulation and look at the summary statistics of the obtained metrics. The PostProcessor module can collect these metrics automatically. If multiple trials are added to the PostProcessor, it can produce the following plots:

* Boxplot of the first crossing time (the first time when half of the agents is in the heated nest and half is in the cold)

  ![first_trials](/Users/Artem/Documents/GitHub/V.Andrei-NestRelocation/Graphics for README/first_trials.png)
  
* Boxplot of the last crossing time (the last time when half of the agents is in the heated nest and half is in the cold)

  ![last_trials](/Users/Artem/Documents/GitHub/V.Andrei-NestRelocation/Graphics for README/last_trials.png)
  
* Boxplot of the total number of crossings (how many times during the simulation there was a 50/50 split between agents in the cold and the heated nests)

  ![numcrossings_trials](/Users/Artem/Documents/GitHub/V.Andrei-NestRelocation/Graphics for README/numcrossings_trials.png)
  
* Boxplot of how many agents were located in the cold nest at the end of the simulation

  
  
    ![finalnum_trials](/Users/Artem/Documents/GitHub/V.Andrei-NestRelocation/Graphics for README/finalnum_trials.png)
  
* Trajectories of the geometrical center of mass for all agents in the x-direction 

  ![cm](/Users/Artem/Documents/GitHub/V.Andrei-NestRelocation/Graphics for README/cm.png)

* Averaged density estimate of trajectories

  ![traj_kernel_density_50](/Users/Artem/Documents/GitHub/AntSimLib/results/GCloud-res/for_spatial_nosize-60/AR_2tun/traj_kernel_density_50.png)

### 2. Exploring a parameter space

Perhaps, for research purposes the most interesting application of this model would be to compare the behavior of the system under different values of a parameter drawn from a certain space. To fascilitate such observations, PostProcessing module is also capable of stroing results for multiple sets of multi-trial runs (with the idea that each set of simulations is ran with a new value of the parameter). 

Each of the four boxplot types described above, can be produced for more than one set of simulations simultaneously.

* For example, here we explored the final number of ants in the cold nest as a function of the architecture of the arena

![final_num_pars](/Users/Artem/Documents/GitHub/V.Andrei-NestRelocation/Graphics for README/final_num_pars.png)

* And here, how the heat implementation affects the final number of the relocated agents (spoiler: it does not)

  ![final_num_pars2](/Users/Artem/Documents/GitHub/V.Andrei-NestRelocation/Graphics for README/final_num_pars2.png)

Such large-scale experiments can take significant amount of time, so we suggest using [our parallelization tool](./simulation code/MultiThreads) to simulate each of the parameter values on a separate core.







