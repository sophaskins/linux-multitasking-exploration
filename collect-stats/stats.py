import psutil
import csv
import time
import pandas as pd
import argparse
import collections

BINARY_BASE = "fake-process"

def get_processes():
    """gets psutil processes for each of the fake-process1,
    fake-process2, fake-process3, etc"""
    processes = []
    for p in psutil.process_iter(attrs=["name"]):
        if p.info["name"].startswith(BINARY_BASE):
            processes.append(p)
    return processes

def write_stats(processes, duration, writer):
    """the main loop of taking stats: gets scheduler
    stats for each process, sleeps for `duration`, then
    grabs them again and writes the delta for each stat to writer"""

    # a future optimization could be saving the `after` for use as
    # the next `before` sample
    before = take_stats_sample(processes)
    time.sleep(duration)
    after = take_stats_sample(processes)
    timestamp = time.time()

    for process, process_stats in after.items():
        stats = {
            "process": process,
            "timestamp": timestamp,
        }
        for stat, value in process_stats.items():
            stats[stat] = value - before[process][stat]

        writer.writerow(stats)


# These are the stats from /proc/$PID/sched that I _think_ are
# monotonically increasing counters.
ADDITIVE_STATS = [
    "se.vruntime",
    "se.sum_exec_runtime",
    "se.nr_migrations",
    "nr_switches",
    "nr_voluntary_switches",
    "nr_involuntary_switches",
    "se.avg.load_sum",
    "se.avg.util_sum",
    "numa_pages_migrated",
]

def take_stats_sample(processes):
    """scrapes stats from /proc/$PID/sched at a point in time. It sums
    the stats for each of the processes' threads"""
    stats = {}
    for process in processes:
        process_stats = collections.defaultdict(int)
        for child in process.threads():
            with open("/proc/{}/task/{}/sched".format(process.pid, child.id), "r") as f:
                thread_stats = parse_sched(f)
                for stat, value in thread_stats.items():
                    if stat in ADDITIVE_STATS:
                        process_stats[stat] += value

        stats[process.info["name"]] = process_stats

    return stats

def parse_sched(sched_file):
    """does the actual parsing of `sched` files"""
    stats = {}
    has_hit_numa_faults = False
    for i, line in enumerate(sched_file):
        if i < 3:
            continue
        if has_hit_numa_faults:
            continue

        stat, _, str_value = line.split()
        value = float(str_value)
        if stat == "total_numa_faults":
            has_hit_numa_faults = True

        stats[stat] = value

    return stats

def do_data_collection(processes, interval, output_filename):
    with open(output_filename, 'w') as csvfile:
        fieldnames = ADDITIVE_STATS + ["process", "timestamp"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        while True:
            write_stats(processes, interval, writer)

processes = get_processes()

parser = argparse.ArgumentParser(description="collect stats from /proc")
parser.add_argument("--output", type=str)
parser.add_argument("--interval", type=int)

args = parser.parse_args()
do_data_collection(processes, args.interval, args.output)
