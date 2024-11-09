# RASH

RASH: Resource Allocation for Smart Homes Considering the Privacy Sensitivity of IoT Applications.


# Requirements
The code developed and tested on Linux. To run it, you need python 3.7+ and Gurobi.
You can check [Gurobi website](https://support.gurobi.com/hc/en-us/articles/360044290292-How-do-I-install-Gurobi-for-Python) for instructions on installation. Install all dependencies via following:
```
pip install -r requirements.txt
```

# Run

To run the simulation go to ```core``` directory and run the following:
```
cd core 
python main.py
```
Results will be stored in ```logs``` directory. ```parameters.txt``` includes all parameters and their values that are set as explained in the paper. CPU cycle, bandwidth and data size are downscaled by 10**9. Time budgets are in the order of miliseconds. You can also adjust simulation configuration via following flags:
```
--objective
  Objective function:
  Possible values: min_max_p or min_max_delay
  Default: min_max_p

--postponing
  Postponing strategy:
  Possible values:  naive, ERAFL_postponing_algo    
  Default: naive

--mode
  Simulation mode:
  Possible values: pre_generated_tasks or new_tasks
  Default: new_tasks

--iterations
  Number of iterations to run the simulation
  Possible values: an integer
  Default: 10
  
--duration
  Duration of the simulation in seconds
  Possible values: an integer
  Default: 60
  
--deltaT
  The time period over which the decision is made (milisecond)
  Possible values: an integer
  Default: 5
```
