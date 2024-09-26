import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter


def stacked_bar(locally_executed, remotely_executed, second_data):

    x = ['Local', 'Remote']

    x_pos = [0.3, 1.6]
    # x_pos = []
    # for i in range(5):
    #     l1 = i * 5
    #     x_pos += [l1+0.3, l1+1.6, l1+2.9]

    x_pos2 = [0.8, 2.1]
    # x_pos2 = []
    # for i in range(5):
    #     l1 = i * 5
    #     x_pos2 += [l1 + 0.8, l1 + 2.1, l1 + 3.4]

    y1, y2, y3, y4, y5, y6, y7, y8, y9 = [], [], [], [], [], [], [], [], []
    for key in locally_executed.keys():
        for my_dict in [locally_executed, remotely_executed]:
            items = my_dict[key]
            my_dict = Counter(items)
            y1.append(my_dict[1])
            y2.append(my_dict[2])
            y3.append(my_dict[3])
            y4.append(my_dict[4])
            y5.append(my_dict[5])
            y6.append(my_dict[6])
            y7.append(my_dict[7])
            y8.append(my_dict[8])
            y9.append(my_dict[9])

    z1, z2, z3, z4, z5, z6, z7, z8, z9 = [], [], [], [], [], [], [], [], []
    for key in locally_executed.keys():
        for my_dict in second_data:
            items = my_dict[key]
            my_dict = Counter(items)
            z1.append(my_dict[1])
            z2.append(my_dict[2])
            z3.append(my_dict[3])
            z4.append(my_dict[4])
            z5.append(my_dict[5])
            z6.append(my_dict[6])
            z7.append(my_dict[7])
            z8.append(my_dict[8])
            z9.append(my_dict[9])

    y1 = np.array(y1)
    y2 = np.array(y2)
    y3 = np.array(y3)
    y4 = np.array(y4)
    y5 = np.array(y5)
    y6 = np.array(y6)
    y7 = np.array(y7)
    y8 = np.array(y8)
    y9 = np.array(y9)

    z1 = np.array(z1)
    z2 = np.array(z2)
    z3 = np.array(z3)
    z4 = np.array(z4)
    z5 = np.array(z5)
    z6 = np.array(z6)
    z7 = np.array(z7)
    z8 = np.array(z8)
    z9 = np.array(z9)

    color2 = [253 / 256, 189 / 256, 112 / 256]
    color3 = [246 / 256, 166 / 256, 85 / 256]
    color4 = [221 / 235, 140 / 235, 75 / 235]
    color5 = [178 / 235, 120 / 235, 63 / 235]
    color6 = [158 / 235, 80 / 235, 53 / 235]
    color7 = [138 / 235, 60 / 235, 43 / 235]
    color8 = [108 / 235, 40 / 235, 30 / 235]
    color9 = [98 / 235, 10 / 235, 15 / 235]

    plt.bar(x_pos, y2, bottom=y1, color=color2, width=0.4, edgecolor='black')
    collection = plt.bar(x_pos2, z2, bottom=z1, color=color2, width=0.4, hatch='...', edgecolor='black')
    for patch in collection.patches:
        patch._hatch_color = [102/256,51/256,51/256]

    plt.bar(x_pos, y3, bottom=y1+y2, color=color3, width=0.4, edgecolor='black')
    collection = plt.bar(x_pos2, z3, bottom=z1+z2, color=color3, width=0.4, hatch='...', edgecolor='black')
    for patch in collection.patches:
        patch._hatch_color = [102/256,51/256,51/256]

    plt.bar(x_pos, y4, bottom=y1+y2+y3, color=color4, width=0.4, edgecolor='black')
    collection = plt.bar(x_pos2, z4, bottom=z1+z2+z3, color=color4, width=0.4, hatch='...', edgecolor='black')
    for patch in collection.patches:
        patch._hatch_color = [102/256,51/256,51/256]

    plt.bar(x_pos, y5, bottom=y1+y2+y3+y4, color=color5, width=0.4, edgecolor='black')
    collection = plt.bar(x_pos2, z5, bottom=z1+z2+z3+z4, color=color5, width=0.4, hatch='...', edgecolor='black')
    for patch in collection.patches:
        patch._hatch_color = [102/256,51/256,51/256]

    plt.bar(x_pos, y6, bottom=y1 + y2 + y3 + y4 + y5, color=color6, width=0.4, edgecolor='black')
    collection = plt.bar(x_pos2, z6, bottom=z1 + z2 + z3 + z4 + z5, color=color6, width=0.4, hatch='...', edgecolor='black')
    for patch in collection.patches:
        patch._hatch_color = [102 / 256, 51 / 256, 51 / 256]

    plt.bar(x_pos, y7, bottom=y1 + y2 + y3 + y4 + y5 + y6, color=color7, width=0.4, edgecolor='black')
    collection = plt.bar(x_pos2, z7, bottom=z1 + z2 + z3 + z4 + z5 + z6, color=color7, width=0.4, hatch='...', edgecolor='black')
    for patch in collection.patches:
        patch._hatch_color = [102 / 256, 51 / 256, 51 / 256]

    plt.bar(x_pos, y8, bottom=y1 + y2 + y3 + y4 + y5 + y6 + y7, color=color8, width=0.4, edgecolor='black')
    collection = plt.bar(x_pos2, z8, bottom=z1 + z2 + z3 + z4 + z5 + z6 + z7, color=color8, width=0.4, hatch='...', edgecolor='black')
    for patch in collection.patches:
        patch._hatch_color = [102 / 256, 51 / 256, 51 / 256]

    plt.bar(x_pos, y9, bottom=y1 + y2 + y3 + y4 + y5 + y6 + y7 + y8, color=color9, width=0.4, edgecolor='black')
    collection = plt.bar(x_pos2, z9, bottom=z1 + z2 + z3 + z4 + z5 + z6 + z7 + z8, color=color9, width=0.4, hatch='...',
                         edgecolor='black')
    for patch in collection.patches:
        patch._hatch_color = [102 / 256, 51 / 256, 51 / 256]

    plt.xticks([0.55,1.85], x, fontsize=9, rotation = 'vertical')
    plt.yticks(fontsize=10)

    legend_patches = [
        mpatches.Patch(facecolor=color9, edgecolor='black', label='Sensitivity level 9'),
        mpatches.Patch(facecolor=color8, edgecolor='black', label='Sensitivity level 8'),
        mpatches.Patch(facecolor=color7, edgecolor='black', label='Sensitivity level 7'),
        mpatches.Patch(facecolor=color6, edgecolor='black', label='Sensitivity level 6'),
        mpatches.Patch(facecolor=color5, edgecolor='black', label='Sensitivity level 5'),
        mpatches.Patch(facecolor=color4, edgecolor='black', label='Sensitivity level 4'),
        mpatches.Patch(facecolor=color3, edgecolor='black', label='Sensitivity level 3'),
        mpatches.Patch(facecolor=color2, edgecolor='black', label='Sensitivity level 2'),
        mpatches.Patch(facecolor='white', edgecolor='black', hatch='...', label='minmax Delay'),
    ]
    # Add legend

    # Update the legend
    # plt.ylim(ymax=100)
    legend = plt.legend(handles=legend_patches, loc='upper left', fontsize=8, fancybox=True, framealpha=0.7,
                       ncol=3)
    plt.ylabel('Number of tasks', fontsize=12)
    plt.xlabel('30% load', fontsize=12)
    plt.savefig("privacy_assessment_constant.pdf", format="pdf", bbox_inches="tight")
    plt.savefig("privacy_assessment.png", bbox_inches='tight')
    plt.show()


def jair_fairness(data):
    resources_per_user = {2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0}
    for resource in data:
        if resource not in resources_per_user:
            resources_per_user[resource] = 0
        resources_per_user[resource] += 1
    print(dict(sorted(resources_per_user.items())))
    # Calculate Jain's fairness index
    num_users = len(resources_per_user)
    total_resources = sum(resources_per_user.values())
    fairness_index = (sum(resources_per_user.values()) ** 2) / (
                num_users * sum(x ** 2 for x in resources_per_user.values()))
    return fairness_index

def read_data(evaluation_period):
    privacy_scores_local_min_max = {1:[]}
    privacy_scores_remote_min_max = {1:[]}
    privacy_scores_local_min = {1:[]}
    privacy_scores_remote_min = {1:[]}
    for criticality_ratio in criticality_list:
        for iteration in range(1, 34):
            path = f'../min_max_obj/tasks/{dropping_strategy}/criticality_ratio_{criticality_ratio}/{iteration}/time_slot_23999.csv'
            path2 = f'../min_max_punaware_obj/tasks/{dropping_strategy}/criticality_ratio_{criticality_ratio}/{iteration}/time_slot_23999.csv'

            with open(path, 'r') as f:
                csv_reader = csv.DictReader(f)
                for row in csv_reader:
                    if evaluation_period['start'] < float(row['arrival_time']) < evaluation_period['end']:
                        if row['completed'] == "True":
                            if float(row['alpha']) == 0:
                                privacy_scores_local_min_max[1].append(float(row['privacy_score']))
                            else:
                                privacy_scores_remote_min_max[1].append(float(row['privacy_score']))

            with open(path2, 'r') as f:
                csv_reader = csv.DictReader(f)
                for row in csv_reader:
                    if evaluation_period['start'] < float(row['arrival_time']) < evaluation_period['end']:
                        if row['completed'] == "True":
                            if float(row['alpha']) == 0:
                                privacy_scores_local_min[1].append(float(row['privacy_score']))
                            else:
                                privacy_scores_remote_min[1].append(float(row['privacy_score']))
    return privacy_scores_local_min_max, privacy_scores_remote_min_max, privacy_scores_local_min, privacy_scores_remote_min


if __name__ == '__main__':
    # read a csv file
    iterations = 17
    privacy_risk = 0
    total_privacy_scores = 0
    load_list = []
    evaluation_period_constant = {'start': 1 * 0 * 1000, 'end': 1 * 30 * 1000}  # ms (4 minutes)
    evaluation_period_burst = {'start': 1 * 30 * 1000, 'end': 1 * 60 * 1000}  # ms (4 minutes)
    criticality_list = [0.3]
    dropping_strategy = 'naive'

    privacy_scores_local_min_max, privacy_scores_remote_min_max, privacy_scores_local_min, privacy_scores_remote_min = read_data(evaluation_period_constant)

    stacked_bar(privacy_scores_local_min_max, privacy_scores_remote_min_max, [privacy_scores_local_min, privacy_scores_remote_min])

    from collections import Counter

    print(dict(sorted(Counter(privacy_scores_local_min_max[1]).items())))
    print(Counter(privacy_scores_local_min[1]))
    print("===============")

    print(Counter(privacy_scores_remote_min_max[1]))
    print(Counter(privacy_scores_remote_min[1]))

    print(len(privacy_scores_remote_min_max[1]))
    print(len(privacy_scores_remote_min[1]))

    print(len(privacy_scores_local_min_max[1]))
    print(len(privacy_scores_local_min[1]))

    print("jair fairness local_min_max:", jair_fairness(privacy_scores_local_min_max[1]), "\n")
    print("jair fairness local_min:", jair_fairness(privacy_scores_local_min[1]), "\n")
    print("jair fairness remote_min_max:", jair_fairness(privacy_scores_remote_min_max[1]), "\n")
    print("jair fairness remote_min:", jair_fairness(privacy_scores_remote_min[1]), "\n")