"""
CSV and data export module for Real-Time System Resource Monitor.
Exports process snapshots and historical metric buffers to CSV format.
"""

from __future__ import annotations
import csv
import os
import time
from typing import List, Sequence, Union
from .process_manager import ProcessInfo
from .monitoring import SystemMetrics


def export_processes_to_csv(
    processes: Sequence[ProcessInfo],
    output_filepath: str,
) -> str:
    """
    Export current snapshot of processes to a CSV file.
    Returns the absolute path of the generated file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
    
    headers = [
        "PID",
        "Process Name",
        "CPU (%)",
        "Memory (%)",
        "Memory RSS (Bytes)",
        "Memory (Human)",
        "Status",
        "Threads",
        "Created Time",
        "User",
    ]

    with open(output_filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for p in processes:
            writer.writerow([
                p.pid,
                p.name,
                f"{p.cpu_percent:.2f}",
                f"{p.memory_percent:.2f}",
                p.memory_rss_bytes,
                p.memory_human,
                p.status,
                p.num_threads,
                p.created_formatted,
                p.username or "N/A",
            ])

    return os.path.abspath(output_filepath)


def export_metrics_history_to_csv(
    metrics_history: Sequence[SystemMetrics],
    output_filepath: str,
) -> str:
    """
    Export collected time-series system metrics to a CSV file.
    Returns the absolute path of the generated file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)

    headers = [
        "Timestamp (Epoch)",
        "Local Time",
        "CPU Utilization (%)",
        "RAM Usage (%)",
        "RAM Used (Bytes)",
        "RAM Total (Bytes)",
        "Disk Occupancy (%)",
        "Disk Used (Bytes)",
        "Disk Total (Bytes)",
        "Net Upload (Bytes/sec)",
        "Net Download (Bytes/sec)",
        "Net Upload (Human)",
        "Net Download (Human)",
    ]

    with open(output_filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for m in metrics_history:
            local_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(m.timestamp))
            writer.writerow([
                f"{m.timestamp:.2f}",
                local_time_str,
                f"{m.cpu_percent:.2f}",
                f"{m.ram_percent:.2f}",
                m.ram_used_bytes,
                m.ram_total_bytes,
                f"{m.disk_percent:.2f}",
                m.disk_used_bytes,
                m.disk_total_bytes,
                f"{m.net_throughput.bytes_sent_per_sec:.2f}",
                f"{m.net_throughput.bytes_recv_per_sec:.2f}",
                m.net_throughput.human_sent,
                m.net_throughput.human_recv,
            ])

    return os.path.abspath(output_filepath)
