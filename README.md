# RASH

RASH: Resource Allocation for Smart Homes Considering the Privacy Sensitivity of IoT Applications.


# Requirements
The code developed and tested on Linux. To run it, you need python 3.7+ and Gurobi.
Install all dependencies via following
```
pip install -r requirements.txt
```

# Run 
```parameters.txt``` includes all parameters and their values that are set as explained in the paper. CPU cycle, bandwidth and data size are downscaled by 10**9. Time budgets are in the order of miliseconds. You can also adjust simulation configuration via following flags:

```
--objective
  Objective function:
  Possible values: min_max_p or min_max_delay
  Default: min_max_p

--postponing
  Postponing strategy:
  Possible values:  naive, ERAFL_postponing_algo, or lbp
  Default: naive

--mode
  Simulation mode:
  Possible values: pre_generated_tasks or new_tasks
  Default: new_tasks

--iterations
  Number of iterations to run the simulation
  Possible values: an integere
  Default: 10
```

To run the simulation go to core directory and run the following:
```
python main.py
```
