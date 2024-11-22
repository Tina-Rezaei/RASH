import sys
import time
import argparse
from logger import *
from postponing import *
from tasks_updater import *
from decision_making import rash
from task_generator import *
from Load_tasks import load_and_reset_tasks

def pars_arguments():
    parser = argparse.ArgumentParser(description="Simulation script for task postponing and optimization.")
    parser.add_argument("--objective", type=str, default='min_max_p', choices=['min_max_p', 'min_max_delay'],
                        help='Optimization objective function: min_max_p or min_max_delay')
    parser.add_argument('--postponing', type=str, default='heuristic', choices=['heuristic', 'ERAFL_postponing_algo'],
                        help='Postponing strategy: heuristic or ERAFL_postponing_algo')
    parser.add_argument('--mode', type=str, default='new_tasks', choices=['pre_generated_tasks', 'new_tasks'],
                        help='Simulation mode: "pre_generated_tasks" to use existing tasks or "new_tasks" to generate new tasks')
    parser.add_argument('--iterations', type=int, default=10, help='Number of iterations to run the simulation')
    parser.add_argument('--deltaT', type=float, default=0.005, help='The time period over which the decision-making algorithm runs in second')
    parser.add_argument('--duration', type=float, default=60, help='Duration of the simulation in seconds.')
    parser.add_argument('--load', type=float, default=0.70, help='System load to be generated in percentage.')

    return parser.parse_args()


def read_constant_params(path):
    params = dict()
    with open(path) as f:
        lines = f.readlines()
        for line in lines:
            key, value = line.strip('\n').split(',')
            params[key] = float(value)
    return params


def calculate_system_load(training_tasks, compute_tasks, current_time):
    """
    calculates total load of the system per second which was handled by the optimizer
    :param training_tasks: a dict of training tasks
    :param compute_tasks: a dict of compute tasks
    :return: two floats: one for handled load and one for used backhaul capacity
    """
    total_current_comp_load = 0
    total_current_backhaul_load = 0
    all_tasks = {**training_tasks, **compute_tasks}
    for task_id, task_specs in all_tasks.items():
        if not task_specs['completed'] and not task_specs['overdue'] and task_specs['arrival_time'] <= current_time:
            if task_specs["alpha"] == 1:
                total_current_backhaul_load += task_specs['data_for_processing'] / task_specs['remained_time_budget']
            else:
                total_current_comp_load += task_specs['remained_comp'] / task_specs['remained_time_budget']

    return total_current_comp_load, total_current_backhaul_load


def check_constraints(solver_solution):
    for task_id in solver_solution.i:
        if pyo.value(solver_solution.B[task_id]) == 'unknown':
            return False
    return True


def optimization_executor(c_queue, t_queue, params, iteration, current_time, time_slot, sim_mode):
    c_execution_queue = {}
    t_execution_queue = {}

    for task_id, task_specs in c_queue.items():
        if not task_specs['completed'] and not task_specs['overdue'] and task_specs['arrival_time'] <= current_time:
            c_execution_queue.update({task_id: task_specs})
    for task_id, task_specs in t_queue.items():
        if not task_specs['completed'] and not task_specs['overdue'] and task_specs['arrival_time'] <= current_time:
            t_execution_queue.update({task_id: task_specs})
    if len(c_execution_queue) == 0 and len(t_execution_queue) == 0:  # no task for execution
        return None, {}, {}

    while True:
        start = time.time()
        solver_solution, solver_status = rash(params, c_execution_queue, t_execution_queue, sim_mode)
        end = time.time()
        if time_slot % 1000 == 0:
            log_function(f"decision making time: {end - start}")
        if solver_status == 'optimal':
            return solver_solution, c_execution_queue, t_execution_queue

        elif solver_status == 'maxTimeLimit':
            result = check_constraints(solver_solution)
            if result:
                return solver_solution, c_execution_queue, t_execution_queue
            else:
                return solver_solution, {}, {}

        if len(c_execution_queue) + len(t_execution_queue) <= 1:
            for task_id, task_specs in c_execution_queue.items():
                c_queue[task_id]["overdue"] = True
            for task_id, task_specs in t_execution_queue.items():
                t_queue[task_id]["overdue"] = True
            return solver_solution, {}, {}

        # there is no optimal or feasible solution, so, postpone some tasks
        postponing_function = postponing_strategies.get(sim_mode["postponing"])
        if postponing_function:
            c_execution_queue, t_execution_queue = postponing_function(
                c_execution_queue, t_execution_queue, params, f'{path_to_save}/{iteration}', time_slot)
        else:
            raise ValueError(f"Unknown postponing strategy: {sim_mode['postponing']}")


def setup_simulation():
    args = pars_arguments()
    param_path = './parameters.txt'
    params = read_constant_params(param_path)

    load = args.load
    iterations = args.iterations
    sim_duration = args.duration * 1000  # convert second to ms
    delta_t = args.deltaT * 1000 # ms
    target_constant_load = load * params['comp_rsc']  # target load per second
    c_load =  target_constant_load
    t_load = 0 * target_constant_load
    task_size_factor = 0.008  # determines task size
    training_tasks_ratio = 1/3  # ratio of training tasks when generating new tasks
    compute_tasks_ratio = 2/3  # ratio of compute tasks when generating new tasks
    logging_frequency = 1  # save logs every 1000 time slots
    max_time_slot = int((sim_duration // delta_t) - 1)
    all_tasks_file = f'time_slot_{max_time_slot}.csv'

    postponing_strategies = {
        "heuristic": heuristic_postponing,
        "ERAFL_postponing_algo": ERAFL_postponing_algo,
    }

    sim_mode = {
        "mode": args.mode,
        "postponing": args.postponing,
        "objective": args.objective
    }

    path_to_save = f'../logs/load_{load}/obj_{sim_mode["objective"]}/postponing_{sim_mode["postponing"]}/duration_{args.duration}/deltaT_{args.deltaT}'
    path_to_load = f'../logs/load_{load}/obj_{sim_mode["objective"]}/postponing_{sim_mode["postponing"]}/duration_{args.duration}/deltaT_{args.deltaT}'

    # Create necessary directories
    logger.create_directories(path_to_save, iterations)

    return load, iterations, sim_duration, delta_t, all_tasks_file, target_constant_load, c_load, t_load, sim_mode, task_size_factor, path_to_save, path_to_load, training_tasks_ratio, compute_tasks_ratio, postponing_strategies, params, logging_frequency


if __name__ == '__main__':

    (load, iterations, sim_duration, delta_t, all_tasks_file,
     target_constant_load, c_load, t_load, sim_mode, task_size_factor,
     path_to_save, path_to_load, training_tasks_ratio, compute_tasks_ratio,
     postponing_strategies, params, logging_frequency) = setup_simulation()

    method_name = 'RASH'

    for iteration in range(0, 10):
        start_time = time.time()
        training_queue = {}
        compute_queue = {}
        tasks_report_log = []
        rsc_report_log = []
        load_log = []

        for time_slot in range(int(sim_duration // delta_t)):
            current_time = time_slot * delta_t

            if sim_mode["mode"] == "pre_generated_tasks":
                # load tasks from the csv file
                if time_slot == 0:
                    compute_tasks, training_tasks = load_and_reset_tasks(
                        os.path.join(path_to_load, f'{iteration}', all_tasks_file), delta_t)
                    # add tasks to task queues
                    compute_queue.update(compute_tasks)
                    training_queue.update(training_tasks)

                # calculate the current load of the system at the current time slot
                total_system_load, total_backhaul_load = calculate_system_load(training_queue, compute_queue, current_time)
                load_increment = target_constant_load - total_system_load

            if sim_mode["mode"] == "new_tasks":
                if time_slot == 0:  # generate the initial load for the first time slot
                    compute_tasks = generate_compute_tasks(params, c_load, current_time, 0,
                                                           delta_t, compute_queue, task_size_factor)
                    training_tasks = generate_training_tasks(params, t_load, current_time, 0, delta_t,
                                                             training_queue, task_size_factor)
                    # add newly generated tasks to task queues
                    compute_queue.update(compute_tasks)
                    training_queue.update(training_tasks)
                    save_tasks({**compute_queue, **training_tasks}, time_slot, f'{path_to_save}/{iteration}')

                elif total_system_load < (2 / 3) * target_constant_load:
                    c_load_increment = load_increment * compute_tasks_ratio
                    t_load_increment = load_increment * training_tasks_ratio
                    compute_tasks = generate_compute_tasks(params, c_load_increment, current_time,
                                                           0, delta_t, compute_queue, task_size_factor)
                    # training_tasks = generate_training_tasks(params, t_load_increment, current_time, 0, delta_t,
                    #                                          training_queue, task_size_factor)

                    save_tasks({**compute_queue, **training_tasks}, time_slot, f'{path_to_save}/{iteration}')
                    # add newly generated tasks to task queues
                    compute_queue.update(compute_tasks)
                    training_queue.update(training_tasks)
                total_system_load, total_backhaul_load = calculate_system_load(training_queue, compute_queue, current_time)
                load_increment = target_constant_load - total_system_load
            # run optimization for all tasks
            solved_model, c_executed_task, t_executed_task = optimization_executor(compute_queue,
                                                                                   training_queue,
                                                                                   params,
                                                                                   iteration,
                                                                                   current_time,
                                                                                   time_slot,
                                                                                   sim_mode)
            # calculate handled system load
            handled_comp_load, handled_bakchaul = calculate_system_load(t_executed_task, c_executed_task, current_time)
            load_log.append({"total_backhaul_load": total_backhaul_load,
                             "total_system_load": total_system_load,
                             "handled_load_per_slot": handled_comp_load})

            # update tasks budget
            compute_queue, training_queue, overdue_tasks = update_tasks(compute_queue,
                                                                        training_queue,
                                                                        c_executed_task,
                                                                        t_executed_task,
                                                                        params,
                                                                        solved_model,
                                                                        current_time,
                                                                        delta_t,
                                                                        time_slot,
                                                                        f'{path_to_save}/{iteration}')

            # log
            tasks_report_log = record_tasks_report(compute_queue, training_queue, c_executed_task, t_executed_task, overdue_tasks,
                                                   time_slot,
                                                   f'{path_to_save}/{iteration}', current_time, tasks_report_log)
            rsc_report_log = record_model_report(solved_model, rsc_report_log)

            # write the recorded log
            if time_slot % logging_frequency == 0:
                save_tasks_report(os.path.join(path_to_save, str(iteration), 'tasks_report.csv'), tasks_report_log)
                save_model_report(os.path.join(path_to_save, str(iteration), 'rec_usage_summary.csv'), rsc_report_log)
                save_load_report(os.path.join(path_to_save, str(iteration), 'load_history.csv'), load_log)
                print(f'iteration : {iteration}, time slot number: {time_slot}. tasks are logged.')
                tasks_report_log = []
                rsc_report_log = []
                load_log = []

        # write the final log
        save_tasks_report(os.path.join(path_to_save, str(iteration), 'tasks_report.csv'), tasks_report_log)
        save_model_report(os.path.join(path_to_save, str(iteration), 'rec_usage_summary.csv'), rsc_report_log)
        save_load_report(os.path.join(path_to_save, str(iteration), 'load_history.csv'), load_log)

        # save all the tasks and their specs and the model
        save_tasks({**compute_queue, **training_tasks}, time_slot, f'{path_to_save}/{iteration}')

        end_time = time.time()
        log_function(f'{end_time - start_time}, load {load}, iteration {iteration}, simulation run time: {sim_duration}, obj {sim_mode["objective"]}, postponing {sim_mode["postponing"]}')

