"""
Unit and integration tests for monitoring, alerts, process management, and exporter.
"""

import os
import tempfile
import pytest

from src.monitoring import (
    calculate_throughput,
    format_bytes,
    format_bytes_speed,
    NetworkThroughput,
    SystemMetrics,
    SystemMonitor,
)
from src.alerts import AlertRule, AlertEvent, AlertManager
from src.process_manager import ProcessInfo, ProcessManager
from src.exporter import export_processes_to_csv, export_metrics_history_to_csv


# -----------------------------------------------------------------------------
# 1. Monitoring & Throughput Tests
# -----------------------------------------------------------------------------

def test_calculate_throughput_normal():
    # 100,000 bytes transferred over 2.0 seconds -> 50,000 B/s
    tp = calculate_throughput(
        prev_bytes_sent=1000,
        prev_bytes_recv=2000,
        curr_bytes_sent=101000,
        curr_bytes_recv=202000,
        elapsed_seconds=2.0,
    )
    assert tp.bytes_sent_per_sec == 50000.0
    assert tp.bytes_recv_per_sec == 100000.0
    assert tp.kbps_sent == (50000.0 * 8) / 1000.0


def test_calculate_throughput_zero_or_negative_elapsed():
    tp = calculate_throughput(100, 100, 200, 200, elapsed_seconds=0.0)
    assert tp.bytes_sent_per_sec == 0.0
    assert tp.bytes_recv_per_sec == 0.0

    tp_neg = calculate_throughput(100, 100, 200, 200, elapsed_seconds=-1.5)
    assert tp_neg.bytes_sent_per_sec == 0.0
    assert tp_neg.bytes_recv_per_sec == 0.0


def test_calculate_throughput_counter_wrap():
    # In case of interface reset where curr < prev
    tp = calculate_throughput(
        prev_bytes_sent=100000,
        prev_bytes_recv=100000,
        curr_bytes_sent=5000,
        curr_bytes_recv=8000,
        elapsed_seconds=1.0,
    )
    assert tp.bytes_sent_per_sec == 0.0
    assert tp.bytes_recv_per_sec == 0.0


def test_format_bytes_human():
    assert format_bytes(500) == "500 B"
    assert format_bytes(1024 * 1.5) == "1.5 KB"
    assert format_bytes(1024 * 1024 * 50) == "50.0 MB"
    assert format_bytes(1024 * 1024 * 1024 * 4) == "4.00 GB"


def test_format_bytes_speed():
    assert format_bytes_speed(500) == "500.0 B/s"
    assert format_bytes_speed(2048) == "2.0 KB/s"
    assert format_bytes_speed(5 * 1024 * 1024) == "5.00 MB/s"


def test_system_monitor_collect():
    monitor = SystemMonitor()
    metrics = monitor.collect_metrics()
    assert isinstance(metrics, SystemMetrics)
    assert 0.0 <= metrics.cpu_percent <= 100.0
    assert 0.0 <= metrics.ram_percent <= 100.0
    assert metrics.ram_total_bytes > 0
    assert metrics.disk_total_bytes > 0

    info = monitor.get_static_system_info()
    assert "hostname" in info
    assert "os" in info
    assert info["logical_cores"] >= 1


# -----------------------------------------------------------------------------
# 2. Alert & Threshold Tests
# -----------------------------------------------------------------------------

def test_alert_rule_validation():
    # Valid rule
    rule = AlertRule(cpu_threshold_pct=80.0, ram_threshold_pct=85.0, disk_threshold_pct=90.0)
    rule.validate()

    # Invalid CPU
    with pytest.raises(ValueError):
        invalid_rule = AlertRule(cpu_threshold_pct=150.0)
        invalid_rule.validate()

    with pytest.raises(ValueError):
        invalid_rule = AlertRule(ram_threshold_pct=-5.0)
        invalid_rule.validate()


def test_alert_manager_triggering():
    manager = AlertManager(AlertRule(cpu_threshold_pct=75.0, ram_threshold_pct=80.0, disk_threshold_pct=90.0))
    manager.cooldown_seconds = 0.0  # zero cooldown for direct testing

    # Under threshold -> No alert
    events = manager.check_metrics(cpu_pct=50.0, ram_pct=60.0, disk_pct=70.0, now=1000.0)
    assert len(events) == 0

    # CPU breach
    events = manager.check_metrics(cpu_pct=85.0, ram_pct=60.0, disk_pct=70.0, now=1001.0)
    assert len(events) == 1
    assert events[0].resource == "CPU"
    assert events[0].level == "WARNING"

    # RAM breach
    events = manager.check_metrics(cpu_pct=50.0, ram_pct=95.0, disk_pct=70.0, now=1002.0)
    assert len(events) == 1
    assert events[0].resource == "RAM"
    assert events[0].level == "CRITICAL"


def test_alert_cooldown():
    manager = AlertManager(AlertRule(cpu_threshold_pct=70.0, ram_threshold_pct=80.0, disk_threshold_pct=90.0))
    manager.cooldown_seconds = 5.0

    # First breach fires
    ev1 = manager.check_metrics(cpu_pct=85.0, ram_pct=50.0, disk_pct=50.0, now=1000.0)
    assert len(ev1) == 1

    # Second breach within 2 seconds suppressed by cooldown
    ev2 = manager.check_metrics(cpu_pct=85.0, ram_pct=50.0, disk_pct=50.0, now=1002.0)
    assert len(ev2) == 0

    # Breach after cooldown expires fires again
    ev3 = manager.check_metrics(cpu_pct=85.0, ram_pct=50.0, disk_pct=50.0, now=1006.0)
    assert len(ev3) == 1


# -----------------------------------------------------------------------------
# 3. Process Manager & Filter Tests
# -----------------------------------------------------------------------------

def test_process_enumeration():
    pm = ProcessManager()
    procs = pm.get_process_list()
    assert isinstance(procs, list)
    assert len(procs) > 0  # Operating system always has running processes

    # Check that current process is in list
    pids = [p.pid for p in procs]
    assert pm.current_pid in pids


def test_process_filtering_and_sorting():
    pm = ProcessManager()
    sample_procs = [
        ProcessInfo(pid=100, name="python.exe", cpu_percent=12.5, memory_percent=2.0, memory_rss_bytes=1024*1024, status="running", num_threads=4, create_time=100.0),
        ProcessInfo(pid=200, name="notepad.exe", cpu_percent=0.5, memory_percent=1.0, memory_rss_bytes=512*1024, status="running", num_threads=2, create_time=200.0),
        ProcessInfo(pid=300, name="chrome.exe", cpu_percent=25.0, memory_percent=8.5, memory_rss_bytes=10*1024*1024, status="running", num_threads=16, create_time=50.0),
    ]

    # Filter by name
    res = pm.filter_and_sort_processes(sample_procs, search_query="note")
    assert len(res) == 1
    assert res[0].pid == 200

    # Filter by PID
    res_pid = pm.filter_and_sort_processes(sample_procs, search_query="300")
    assert len(res_pid) == 1
    assert res_pid[0].name == "chrome.exe"

    # Sort by CPU descending
    res_sort_cpu = pm.filter_and_sort_processes(sample_procs, sort_by="cpu_percent", descending=True)
    assert [p.pid for p in res_sort_cpu] == [300, 100, 200]

    # Sort by Memory descending
    res_sort_mem = pm.filter_and_sort_processes(sample_procs, sort_by="memory_percent", descending=True)
    assert [p.pid for p in res_sort_mem] == [300, 100, 200]


def test_self_termination_safeguard():
    pm = ProcessManager()
    success, msg = pm.terminate_process(pm.current_pid)
    assert success is False
    assert "Cannot terminate the System Resource Monitor itself" in msg


def test_system_process_termination_safeguard():
    pm = ProcessManager()
    success, msg = pm.terminate_process(4)  # Windows System PID
    assert success is False
    assert "Cannot terminate protected Windows Kernel/System process" in msg


# -----------------------------------------------------------------------------
# 4. Exporter Tests
# -----------------------------------------------------------------------------

def test_export_processes_csv():
    sample_procs = [
        ProcessInfo(pid=101, name="test1.exe", cpu_percent=5.0, memory_percent=1.5, memory_rss_bytes=1024*1024, status="running", num_threads=2, create_time=100.0, username="TESTUSER"),
        ProcessInfo(pid=102, name="test2.exe", cpu_percent=10.0, memory_percent=2.5, memory_rss_bytes=2*1024*1024, status="running", num_threads=4, create_time=150.0, username="TESTUSER"),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_file = os.path.join(tmpdir, "test_processes.csv")
        out_path = export_processes_to_csv(sample_procs, csv_file)
        assert os.path.exists(out_path)

        with open(out_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 3  # Header + 2 data rows
            assert "PID,Process Name" in lines[0]
            assert "101,test1.exe" in lines[1]
            assert "102,test2.exe" in lines[2]


def test_export_metrics_csv():
    sample_metrics = [
        SystemMetrics(
            timestamp=1700000000.0,
            cpu_percent=35.5,
            ram_percent=60.2,
            ram_used_bytes=8*1024*1024*1024,
            ram_total_bytes=16*1024*1024*1024,
            disk_percent=45.0,
            disk_used_bytes=200*1024*1024*1024,
            disk_total_bytes=500*1024*1024*1024,
            net_throughput=NetworkThroughput(bytes_sent_per_sec=1024.0, bytes_recv_per_sec=2048.0),
            cpu_cores_logical=8,
        )
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_file = os.path.join(tmpdir, "test_metrics.csv")
        out_path = export_metrics_history_to_csv(sample_metrics, csv_file)
        assert os.path.exists(out_path)

        with open(out_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 2  # Header + 1 data row
            assert "CPU Utilization (%)" in lines[0]
            assert "35.50" in lines[1]
