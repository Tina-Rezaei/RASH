import os
import sys
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import TerminationCondition


def constraint_total_bandwidth_usage(model, bandwidth_budget):
    return pyo.summation(model.B) <= bandwidth_budget


def constraint_total_bandwidth_auxiliary(model, i):
    return model.b[i] * model.B[i] == 1


def constraint_total_backhaul_bandwidth(model, backhaul_bandwidth_budget):
    return sum(model.alpha[i] * model.bB[i] for i in model.i) <= backhaul_bandwidth_budget

def constraint_total_backhaul_auxiliary(model, i):
    return model.bb[i] * model.bB[i] == 1


def constraint_total_cpu_frequency(model, cpu_cycle_frequency):
    return pyo.summation(model.F) <= cpu_cycle_frequency


def constraint_total_cpu_frequency_auxiliary(model, i):
    return model.f[i] * model.F[i] == 1


def constraint_time_budget_training(model, i):
    return model.alpha[i] * (model.D[i] * model.b[i] + model.D_p[i] * model.bb[i]) + \
        (1 - model.alpha[i]) * (model.D[i] * model.b[i] + model.D_p[i] * model.e[i] * model.N_c[i] * model.f[i] +
                                (model.M[i] * model.bb[i])) <= model.t[i]


def constraint_time_budget_compute(model, i):
    return model.alpha[i] * (model.D[i] * model.b[i] + model.D[i] * model.bb[i]) + \
        (1 - model.alpha[i]) * (model.D[i] * model.b[i] + model.Z[i] * model.f[i]) <= model.t[i]


def constraint_risk(model, i):
    return model.r[i] == model.p[i] * model.alpha[i]


def constraint_risk_auxiliary(model, i):
    return model.R >= model.r[i]


def constraint_time_auxiliary_compute(model, i):
    return model.T >= model.alpha[i] * (model.D[i] * model.b[i] + model.D_p[i] * model.bb[i]) + \
                (1 - model.alpha[i]) * (model.D[i] * model.b[i] + model.D_p[i] * model.e[i] * model.N_c[i] * model.f[i] +
                                (model.M[i] * model.bb[i]))


def constraint_time_auxiliary_training(model, i_c):
    return model.T >= model.alpha[i_c] * (model.D[i_c] * model.b[i_c] + model.D[i_c] * model.bb[i_c]) + \
               (1 - model.alpha[i_c]) * (model.D[i_c] * model.b[i_c] + model.Z[i_c] * model.f[i_c])


def objective_risk_minimization(model):
    return model.R


def objective_delay_minimization(model):
    return model.T


def rash(constant_params, compute_tasks, training_tasks, sim_mode):
    bandwidth_budget, backhaul_bandwidth_budget, cpu_cycle_frequency = constant_params['bandwidth'], constant_params['backhaul'], constant_params['comp_rsc']

    # all training tasks params
    t_tasks_data_size = {}
    t_tasks_tobe_processed_data_size = {}
    t_tasks_model_size = {}
    t_tasks_required_comp = {}
    t_tasks_time_budget = {}
    t_tasks_privacy_score = {}
    t_tasks_criticality_score = {}
    t_tasks_epoch = {}
    t_tasks_comp_per_bit = {}
    t_tasks_ids = []

    # all compute tasks params
    c_tasks_data_size = {}
    c_tasks_tobe_processed_data_size = {}
    c_tasks_required_comp = {}
    c_tasks_time_budget = {}
    c_tasks_privacy_score = {}
    c_tasks_criticality_score = {}
    c_tasks_ids = []

    for task_id, specs in training_tasks.items():
        t_tasks_data_size[task_id] = training_tasks[task_id]['untransmitted_data']
        t_tasks_tobe_processed_data_size[task_id] = training_tasks[task_id]['data_for_processing']
        t_tasks_model_size[task_id] = training_tasks[task_id]['model_size']
        t_tasks_required_comp[task_id] = training_tasks[task_id]['remained_comp']
        t_tasks_time_budget[task_id] = training_tasks[task_id]['remained_time_budget']
        t_tasks_privacy_score[task_id] = training_tasks[task_id]['privacy_score']
        t_tasks_criticality_score[task_id] = training_tasks[task_id]['criticality_score']
        t_tasks_epoch[task_id] = training_tasks[task_id]['epoch']
        t_tasks_comp_per_bit[task_id] = training_tasks[task_id]['comp_per_bit']
        t_tasks_ids.append(task_id)

    for task_id, specs in compute_tasks.items():
        c_tasks_data_size[task_id] = compute_tasks[task_id]['untransmitted_data']
        c_tasks_required_comp[task_id] = compute_tasks[task_id]['remained_comp']
        c_tasks_tobe_processed_data_size[task_id] = compute_tasks[task_id]['data_for_processing']
        c_tasks_time_budget[task_id] = compute_tasks[task_id]['remained_time_budget']
        c_tasks_privacy_score[task_id] = compute_tasks[task_id]['privacy_score']
        c_tasks_criticality_score[task_id] = compute_tasks[task_id]['criticality_score']
        c_tasks_ids.append(task_id)


    model = pyo.ConcreteModel()

    model.i = pyo.Set(initialize=t_tasks_ids + c_tasks_ids)
    model.i_t = pyo.Set(initialize=t_tasks_ids)
    model.i_c = pyo.Set(initialize=c_tasks_ids)

    # training tasks params
    model.M = pyo.Param(model.i_t, initialize=t_tasks_model_size)

    # common parameters
    t_tasks_data_size.update(c_tasks_data_size)
    model.D = pyo.Param(model.i, initialize=t_tasks_data_size)

    t_tasks_tobe_processed_data_size.update(c_tasks_tobe_processed_data_size)
    model.D_p = pyo.Param(model.i, initialize=t_tasks_tobe_processed_data_size)

    t_tasks_time_budget.update(c_tasks_time_budget)
    model.t = pyo.Param(model.i, initialize=t_tasks_time_budget)

    t_tasks_privacy_score.update(c_tasks_privacy_score)
    model.p = pyo.Param(model.i, initialize=t_tasks_privacy_score)

    t_tasks_required_comp.update(c_tasks_required_comp)
    model.Z = pyo.Param(model.i, initialize=t_tasks_required_comp)

    model.e = pyo.Param(model.i, initialize=t_tasks_epoch)

    model.N_c = pyo.Param(model.i, initialize=t_tasks_comp_per_bit)

    # maximum privacy-sensitivity score
    max_p = max([value for key, value in t_tasks_privacy_score.items()])

    #  variables
    model.F = pyo.Var(model.i, bounds=(0.0001, cpu_cycle_frequency))  # Frequency variables

    model.B = pyo.Var(model.i, bounds=(0.0001, bandwidth_budget))  # Bandwidth variables

    model.bB = pyo.Var(model.i, bounds=(0.0001, backhaul_bandwidth_budget))  # Backhaul Bandwidth variables

    model.alpha = pyo.Var(model.i, domain=pyo.Binary)

    model.f = pyo.Var(model.i, bounds=(1 / cpu_cycle_frequency, 1 / 0.001))  # auxilary variable

    model.b = pyo.Var(model.i, bounds=(1 / bandwidth_budget, 1 / 0.001))  # auxilary variable for bandwidth

    model.bb = pyo.Var(model.i,
                       bounds=(1 / backhaul_bandwidth_budget, 1 / 0.001))  # auxilary variable for backhaul bandwidth

    model.r = pyo.Var(model.i, bounds=(0, max_p))

    model.R = pyo.Var(within=pyo.Integers, bounds=(0, max_p))

    model.T = pyo.Var(bounds=(0, 310000))  # up to 300000 ms (5m)

    model.s = Var(model.i, domain=pyo.Binary)  # satisfaction

    # set alpha based on the status of "decided" parameter and current value of alpha
    for task_id, task_specs in compute_tasks.items():
        if task_specs['decided'] == True:
            if task_specs['alpha'] < 0.5:
                model.alpha[task_id].fixed = True
                model.alpha[task_id].value = 0

            else:
                model.alpha[task_id].fixed = True
                model.alpha[task_id].value = 1

    for task_id, task_specs in training_tasks.items():
        if task_specs['decided'] == True:
            if task_specs['alpha'] < 0.5:
                model.alpha[task_id].fixed = True
                model.alpha[task_id].value = 0

            else:
                model.alpha[task_id].fixed = True
                model.alpha[task_id].value = 1

    # constraints
    model.Constraint1 = pyo.Constraint(expr=constraint_total_bandwidth_usage(model, bandwidth_budget))
    model.Constraint2 = pyo.Constraint(expr=constraint_total_backhaul_bandwidth(model, backhaul_bandwidth_budget))
    model.Constraint3 = pyo.Constraint(expr=constraint_total_cpu_frequency(model, cpu_cycle_frequency))
    model.Constraint4 = pyo.Constraint(model.i, rule=constraint_total_bandwidth_auxiliary)
    model.Constraint5 = pyo.Constraint(model.i, rule=constraint_total_backhaul_auxiliary)
    model.Constraint6 = pyo.Constraint(model.i, rule=constraint_total_cpu_frequency_auxiliary)
    model.Constraint7 = pyo.Constraint(model.i_t, rule=constraint_time_budget_training)
    model.Constraint8 = pyo.Constraint(model.i_c, rule=constraint_time_budget_compute)

    if sim_mode["objective"] == "min_max_p":
        model.Constraint9 = pyo.Constraint(model.i, rule=constraint_risk)
        model.Constraint10 = pyo.Constraint(model.i, rule=constraint_risk_auxiliary)
        model.OBJ = pyo.Objective(expr=objective_risk_minimization(model), sense=pyo.minimize)
    elif sim_mode["objective"] == "min_max_delay":
        model.Constraint9 = pyo.Constraint(model.i_t, rule=constraint_time_auxiliary_compute)
        model.Constraint10 = pyo.Constraint(model.i_c, rule=constraint_time_auxiliary_training)
        model.OBJ = pyo.Objective(expr=objective_delay_minimization(model), sense=pyo.minimize)

    instance = model.create_instance()

    # call solver
    opt = pyo.SolverFactory('gurobi')

    # change solver options
    opt.options['timelimit'] = 5
    opt.options['NonConvex'] = 2
    opt.options['Presolve'] = 1
    # opt.options['ScaleFlag'] = 2
    opt.options['ObjScale'] = -1
    opt.options['AggFill'] = 0
    opt.options['Method'] = 4
    # opt.options['Method'] = 3
    opt.options['logfile'] = 'gurobi.log'
    opt.options['BarHomogeneous'] = 1
    opt.options['InfUnbdInfo'] = 1

    try:
        # Uncomment the following two lines to see the solver details
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")

        # solve the problem
        solver_parameters = "ResultFile=model.ilp"
        results = opt.solve(instance, tee=True, options_string=solver_parameters)
        # instance.display()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if results.solver.termination_condition == TerminationCondition.infeasible:
            print("---------- INFEASIBLE ---------")
            # solver_model = opt._solver_model()
            # solver_model.computeIIS()
            # solver_model.write("model.ilp")
            print("IIS written to model.ilp")
            instance.write('infeasible.lp', io_options={'symbolic_solver_labels': True})
            # instance.display()
            return instance, results.solver.termination_condition

        elif results.solver.termination_condition == TerminationCondition.maxTimeLimit:
            print("Time limit reached")
            return instance, results.solver.termination_condition

        elif results.solver.termination_condition != TerminationCondition.optimal:
            print("non_optimal")
        # print(results.solver.termination_condition)
        # print(results.solver.status)
        return instance, results.solver.termination_condition
    except Exception as e:
        # Enable std out to ses the error
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        instance.write('infeasible.lp', io_options={'symbolic_solver_labels': True})
        print(f'Error raised in decision making \n {e}')
        return instance, e


