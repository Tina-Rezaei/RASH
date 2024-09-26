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


def plot_utilization(plot_dictionary, plot_dictionary2, plot_name):
    plt.clf()
    datasets = []
    for i in range(len(plot_dictionary)):
        df = pd.DataFrame(plot_dictionary[i])
        datasets.append(df.fillna(df.median()))

    # Define which colours you want to use
    color1 = "#0b84a5"
    color2 = "#f6c85f"

    # Define the groups
    labels1 = plot_dictionary[0].keys()
    fig, ax = plt.subplots()
    # ax2 = ax.twinx()
    for i, label in enumerate(labels1):
        values = [d[label] for d in [plot_dictionary[0], plot_dictionary[1]]]
        values2 = [d[label] for d in [plot_dictionary2[0], plot_dictionary2[1]]]

        base_position1 = i * 3
        # Define the positions for the first set of box plots
        positions1 = [base_position1, base_position1 + 1]

        box = ax.boxplot(values, positions=positions1, widths=0.7, patch_artist=True,
                         boxprops=dict(facecolor=color1), showfliers=False)

        for element in ['whiskers', 'fliers', 'medians', 'caps']:
            plt.setp(box[element], color='black')
            plt.setp(box['medians'], color='black')
        box['boxes'][0].set_facecolor(color1)
        box['boxes'][1].set_facecolor(color2)
        box['medians'][1].set_color(color2)

        # Define the positions for the second set of box plots
        # positions2 = [base_position1 + 0.5, base_position1 + 1.8]
        #
        # box2 = ax2.boxplot(values2, positions=positions2, widths=0.7, patch_artist=True,
        #                   boxprops=dict(facecolor="green"), showfliers=False)
        # for element in ['whiskers', 'caps', 'medians']:
        #     plt.setp(box2[element], color='darkgreen')

    # Set x-axis labels
    labels = ["70%", "100%", '150%']
    # ax2.set_ylabel("System load", color="green", fontsize=16)
    # ax2.tick_params(axis='y', labelcolor="green", labelsize=14)
    plt.xticks([0.5, 3.5, 6.5], labels, fontsize=12)
    plt.yticks(fontsize=12)
    legend_patches = [
        mpatches.Patch(facecolor=color1, edgecolor='black', label='RASH'),
        mpatches.Patch(facecolor=color2, edgecolor='black', label='MinMaxDelay'),
        # mpatches.Patch(facecolor="green", edgecolor='black', label='System load - RASH'),

    ]

    legend = plt.legend(handles=legend_patches, loc='upper left', fontsize=14, fancybox=True, framealpha=0.7,
                        mode="expand", ncol=2)

    # Set plot title and labels
    plt.ylabel(plot_name, fontsize=14)
    # plt.xlabel("Time period", fontsize=12)

    # plt.legend(handles=legend_elements, fontsize=13, loc="upper right")
    plt.grid(color='lightgray')
    # plt.yscale('symlog')
    # ticks = [0, 1, 10]
    labels = ['0', '1', '10']
    # plt.yticks(ticks, labels)
    plt.xlabel("Load", fontsize=16)
    plt.ylim(ymax=1.2)

    # plt.savefig(f'{plot_name}_{backhaul}_{scheme_number}')
    plt.savefig(f"{plot_name}.pdf", format="pdf", bbox_inches="tight")
    plt.savefig(f"{plot_name}.png", bbox_inches="tight")
    plt.show()


if __name__ == '__main__':
    param_path = "../core/parameters.txt"
    params = read_constant_params(param_path)
    load_list = [0.7, 1, 1.5]

    constant_load_period = {"start": 0, "end": 30 * 1000 / 5}
    burst_load_period = {"start": 30 * 1000 / 5, "end": 60 * 1000 / 5}

    total_tasks_comp_utilization1 = {}
    total_tasks_comp_utilization2 = {}
    total_tasks_comp_utilization1_burst = {}
    total_tasks_comp_utilization2_burst = {}
    comp_load1 = {}
    comp_load2 = {}
    comp_load1_burst = {}
    comp_load2_burst = {}

    data_size_1 = {}
    data_size_burst_1 = {}
    data_size_2 = {}
    data_size_burst_2 = {}

    total_load = {}
    total_load_burst = {}


    iterations = 11
    for ratio in load_list:
        for iteration in range(0, 10):
            path = f'../logs/min_max_p_{ratio}/tasks/naive/{iteration}'
            path2 = f'../logs/min_max_D_{ratio}/tasks/naive/{iteration}/'

            # ======================= constant load ===========================
            # first path
            # computation load data
            comp_load1[ratio] = comp_load1.get(ratio, []) + read_comp_load(os.path.join(path, "load_history.txt"), constant_load_period)
            bandwidth, comp, backhaul = read_data(os.path.join(path, 'rec_usage_summary.csv'), constant_load_period)
            data_size_1[ratio] = data_size_1.get(ratio, []) + read_data_size(os.path.join(path, "time_slot_11999.csv"), constant_load_period)
            total_tasks_comp_utilization1[ratio] = total_tasks_comp_utilization1.get(ratio, []) + comp

            # second path
            comp_load2[ratio] = comp_load2.get(ratio, []) + read_comp_load(os.path.join(path2, "load_history.txt"), constant_load_period)
            bandwidth, comp, backhaul = read_data(os.path.join(path2, "rec_usage_summary.csv"), constant_load_period)
            data_size_2[ratio] = data_size_2.get(ratio, []) + read_data_size(os.path.join(path2, "time_slot_11999.csv"), constant_load_period)
            total_tasks_comp_utilization2[ratio] = total_tasks_comp_utilization2.get(ratio, []) + comp


            # load = 0
            # total_load[ratio] = total_load.get(ratio, []) + load
            # total_load_burst[ratio] = total_load.get(ratio, []) + load

    plot_utilization([
        total_tasks_comp_utilization1,
        total_tasks_comp_utilization2,
    ], [comp_load1, comp_load2],
    'Computation resource utilization (%)')
