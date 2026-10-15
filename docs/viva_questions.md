# Operating Systems Mini Project: Viva & Oral Defense Preparation Guide
## Real-Time System Resource Monitor

- **Student:** Sandesh Barde (25ET2021031)
- **Year / Branch:** SE - AI & Data Science (AIDS)
- **Subject:** Operating System (OS)

This guide provides deep answers to likely examiner and professor viva questions covering OS theory, systems programming, multithreading, concurrency, and security.

---

### Q1. What is the core objective of your project?
**Answer:**
The objective is to provide a non-intrusive, real-time operating system resource monitoring dashboard capable of observing low-level CPU utilization, physical RAM allocation, filesystem occupancy, network throughput, and active user processes on Windows 11. It provides process inspection and safe process management while demonstrating OS concepts such as Process Control Blocks (PCBs), process states, context switches, system metrics telemetry, multithreaded GUI concurrency, and access control.

---

### Q2. How is CPU utilization calculated by the OS and by your application?
**Answer:**
The OS kernel tracks CPU time across states: User Mode, Kernel Mode (System), Idle, and I/O Wait (or DPC/Interrupts on Windows).
CPU utilization is not an instantaneous scalar; it represents the proportion of non-idle CPU cycles spent over a finite time window $\Delta t$:
$$\text{CPU \%} = \frac{\Delta t_{\text{active}}}{\Delta t_{\text{total}}} \times 100 = \left(1 - \frac{\Delta t_{\text{idle}}}{\Delta t_{\text{total}}}\right) \times 100$$
In our application, we utilize `psutil.cpu_percent(interval=None)`. Calling it with `interval=None` compares the hardware timer counter difference between two periodic calls non-blockingly, avoiding thread stalls.

---

### Q3. How do you calculate Network Upload and Download throughput?
**Answer:**
Network cards and OS network stacks (NDIS on Windows) do not output a continuous "speed" value; they maintain cumulative packet and byte counters (`bytes_sent` and `bytes_recv`) in network interface structures.
To derive throughput:
1. Sample cumulative counters $C_1$ at time $t_1$.
2. Sample cumulative counters $C_2$ at time $t_2$.
3. Compute throughput:
   $$\text{Throughput (Bytes/sec)} = \frac{C_2 - C_1}{t_2 - t_1}$$
Our implementation also guards against counter wraps (e.g., adapter resets) where $C_2 < C_1$, returning zero rather than negative or erroneous values.

---

### Q4. What is the difference between Virtual Memory and Resident Set Size (RSS)?
**Answer:**
- **Virtual Memory Size (VMS):** Total address space assigned to a process by the OS memory manager, including memory mapped files, shared libraries, and pages currently swapped out to the Windows paging file (`pagefile.sys`).
- **Resident Set Size (RSS) / Working Set:** The actual subset of a process's virtual memory pages currently residing in physical RAM.
Our monitor highlights physical RAM usage and RSS for accurate diagnosis of physical memory pressure.

---

### Q5. How does your application prevent the GUI from freezing during process scans?
**Answer:**
Tkinter is single-threaded and executes an event dispatch loop (`mainloop()`). If intensive OS polling (such as iterating over 300+ processes or disk I/O) occurred directly on the GUI thread, the window would freeze, drop user keystrokes, and trigger "Application Not Responding" (ANR).
We solved this by establishing a **Producer-Consumer multithreaded architecture**:
- A dedicated daemon worker thread (`MetricsCollectorThread`) polls OS metrics periodically.
- Snapshots are written to shared data buffers protected by a mutual exclusion lock (`threading.Lock`).
- The GUI thread executes a lightweight timer callback (`root.after()`) every 500ms to read the thread-safe snapshot and repaint the UI.

---

### Q6. Why did you choose pure Tkinter Canvas for charts instead of Matplotlib?
**Answer:**
While Matplotlib is widely used for static plotting, embedding heavy `FigureCanvasTkAgg` in a real-time 1-second refresh cycle introduces severe memory overhead, CPU consumption (due to repetitive Agg software rendering), and platform instability on Python 3.13.
Our custom `MiniChart` widget draws vector polylines directly on a native `tk.Canvas` with double-buffered hardware drawing. It supports smooth 60-second scrolling history with zero external C-dependencies and minimal memory footprint.

---

### Q7. How do you handle processes with elevated or kernel security permissions?
**Answer:**
On modern OSs with User Account Control (UAC) and discretionary access control lists (DACLs), standard user-level applications cannot inspect the memory or terminate processes belonging to `SYSTEM` or other privileged users (e.g., `csrss.exe`, `lsass.exe`, `services.exe`).
Attempting to inspect protected processes raises `psutil.AccessDenied`.
Our `ProcessManager` intercepts `psutil.AccessDenied`, `psutil.NoSuchProcess`, and `psutil.ZombieProcess`, returning safe placeholders like `[Protected / Access Denied]` without crashing the monitor.

---

### Q8. What safeguards prevent accidental system harm or crashes?
**Answer:**
1. **Self-Termination Prevention:** Checks target PID against `os.getpid()`. If the user attempts to terminate the monitor, the action is blocked.
2. **System / Idle Process Protection:** PID 0 (System Idle) and PID 4 (System Kernel) are hard-coded against termination.
3. **Explicit Confirmation Modal:** Users are prompted with process name, PID, and an unsaved data warning before any termination signal is sent.
4. **Graceful Signal Escalation:** The manager first invokes `proc.terminate()` (graceful close request) and waits up to 1.5 seconds before falling back to `proc.kill()` (forced termination).

---

### Q9. How do your alert thresholds and cooldowns work?
**Answer:**
The `AlertManager` validates that thresholds remain between 1.0% and 99.0%. When a metric crosses the threshold, an `AlertEvent` is generated. To prevent alert spamming (which would flood the event log every 1 second), a configurable cooldown (e.g., 5 seconds per resource) suppresses duplicate alerts until the resource either stabilizes or remains in prolonged breach.

---

### Q10. What are the key limitations of your system?
**Answer:**
1. **User Mode Scope:** Operates in user space without a custom kernel driver; metrics reflect OS abstraction layers rather than direct raw hardware registers.
2. **Sampling Granularity:** Sampling at 1-second intervals captures average utilization over that window; brief micro-bursts shorter than the sampling window may be smoothed out.
3. **Elevated Process Visibility:** Command line and executable paths for elevated administrative processes cannot be retrieved unless the monitor is run as Administrator.
