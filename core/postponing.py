import os
import json
import logger


def log_postponement(tasks_ids, time_slot, path_to_save):
    if os.path.exists(os.path.join(path_to_save, 'postponement_log')):
        with open(os.path.join(path_to_save, 'postponement_log'), 'r') as f:
            postpone_dict = json.load(f)
        elements = postpone_dict.get(str(time_slot),[])
        elements.append(tasks_ids)
        postpone_dict[time_slot] = elements
        with open(os.path.join(path_to_save, 'postponement_log'), 'w') as f:
            json.dump(postpone_dict, f)
    else:
        with open(os.path.join(path_to_save, 'postponement_log'), 'w') as f:
            json.dump({time_slot:[tasks_ids]}, f)


def calculate_total_demand(compute_tasks, training_tasks):
    total_f = 0
    total_b = 0
    all_tasks = {}

    # Calculate total computation and bandwidth demand
    for task_id, task_specs in {**compute_tasks, **training_tasks}.items():
        if task_specs["alpha"] == 0:
            total_f += task_specs['remained_comp'] / task_specs['remained_time_budget']
        else:
            total_b += task_specs['untransmitted_data'] / task_specs['remained_time_budget']
        all_tasks[task_id] = task_specs

    return total_f, total_b, all_tasks


def postpone_excessive_computation(all_tasks_sorted, f_excessive):
    f_dropped = 0
    postponed_tasks = []
    waiting_queue = {}

    while f_dropped < f_excessive and len(all_tasks_sorted) > 1:
        task_id, task_specs = list(all_tasks_sorted.items())[0]
        all_tasks_sorted.pop(task_id)
        waiting_queue[task_id] = task_specs
        postponed_tasks.append(task_id)

        if task_specs["alpha"] == 0:
            f_dropped += task_specs['remained_comp'] / task_specs['remained_time_budget']

    return all_tasks_sorted, waiting_queue, postponed_tasks


def restore_backhaul_tasks(sorted_waiting_queue, postponed_tasks, b_excessive, all_tasks_sorted):
    backhaul_returned = 0

    while backhaul_returned < b_excessive and len(sorted_waiting_queue) > 0:
        task_id, task_specs = list(sorted_waiting_queue.items())[0]
        # Check task eligibility for backhaul reassignment
        if task_specs["alpha"] == 0 and task_specs["decided"]:
            sorted_waiting_queue.pop(task_id)
            continue

        sorted_waiting_queue.pop(task_id)
        postponed_tasks.remove(task_id)
        all_tasks_sorted[task_id] = task_specs
        backhaul_returned += task_specs['untransmitted_data'] / task_specs['remained_time_budget']

    return all_tasks_sorted


def heuristic_postponing(compute_tasks, training_tasks, params, path_to_save, time_slot):
    print("enter postponi")
    postponed_tasks = []
    waiting_queue = {}

    # calculate total CPU ad bandwidth demand by all tasks
    total_required_f, total_required_b, all_tasks = calculate_total_demand(compute_tasks, training_tasks)

    all_tasks_sorted = dict(sorted(all_tasks.items(), key=lambda item: (item[1]['remained_time_budget']), reverse=True))

    # determine excessive computation and bandwidth demand
    f_excessive = total_required_f - params['comp_rsc']
    b_excessive = total_required_b - params["backhaul"]

    if f_excessive > 0:
        all_tasks_sorted, waiting_queue, postponed_tasks = postpone_excessive_computation(all_tasks_sorted, f_excessive)
    else:
        # although there is no excessive demand, still one task should be postponed since the problem was infeasible
        logger.log_function("naive postponing required. total required computation by local tasks is lower than "
                            "available computational resources.")
        task_id, task_specs = list(all_tasks_sorted.items())[0]
        all_tasks_sorted.pop(task_id)
        waiting_queue.update({task_id: task_specs})
        postponed_tasks.append(task_id)

    #  bring back tasks from waiting queue to utilize backhaul
    # sorted_data = sorted(waiting_queue.items(), key=lambda item: (item[1]['remained_time_budget']))
    # sorted_waiting_queue = {key: value for key, value in sorted_data}
    # all_tasks_sorted = restore_backhaul_tasks(sorted_waiting_queue, postponed_tasks, b_excessive, all_tasks_sorted)

    log_postponement(postponed_tasks, time_slot, path_to_save)
    c_executed_tasks = {key: value for key, value in all_tasks_sorted.items() if value['task_type'] == 'compute'}
    t_executed_tasks = {key: value for key, value in all_tasks_sorted.items() if value['task_type'] == 'training'}

    return c_executed_tasks, t_executed_tasks


def ERAFL_postponing_algo(compute_tasks, training_tasks, params, path_to_save, time_slot):
    postponed_tasks = []
    all_tasks = {**compute_tasks, **training_tasks}
    all_tasks_sorted = dict(sorted(all_tasks.items(), key=lambda item: item[1]['remained_comp'], reverse=True))
    task_id, task_specs = list(all_tasks_sorted.items())[0]
    all_tasks_sorted.pop(task_id)

    postponed_tasks.append(task_id)
    log_postponement(postponed_tasks, time_slot, path_to_save)

    c_executed_tasks = {}
    t_executed_tasks = {}

    for task_id,task_specs in all_tasks_sorted.items():
        if task_specs['task_type'] == "compute":
            c_executed_tasks[task_id] = task_specs
        else:
            t_executed_tasks[task_id] = task_specs

    return c_executed_tasks, t_executed_tasks

