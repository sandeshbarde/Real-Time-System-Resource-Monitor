# Real-Time System Resource Monitor

A high-performance, multithreaded desktop application for monitoring CPU, RAM, Disk, Network I/O, and Processes in real-time on Windows 11. Built as an academic Operating Systems (OS) mini project.

---

### Student Information
- **Name:** Sandesh Barde
- **PRN / ERP:** 25ET2021031
- **Year / Class:** Second Year (SE)
- **Branch:** Artificial Intelligence & Data Science (AIDS)
- **Course:** Operating System Mini Project

---

## Key Highlights & Architecture
- **Non-blocking Multithreaded Engine:** Dedicated background worker collects OS hardware telemetry via `psutil` and dispatches thread-safe snapshots to a lightweight Tkinter GUI.
- **Pure Tkinter Canvas Charts:** Real-time 60-second scrolling historical charts with zero bulky graphics dependencies (no Matplotlib/OpenGL crashes or bloat).
- **Process Management & Safety:** Search, sort, inspect PID/threads/command line, and terminate processes safely with self-termination protection and confirmation prompts.
- **Configurable Alerts & Cooldowns:** Threshold notifications for CPU, RAM, and Disk with rate-limited alert logging to prevent event flooding.
- **CSV Exporters:** Export process snapshots and time-series telemetry records directly to CSV.

---

## Directory Structure

```text
os/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Application launcher & entry point
│   ├── monitoring.py           # Hardware counters, throughput, & platform info
│   ├── process_manager.py      # Process enumeration, sorting, & safe termination
│   ├── alerts.py               # Threshold rules & alert cooldown manager
│   ├── exporter.py             # CSV export utilities
│   └── ui/
│       ├── __init__.py
│       ├── theme.py            # Dark navy palette & typography design tokens
│       ├── chart_widget.py     # Pure Tkinter Canvas time-series chart
│       ├── process_view.py     # Filterable, sortable process table view
│       ├── side_panel.py       # Hardware specs, thresholds & notification log
│       └── main_window.py      # Master window orchestrator & background thread
├── tests/
│   └── test_monitor.py         # 15 unit & integration tests (pytest)
├── docs/
│   ├── project_report.md       # Comprehensive academic project report
│   ├── test_plan.md            # Detailed test cases, execution results & matrix
│   ├── viva_questions.md       # Complete OS mini project viva & oral prep
│   ├── sample_processes.csv    # Real sample process snapshot export
│   └── sample_metrics_history.csv # Real sample telemetry export
├── requirements.txt            # Project dependencies
├── README.md                   # Setup guide and documentation
└── .gitignore                  # Git tracking rules
```

---

## Prerequisites
- **Operating System:** Windows 10 / Windows 11 (64-bit recommended)
- **Python:** Python 3.10 or higher (Tested on Python 3.13.14)

---

## Setup & Execution (Windows PowerShell)

### 1. Open PowerShell & Navigate to Project Directory
```powershell
cd "c:\Users\sande\OneDrive\Desktop\os"
```

### 2. (Optional) Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Run Automated Unit Tests
```powershell
pytest tests -v
```
*(All 15 test cases covering throughput formulas, counter wraps, thresholds, cooldowns, process filters, self-kill protection, and CSV exports should pass.)*

### 5. Launch the Desktop Application
```powershell
python src/main.py
```

---

## Practical Demonstration Checklist for Viva / Evaluation

1. **Dashboard Initialization:**
   - Verify that the four top metric cards (CPU, RAM, Disk, Network) initialize without crashing or blocking.
   - Verify that system specs (Host name, OS version, logical cores, total memory) display accurately in the right-side panel.
2. **Dynamic Canvas Charts:**
   - Observe the CPU Load (blue) and RAM Load (purple) charts smoothly updating every second with bounded 60-second historical data.
3. **Process Filtering & Sorting:**
   - Type a query in the "Filter Processes" box (e.g., `python`, `code`, or a specific PID) and see instant results.
   - Click table column headers ("CPU %", "RAM %", "PID", "Process Name") to sort ascending and descending.
4. **Detailed Process Inspection:**
   - Select any process and click **"View Details"** (or double click) to view memory RSS, thread counts, creation timestamp, and command line.
5. **Safe Process Termination:**
   - Select an expendable test process (e.g., open a `notepad.exe` window).
   - Click **"End Process"**. Notice the explicit confirmation dialog warning about unsaved data.
   - Confirm to terminate the process and verify its immediate removal from the table.
   - Try terminating the monitor itself or a protected system PID to witness the safety refusal dialog.
6. **Alert Thresholds:**
   - Set the CPU or RAM alert limit below current usage in the side panel and click **"Apply Settings"**.
   - Notice the immediate entry in the Notification & Alert Log.
7. **CSV Data Export:**
   - Click **"Export Processes (CSV)"** to save a snapshot of running processes.
   - Click **"Export Metrics History (CSV)"** to save time-series resource logs.
8. **Clean Shutdown:**
   - Close the application window and confirm that the background worker thread exits immediately without zombie processes or frozen console prompts.

---

## License & Academic Disclaimer
Developed solely for academic evaluation by **Sandesh Barde (25ET2021031)** for the **Operating System Mini Project**, AI & Data Science Department.
