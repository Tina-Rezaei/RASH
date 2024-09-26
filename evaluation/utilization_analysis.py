import os
import csv

import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    model_name = 'RASH'
    path = '../min_max_obj/models/naive/criticality_ratio_0.3/'
    load_history_path = '../min_max_obj/tasks/naive/criticality_ratio_0.3/'
    iterations = 5
    rsc_utilization_dict = {}
    bandwidth_utilization_dict = {}
    x_axis_dict = {}
    total_load_dict = {}
    for iteration in range(10, 43):
        # read the csv file and plot the first column as y and number of row as x
        reader = csv.reader(open(os.path.join(path, f'{iteration}', 'rec_usage_summary.csv'), 'r'))
        utilization_list = list(reader)
        load_reader = csv.reader(open(os.path.join(load_history_path, f'{iteration}', 'load_history.txt'), 'r'))
        load_list = list(load_reader)
        rsc_utilization = []
        bandwidth_utilization = []
        total_load = []
        print(len(utilization_list))
        for i in range(1,len(utilization_list)-100, 100):
            relaxed_value = np.mean([float(utilization_list[j][1])/1 for j in range(i, i+100)])
            rsc_utilization.append(relaxed_value)
            # rsc_utilization.append(float(utilization_list[i][2])/2000)
            relaxed_value = np.mean([float(utilization_list[j][2])/0.032 for j in range(i, i+100)])
            bandwidth_utilization.append(relaxed_value)
            # bandwidth_utilization.append(float(utilization_list[i][1])/80)
            total_load.append(float(load_list[i][1]))
        x_axis = [i for i in range(len(rsc_utilization))]
        x_axis_dict.update({iteration: x_axis})
        rsc_utilization_dict.update({iteration: rsc_utilization})
        bandwidth_utilization_dict.update({iteration: bandwidth_utilization})

    plt.plot(x_axis_dict[12], rsc_utilization_dict[39], label='iteration 0')
    # plt.yscale('log')
    plt.xlabel('Time Slot')
    plt.ylabel('Computational Resource Utilization')
    plt.savefig('backhaul_rsc_utilization.pdf')
    plt.ylim(ymin=0)
    plt.show()
