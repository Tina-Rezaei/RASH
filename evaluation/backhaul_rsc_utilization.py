import sys
sys.path.insert(1, '../core/')
from Load_tasks import load_tasks
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
import csv
import os.path

def read_constant_params(path):
    params = dict()
    with open(path) as f:
        lines = f.readlines()
        for line in lines:
            key, value = line.strip('\n').split(',')
            params[key] = float(value)
    return params


def read_comp_load(path, load_period):
    comp_load = []
    with open(path, 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if load_period["start"] <= int(csv_reader.line_num) <= load_period["end"]:
                if len(row) == 2:
                    comp_load.append(float(row[0]))
                else:
                    comp_load.append(float(row[1]))
    return comp_load


def read_data_size(path, load_period):
    data_size = []
    compute_tasks, training_tasks = load_tasks(path)
    all_tasks = {**compute_tasks, **training_tasks}
    for task_is, task_specs in all_tasks.items():
        if load_period["start"] <= int(task_specs["arrival_time"]/5) <= load_period["end"]:
            data_size.append(float(task_specs["data_size"]))
    return data_size


def read_data(path, load_period):
    comp_rsc_utilizatio = []
    bandwidth_rsc_utilization = []
    backhaul_rsc_utilization = []

    with open(path, 'r') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            if load_period["start"] <= int(csv_reader.line_num) <= load_period["end"]:
                comp_rsc_utilizatio.append(float(row[" comp_rsc_usage"])/float(params["comp_rsc"]))
                try:
                    bandwidth_rsc_utilization.append(float(row[" bandwidth_usage"])/float(params["bandwidth"]))
                except:
                    bandwidth_rsc_utilization.append(float(row["bandwidth_usage"])/float(params["bandwidth"]))

                backhaul_rsc_utilization.append(float(row[" backhaul_usage"])/float(params["backhaul"]))

    return bandwidth_rsc_utilization, comp_rsc_utilizatio, backhaul_rsc_utilization


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


def outlier_detection(data):
    print(len(data))
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)

    # Calculate IQR
    IQR = Q3 - Q1

    # Determine the outlier threshold
    lower_threshold = Q1 - 1.5 * IQR
    upper_threshold = Q3 + 1.5 * IQR

    # Identify outliers
    outliers = [x for x in data if x < lower_threshold or x > upper_threshold]

    # Print outliers
    print("Outliers:", len(outliers))


def plot_utilization(box_group1, box_group2, plot_name):
    color1 = "#0b84a5"
    color2 = "#f6c85f"
    color3 = "green"
    edge_color = "black"

    labels = list(box_group1[0].keys())
    fig, ax = plt.subplots()
    ax2 = ax.twinx()

    # Draw grid lines first
    ax.grid(color='lightgray', zorder=0)

    for i, label in enumerate(labels):
        values1 = [d[label] for d in box_group1]
        values2 = [d[label] for d in box_group2]

        base_position = i * 4
        positions1 = [base_position + 0.8, base_position + 1.6]
        positions2 = [base_position + 2.4]

        # Plot the first set of box plots
        box1 = ax.boxplot(values1, positions=positions1, widths=0.7, patch_artist=True,
                          boxprops=dict(facecolor=color1, edgecolor=edge_color), showfliers=False)
        for patch, color in zip(box1['boxes'], [color1, color2]):
            patch.set_facecolor(color)
        for element in ['whiskers', 'caps', 'medians']:
            plt.setp(box1[element], color=edge_color)
        box1['medians'][1].set_color(color2)

        ax.set_ylabel("Backhaul Utilization (%)", color="black", fontsize=14)
        ax.tick_params(axis='y', labelcolor="black", labelsize=12)
        # mean = np.mean(values1)
        # ax.scatter([base_position + 0.8], mean, color='red', marker='o', label='Mean')

        # Plot the second set of box plots
        box2 = ax2.boxplot(values2, positions=positions2, widths=0.7, patch_artist=True,
                           boxprops=dict(facecolor="green", edgecolor=edge_color), showfliers=False)
        for element in ['whiskers', 'caps', 'medians']:
            plt.setp(box2[element], color='darkgreen')

    ax2.set_ylabel("Data size", color="green", fontsize=16)
    ax2.tick_params(axis='y', labelcolor="green", labelsize=14)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

    plt.xlabel("Load", fontsize=16)
    ax.set_xlabel("Load", fontsize=16)
    # Set x-axis labels
    x_labels = ["70%", "100%", "150%"]
    plt.xticks([1.5, 5.5, 9.5], x_labels, fontsize=16)

    # Create the legend
    legend_patches = [
        mpatches.Patch(facecolor=color1, edgecolor=edge_color, label='RASH'),
        mpatches.Patch(facecolor=color2, edgecolor=edge_color, label='MinMaxDelay'),
        mpatches.Patch(facecolor='green', edgecolor='green', label='Data Size (Mb)')
    ]

    plt.legend(handles=legend_patches, loc='upper left', bbox_to_anchor=(0, 1), fontsize=14, fancybox=True,
               framealpha=0.7, ncol=2, borderaxespad=0.1)
    # Adjust layout to make room for the legend
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    # Set plot title and labels

    # plt.subplots_adjust(bottom=0.1)  # Adjust the bottom margin

    # Save the figure
    plt.savefig(f"{plot_name}.pdf", format="pdf", bbox_inches="tight")
    plt.savefig(f"{plot_name}.png", bbox_inches="tight")
    plt.show()


if __name__ == '__main__':

    param_path = "../core/parameters.txt"
    params = read_constant_params(param_path)
    load_list = [0.7, 1, 1.5]

    constant_load_period = {"start": 0, "end": (60 * 1000 )/ 5}

    total_tasks_bandwidth_utilization1 = {}
    total_tasks_bandwidth_utilization2 = {}
    total_tasks_bandwidth_utilization1_burst = {}
    total_tasks_bandwidth_utilization2_burst = {}

    total_tasks_backhaul_utilization1 = {}
    total_tasks_backhaul_utilization2 = {}
    total_tasks_backhaul_utilization1_burst = {}
    total_tasks_backhaul_utilization2_burst = {}

    data_size_1 = {}
    data_size_burst_1 = {}
    data_size_2 = {}
    data_size_burst_2 = {}

    total_load = {}
    total_load_burst = {}
    log_file_name = "time_slot_11999.csv"
    iterations = 11
    for ratio in load_list:
        for iteration in range(0, 10):
            time = [i*5 for i in range(11999)]
            baseline_utilization = []
            proposal_utilization = []
            path = f'../logs/min_max_p_{ratio}/tasks/naive/{iteration}/'
            path2 = f'../logs/min_max_D_{ratio}/tasks/naive/{iteration}/'

            # first path
            # computation load data
            bandwidth, comp, backhaul = read_data(os.path.join(path, 'rec_usage_summary.csv'), constant_load_period)
            data_size_1[ratio] = data_size_1.get(ratio, []) + read_data_size(os.path.join(path, log_file_name), constant_load_period)
            total_tasks_bandwidth_utilization1[ratio] = total_tasks_bandwidth_utilization1.get(ratio, []) + bandwidth
            total_tasks_backhaul_utilization1[ratio] = total_tasks_backhaul_utilization1.get(ratio, []) + backhaul
            proposal_utilization = bandwidth

            # second path
            bandwidth, comp, backhaul = read_data(os.path.join(path2, "rec_usage_summary.csv"), constant_load_period)
            data_size_2[ratio] = data_size_2.get(ratio, []) + read_data_size(os.path.join(path2, log_file_name), constant_load_period)
            total_tasks_bandwidth_utilization2[ratio] = total_tasks_bandwidth_utilization2.get(ratio, []) + bandwidth
            total_tasks_backhaul_utilization2[ratio] = total_tasks_backhaul_utilization2.get(ratio, []) + backhaul
            baseline_utilization = bandwidth

        # Plotting
            fig, ax = plt.subplots(1, 1, figsize=(10, 8), sharex=True)

            # Line plot overlay
            ax.plot(time, proposal_utilization, label='RASH', color="#0b84a5")
            ax.plot(time, baseline_utilization, label='MinMaxDelay', color="#f6c85f")
            ax.set_xlabel('Time (ms)',  fontsize=20)
            ax.set_ylabel('Backhaul Utilization (%)',  fontsize=20)
            ax.legend(loc='upper left', fontsize=18, mode="expand", ncol=2)
            plt.xticks(fontsize=18)
            plt.yticks(fontsize=18)
            plt.tight_layout()
            plt.ylim(ymax=1.15)
            plt.savefig("bakhaul-over-time.pdf", format="pdf")

            plt.show()
            # plt.show()
    plot_utilization([
        total_tasks_backhaul_utilization1,
        total_tasks_backhaul_utilization2,
    ], [  data_size_2],
        'Backhaul resource utilization')
