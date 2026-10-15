# Real-Time System Resource Monitor
## Academic Mini Project Report

**Subject:** Operating System  
**Academic Year:** 2025 – 2026  

---

### Student Details
- **Student Name:** Sandesh Barde  
- **Year / Class:** Second Year (SE)  
- **Branch:** Artificial Intelligence & Data Science (AIDS)  
- **ERP / PRN:** 25ET2021031  

---

## Certificate of Authenticity

This is to certify that the mini project entitled **"Real-Time System Resource Monitor"** submitted by **Sandesh Barde (PRN: 25ET2021031)**, student of **Second Year (SE) Artificial Intelligence & Data Science**, is a bonafide work completed under the guidance of the faculty in partial fulfillment of the requirements for the subject **Operating System**.

\
\
\
\
__________________________________ &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; __________________________________  
**Project Guide / Faculty Mentor** &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; **Head of Department (AIDS)**  

\
\
Date: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_  
Place: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_  

---

## Declaration

I hereby declare that the project entitled **"Real-Time System Resource Monitor"** was designed and implemented by me under the supervision of my subject guide. The work presented herein is original and has not been submitted elsewhere for the award of any degree or diploma. Any intellectual material cited has been appropriately referenced.

\
\
\
__________________________________  
**Sandesh Barde**  
PRN: 25ET2021031  
SE - AI & Data Science  

---

## Acknowledgement

I express my deepest gratitude to our faculty mentors and the Department of Artificial Intelligence & Data Science for providing the resources, guidance, and encouraging environment necessary to successfully execute this Operating System mini project.

I am also thankful to my peers for their constructive feedback and discussions on operating system scheduling, memory management, and process synchronization principles that contributed to the design of this software.

---

## Abstract

Operating systems act as the primary intermediary between physical computing hardware and user applications. Understanding resource distribution—specifically Central Processing Unit (CPU) utilization, physical memory (RAM) allocation, disk filesystem occupancy, network input/output (I/O) throughput, and active user processes—is essential for software performance engineering and system administration.

This project presents the **Real-Time System Resource Monitor**, a robust desktop application engineered in Python 3.10+ utilizing Tkinter and `psutil`. Designed with a multithreaded architecture, the application decouples heavy OS metric acquisition from the user interface dispatch loop, ensuring sub-second response times without interface freezing. The software integrates bounded time-series vector graphing, interactive process filtering and sorting, safe process termination with hierarchical confirmation modals, threshold-based health alerts, and dual CSV export engines. All 15 automated test cases passed with 100% compliance.

**Keywords:** Operating System, Resource Monitoring, Multithreading, Process Management, CPU Scheduling, RAM Telemetry, Tkinter, psutil.

---

## Table of Contents
1. [Introduction and Problem Statement](#1-introduction-and-problem-statement)
2. [Aim, Objectives, and Scope](#2-aim-objectives-and-scope)
3. [Hardware and Software Requirements](#3-hardware-and-software-requirements)
4. [System Architecture and Module Descriptions](#4-system-architecture-and-module-descriptions)
5. [Algorithms and Mathematical Formulas](#5-algorithms-and-mathematical-formulas)
6. [Implementation Details](#6-implementation-details)
7. [Test Plan and Verification Results](#7-test-plan-and-verification-results)
8. [Demonstration and Visual Layout](#8-demonstration-and-visual-layout)
9. [Advantages and Limitations](#9-advantages-and-limitations)
10. [Future Scope](#10-future-scope)
11. [Conclusion and References](#11-conclusion-and-references)

---

## 1. Introduction and Problem Statement

Modern operating systems manage thousands of concurrent execution threads across multicore architectures. When hardware resources become bottlenecked—whether due to memory leaks, runaway compute loops, or background network I/O contention—system responsiveness degrades.

Standard built-in tools (such as Windows Task Manager) are comprehensive but complex, proprietary, and closed for programmatic analysis or academic inspection. Conversely, command-line inspection tools (`top`, `Get-Process`) do not provide accessible real-time time-series visualization or straightforward telemetry export for non-technical users.

**Problem Statement:**  
To engineer an open, lightweight, cross-platform, and multithreaded desktop resource monitoring application that captures OS performance metrics in real time, provides graphical visualization without heavy external graphing dependencies, allows safe process inspection, and exports time-series logs for performance analysis.

---

## 2. Aim, Objectives, and Scope

### Aim:
To develop a responsive real-time Operating System performance and process management monitor tailored for Windows 11.

### Objectives:
1. Capture real-time hardware telemetry (CPU percentage, RAM occupancy, storage capacity, and network throughput).
2. Render responsive 60-second historical trend graphs using lightweight native canvas vector rendering.
3. Provide an interactive process manager supporting live multi-parameter sorting (by CPU, RAM, PID, or name) and substring search.
4. Implement safe process termination safeguards (preventing monitor suicide or kernel process termination).
5. Support configurable health alert thresholds with cooldown mechanisms to prevent event logging storms.
6. Provide snapshot and time-series export to comma-separated values (CSV) format.

### Scope:
The monitor operates within Windows 11 user mode using safe kernel abstraction APIs (`psutil`). It handles access control boundaries gracefully without requiring continuous elevated administrator rights.

---

## 3. Hardware and Software Requirements

### Hardware Requirements:
- **Processor:** Dual-core x86_64 or ARM64 processor (Quad-core 2.0 GHz+ recommended)
- **Memory (RAM):** Minimum 2 GB (4 GB recommended)
- **Storage:** 50 MB available disk space
- **Display:** Minimum resolution of $1024 \times 768$ pixels

### Software Requirements:
- **Operating System:** Microsoft Windows 10 / 11 (64-bit)
- **Programming Language:** Python 3.10 to 3.13 (Tested on Python 3.13.14)
- **Core Libraries:**
  - `psutil` (v5.9.0+): Operating system and process abstraction
  - `tkinter` / `ttk`: Graphical desktop environment
  - `csv`, `threading`, `time`, `platform`: Python Standard Library
- **Development & Testing:** `pytest` (v7.0.0+)

---

## 4. System Architecture and Module Descriptions

The application employs a **Producer-Consumer Multithreaded Architecture**:

```
+-------------------------------------------------------------+
|                     Operating System                        |
|       (Windows Kernel, NDIS, Pagefile, Storage Drivers)      |
+-------------------------------------------------------------+
                               |
                        [psutil APIs]
                               |
                               v
+-------------------------------------------------------------+
|                  Background Worker Thread                   |
|                (MetricsCollectorThread)                     |
|  - Queries CPU time deltas non-blockingly                   |
|  - Computes Network Throughput: delta_bytes / delta_time    |
|  - Iterates Process Control Blocks (safe error catching)    |
|  - Checks Threshold Rules & Updates Alert Queue             |
+-------------------------------------------------------------+
                               |
                     [threading.Lock Protected]
                               |
                               v
+-------------------------------------------------------------+
|                      Main GUI Thread                        |
|                     (Tkinter Event Loop)                    |
|  - Reads thread-safe snapshot every 500ms                   |
|  - Updates Metric Cards (CPU, RAM, Disk, Net)               |
|  - Draws glowing time-series lines on tk.Canvas             |
|  - Filters & populates Process Table (ttk.Treeview)         |
|  - Renders System Hardware specs & alerts in Side Panel     |
|  - Dispatches CSV Exporter on user action                   |
+-------------------------------------------------------------+
```

### Module Breakdown:
1. **`src/main.py`**: Application bootstrap, environment checks, and window lifecycle management.
2. **`src/monitoring.py`**: Hardware metric acquisition, network throughput computation, rate-of-change smoothing, and static hardware identification.
3. **`src/process_manager.py`**: Process iteration, filtering, sorting, extended parameter inspection, and protected process termination.
4. **`src/alerts.py`**: Validation of resource thresholds, breach detection, and cooldown management.
5. **`src/exporter.py`**: Writing process snapshots and chronological telemetry buffers to structured CSV files.
6. **`src/ui/`**: Complete user interface containing `MainWindow`, `MiniChart`, `ProcessView`, `SidePanel`, and `theme.py`.

---

## 5. Algorithms and Mathematical Formulas

### 1. CPU Utilization Over Interval $\Delta t$:
The OS kernel accumulates active cycles ($t_{\text{user}} + t_{\text{system}}$) and idle cycles ($t_{\text{idle}}$). CPU percentage is defined as:
$$\text{CPU \%} = \left( 1 - \frac{t_{\text{idle}}(t_2) - t_{\text{idle}}(t_1)}{(t_{\text{active}}(t_2) + t_{\text{idle}}(t_2)) - (t_{\text{active}}(t_1) + t_{\text{idle}}(t_1))} \right) \times 100$$
Using `psutil.cpu_percent(interval=None)` calculates this ratio non-blockingly between successive sampling ticks.

### 2. Network Throughput Rate:
Network cards accumulate byte transfer counters. Throughput is the derivative over time:
$$\text{Throughput}_{\text{Upload}} = \frac{\max(0, B_{\text{sent}}(t_2) - B_{\text{sent}}(t_1))}{t_2 - t_1}$$
$$\text{Throughput}_{\text{Download}} = \frac{\max(0, B_{\text{recv}}(t_2) - B_{\text{recv}}(t_1))}{t_2 - t_1}$$
The $\max(0, \cdot)$ operator guards against counter reset wraps during adapter re-initialization.

### 3. Canvas Vector Graph Coordinate Transformation:
Given viewport dimensions $(W, H)$ with padding $(P_L, P_R, P_T, P_B)$ and value $V \in [0, 100]$:
$$X_i = P_L + i \cdot \left(\frac{W - P_L - P_R}{N - 1}\right)$$
$$Y_i = P_T + (H - P_T - P_B) \cdot \left(1.0 - \frac{V_i}{100.0}\right)$$

---

## 6. Implementation Details

### Concurrency and Thread Safety:
Tkinter is not thread-safe. Modifying GUI widgets directly from secondary threads causes race conditions and memory corruption. In this implementation:
- The worker thread updates shared data structures inside a mutex:
  ```python
  with self._data_lock:
      self.latest_metrics = metrics
      self.metrics_history.append(metrics)
      self.current_processes = processes
  ```
- The UI thread reads this snapshot inside `self.after(500, self._gui_refresh_cycle)` on the main event loop, achieving thread safety.

### Error Handling for Protected Processes:
When accessing restricted system processes (e.g., `Secure System`, `csrss.exe`), Windows blocks access. Our code handles this gracefully:
```python
except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
    continue
```

---

## 7. Test Plan and Verification Results

The test suite was executed using `pytest 9.1.1` on Python `3.13.14`. All 15 tests passed:

- `test_calculate_throughput_normal` — **PASSED**
- `test_calculate_throughput_zero_or_negative_elapsed` — **PASSED**
- `test_calculate_throughput_counter_wrap` — **PASSED**
- `test_format_bytes_human` — **PASSED**
- `test_format_bytes_speed` — **PASSED**
- `test_system_monitor_collect` — **PASSED**
- `test_alert_rule_validation` — **PASSED**
- `test_alert_manager_triggering` — **PASSED**
- `test_alert_cooldown` — **PASSED**
- `test_process_enumeration` — **PASSED**
- `test_process_filtering_and_sorting` — **PASSED**
- `test_self_termination_safeguard` — **PASSED**
- `test_system_process_termination_safeguard` — **PASSED**
- `test_export_processes_csv` — **PASSED**
- `test_export_metrics_csv` — **PASSED**

---

## 8. Demonstration and Visual Layout

### Dashboard Layout Scheme:
```text
+----------------------------------------------------------------------------------+
| REAL-TIME SYSTEM RESOURCE MONITOR  [Export Processes CSV] [Export Metrics CSV]  |
+----------------------------------------------------------------------------------+
| [ CPU UTILIZATION ]  [ MEMORY (RAM) ]   [ PRIMARY DISK ]   [ NETWORK I/O ]       |
|      18.4%                62.1%              48.2%             142.5 KB/s        |
|  16 Cores | 3.2GHz   10.2 / 16.0 GB      240 / 500 GB      ▲ 24KB/s | ▼ 118KB/s  |
+----------------------------------------------------------+-----------------------+
|  [ CPU Load Chart - 60s ]   [ RAM Load Chart - 60s ]     | SYSTEM OVERVIEW       |
|  (Smooth Vector Graph)      (Smooth Vector Graph)        | Host: Sandesh-PC      |
|                                                          | OS: Windows 11 AMD64  |
+----------------------------------------------------------+ Cores: 16 Logical     |
| Filter: [chrome___________] [Clear]     Showing: 12 / 331| RAM: 16.0 GB          |
+-----+-------------------+-------+-------+----------+-----+ Uptime: 4h 12m 30s    |
| PID | Process Name      | CPU % | RAM % | Memory   |Thrd |-----------------------|
+-----+-------------------+-------+-------+----------+-----+ ALERTS & THRESHOLDS   |
| 4512| chrome.exe        | 14.2% |  4.5% | 720.4 MB | 32  | Refresh Rate: 1.0s    |
| 8920| python.exe        |  3.1% |  1.2% | 192.0 MB |  8  | CPU Limit: 85%        |
| 1204| code.exe          |  1.8% |  3.1% | 496.2 MB | 24  | RAM Limit: 90%        |
| ... | ...               | ...   | ...   | ...      | ... | Disk Limit: 90%       |
+-----+-------------------+-------+-------+----------+-----+ [ Apply Settings ]     |
| [View Details]                             [End Process] |                       |
+----------------------------------------------------------+ NOTIFICATION LOG      |
| Status: Monitoring active. Last Sample: 13:30:15         | [INFO] Monitor started|
+----------------------------------------------------------+-----------------------+
```

*(Note: Replace textual mockups with genuine window screen captures during project submission).*

---

## 9. Advantages and Limitations

### Advantages:
1. **Zero Heavy Dependencies:** Eliminates bulky C++ or OpenGL packages; runs cleanly with standard Tkinter.
2. **Decoupled Responsiveness:** Multithreaded architecture maintains a responsive UI during heavy process scans.
3. **Safety Protection:** Safeguards against self-termination or kernel process termination.
4. **Transparent Codebase:** Clear, modular design well-suited for academic review and viva examination.

### Limitations:
1. **User Mode Scope:** Gathers telemetry through OS APIs without a custom kernel driver; hardware register counters are abstracted by Windows.
2. **Sampling Granularity:** Default 1-second sampling window smooths out microsecond spikes.
3. **Restricted Process Details:** Command lines for elevated system processes are protected by Windows security policies unless run as Administrator.

---

## 10. Future Scope
- **GPU Telemetry:** Integrate DirectX/WMI performance counters to track dedicated GPU compute utilization and VRAM occupancy.
- **Statistical Anomaly Detection:** Implement offline rolling Z-score analysis to identify runaway memory leaks automatically.
- **Per-Process I/O Metrics:** Track disk read/write bandwidth consumption per individual PID.

---

## 11. Conclusion and References

The **Real-Time System Resource Monitor** successfully fulfills all objectives of an academic Operating System mini project. It provides an efficient, transparent, and aesthetically polished desktop tool that illustrates fundamental OS concepts—from CPU scheduling and virtual memory allocation to multithreaded synchronization and safe process control.

### References:
1. Silberschatz, A., Galvin, P. B., & Gagne, G. *Operating System Concepts* (10th ed.). John Wiley & Sons, 2018.
2. Tanenbaum, A. S., & Bos, H. *Modern Operating Systems* (4th ed.). Pearson, 2015.
3. Giampaolo Rodola et al. *psutil: Cross-platform lib for process and system monitoring in Python*. Documentation (2025).
4. Python Software Foundation. *Tkinter — Python interface to Tcl/Tk*. Official Documentation.
5. Microsoft Corporation. *Windows Architecture and System Internals*, Microsoft Learn.
