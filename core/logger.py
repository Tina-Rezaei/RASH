import os
import csv
import json
import shutil
import pickle
import pyomo.environ as pyo

def log_function(message):
    with open("log.txt", "a") as f:
        f.write(f'{message} \n')



def create_directories(path, iterations):
    if os.path.exists(path):
        shutil.rmtree(path)
    for i in range(iterations):
        os.makedirs(f'{path}/{i}', exist_ok=True)
        os.makedirs(f'{path}/{i}', exist_ok=True)



def record_tasks_report(c_queue, t_queue, c_execution_queue, t_execution_queue, overdue_tasks_list, time_slot, path, current_time, tasks_report_log):
    '''
    this record all the tasks report into a list
    :param c_queue:
    :param t_queue:
    :param c_execution_queue:
    :param t_execution_queue:
    :param time_slot:
    :param path:
    :return:
    '''

    total_tasks_generated = 0
    overdue_tasks = 0
    completed_tasks = 0
    postponed_tasks_count = ""
    postponed_tasks_ids = ""
    postpone_calls = ""
    processed_tasks = len(c_execution_queue) + len(t_execution_queue)
    overdue_tasks_ids = '-'.join([str(task_id) for task_id in overdue_tasks_list])  # for the current time slot
    processed_tasks_ids = [key for key,value in c_execution_queue.items()] + [key for key,value in t_execution_queue.items()]

    all_tasks = {**c_queue, **t_queue}
    for task_id, task_specs in all_tasks.items():
        if task_specs['arrival_time'] <= current_time:
            total_tasks_generated += 1
        if task_specs['arrival_time'] <= current_time and task_specs['completed']:
            completed_tasks += 1
        if task_specs['overdue']:
            overdue_tasks += 1

    if os.path.exists(os.path.join(path, 'postponement_log')):
        with open(os.path.join(path, 'postponement_log'), 'r') as f:
            postponement_dict = json.load(f)
        if str(time_slot) in postponement_dict.keys():
            postponed_tasks = postponement_dict[str(time_slot)]
            postpone_calls = len(postponed_tasks)
            postponed_tasks_ids = "-".join([['-'.join(str(task_id) for task_id in id_set)][0] for id_set in postponed_tasks])
            postponed_tasks_count = len(postponed_tasks_ids.split('-'))

    tasks_report_log.append({"time_slot": time_slot,
                             "total_tasks_generated": total_tasks_generated,
                             "processed_tasks": processed_tasks,
                             "completed_tasks": completed_tasks,
                             "overdue_tasks": overdue_tasks,
                             "overdue_tasks_ids": overdue_tasks_ids,
                             "postponed_tasks_count": postponed_tasks_count,
                             "postponed_tasks_ids": postponed_tasks_ids,
                             "postpone_calls": postpone_calls,
                             "processed_tasks_ids": processed_tasks_ids
                             })
    return tasks_report_log


def record_model_report(model, rsc_report_log):
    consumed_comp_rsc = 0
    consumed_backhaul = 0
    consumed_bandwidth = 0
    try:
        for task_id in model.i:
            consumed_bandwidth += pyo.value(model.B[task_id])
            if pyo.value(model.alpha[task_id]) < 0.5:  # when alpha is zero, local execution
                consumed_comp_rsc += pyo.value(model.F[task_id])
            else:  # when alpha is one, remote execution
                consumed_backhaul += pyo.value(model.bB[task_id])

    except Exception as e:
        consumed_comp_rsc = 0
        consumed_backhaul = 0
        consumed_bandwidth = 0
        print("error raised her", e)

    rsc_report_log.append({"consumed_comp_rsc": consumed_comp_rsc,
                           "consumed_backhaul": consumed_backhaul,
                           "consumed_bandwidth": consumed_bandwidth
                           })
    return rsc_report_log


def save_tasks_report(path, tasks_report_log):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(
                "time slot, total tasks, processed tasks, completed tasks, #overdue tasks, overdue tasks id(recent), "
                "#postponed tasks, postponed tasks ids, # postpone calls, processed_tasks_ids\n")

    with open(path, 'a') as f:
        for element in tasks_report_log:
            f.write(f'{element["time_slot"]}, '
                    f'{element["total_tasks_generated"]}, '
                    f'{element["processed_tasks"]}, '
                    f'{element["completed_tasks"]}, '
                    f'{element["overdue_tasks"]}, '
                    f'{element["overdue_tasks_ids"]}, '
                    f'{element["postponed_tasks_count"]}, '
                    f'{element["postponed_tasks_ids"]}, '
                    f'{element["postpone_calls"]}, '
                    f'{element["processed_tasks_ids"]}\n')


def save_model_report(path, rsc_report_log):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write("bandwidth_usage, comp_rsc_usage, backhaul_usage\n")
    for element in rsc_report_log:
        with open(path, 'a') as f:
            f.write(f'{element["consumed_bandwidth"]}, '
                    f'{element["consumed_comp_rsc"]}, '
                    f'{element["consumed_backhaul"]}\n')


def save_load_report(path, load_log):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write("total_backhaul_load, total_system_load, handled_load_per_slot\n")
    with open(path, 'a') as f:
        for element in load_log:
            f.write(f'{element["total_backhaul_load"]}, '
                    f'{element["total_system_load"]}, '
                    f'{element["handled_load_per_slot"]}\n')


def save_tasks(tasks, time_slot_number, path):
    '''
    this function saves the tasks in a csv file
    :return:
    '''

    with open(os.path.join(path, f'time_slot_{time_slot_number}.csv'), 'w') as f:
        f.write(
            'time slot,task_id,task_type,arrival_time,time_budget,remained_time_budget,required_comp,remained_comp,data_size,untransmitted_data,data_for_processing,privacy_score,decided,completed,overdue,criticality_score,alpha,model_size,epoch,comp_per_bit\n')

    for task_id, task_specs in tasks.items():
        with open(os.path.join(path, f'time_slot_{time_slot_number}.csv'), 'a') as f:
            writer = csv.writer(f)
            writer.writerow(
                [task_specs['time_slot_arrival'], task_id, task_specs['task_type'], task_specs['arrival_time'],
                 task_specs['time_budget'], task_specs['remained_time_budget'],
                 task_specs['required_comp'], task_specs['remained_comp'], task_specs['data_size'],
                 task_specs['untransmitted_data'], task_specs['data_for_processing'],
                 task_specs['privacy_score'], task_specs['decided'], task_specs['completed'],
                 task_specs['overdue'], task_specs['criticality_score'], task_specs['alpha'],
                 task_specs['model_size'] if task_specs['task_type'] == 'training' else None,
                 task_specs['epoch'] if task_specs['task_type'] == 'training' else None,
                 task_specs['comp_per_bit'] if task_specs['task_type'] == 'training' else None])


def save_model(model, model_name, time_slot_number, path, ):
    with open(os.path.join(path, f'{model_name}_{time_slot_number}'), 'wb') as f:
        pickle.dump(model, f)