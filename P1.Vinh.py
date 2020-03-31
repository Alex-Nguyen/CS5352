"""
Vinh T. Nguyen
"""

from memory_profiler import memory_usage
import psutil
import os
import cProfile
import re
from random import seed
from random import randint
import io
import pstats
from pstats import SortKey
import multiprocessing as mp
import time
import marshal
import pandas as pd
pd.options.display.float_format = '{:,.5f}'.format
"""
First come first serve algorithm
@input: data list
@output none
"""


def first_come_first_serve(process_data):
    _pid = os.getpid()
    _py = psutil.Process(_pid)
    print(f"FCFO : {_pid}")
    _data = process_data.copy()
    total_waiting_time = 0
    total_turnaround_time = 0
    waiting_time = [0]
    turnaround_time = []

    for i in range(1, len(_data)):
        wt = _data[i - 1][1] + waiting_time[i - 1]
        waiting_time.append(wt)

    for i in range(len(_data)):
        tt = _data[i][1] + waiting_time[i]
        turnaround_time.append(tt)

    for i in range(len(_data)):
        total_waiting_time += waiting_time[i]
        total_turnaround_time += turnaround_time[i]
    print(f'Average Turnaround Time: {total_turnaround_time / 4}')
    print(f'Average Waiting Time: {total_waiting_time / 4}')


"""
Shortest Job First Algorithm
@input: data list
@output none
"""


def shortest_job_first(process_data):
    _pid = os.getpid()
    _py = psutil.Process(_pid)
    print(f"Shortest job first pid : {_pid}")
    _data = process_data.copy()
    total_waiting_time = 0
    total_turnaround_time = 0
    _data.sort(key=lambda x: x[1])
    waiting_time = [0]
    turnaround_time = []
    for i in range(1, len(_data)):
        wt = _data[i - 1][1] + waiting_time[i - 1]
        waiting_time.append(wt)

    for i in range(len(_data)):
        tt = _data[i][1] + waiting_time[i]
        turnaround_time.append(tt)

    for i in range(len(_data)):
        total_waiting_time += waiting_time[i]
        total_turnaround_time += turnaround_time[i]
    print(f'Average Turnaround Time: {total_turnaround_time / len(_data)}')
    print(f'Average Waiting Time: {total_waiting_time / len(_data)}')


def monitor(target):
    worker_process = mp.Process(target=target)
    worker_process.start()
    p = psutil.Process(worker_process.pid)

    # log cpu usage of `worker_process` every 10 ms
    cpu_percents = []
    while worker_process.is_alive():
        cpu_percents.append(p.cpu_percent())
        time.sleep(0.01)

    worker_process.join()
    return cpu_percents


if __name__ == "__main__":
    # Data for processing
    number_of_jobs = int(input("Enter the number of jobs: "))
    data = []
    seed(10)
    for i in range(number_of_jobs):
        data.append([i, randint(2, 50)])
    pid = os.getpid()
    py = psutil.Process(pid)

    # Measure memory performance
    sjf_mem = memory_usage((shortest_job_first, (data,)))
    fcfs_mem = memory_usage((first_come_first_serve, (data,)))
    SJF_PROFFILE = 'sjf.profile'
    cProfile.run('shortest_job_first(data)', SJF_PROFFILE)
    stats = pstats.Stats(SJF_PROFFILE)
    sjf_total_tt = 0  # Total in seconds
    with open(SJF_PROFFILE, 'rb') as f:
        viewer = marshal.load(f)
        for func, (cc, nc, tt, ct, callers) in viewer.items():
            sjf_total_tt += tt

    FIFO_PROFFILE = 'fifo.profile'
    cProfile.run('first_come_first_serve(data)', FIFO_PROFFILE)
    fifo_stats = pstats.Stats(FIFO_PROFFILE)
    fifo_total_tt = 0  # Total in seconds
    with open(FIFO_PROFFILE, 'rb') as f:
        viewer = marshal.load(f)
        for func, (cc, nc, tt, ct, callers) in viewer.items():
            fifo_total_tt += tt

    shortest_job_first(data)
    sjb_cpu_percentage = psutil.cpu_percent(interval=1)
    sjf_mem_rss = py.memory_info().rss
    sjf_mem_vms = py.memory_info().vms
    sjf_mem_fagefaults = py.memory_info().num_page_faults
    sjf_diskusage_writecount = psutil.disk_io_counters().write_count
    # print(f"After SJF: {psutil.cpu_percent(interval=1)}")
    # print(f"Disk usage: {psutil.disk_io_counters()}")
    # print(f"Memory info: {py.memory_info()}")
    first_come_first_serve(data)
    fifo_cpu_percentage = psutil.cpu_percent(interval=1)
    fifo_mem_rss = py.memory_info().rss
    fifo_mem_vms = py.memory_info().vms
    fifo_mem_pagefaults = py.memory_info().num_page_faults
    fifo_diskusage_writecount = psutil.disk_io_counters().write_count

    df = pd.DataFrame(columns=['Measure', 'SJF', 'FIFO'])
    df.loc[0] = ['Memory Usage (MB)', sjf_mem[0], fcfs_mem[0]]
    df.loc[1] = ['CPU Usage (%)', sjb_cpu_percentage, fifo_cpu_percentage]
    df.loc[2] = ['Hard Drive Usage (Writes)', sjf_diskusage_writecount, fifo_diskusage_writecount]
    df.loc[3] = ['Resident Set Size (Bytes)', sjf_mem_rss, fifo_mem_rss]
    df.loc[4] = ['Virtual Memory Size (Bytes)', sjf_mem_vms, fifo_mem_vms]
    df.loc[5] = ['Page Faults', sjf_mem_fagefaults, fifo_mem_pagefaults]
    df.loc[6] = ['Running Time (Seconds)', sjf_total_tt, fifo_total_tt]

    print(df)


    # import matplotlib.pyplot as plt, mpld3
    #
    # plt.plot([3, 1, 4, 1, 5], 'ks-', mec='w', mew=5, ms=20)
    # mpld3.show()
