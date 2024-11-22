import pyomo.environ as pyo
import os


def update_tasks(c_queue, t_queue, c_execution_queue, t_execution_queue, params, solver_solution, current_time, delta_t, time_slot, path):
    # delta_t = delta_t * 0.001  # convert to ms
    comp_rsc = params['comp_rsc']  # cpu cycles per time unit
    backhaul = params['backhaul']  # backhaul capacity
    overdue_tasks = []
    # update time budget of all tasks that are not completed or overdue
    for task_id, task_specs in c_queue.items():
        if c_queue[task_id]['overdue']:
            overdue_tasks.append(task_id)
        if not task_specs['completed'] and not task_specs['overdue'] and task_specs['arrival_time'] <= current_time:
            c_queue[task_id]['remained_time_budget'] = c_queue[task_id]['remained_time_budget'] - delta_t
            if c_queue[task_id]['remained_time_budget'] <= 0:
                c_queue[task_id]['overdue'] = True
                c_queue[task_id]['remained_time_budget'] = 0
                overdue_tasks.append(task_id)
                # with open(os.path.join(path, "overdue_log.txt"), 'a') as f: # log overdue tasks
                #     f.write(f"{time_slot}, {task_id}\n")
                # c_queue[task_id]['remained_time_budget'] = 0

    for task_id, task_specs in t_queue.items():
        if t_queue[task_id]['overdue']:
            overdue_tasks.append(task_id)
        if not task_specs['completed'] and not task_specs['overdue'] and task_specs['arrival_time'] <= current_time:
            t_queue[task_id]['remained_time_budget'] = t_queue[task_id]['remained_time_budget'] - delta_t
            if t_queue[task_id]['remained_time_budget'] <= 0:
                t_queue[task_id]['overdue'] = True
                t_queue[task_id]['remained_time_budget'] = 0
                overdue_tasks.append(task_id)
                # with open(os.path.join(path, "overdue_log.txt"), 'a') as f:  # log overdue tasks
                #     f.write(f"{time_slot}, {task_id}")
                # t_queue[task_id]['remained_time_budget'] = 0

    # update resources of tasks executed in the last time slot
    for task_id, task_specs in c_execution_queue.items():
        c_queue[task_id]['alpha'] = pyo.value(solver_solution.alpha[task_id])
        c_queue[task_id]['decided'] = True
        # calculate transmitted data and processed data based on allocated resources
        if pyo.value(solver_solution.alpha[task_id]) == 1:
            transmitted_data = delta_t * pyo.value(solver_solution.B[task_id])
            processed_data = (delta_t * pyo.value(solver_solution.bb[task_id]))
            if transmitted_data - processed_data <= 0:
                task_specs['data_for_processing'] -= transmitted_data
            else:
                task_specs['data_for_processing'] -= processed_data

            if task_specs['data_for_processing'] <= 0:
                c_queue[task_id]['completed'] = True
                c_queue[task_id]['overdue'] = False
                c_queue[task_id]['remained_comp'] = 0
                c_queue[task_id][''] = task_specs['untransmitted_data'] - transmitted_data

        else:
            if task_specs['remained_comp'] - delta_t * pyo.value(solver_solution.F[task_id]) <= 0:
                c_queue[task_id]['completed'] = True
                c_queue[task_id]['overdue'] = False
                c_queue[task_id]['remained_comp'] = 0
            else:
                c_queue[task_id]['remained_comp'] = task_specs['remained_comp'] - delta_t * pyo.value(
                    solver_solution.F[task_id])

        # update the rest amount of data needed to transmit from iot device to edge server
        if task_specs['untransmitted_data'] - delta_t * pyo.value(solver_solution.B[task_id]) > 0:
            c_queue[task_id]['untransmitted_data'] = task_specs['untransmitted_data'] - delta_t * pyo.value(
                solver_solution.B[task_id])
        else:
            c_queue[task_id]['untransmitted_data'] = 0

    for task_id, task_specs in t_execution_queue.items():
        t_queue[task_id]['alpha'] = pyo.value(solver_solution.alpha[task_id])
        t_queue[task_id]['decided'] = True
        # calculate transmitted data and processed data based on allocated resources
        transmitted_data = delta_t * pyo.value(solver_solution.B[task_id])
        if pyo.value(solver_solution.alpha[task_id]) == 0:
            processed_data = (delta_t * pyo.value(solver_solution.F[task_id])) / (task_specs['epoch'] * task_specs['comp_per_bit'])
        else:
            processed_data = (delta_t * pyo.value(solver_solution.bb[task_id]))

        if transmitted_data - processed_data <= 0:
            task_specs['data_for_processing'] -= transmitted_data
            t_queue[task_id]['remained_comp'] = task_specs['remained_comp'] - task_specs['epoch'] * task_specs['comp_per_bit'] * transmitted_data
        else:
            task_specs['data_for_processing'] -= processed_data
            t_queue[task_id]['remained_comp'] = task_specs['remained_comp'] - task_specs['epoch'] * task_specs['comp_per_bit'] * processed_data

        if task_specs['data_for_processing'] <= 0:
            t_queue[task_id]['completed'] = True
            t_queue[task_id]['overdue'] = False
            t_queue[task_id]['remained_comp'] = 0
            t_queue[task_id]['untransmitted_data'] = task_specs['untransmitted_data'] - transmitted_data
        else:

            # update the rest amount of data needed to transmit from iot device to edge server
            if task_specs['untransmitted_data'] - transmitted_data > 0:
                t_queue[task_id]['untransmitted_data'] = task_specs['untransmitted_data'] - transmitted_data
            else:
                t_queue[task_id]['untransmitted_data'] = 0

    # after updating all tasks, check if they are still feasible given maximum resources
    for task_id, task_specs in c_queue.items():
        if task_specs["remained_time_budget"] > 0 and task_specs['decided'] == True and task_specs["alpha"] == 0:
            if task_specs["completed"] != True:
                if task_specs["remained_comp"]/task_specs["remained_time_budget"] > comp_rsc:
                    c_queue[task_id]['overdue'] = True
                    overdue_tasks.append(task_id)

    for task_id, task_specs in t_queue.items():
        if task_specs["remained_time_budget"] > 0 and task_specs['decided'] and task_specs["alpha"] == 0:
            if task_specs["completed"] != True:
                if task_specs["remained_comp"] / comp_rsc + task_specs["model_size"] / backhaul > task_specs["remained_time_budget"]:
                    t_queue[task_id]['overdue'] = True
                    overdue_tasks.append(task_id)

    return c_queue, t_queue, overdue_tasks


    # todo: when offloading decision is made, but time is not enough to execute the task because it has been postponed a lot, then the task should be dropped

