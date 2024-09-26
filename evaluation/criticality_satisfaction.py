from Load_tasks import load_tasks
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.ticker as ticker
from matplotlib.patches import Patch
import matplotlib.patches as mpatches


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
    overdue_tasks = 0
    completed_tasks = 0
    total_training_tasks = 0
    total_satisfied_training = 0
    total_compute_tasks = 0
    total_processed_tasks = 0
    for task_id, task_specs in tasks.items():
        if evaluation_period['start'] <task_specs['arrival_time'] < evaluation_period['end']:
            total_tasks += 1
            if task_specs['overdue'] == True or task_specs['completed'] == True:
                    total_processed_tasks += 1
                    if task_specs['criticality_score'] == 1:
                        total_critical_tasks += 1
                    if task_specs['criticality_score'] == 0:
                        total_noncritical_tasks += 1
                    if task_specs['task_type'] == 'training':
                        total_training_tasks += 1

            if task_specs['overdue'] == True:
                overdue_tasks += 1
            if task_specs['completed'] == True:
                completed_tasks += 1
            if task_specs['completed'] == True and task_specs['criticality_score'] == 1:
                satisfied_critical_tasks += 1
            if task_specs['completed'] == True and task_specs['criticality_score'] == 0:
                satisfied_noncritical_tasks += 1
            if task_specs['task_type'] == 'training' and task_specs['completed'] == True:
                total_satisfied_training += 1
            if task_specs['task_type'] == 'compute':
                total_compute_tasks += 1

    print(total_critical_tasks)
    print("total tasks: ", total_tasks)
    print("total satisfied tasks: ", satisfied_critical_tasks+satisfied_noncritical_tasks)
    print("overdue tasks: ", overdue_tasks)
    print("completed tasks: ", completed_tasks)
    print("total critical tasks: ", total_critical_tasks)
    print("total non-critical tasks: ", total_noncritical_tasks)
    print("total satisfied critical tasks: ", satisfied_critical_tasks)
    print("total satisfied non-critical tasks: ", satisfied_noncritical_tasks)
    print("total training tasks:", total_training_tasks)
    print("total satisfied training tasks", total_satisfied_training)
    print("total compute tasks: ", total_compute_tasks)
    print("total satisfaction ratio:", completed_tasks/total_processed_tasks)
    print("total processed tasks:", total_processed_tasks)
    return satisfied_critical_tasks/total_critical_tasks, satisfied_noncritical_tasks/total_noncritical_tasks, (satisfied_critical_tasks+satisfied_noncritical_tasks)/(total_processed_tasks)


def group_box_plot(plot_dictionary, plot_name):
    plt.clf()
    datasets = []
    for i in range(len(plot_dictionary)):
        df = pd.DataFrame(plot_dictionary[i])
        datasets.append(df.fillna(df.median()))
    print(datasets)

    # Define which colours you want to use
    colours = ['red', 'red', 'blue', 'blue']
    color1 = [221/235, 170/235, 51/235]
    color2 = [187/235, 85/235, 102/235]
    color3 = [0 / 235, 68 / 235, 136 / 235]

    # Define the groups
    groups = ['critical tasks', 'non-critical tasks']
    labels = plot_dictionary[0].keys()
    fig, ax = plt.subplots()
    for i, label in enumerate(labels):
        print(label)
        values = [d[label] for d in [plot_dictionary[0], plot_dictionary[1]]]
        values2 = [d[label] for d in [plot_dictionary[2], plot_dictionary[3]]]
        values3 = [d[label] for d in [plot_dictionary[4], plot_dictionary[5]]]

        box = ax.boxplot(values, positions=[i * 7, i * 7 + 0.7], widths=0.5, patch_artist=True,
                         boxprops=dict(facecolor=colours[i]))
        box2 = ax.boxplot(values2, positions=[i * 7 + 1.6, i * 7 + 2.3], widths=0.5, patch_artist=True,
                          boxprops=dict(facecolor=colours[i]))
        box3 = ax.boxplot(values3, positions=[i * 7 + 3.2, i * 7+3.9], widths=0.5, patch_artist=True,
                          boxprops=dict(facecolor=colours[i]))

        for element in ['whiskers', 'fliers', 'medians', 'caps']:
            plt.setp(box[element], color='black')
            plt.setp(box['medians'], color='red')
        box['boxes'][0].set_facecolor(color1)
        box['boxes'][1].set_facecolor(color1)
        box['boxes'][1].set(hatch='/')

        for element in ['whiskers', 'fliers', 'medians', 'caps']:
            plt.setp(box2[element], color='black')
            plt.setp(box2['medians'], color='red')

        box2['boxes'][0].set_facecolor(color2)
        box2['boxes'][1].set_facecolor(color2)
        box2['boxes'][1].set(hatch='/')

        for element in ['whiskers', 'fliers', 'medians', 'caps']:
            plt.setp(box3[element], color='black')
            plt.setp(box3['medians'], color='red')

        box3['boxes'][0].set_facecolor(color3)
        box3['boxes'][1].set_facecolor(color3)
        box3['boxes'][1].set(hatch='/')

    # Set x-axis labels
    plt.xticks(range(2, len(labels) * 7 + 2, 7), labels, fontsize=12)
    plt.yticks(fontsize=12)
    plt.ylim(ymax=1.1, ymin=0.5)
    # Add legend
    legend_patches = [
        mpatches.Patch(facecolor=color1, edgecolor='black', label='critical tasks-cps'),
        mpatches.Patch(facecolor=color1, edgecolor='black', hatch='///', label='critical tasks-naive'),
        mpatches.Patch(facecolor=color2, edgecolor='black', label='non-critical tasks-cps'),
        mpatches.Patch(facecolor=color2, edgecolor='black', hatch='///', label='non-critical tasks-naive'),
        mpatches.Patch(facecolor=color3, edgecolor='black', label='total tasks-cps'),
        mpatches.Patch(facecolor=color3, edgecolor='black', hatch='///', label='total tasks-naive'),
    ]

    legend = plt.legend(handles=legend_patches, loc='upper left', fontsize=8, fancybox=True, framealpha=0.7,
                        mode="expand", ncol=3)

    # Set plot title and labels
    plt.ylabel(plot_name, fontsize=12)
    plt.xlabel("Criticality ratio", fontsize=12)


    # plt.legend(handles=legend_elements, fontsize=13, loc="upper right")
    plt.grid(color='lightgray')
    # plt.savefig(f'{plot_name}_{backhaul}_{scheme_number}')
    plt.savefig(f"{plot_name}.pdf", format="pdf", bbox_inches="tight")
    plt.savefig(f"{plot_name}.png", bbox_inches="tight")
    plt.show()


if __name__ == '__main__':
    iterations = 10
    evaluation_period = {'start': 1 * 0 * 1000, 'end': 1 * 30 * 1000}  # ms (4 minutes)
    evaluation_period_burst = {'start': 1 * 30 * 1000, 'end': 1 * 70 * 1000}  # ms (4 minutes)
    satifaction_ratio_critical_tasks_naive = {}
    satifaction_ratio_critical_tasks_cps = {}
    satifaction_ratio_noncritical_tasks_naive = {}
    satifaction_ratio_noncritical_tasks_cps = {}
    total_satisfaction_ratio_naive = {}
    total_satisfaction_ratio_cps = {}

    total_satisfaction_ratio_minmax_burst = {}
    total_satisfaction_ratio_min_burst = {}

    criticality_ratio_list = [0.3]
    naive_postponing = 'naive'
    cps_postponing = 'cps'

    for ratio in criticality_ratio_list:
        for iteration in range(0, 10):
            path1 = f'../min_max_p_(0.66,500)/tasks/{naive_postponing}/criticality_ratio_{ratio}/{iteration}/time_slot_23999.csv'
            path2 = f'../min_max_p_(0.66,500)/tasks/{cps_postponing}/criticality_ratio_{ratio}/{iteration}/time_slot_23999.csv'

            compute_tasks_naive, training_tasks_naive = load_tasks(path1)
            compute_tasks_cps, training_tasks_cps = load_tasks(path2)

            all_tasks = {**compute_tasks_naive, **training_tasks_naive}
            all_tasks2 = {**compute_tasks_cps, **training_tasks_cps}

            ratio_critical_naive, ratio_noncritical_naive, total_satisfaction_naive = criticality_satisfaction(all_tasks, evaluation_period_burst)
            ratio_critical_cps, ratio_noncritical_cps, total_satisfaction_cps = criticality_satisfaction(all_tasks2, evaluation_period_burst)

            values = satifaction_ratio_critical_tasks_naive.get(ratio, [])
            values.append(ratio_critical_naive)
            satifaction_ratio_critical_tasks_naive[ratio] = values

            values = satifaction_ratio_noncritical_tasks_naive.get(ratio, [])
            values.append(ratio_noncritical_naive)
            satifaction_ratio_noncritical_tasks_naive[ratio] = values

            values = total_satisfaction_ratio_naive.get(ratio, [])
            values.append(total_satisfaction_naive)
            total_satisfaction_ratio_naive[ratio] = values

            # cps
            values = satifaction_ratio_critical_tasks_cps.get(ratio, [])
            values.append(ratio_critical_cps)
            satifaction_ratio_critical_tasks_cps[ratio] = values

            values = satifaction_ratio_noncritical_tasks_cps.get(ratio, [])
            values.append(ratio_noncritical_cps)
            satifaction_ratio_noncritical_tasks_cps[ratio] = values

            values = total_satisfaction_ratio_cps.get(ratio, [])
            values.append(total_satisfaction_cps)
            total_satisfaction_ratio_cps[ratio] = values


            # # ================================= burst time period =======================
            # ratio_critical_naive, ratio_noncritical_naive, total_satisfaction_naive = criticality_satisfaction(
            #     all_tasks, evaluation_period_burst)
            # ratio_critical_cps, ratio_noncritical_cps, total_satisfaction_cps = criticality_satisfaction(all_tasks2,
            #                                                                                              evaluation_period_burst)
            #
            # values = total_satisfaction_ratio_naive.get(ratio, [])
            # values.append(total_satisfaction_naive)
            # total_satisfaction_ratio_naive[ratio] = values

            # cps
            #
            # values = total_satisfaction_ratio_cps.get(ratio, [])
            # values.append(total_satisfaction_cps)
            # total_satisfaction_ratio_cps[ratio] = values
    # print(satifaction_ratio_critical_tasks_cps)
    print(satifaction_ratio_critical_tasks_naive)
    print(satifaction_ratio_noncritical_tasks_naive)
    print(total_satisfaction_ratio_naive)
    group_box_plot([satifaction_ratio_critical_tasks_cps,
                    satifaction_ratio_critical_tasks_naive,
                    satifaction_ratio_noncritical_tasks_cps,
                    satifaction_ratio_noncritical_tasks_naive,
                    total_satisfaction_ratio_cps,
                    total_satisfaction_ratio_naive
                    ],
                   'Satisfaction ratio')

    print("============================")
    print(satifaction_ratio_critical_tasks_naive)
    print(satifaction_ratio_noncritical_tasks_naive)

