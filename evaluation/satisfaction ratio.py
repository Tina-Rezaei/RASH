import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.ticker as ticker
from matplotlib.patches import Patch
import matplotlib.patches as mpatches
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../core/')
from Load_tasks import load_tasks_from_csv


def criticality_satisfaction(tasks, evaluation_period):
    """
    :param tasks:
    :param evaluation_period: the period of time that we want to evaluate the criticality satisfaction ratio (ms)
    :return:
    """
    print("here")
    satisfied_critical_tasks = 0
    satisfied_noncritical_tasks = 0
    total_critical_tasks = 0
    total_noncritical_tasks = 0
    total_tasks = 0
    total_processed_tasks = 0
    overdue_tasks = 0
    completed_tasks = 0
    total_training_tasks = 0
    total_satisfied_training = 0
    total_compute_tasks = 0
    total_satisfied_compute = 0

    for task_id, task_specs in tasks.items():
        if evaluation_period['start'] <= task_specs['arrival_time'] <= evaluation_period['end']:
            total_tasks += 1
            if task_specs['overdue'] == True or task_specs['completed'] == True:
                total_processed_tasks += 1
            else:
                continue
            if task_specs['overdue'] == True:
                overdue_tasks += 1
            if task_specs['completed'] == True:
                completed_tasks += 1
            if task_specs['criticality_score'] == 1:
                total_critical_tasks += 1
            if task_specs['criticality_score'] == 0:
                total_noncritical_tasks += 1
            if task_specs['completed'] == True and task_specs['criticality_score'] == 1:
                satisfied_critical_tasks += 1
            if task_specs['completed'] == True and task_specs['criticality_score'] == 0:
                satisfied_noncritical_tasks += 1
            if task_specs['task_type'] == 'training':
                total_training_tasks += 1
            if task_specs['task_type'] == 'training' and task_specs['completed'] == True:
                total_satisfied_training += 1
            if task_specs['task_type'] == 'compute':
                total_compute_tasks += 1
            if task_specs['task_type'] == 'compute' and task_specs['completed'] == True:
                total_satisfied_compute += 1

    print(total_critical_tasks)
    print("total tasks: ", total_tasks)
    print("total processed tasks: ", total_processed_tasks)
    print("overdue tasks: ", overdue_tasks)
    print("completed tasks: ", completed_tasks)
    print("total critical tasks: ", total_critical_tasks)
    print("total non-critical tasks: ", total_noncritical_tasks)
    print("total satisfied critical tasks: ", satisfied_critical_tasks)
    print("total satisfied non-critical tasks: ", satisfied_noncritical_tasks)
    print("total training tasks:", total_training_tasks)
    print("total satisfied training tasks", total_satisfied_training)
    print("total compute tasks: ", total_compute_tasks)
    print("total satisfied compute tasks: ", total_satisfied_compute)
    print("total satisfaction ratio:", completed_tasks / total_processed_tasks)
    return total_satisfied_training/total_training_tasks, total_satisfied_compute/total_compute_tasks, completed_tasks / total_processed_tasks



def group_box_plot(plot_dictionary, legend1, legend2, y_axis, plot_name):
    """
    this function plots box plot for each of the arguments
    :param non_critical_tasks_time_utilization:
    :param critical_tasks_time_utilization:
    :return:
    """
    plt.clf()
    datasets = []
    for i in range(len(plot_dictionary)):
        max_length = max(len(arr) for arr in plot_dictionary[i].values())
        for key, values in plot_dictionary[i].items():
            padded_values = values + [float('nan')] * (max_length - len(values))
            df = pd.DataFrame({key: padded_values})
            datasets.append(df.fillna(df.median()))
    print(datasets)

    # Define which colours you want to use
    colours = ['red', 'red', 'blue', 'blue']
    color1 = "#0b84a5"
    color2 = "#f6c85f"

    # Define the groups
    groups = ['critical tasks', 'non-critical tasks']
    labels = plot_dictionary[0].keys()
    fig, ax = plt.subplots()
    for i, label in enumerate(labels):
        print(label)
        values = [d[label] for d in [plot_dictionary[0], plot_dictionary[1]]]
        # values2 = [d[label] for d in [plot_dictionary[2], plot_dictionary[3]]]
        step = 0.9
        box = ax.boxplot(values, positions=[i * 5, i * 5 + step], widths=0.7, patch_artist=True,
                         boxprops=dict(facecolor=colours[i]), showfliers=True)
        # box2 = ax.boxplot(values2, positions=[i * 7 + 1.6, i * 7 + 2.3], widths=0.5, patch_artist=True,
        #                   boxprops=dict(facecolor=colours[i]))

        for element in ['whiskers', 'fliers', 'medians', 'caps']:
            plt.setp(box[element], color='black')
            plt.setp(box['medians'], color='black')
        box['boxes'][0].set_facecolor(color1)
        box['boxes'][1].set_facecolor(color2)
        # box['medians'][1].set_color(color2)

        # box['boxes'][1].set(hatch='/')

        # for element in ['whiskers', 'fliers', 'medians', 'caps']:
        #     plt.setp(box2[element], color='black')
        #     plt.setp(box2['medians'], color='red')
        #
        # box2['boxes'][0].set_facecolor(color2)
        # box2['boxes'][1].set_facecolor(color2)
        # box2['boxes'][1].set(hatch='/')

    # Set x-axis labels
    labels = ["70%","100%","150%"]
    plt.xticks([i * 5 + step / 2 for i in range(len(labels))], labels, fontsize=14)
    plt.yticks(fontsize=12)
    plt.ylim(ymax=1.02)
    # Add legend
    legend_patches = [
        mpatches.Patch(facecolor=color1, edgecolor='black', label=legend1),
        mpatches.Patch(facecolor=color2, edgecolor='black', label=legend2),

    ]

    legend = plt.legend(handles=legend_patches, loc='upper left', fontsize=14, fancybox=True, framealpha=0.7,
                        mode="expand", ncol=2)

    # Set plot title and labels
    plt.ylabel(y_axis, fontsize=16)
    plt.xlabel("Load", fontsize=16)

    # plt.legend(handles=legend_elements, fontsize=13, loc="upper right")
    plt.grid(color='lightgray')
    # plt.savefig(f'{plot_name}_{backhaul}_{scheme_number}')
    plt.savefig(f"{plot_name}.pdf", format="pdf", bbox_inches="tight")
    plt.show()


if __name__ == '__main__':
    iterations = 11
    evaluation_period = {'start': 1 * 0 * 1000, 'end': 1 * 60 * 1000}  # ms

    total_satisfaction_ratio_minmax_p = {}
    total_satisfaction_ratio_minmax_D = {}
    training_satisfaction_minmax_p = {}
    execute_satisfaction_minmax_p = {}

    criticality_ratio_list = [0.5]
    naive_postponing = 'naive'
    cps_postponing = 'cps'
    load_based_postoning = "lbp"
    load_list = [0.7, 1, 1.5]
    log_file_name = "time_slot_11999.csv"
    for load in load_list:
        for iteration in range(0, 10):
            print(load, iteration)
            path1 = f'../logs/min_max_p_{load}/heuristic/{iteration}/{log_file_name}'
            # if load == 0.7:
            #     path1 = f'../logs/min_max_p_{load}_test/tasks/{naive_postponing}/{iteration}/{log_file_name}'
            path2 = f'../logs/min_max_delay_{load}/heuristic/{iteration}/{log_file_name}'

            compute_tasks_naive, training_tasks_naive = load_tasks_from_csv(path1)
            compute_tasks_cps, training_tasks_cps = load_tasks_from_csv(path2)

            all_tasks = {**compute_tasks_naive, **training_tasks_naive}
            all_tasks2 = {**compute_tasks_cps, **training_tasks_cps}

            training_satisfaction, execute_satisfaction, total_satisfaction_naive = criticality_satisfaction(
                all_tasks, evaluation_period)
            ratio_critical_cps, ratio_noncritical_cps, total_satisfaction_cps = criticality_satisfaction(all_tasks2,
                                                                                                         evaluation_period)

            values = total_satisfaction_ratio_minmax_p.get(load, [])
            values.append(total_satisfaction_naive)
            total_satisfaction_ratio_minmax_p[load] = values

            # cps
            values = total_satisfaction_ratio_minmax_D.get(load, [])
            values.append(total_satisfaction_cps)
            total_satisfaction_ratio_minmax_D[load] = values

            # training and execute
            values = training_satisfaction_minmax_p.get(load, [])
            values.append(training_satisfaction)
            training_satisfaction_minmax_p[load] = values

            values = execute_satisfaction_minmax_p.get(load, [])
            values.append(execute_satisfaction)
            execute_satisfaction_minmax_p[load] = values


    group_box_plot([
        total_satisfaction_ratio_minmax_p,
        total_satisfaction_ratio_minmax_D,
    ],'RASH',
                  'MinMaxDelay',
                  'Satisfaction ratio (%)',
                  'Satisfaction_ratio')
