import sys
sys.path.insert(1, '../core/')
from Load_tasks import load_tasks_from_csv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np


def time_budget_utilization(tasks):
    tasks_time_utilization = []
    for task_id, task_specs in tasks.items():
            tasks_time_utilization.append((task_specs['time_budget'] - task_specs['remained_time_budget'])/task_specs['time_budget'])
    return tasks_time_utilization


def training_vs_execute_utilization(tasks):
    training_utilization = []
    execute_utilization = []
    for task_id, task_specs in tasks.items():
        if task_specs["task_type"] == "training":
            training_utilization.append((task_specs['time_budget'] - task_specs['remained_time_budget'])/task_specs['time_budget'])
        else:
            execute_utilization.append((task_specs['time_budget'] - task_specs['remained_time_budget'])/task_specs['time_budget'])
    return training_utilization, execute_utilization


def plot_time_utilization(plot_dictionary, legend1, legend2, y_axis, plot_name):
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
        for key,values in plot_dictionary[i].items():
            padded_values = values + [float('nan')] * (max_length - len(values))
            df = pd.DataFrame({key: padded_values})
            datasets.append(df.fillna(df.median()))
    print(datasets)

    # Define which colours you want to use
    colours = ['red', 'red', 'blue', 'blue']
    # color1 = [221 / 235, 170 / 235, 51 / 235]
    # color2 = [187 / 235, 85 / 235, 102 / 235]
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
        step = 0.8
        box = ax.boxplot(values, positions=[i * 5, i * 5 + step], widths=0.7, patch_artist=True,
                         boxprops=dict(facecolor=colours[i]), showfliers=False)
        # box2 = ax.boxplot(values2, positions=[i * 7 + 1.6, i * 7 + 2.3], widths=0.5, patch_artist=True,
        #                   boxprops=dict(facecolor=colours[i]))

        for element in ['whiskers', 'fliers', 'medians', 'caps']:
            plt.setp(box[element], color='black')
            plt.setp(box['medians'], color='black')
        box['boxes'][0].set_facecolor(color1)
        box['boxes'][1].set_facecolor(color2)
        # box['boxes'][1].set(hatch='//')
        # box['boxes'][1].set(hatch='/')

        # for element in ['whiskers', 'fliers', 'medians', 'caps']:
        #     plt.setp(box2[element], color='black')
        #     plt.setp(box2['medians'], color='red')
        #
        # box2['boxes'][0].set_facecolor(color2)
        # box2['boxes'][1].set_facecolor(color2)
        # box2['boxes'][1].set(hatch='/')

    # Set x-axis labels
    labels = ["70%","100%", "150%"]
    plt.xticks([i * 5 + step/2 for i in range(len(labels))], labels, fontsize=14)
    plt.yticks(fontsize=12)
    plt.ylim(ymax=1.2)
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

    load_list = [0.7, 1, 1.5]
    tasks_time_utilization_cps = {}
    tasks_time_utilization_naive = {}
    training_utilization_total = {}
    execute_utilization_total = {}
    iterations = 10

    for load in load_list:
        for iteration in range(iterations):
            path = f'../logs/min_max_p_{load}/heuristic/{iteration}/time_slot_11999.csv'
            path2 = f'../logs/min_max_delay_{load}/heuristic/{iteration}/time_slot_11999.csv'

            # RASH
            compute_tasks, training_tasks = load_tasks_from_csv(path)
            all_tasks = {**compute_tasks, **training_tasks}
            tasks_time_utilization = time_budget_utilization(all_tasks)
            tasks_time_utilization_cps[load] = tasks_time_utilization_cps.get(load, []) + tasks_time_utilization

            # MinMaxDelay
            compute_tasks, training_tasks = load_tasks_from_csv(path2)
            all_tasks = {**compute_tasks, **training_tasks}
            tasks_time_utilization = time_budget_utilization(all_tasks)
            tasks_time_utilization_naive[load] = tasks_time_utilization_naive.get(load, []) + tasks_time_utilization

            # training vs execute
            compute_tasks, training_tasks = load_tasks_from_csv(path2)
            all_tasks = {**compute_tasks, **training_tasks}
            training_utilization, execute_utilization = training_vs_execute_utilization(all_tasks)
            training_utilization_total[load] = training_utilization_total.get(load, []) + training_utilization
            execute_utilization_total[load] = execute_utilization_total.get(load, []) + execute_utilization

    for key, value in tasks_time_utilization_cps.items():
        print(len(tasks_time_utilization_naive[key]))
        print(len(tasks_time_utilization_cps[key]))
    print("==============")
    plot_time_utilization([tasks_time_utilization_cps,
                           tasks_time_utilization_naive,
                           ],
                          'RASH',
                          'MinMaxDelay',
                          'Time budget utilization',
                          'Time_budget_utilization')


    # plot_time_utilization([training_utilization_total,
    #                        execute_utilization_total,
    #                        ],
    #                       'Training',
    #                       'Execute',
    #                       'Time budget utilization',
    #                       'Training_vs_execute')

