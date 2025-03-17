import os

date = input("please enter the date you want to input data for: 'dd mm'\n")

worker_list = []

workers = input("number of workers:\n")
for i in range(0,int(workers)):
    worker_data = input("name, start, end: ").lower()
    worker_data = worker_data.split()
    # worker_list.append({worker, hour_start, hour_end})
    worker_list.append(worker_data)

for i in range(0, len(worker_list)):
    print(worker_list[i][0], worker_list[i][1], worker_list[i][2])
