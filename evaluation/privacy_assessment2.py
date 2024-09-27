import numpy as np
import matplotlib.pyplot as plt
import csv

from collections import Counter

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

import numpy as np
import matplotlib.pyplot as plt

import numpy as np
import matplotlib.pyplot as plt


def plot_privacy_sensitivity(privacy_scores_local1, privacy_scores_remote1, privacy_scores_local2, privacy_scores_remote2, all_tasks_min_max, all_tasks_min):
    categories = np.arange(2, 10)  # Privacy sensitivity levels
    # Using colorblind-friendly colors
    total_color2 = '#f2c45f'
    remote_color2 = '#cf8b38'
    total_color1 = '#5FA8C6'
    remote_color1 = '#2066a8'  
    # Count the number of tasks executed remotely for each sensitivity level for dataset 1
    remote_counts1 = [sum(1 for score in privacy_scores_remote1 if score == sensitivity) for sensitivity in categories]
    local_counts1 = [sum(1 for score in privacy_scores_local1 if score == sensitivity) for sensitivity in categories]
    total_counts1 = [remote_counts1[i] + local_counts1[i] for i in range(len(remote_counts1))]
    all_tasks1 = [sum(1 for score in all_tasks_min_max if score == sensitivity) for sensitivity in categories]

    # Count the number of tasks executed remotely for each sensitivity level for dataset 2
    remote_counts2 = [sum(1 for score in privacy_scores_remote2 if score == sensitivity) for sensitivity in categories]
    local_counts2 = [sum(1 for score in privacy_scores_local2 if score == sensitivity) for sensitivity in categories]
    total_counts2 = [remote_counts2[i] + local_counts2[i] for i in range(len(remote_counts2))]
    all_tasks2 = [sum(1 for score in all_tasks_min if score == sensitivity) for sensitivity in categories]

    # Calculate the percentage of tasks executed remotely for each sensitivity level for dataset 1
    remote_percentages1 = [remote_counts1[i] / total_counts1[i] for i in range(len(remote_counts1))]

    # Calculate the percentage of satisfied for each sensitivity level tasks for dataset 1
    satisfied_percentages1 = [total_counts1[i] / all_tasks1[i] for i in range(len(all_tasks1))]

    # Calculate the percentage of tasks executed remotely for each sensitivity level for dataset 2
    remote_percentages2 = [remote_counts2[i] / total_counts2[i] for i in range(len(remote_counts2))]

    # Calculate the percentage of satisfied for each sensitivity level tasks for dataset 2
    satisfied_percentages2 = [total_counts2[i] / all_tasks2[i] for i in range(len(all_tasks2))]

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 6))

    # Width of each bar
    bar_width = 0.35

    # X positions for the bars
    x1 = categories - bar_width / 2
    x2 = categories + bar_width / 2

    # Green bars represent total tasks for dataset 1
    # ax.bar(x1, np.ones_like(categories), color=total_color1, width=bar_width, alpha=0.5, label='Total Tasks - RASH')
    ax.bar(x1, satisfied_percentages1, color=total_color1, width=bar_width, alpha=0.5, label='Total Tasks - RASH')

    # Red bars represent tasks executed remotely for dataset 1
    ax.bar(x1, remote_percentages1, color=remote_color1, width=bar_width, alpha=0.5, label='Remote Execution - RASH')

    # Blue bars represent total tasks for dataset 2
    # ax.bar(x2, np.ones_like(categories), color=total_color2, width=bar_width, alpha=0.5, label='Total Tasks - MinMax D')
    ax.bar(x2, satisfied_percentages2, color=total_color2, width=bar_width, alpha=0.5, label='Total Tasks - MinMaxDelay')

    # Orange bars represent tasks executed remotely for dataset 2
    ax.bar(x2, remote_percentages2, color=remote_color2, width=bar_width, alpha=0.5, label='Remote Execution - MinMaxDelay')

    # ax.set_xlabel('Privacy Sensitivity Level',fontsize=14)
    plt.xlabel('Privacy Sensitivity Level',fontsize=20)
    # ax.set_ylabel('Percentage of Tasks', fontsize=14)
    plt.ylabel('Percentage of Tasks', fontsize=20)
    # ax.set_title('Privacy Sensitivity vs. Remote Execution')

    # ax.set_xticks(categories)
    plt.xticks(categories, fontsize=14)
    ax.set_xticklabels(categories)
    # ax.set_yticks(np.arange(0, 1.1, 0.1), fontsize=12)
    plt.yticks(np.arange(0, 1.1, 0.1), fontsize=14)
    ax.set_ylim(0, 1.3)
    ax.legend(fontsize=16, ncol=2, fancybox=True, loc='upper center', framealpha=0.7, mode= "expand")
    # plt.ylim(ymin=0, ymax=1.23)
    plt.savefig("privacy_assessment_150.pdf", format="pdf", bbox_inches='tight')
    plt.show()


# def plot_privacy_sensitivity(privacy_scores_local1, privacy_scores_remote1, privacy_scores_local2, privacy_scores_remote2):
#     categories = np.arange(2, 10)  # Privacy sensitivity levels
#
#     # Count tasks for dataset 1
#     remote_counts1 = [sum(1 for score in privacy_scores_remote1 if score == sensitivity) for sensitivity in categories]
#     local_counts1 = [sum(1 for score in privacy_scores_local1 if score == sensitivity) for sensitivity in categories]
#     total_counts1 = [remote_counts1[i] + local_counts1[i] for i in range(len(remote_counts1))]
#
#     # Count tasks for dataset 2
#     remote_counts2 = [sum(1 for score in privacy_scores_remote2 if score == sensitivity) for sensitivity in categories]
#     local_counts2 = [sum(1 for score in privacy_scores_local2 if score == sensitivity) for sensitivity in categories]
#     total_counts2 = [remote_counts2[i] + local_counts2[i] for i in range(len(remote_counts2))]
#
#     fig, ax = plt.subplots(figsize=(12, 6))
#     bar_width = 0.35
#     x1 = categories - bar_width / 2
#     x2 = categories + bar_width / 2
#
#     # Stacked bars for dataset 1
#     ax.bar(x1, total_counts1, color='green', width=bar_width,  alpha=0.5, label='Total Tasks - RASH')
#     ax.bar(x1, remote_counts1, color='red', width=bar_width,  alpha=0.5, label='Remote Tasks - RASH')
#
#     # Stacked bars for dataset 2
#     ax.bar(x2, total_counts2, color='blue', width=bar_width,  alpha=0.5, label='Total Tasks - MinmaxD')
#     ax.bar(x2, remote_counts2, color='orange', width=bar_width,  alpha=0.5, label='Remote Tasks - MinmaxD')
#
#     plt.xlabel('Privacy Sensitivity Level', fontsize=18)
#     plt.ylabel('Number of Tasks', fontsize=18)
#     plt.xticks(categories, fontsize=14)
#     plt.yticks(fontsize=14)
#     ax.set_ylim(0, max(max(total_counts1), max(total_counts2)) * 1.1)
#     ax.legend(fontsize=14, ncol=2, fancybox=True, loc='upper center', framealpha=0.7, mode= "expand")
#     plt.savefig("privacy_assessment_modified.pdf", format="pdf", bbox_inches='tight')
#     plt.show()


def plot_privacy_sensitivity_with_line(privacy_scores_local1, privacy_scores_remote1, privacy_scores_local2, privacy_scores_remote2, all_tasks_min_max, all_tasks_min):
    categories = np.arange(2, 10)  # Privacy sensitivity levels

    # Count tasks and calculate percentages for dataset 1
    remote_counts1 = [sum(1 for score in privacy_scores_remote1 if score == sensitivity) for sensitivity in categories]
    local_counts1 = [sum(1 for score in privacy_scores_local1 if score == sensitivity) for sensitivity in categories]
    total_counts1 = [remote_counts1[i] + local_counts1[i] for i in range(len(remote_counts1))]
    remote_percentages1 = [remote_counts1[i] / total_counts1[i] if total_counts1[i] != 0 else 0 for i in range(len(remote_counts1))]

    # Count tasks and calculate percentages for dataset 2
    remote_counts2 = [sum(1 for score in privacy_scores_remote2 if score == sensitivity) for sensitivity in categories]
    local_counts2 = [sum(1 for score in privacy_scores_local2 if score == sensitivity) for sensitivity in categories]
    total_counts2 = [remote_counts2[i] + local_counts2[i] for i in range(len(remote_counts2))]
    remote_percentages2 = [remote_counts2[i] / total_counts2[i] if total_counts2[i] != 0 else 0 for i in range(len(remote_counts2))]

    fig, ax1 = plt.subplots(figsize=(12, 6))
    bar_width = 0.35
    x1 = categories - bar_width / 2
    x2 = categories + bar_width / 2

    # Bar chart for total tasks
    ax1.bar(x1, total_counts1, color='gray', width=bar_width, label='Total Tasks - RASH')
    ax1.bar(x2, total_counts2, color='blue', width=bar_width, label='Total Tasks - MinmaxDelay')

    # Line chart for remote task percentages
    ax2 = ax1.twinx()
    ax2.plot(categories, remote_percentages1, color='red', marker='o', label='Remote Execution % - RASH')
    ax2.plot(categories, remote_percentages2, color='orange', marker='o', label='Remote Execution % - MinmaxDelay')

    ax1.set_xlabel('Privacy Sensitivity Level', fontsize=18)
    ax1.set_ylabel('Number of Tasks', fontsize=18)
    ax2.set_ylabel('Percentage of Remote Tasks', fontsize=18)

    ax1.set_xticks(categories)
    ax1.set_xticklabels(categories)
    ax1.legend(loc='upper left', fontsize=14)
    ax2.legend(loc='upper right', fontsize=14)

    # Setting the percentage range from 0 to 100 for the secondary y-axis
    ax2.set_ylim(0, 1)
    ax2.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))

    plt.savefig("privacy_assessment_bar_line.pdf", format="pdf", bbox_inches='tight')
    plt.show()


def read_data(evaluation_period):
    privacy_scores_local_min_max = {1:[]}
    privacy_scores_remote_min_max = {1:[]}
    privacy_scores_local_min = {1:[]}
    privacy_scores_remote_min = {1:[]}
    all_tasks_min_max = {1:[]}
    all_tasks_min = {1:[]}
    privacy_score_difference = []

    for iteration in range(0, 10):
        path = f'../logs/min_max_p_1.5/{dropping_strategy}/{iteration}/time_slot_11999.csv'
        path2 = f'../logs/min_max_delay_1.5/{dropping_strategy}/{iteration}/time_slot_11999.csv'

        total_lost_privacy_1 = 0
        total_lost_privacy_2 = 0
        with open(path, 'r') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                if evaluation_period['start'] < float(row['arrival_time']) < evaluation_period['end']:
                    if row['completed'] == "True":
                        if float(row['alpha']) == 0:
                            privacy_scores_local_min_max[1].append(float(row['privacy_score']))
                        else:
                            privacy_scores_remote_min_max[1].append(float(row['privacy_score']))
                            total_lost_privacy_1 += float(row['privacy_score'])
                    if row['overdue'] != "False" or row['completed'] != "False":
                        all_tasks_min_max[1].append(float(row['privacy_score']))

        with open(path2, 'r') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                if evaluation_period['start'] < float(row['arrival_time']) < evaluation_period['end']:
                    if row['completed'] == "True":
                        if float(row['alpha']) == 0:
                            privacy_scores_local_min[1].append(float(row['privacy_score']))
                        else:
                            privacy_scores_remote_min[1].append(float(row['privacy_score']))
                            total_lost_privacy_2 += float(row['privacy_score'])

                    if row['overdue'] != "False" or row['completed'] != "False":
                        all_tasks_min[1].append(float(row['privacy_score']))
        privacy_score_difference.append(total_lost_privacy_2 - total_lost_privacy_1)
    plt.boxplot(privacy_score_difference)
    plt.show()
    return privacy_scores_local_min_max, privacy_scores_remote_min_max, privacy_scores_local_min, privacy_scores_remote_min, all_tasks_min_max, all_tasks_min


if __name__ == '__main__':
    # read a csv file
    iterations = 17
    privacy_risk = 0
    total_privacy_scores = 0
    load_list = []
    evaluation_period = {'start': 1 * 0 * 1000, 'end': 1 * 30 * 1000}  # ms (4 minutes)
    dropping_strategy = 'heuristic'

    privacy_scores_local_min_max, privacy_scores_remote_min_max, privacy_scores_local_min, privacy_scores_remote_min, all_tasks_min_max, all_tasks_min = read_data(evaluation_period)

    print(dict(sorted(Counter(privacy_scores_local_min_max[1]).items())))
    print(Counter(privacy_scores_local_min[1]))
    print(Counter(privacy_scores_local_min_max[1]))
    print("===============")

    print(Counter(privacy_scores_remote_min_max[1]))
    print(Counter(privacy_scores_remote_min[1]))

    print(len(privacy_scores_remote_min_max[1]))
    print(len(privacy_scores_remote_min[1]))

    print(len(privacy_scores_local_min_max[1]))
    print(len(privacy_scores_local_min[1]))


    # plot_privacy_sensitivity_with_line(privacy_scores_local_min_max[1], privacy_scores_remote_min_max[1], privacy_scores_local_min[1], privacy_scores_remote_min[1], all_tasks_min_max[1], all_tasks_min[1])
    plot_privacy_sensitivity(privacy_scores_local_min_max[1], privacy_scores_remote_min_max[1], privacy_scores_local_min[1], privacy_scores_remote_min[1], all_tasks_min_max[1], all_tasks_min[1])
