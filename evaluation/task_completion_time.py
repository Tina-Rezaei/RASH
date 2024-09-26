from Load_tasks import load_tasks
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np


def time_budget_utilization(tasks, evaluation_period):
    total_tasks_time_utilization = []
    for task_id, task_specs in tasks.items():
        if evaluation_period['start'] <= int(task_specs['arrival_time']) <= evaluation_period['end']:
            print(evaluation_period)
            # if task_specs['completed'] == True and task_specs['criticality_score'] == 1:
            if task_specs['completed'] == True:
                if task_specs['remained_time_budget'] > 0:
                    total_tasks_time_utilization.append((task_specs['time_budget'] - task_specs['remained_time_budget'])/task_specs['time_budget'])
                else:
                    total_tasks_time_utilization.append(1)
    return total_tasks_time_utilization


def pad_array_with_nan(array, target_length):
    padded_array = np.pad(array, (0, target_length - len(array)), mode='constant', constant_values=np.nan)
    return padded_array


def plot_time_utilization(plot_dictionary, plot_name):
    plt.clf()

    # Determine the maximum length among all arrays
    max_length = max(len(array) for subdict in plot_dictionary for array in subdict.values())

    # Pad arrays with NaN values to ensure they all have the same length
    padded_data = [{key: pad_array_with_nan(array, max_length) for key, array in subdict.items()} for subdict in
                   plot_dictionary]

    # Define colours
    colours = ['red', 'red', 'blue', 'blue']
    color1 = [221 / 235, 170 / 235, 51 / 235]

    # Define labels
    labels = list(plot_dictionary[0].keys())

    # Plot boxplots
    fig, ax = plt.subplots()
    for i, label in enumerate(labels):
        positions = [i * 2, i*2 + 0.6, i*2+1.6, i*2+2.2]
        print(positions)
        for j, data_dict in enumerate(padded_data):
            try:
                values = data_dict[label]
                # Remove NaN values
                values = values[~np.isnan(values)]
                if len(values) > 0:
                    box = ax.boxplot(values, positions=[positions[j]], widths=0.5, patch_artist=True,
                                     boxprops=dict(facecolor=colours[i]), showfliers=False)
                    for element in ['whiskers', 'fliers', 'medians', 'caps']:
                        plt.setp(box[element], color='black')
                        box['boxes'][0].set_facecolor(color1)
                    if j% 2 == 1:
                        box['boxes'][0].set(hatch='/')
            except:
                print("")

    # Set x-axis labels
    # labels = ["30%", "70%", "200%"]
    labels = ["30%", "90%"]
    # plt.xticks([0, 2, 4], labels, fontsize=12)
    plt.xticks([0, 2], labels, fontsize=12)
    plt.yticks(fontsize=14)

    # Add legend
    legend_patches = [
        mpatches.Patch(facecolor=color1, edgecolor='black', label='RASH'),
        mpatches.Patch(facecolor=color1, edgecolor='black', hatch='///', label='Minmax Delay'),
    ]

    legend = plt.legend(handles=legend_patches, loc='upper left', fontsize=11, fancybox=True, framealpha=0.7,
                        mode="expand", ncol=3)

    # Set plot title and labels
    plt.ylabel(plot_name, fontsize=14)
    plt.xlabel("Computation load", fontsize=14)
    plt.ylim(ymax=1.2)

    plt.grid(color='lightgray')

    plt.savefig(f"{plot_name}.pdf", format="pdf", bbox_inches="tight")
    plt.savefig(f"{plot_name}.png", bbox_inches="tight")
    plt.show()


if __name__ == '__main__':

    criticality_ratio = [0.5]
    evaluation_period_constant = {'start': 1 * 0 * 1000, 'end': 1 * 30 * 1000}  # ms (4 minutes)
    evaluation_period_burst = {'start': 1 * 30 * 1000, 'end': 1 * 60 * 1000}  # ms (4 minutes)

    total_tasks_time_utilization_minmax = {}
    total_tasks_time_utilization_min = {}

    total_tasks_time_utilization_minmax_burst = {}
    total_tasks_time_utilization_min_burst = {}
    iterations = 11
    for ratio in criticality_ratio:
        for iteration in range(0, 10):
            path = f'../min_max_p_(0.66,500)/tasks/naive/criticality_ratio_{ratio}/{iteration}/time_slot_23999.csv'
            path2 = f'../min_max_delay_(0.66,500)/tasks/naive/criticality_ratio_{ratio}/{iteration}/time_slot_23999.csv'

            # cps
            compute_tasks, training_tasks = load_tasks(path)
            all_tasks = {**compute_tasks, **training_tasks}
            total_tasks_time_utilization = time_budget_utilization(all_tasks, evaluation_period_constant)
            total_tasks_time_utilization_minmax[ratio] = total_tasks_time_utilization_minmax.get(ratio, []) + total_tasks_time_utilization

            # naive
            compute_tasks, training_tasks = load_tasks(path2)
            all_tasks = {**compute_tasks, **training_tasks}
            total_tasks_time_utilization = time_budget_utilization(all_tasks, evaluation_period_constant)
            total_tasks_time_utilization_min[ratio] = total_tasks_time_utilization_min.get(ratio, []) + total_tasks_time_utilization

            # ============================== burst load =============================
            if ratio == 0.3:
                continue
            # cps
            compute_tasks, training_tasks = load_tasks(path)
            all_tasks = {**compute_tasks, **training_tasks}
            total_tasks_time_utilization = time_budget_utilization(all_tasks, evaluation_period_burst)
            total_tasks_time_utilization_minmax_burst[ratio] = total_tasks_time_utilization_minmax_burst.get(ratio,
                                                                                                 []) + total_tasks_time_utilization

            # naive
            compute_tasks, training_tasks = load_tasks(path2)
            all_tasks = {**compute_tasks, **training_tasks}
            total_tasks_time_utilization = time_budget_utilization(all_tasks, evaluation_period_burst)
            total_tasks_time_utilization_min_burst[ratio] = total_tasks_time_utilization_min_burst.get(ratio,
                                                                                           []) + total_tasks_time_utilization

    for key, value in total_tasks_time_utilization_minmax.items():
        print(len(total_tasks_time_utilization_min[key]))
        print(len(total_tasks_time_utilization_minmax[key]))
    print("==============")
    plot_time_utilization([
                            total_tasks_time_utilization_minmax,
                            total_tasks_time_utilization_min,
                            total_tasks_time_utilization_minmax_burst,
                            total_tasks_time_utilization_min_burst
                           ],
                          'Time budget utilization')