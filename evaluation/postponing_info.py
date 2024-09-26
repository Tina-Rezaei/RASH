import csv
import matplotlib.pyplot as plt
from collections import Counter
import sys
sys.path.insert(1, '../core/')
from Load_tasks import load_tasks_from_csv



def read_data(path):
    compute_tasks, training_tasks = load_tasks_from_csv(path)
    all_tasks = {**compute_tasks, **training_tasks}
    return all_tasks


def training_vs_execute(tasks_ids, all_tasks):
    training_tasks_ids = []
    execute_tasks_ids = []
    for task_id, task_specs in all_tasks.items():
        if task_specs["task_type"] == "training":
            training_tasks_ids.append(task_id)
        else:
            execute_tasks_ids.append(task_id)

    counter = 0
    training_execute = {"training": [], "execute": []}
    for id in tasks_ids:
        if id in training_tasks_ids:
            counter += 1
            training_execute["training"].append(id)
        else:
            training_execute["execute"].append(id)

    return training_execute, len(training_execute["training"])/len(training_tasks_ids)


iterations = 10
postponing_happened = []
postponing_calls = []
number_of_outstanding_tasks_list = []
ratio_of_postponed_tasks = []
potponed_training_percentages_list = []
potponed_execute_percentages_list = []
percentage_training_postponed_list = []

for iter in range(iterations):
    base_path = f"/home/tina/PycharmProjects/RASH/logs/min_max_p_0.7/tasks/naive/{iter}/"
    path = f"/home/tina/PycharmProjects/RASH/logs/min_max_p_0.7/tasks/naive/{iter}/tasks_report.csv"
    all_tasks = read_data(base_path + "time_slot_11999.csv")

    # read tasks report for each iteration
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        number_of_postponed_tasks_list = []
        counter = 0
        total_time_slots = 0
        for line in reader:
            total_time_slots += 1
            if line[" #postponed tasks"] != ' ':
                number_of_postponed_tasks = (int(line[" #postponed tasks"]))
                number_of_postponed_tasks_list.append(number_of_postponed_tasks)
                number_of_outstanding_tasks = (int(line[" total tasks"]) - int(line[" #overdue tasks"]) - int(line[" completed tasks"]))
                ratio_of_postponed_tasks.append(number_of_postponed_tasks/number_of_outstanding_tasks)
                if number_of_postponed_tasks/number_of_outstanding_tasks > 1:
                    print(number_of_postponed_tasks/number_of_outstanding_tasks)
                    print(iter, line["time slot"])
                    print("=================================")
                counter += 1
                # check percentage of training tasks and execute tasks among postponed tasks
                postponed_tasks_ids = [int(element) for element in line[" postponed tasks ids"].split("-")]
                training_execute, percentage_training_postponed = training_vs_execute(postponed_tasks_ids, all_tasks)
                percentage_training_postponed_list.append(percentage_training_postponed)
                training_percentages = len(training_execute["training"])/len(postponed_tasks_ids)
                execute_percentages = len(training_execute["execute"])/len(postponed_tasks_ids)
                potponed_training_percentages_list.append(training_percentages)
                potponed_execute_percentages_list.append(execute_percentages)
                print("percentages:", training_percentages, execute_percentages)
            if line[" # postpone calls"] != ' ':
                postponing_calls.append(int(line[" # postpone calls"]))


        print(counter, total_time_slots)

        # postponing_happened.append(counter/total_time_slots)
        # plt.boxplot(number_of_postponed_tasks)
        # plt.show()

plt.title("number of times postponing happens")
plt.boxplot(postponing_happened)
plt.show()

plt.title("ratio of training tasks compared to execute tasks among postponed tasks")
plt.boxplot(potponed_training_percentages_list)
plt.show()

plt.title("ratio of execute tasks compared to training tasks among postponed tasks")
plt.boxplot(potponed_execute_percentages_list)
plt.show()

plt.title("percentage of training tasks among postponed tasks")
plt.boxplot(percentage_training_postponed_list)
plt.show()


plt.title("ratio of postponed tasks")
plt.boxplot(ratio_of_postponed_tasks)
plt.show()


counter = Counter(postponing_calls)
total_count = len(postponing_calls)
percentages = {key: (value/total_count) * 100 for key, value in counter.items()}

for key, value in percentages.items():
    print(key, value)























