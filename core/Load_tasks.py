import os
import csv


def load_tasks_from_csv(path):
    """
    this function reads the tasks at each time slot from a csv file excluding the header
    :param path: The path to the CSV file containing the tasks.
    :return: Two dictionaries: compute_tasks and training_tasks.
    """
    #    this function reads the tasks at each time slot from a csv file excluding the header
    training_tasks = {}
    compute_tasks = {}
    with open(os.path.join(path), 'r') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            if row['task_type'] == 'training':
                training_tasks.update({int(row['task_id']): {'data_size': float(row['data_size']),
                                                             'untransmitted_data': float(row['untransmitted_data']),
                                                             'data_for_processing': float(row['data_for_processing']),
                                                             'model_size': float(row['model_size']),
                                                             'epoch': float(row['epoch']),
                                                             'required_comp': float(row['required_comp']),
                                                             'remained_comp': float(row['remained_comp']),
                                                             'time_budget': float(row['time_budget']),
                                                             'remained_time_budget': float(row['remained_time_budget']),
                                                             'arrival_time': float(row['arrival_time']),
                                                             'comp_per_bit': float(row['comp_per_bit']),
                                                             'privacy_score': float(row['privacy_score']),
                                                             'criticality_score': float(row['criticality_score']),
                                                             'task_type': row['task_type'],
                                                             'alpha': float(row['alpha']),
                                                             'decided': row['decided'] == 'True',
                                                             'overdue': row['overdue'] == 'True',
                                                             'completed': row['completed'] == 'True'
                                                             }})

            if row['task_type'] == 'compute':
                compute_tasks.update({int(row['task_id']): {'data_size': float(row['data_size']),
                                                            'untransmitted_data': float(row['untransmitted_data']),
                                                            'data_for_processing': float(row['data_for_processing']),
                                                            'required_comp': float(row['required_comp']),
                                                            'remained_comp': float(row['remained_comp']),
                                                            'time_budget': float(row['time_budget']),
                                                            'remained_time_budget': float(row['remained_time_budget']),
                                                            'arrival_time': float(row['arrival_time']),
                                                            'comp_per_bit': float(row['comp_per_bit']) if row['task_type'] == 'training' else '',
                                                            'privacy_score': float(row['privacy_score']),
                                                            'criticality_score': float(row['criticality_score']),
                                                            'epoch': float(row['epoch']) if row['task_type'] == 'training' else '',
                                                            'model_size': float(row['model_size']) if row['task_type'] == 'training' else '',
                                                            'task_type': row['task_type'],
                                                            'alpha': float(row['alpha']),
                                                            'decided': row['decided'] == 'True',
                                                            'overdue': row['overdue'] == 'True',
                                                            'completed': row['completed'] == 'True',
                                                            }})

    return compute_tasks, training_tasks


def load_and_reset_tasks(path, delta_t):
    """
    this function reads the tasks at each time slot from a csv file and reset task parameters
    :param path: The path to the CSV file containing the tasks.
    :return: Two dictionaries: compute_tasks and training_tasks.
    """
    #    this function reads the tasks at each time slot from a csv file excluding the header
    training_tasks = {}
    compute_tasks = {}
    with open(os.path.join(path), 'r') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            if row['task_type'] == 'training':
                training_tasks.update({int(row['task_id']): {'data_size': float(row['data_size']),
                                                             'untransmitted_data': float(row['data_size']),
                                                             'data_for_processing': float(row['data_size']),
                                                             'model_size': float(row['model_size']),
                                                             'epoch': float(row['epoch']),
                                                             'required_comp': float(row['required_comp']),
                                                             'remained_comp': float(row['required_comp']),
                                                             'time_budget': float(row['time_budget']),
                                                             'remained_time_budget': float(row['time_budget']),
                                                             'arrival_time': float(row['arrival_time']),
                                                             'time_slot_arrival': float(row['arrival_time']) // delta_t,
                                                             'comp_per_bit': float(row['comp_per_bit']),
                                                             'privacy_score': float(row['privacy_score']),
                                                             'criticality_score': float(row['criticality_score']),
                                                             'task_type': row['task_type'],
                                                             'alpha': 0,
                                                             'decided': False,
                                                             'overdue': False,
                                                             'completed': False
                                                             }})

            if row['task_type'] == 'compute':
                compute_tasks.update({int(row['task_id']): {'data_size': float(row['data_size']),
                                                            'untransmitted_data': float(row['data_size']),
                                                            'data_for_processing': float(row['data_size']),
                                                            'required_comp': float(row['required_comp']),
                                                            'remained_comp': float(row['required_comp']),
                                                            'time_budget': float(row['time_budget']),
                                                            'remained_time_budget': float(row['time_budget']),
                                                            'arrival_time': float(row['arrival_time']),
                                                            'time_slot_arrival': float(row['arrival_time']) // delta_t,
                                                            'comp_per_bit': '',
                                                            'privacy_score': float(row['privacy_score']),
                                                            'criticality_score': float(row['criticality_score']),
                                                            'epoch': '',
                                                            'model_size': '',
                                                            'task_type': row['task_type'],
                                                            'alpha': 0,
                                                            'decided':  False,
                                                            'overdue':  False,
                                                            'completed': False,
                                                            }})

    return compute_tasks, training_tasks

