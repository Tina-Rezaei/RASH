import random
import numpy as np


def is_task_feasible(params, required_comp, time_budget, data_size):
    """Check if a generated task is feasible in terms of computation or transmission."""
    local_comp_feasible = required_comp / time_budget <= params['comp_rsc']
    remote_transmission_feasible = data_size / params['bandwidth'] + data_size / params['backhaul'] <= time_budget
    return local_comp_feasible or remote_transmission_feasible


def is_task_size_sufficient(params, required_comp, time_budget, task_load_factor):
    """Check if the task's size is above the load threshold."""
    return required_comp / time_budget >= params['comp_rsc'] * task_load_factor


def exceeds_cpu_budget(total_comp, required_comp, time_budget, cpu_cycles_budget):
    """Check if the total computation exceeds the CPU budget."""
    return sum(total_comp) + required_comp / time_budget > 1.5 * cpu_cycles_budget


def generate_compute_tasks(params, cpu_cycles_budget, current_time, time_chunk, delta_t, compute_queue, task_load_factor):
    compute_tasks = {}
    total_comp = []
    task_id = max(compute_queue.keys()) + 2 if len(compute_queue) > 0 else 1

    while True:
        data_size = random.uniform(params['execute_data_size_l'], params['execute_data_size_u'])
        required_comp = random.uniform(params['execute_required_comp_l'], params['execute_required_comp_u'])
        time_budget = int(random.uniform(params['execute_time_budget_l'], params['execute_time_budget_u']))
        arrival_time = current_time + random.uniform(0, time_chunk)
        privacy_score = random.randint(2, 9)
        criticality_score = 0

        if not is_task_feasible(params, required_comp, time_budget, data_size):
            continue

        if not is_task_size_sufficient(params, required_comp, time_budget, task_load_factor):
            continue

        if exceeds_cpu_budget(total_comp, required_comp, time_budget, cpu_cycles_budget):
            continue

        compute_tasks[task_id] = {'data_size': data_size,
                                  'untransmitted_data': data_size,
                                  'data_for_processing': data_size,
                                  'required_comp': required_comp,
                                  'remained_comp': required_comp,
                                  'time_budget': time_budget,
                                  'remained_time_budget': time_budget,
                                  'privacy_score': privacy_score,
                                  'criticality_score': criticality_score,
                                  'task_type': 'compute',
                                  'arrival_time': arrival_time,
                                  'time_slot_arrival': arrival_time // delta_t,
                                  'alpha': 0,
                                  'decided': False,
                                  'overdue': False,
                                  'completed': False
                                  }
        task_id += 2
        total_comp.append(required_comp/time_budget)
        if sum(total_comp) > cpu_cycles_budget:
            total_tasks_count = len(compute_tasks)
            time_slot_chunk = time_chunk / total_tasks_count
            i = 0
            for key, value in compute_tasks.items():
                arrival_time = current_time + random.uniform(i * time_slot_chunk, (i+1) * time_slot_chunk)
                compute_tasks[key]["arrival_time"] = arrival_time
                compute_tasks[key]["time_slot_arrival"] = arrival_time // delta_t
                i += 1

            return compute_tasks


def generate_training_tasks(params, cpu_cycles_budget, current_time, time_chunk, delta_t, training_queue, task_load_factor):
    '''
    :param params:
    :param cpu_cycles_budget: target cpu cycles budget(number of cpu cycles per second) to generate
    :param current_time:
    :param time_chunk:
    :param starting_task_id:
    :return:
    '''
    training_tasks = {}
    total_comp = []
    task_id = max(training_queue.keys()) + 2 if len(training_queue) > 0 else 0

    # If cpu budget for generating training tasks is too small then it is not possible to generate training tasks
    smallest_t_task = params['training_data_size_l'] * params['epoch_l'] * int(500 / 40 * params['model_size_l'])
    if smallest_t_task / params["training_time_budget_u"] > 1.2 * cpu_cycles_budget:
        return training_tasks

    while True:
        data_size =  random.uniform(params['training_data_size_l'], params['training_data_size_u'])
        model_size =  random.uniform(params['model_size_l'], params['model_size_u'])
        epoch = int(random.randrange(params['epoch_l'], params['epoch_u']))
        time_budget = int( random.uniform(params['training_time_budget_l'], params['training_time_budget_u']))
        computation_per_bit = int(500 / 40 * model_size)
        privacy_score = random.randint(2, 9)
        criticality_score = 0  # always zero for training tasks

        required_comp = data_size * epoch * computation_per_bit

        if not is_task_size_sufficient(params, required_comp, time_budget, task_load_factor):
            continue

        if exceeds_cpu_budget(total_comp, required_comp, time_budget, cpu_cycles_budget):
            break  # Stop if adding this task would exceed the CPU budget

        # Check if the generated task is computationally feasible either locally or remotely
        if data_size / params['bandwidth'] + required_comp/time_budget + model_size/time_budget > params['comp_rsc'] and data_size / params['bandwidth'] + data_size / params['backhaul'] > time_budget:
            continue

        # Check if the generated task is not too big
        if (required_comp / time_budget) > 0.5 * cpu_cycles_budget:
            continue

        total_comp.append(required_comp/time_budget)
        arrival_time = current_time + random.uniform(0, time_chunk)
        training_tasks[task_id] = {'data_size': data_size,
                                   'untransmitted_data': data_size,
                                   'data_for_processing': data_size,
                                   'model_size': model_size,
                                   'untransmitted_model': model_size,
                                   'epoch': epoch,
                                   'required_comp': required_comp,
                                   'remained_comp': required_comp,
                                   'time_budget': time_budget,
                                   'remained_time_budget': time_budget,
                                   'arrival_time': arrival_time,
                                   'time_slot_arrival': arrival_time // delta_t,
                                   'comp_per_bit': computation_per_bit,
                                   'privacy_score': privacy_score,
                                   'criticality_score': criticality_score,
                                   'task_type': 'training',
                                   'alpha': 0,
                                   'decided': False,
                                   'overdue': False,
                                   'completed': False
                                   }
        task_id += 2

        if sum(total_comp) > cpu_cycles_budget:
            return training_tasks

