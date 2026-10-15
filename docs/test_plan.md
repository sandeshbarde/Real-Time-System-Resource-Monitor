# Software Test Plan & Execution Report
## Real-Time System Resource Monitor

- **Student:** Sandesh Barde (25ET2021031)
- **Course:** Operating System Mini Project
- **Class / Branch:** SE - Artificial Intelligence & Data Science (AIDS)
- **Test Framework:** `pytest 9.1.1` on Python `3.13.14` (Windows 11 AMD64)

---

## 1. Scope & Objective
The objective of this test plan is to rigorously validate the computational accuracy, thread safety, access control safeguards, error resiliency, and export integrity of the Real-Time System Resource Monitor.

---

## 2. Test Cases Specification

| Test ID | Module | Function Tested | Description & Inputs | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | `monitoring` | `calculate_throughput` | Bytes transmitted = 100,000, Elapsed = 2.0s | Rate = 50,000.0 B/s, accurate Kbps conversion | 50000.0 B/s | **PASSED** |
| **TC-02** | `monitoring` | `calculate_throughput` | Zero or negative elapsed time (`elapsed <= 0.0`) | Returns 0.0 B/s gracefully without DivisionByZero | 0.0 B/s returned | **PASSED** |
| **TC-03** | `monitoring` | `calculate_throughput` | Network adapter reset / counter wrap (`curr < prev`) | Returns 0.0 B/s without negative throughput | 0.0 B/s returned | **PASSED** |
| **TC-04** | `monitoring` | `format_bytes` | Bytes inputs: 500 B, 1.5 KB, 50 MB, 4 GB | Accurate human-readable decimal strings | Exact string format match | **PASSED** |
| **TC-05** | `monitoring` | `format_bytes_speed` | Rate inputs: 500 B/s, 2048 B/s, 5 MB/s | Accurate rate formatting (B/s, KB/s, MB/s) | Exact rate format match | **PASSED** |
| **TC-06** | `monitoring` | `SystemMonitor.collect_metrics` | Live OS query via `psutil` | Valid percentages [0-100%], non-zero RAM/Disk | Genuine metrics collected | **PASSED** |
| **TC-07** | `alerts` | `AlertRule.validate` | Threshold limits out of bounds (<1.0% or >99.0%) | Raises `ValueError` with descriptive message | Raises `ValueError` as expected | **PASSED** |
| **TC-08** | `alerts` | `AlertManager.check_metrics` | Metrics crossing threshold values | Triggers `WARNING` or `CRITICAL` alert events | Alert event created with correct metadata | **PASSED** |
| **TC-09** | `alerts` | `AlertManager` cooldown | Repeated breaches within cooldown interval (5s) | Suppresses duplicates until interval expires | Second breach suppressed, third allowed | **PASSED** |
| **TC-10** | `process_manager` | `get_process_list` | Live process iteration | List of `ProcessInfo` objects, contains current PID | Successful iteration over live OS processes | **PASSED** |
| **TC-11** | `process_manager` | `filter_and_sort_processes` | Search by query (`notepad`), sort by CPU/RAM | Case-insensitive filter and verified sort order | Correctly filtered and ordered list | **PASSED** |
| **TC-12** | `process_manager` | `terminate_process` | Target PID = `os.getpid()` (Self PID) | Refuses termination with safety message | Returns `(False, "Cannot terminate...")` | **PASSED** |
| **TC-13** | `process_manager` | `terminate_process` | Target PID = 4 (Windows System Process) | Refuses termination of kernel processes | Returns `(False, "Cannot terminate protected...")` | **PASSED** |
| **TC-14** | `exporter` | `export_processes_to_csv` | Export `ProcessInfo` sequence to temp CSV | File created, valid headers, matching row count | Generated valid CSV file | **PASSED** |
| **TC-15** | `exporter` | `export_metrics_history_to_csv`| Export `SystemMetrics` queue to temp CSV | File created, epoch & formatted timestamps | Generated valid CSV file | **PASSED** |

---

## 3. Actual Execution Log
Executed command: `python -m pytest tests -v` in project root directory:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- C:\...\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\sande\OneDrive\Desktop\os
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False
collected 15 items

tests/test_monitor.py::test_calculate_throughput_normal PASSED           [  6%]
tests/test_monitor.py::test_calculate_throughput_zero_or_negative_elapsed PASSED [ 13%]
tests/test_monitor.py::test_calculate_throughput_counter_wrap PASSED     [ 20%]
tests/test_monitor.py::test_format_bytes_human PASSED                    [ 26%]
tests/test_monitor.py::test_format_bytes_speed PASSED                    [ 33%]
tests/test_monitor.py::test_system_monitor_collect PASSED                [ 40%]
tests/test_monitor.py::test_alert_rule_validation PASSED                 [ 46%]
tests/test_monitor.py::test_alert_manager_triggering PASSED              [ 53%]
tests/test_monitor.py::test_alert_cooldown PASSED                        [ 60%]
tests/test_monitor.py::test_process_enumeration PASSED                   [ 66%]
tests/test_monitor.py::test_process_filtering_and_sorting PASSED         [ 73%]
tests/test_monitor.py::test_self_termination_safeguard PASSED            [ 80%]
tests/test_monitor.py::test_system_process_termination_safeguard PASSED  [ 86%]
tests/test_monitor.py::test_export_processes_csv PASSED                  [ 93%]
tests/test_monitor.py::test_export_metrics_csv PASSED                    [100%]

============================= 15 passed in 9.31s ==============================
```

---

## 4. Manual GUI & Thread Concurrency Verification Matrix

| Area | Manual Checkpoint | Verification Method | Outcome |
| :--- | :--- | :--- | :--- |
| **Concurrency** | Worker Thread vs Tkinter Loop | Inspect thread safety during heavy process table sorting | GUI remains 100% responsive, no freezing |
| **Resilience** | Access Denied Processes | Double click on system PID (e.g. `csrss.exe`) | Displays `[Protected / Access Denied]` without crashing |
| **Process Death**| Target Terminated externally | Terminate a process from external task manager while selected | Application reports graceful disappearance on next tick |
| **Clean Exit** | Window Close Event | Monitor thread state upon window close | Worker loop flags `running=False`, thread terminates immediately |
