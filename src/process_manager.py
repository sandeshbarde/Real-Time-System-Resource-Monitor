"""
Process management module for Real-Time System Resource Monitor.
Enumerates processes safely, formats metadata, and provides safe termination
with access control checks and safeguards against self-termination.
"""

from __future__ import annotations
import os
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple
import psutil

from .monitoring import format_bytes


@dataclass
class ProcessInfo:
    """Safe model containing process snapshot data."""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_rss_bytes: int
    status: str
    num_threads: int
    create_time: float
    username: Optional[str] = None

    @property
    def memory_human(self) -> str:
        return format_bytes(self.memory_rss_bytes)

    @property
    def created_formatted(self) -> str:
        if self.create_time <= 0:
            return "N/A"
        try:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.create_time))
        except Exception:
            return "N/A"


class ProcessManager:
    """
    Manages process enumeration, sorting, searching, and protected termination.
    """

    def __init__(self) -> None:
        self.current_pid: int = os.getpid()

    def get_process_list(self) -> List[ProcessInfo]:
        """
        Enumerate all active processes on the system safely.
        Catches AccessDenied, NoSuchProcess, ZombieProcess without crashing.
        """
        procs: List[ProcessInfo] = []
        
        # We iterate over process generator
        for p in psutil.process_iter(
            attrs=["pid", "name", "cpu_percent", "memory_percent", "memory_info", "status", "num_threads", "create_time", "username"]
        ):
            try:
                info = p.info
                pid = info.get("pid")
                if pid is None:
                    continue

                name = info.get("name") or "Unknown"
                cpu = info.get("cpu_percent") or 0.0
                mem_pct = info.get("memory_percent") or 0.0
                
                mem_info = info.get("memory_info")
                mem_rss = mem_info.rss if mem_info else 0
                
                status = info.get("status") or "running"
                threads = info.get("num_threads") or 0
                ctime = info.get("create_time") or 0.0
                uname = info.get("username")

                procs.append(
                    ProcessInfo(
                        pid=pid,
                        name=name,
                        cpu_percent=float(cpu),
                        memory_percent=float(mem_pct),
                        memory_rss_bytes=mem_rss,
                        status=str(status),
                        num_threads=int(threads),
                        create_time=float(ctime),
                        username=uname,
                    )
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception:
                # Guard against any unforeseen platform exceptions
                continue

        return procs

    def filter_and_sort_processes(
        self,
        processes: List[ProcessInfo],
        search_query: str = "",
        sort_by: str = "cpu_percent",  # "pid", "name", "cpu_percent", "memory_percent"
        descending: bool = True,
    ) -> List[ProcessInfo]:
        """Filter process list by PID or Name, and sort according to column."""
        query = search_query.strip().lower()
        if query:
            filtered = [
                p for p in processes
                if query in p.name.lower() or query in str(p.pid)
            ]
        else:
            filtered = list(processes)

        def sort_key(p: ProcessInfo):
            if sort_by == "pid":
                return p.pid
            elif sort_by == "name":
                return p.name.lower()
            elif sort_by == "cpu_percent":
                return p.cpu_percent
            elif sort_by == "memory_percent":
                return p.memory_percent
            elif sort_by == "memory_rss":
                return p.memory_rss_bytes
            return p.cpu_percent

        filtered.sort(key=sort_key, reverse=descending)
        return filtered

    def get_process_details(self, pid: int) -> Tuple[bool, str, Optional[dict]]:
        """
        Fetch extended details for a specific PID.
        Returns: (success, message, detail_dict)
        """
        try:
            p = psutil.Process(pid)
            with p.oneshot():
                name = p.name()
                status = p.status()
                threads = p.num_threads()
                cpu = p.cpu_percent(interval=None)
                mem = p.memory_info()
                mem_pct = p.memory_percent()
                create_time = p.create_time()
                
                # Extended info that may trigger AccessDenied on system processes
                cmdline = "N/A"
                cwd = "N/A"
                exe = "N/A"
                username = "N/A"
                try:
                    cmdline = " ".join(p.cmdline()) if p.cmdline() else "N/A"
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    cmdline = "[Protected / Access Denied]"

                try:
                    exe = p.exe()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    exe = "[Protected / Access Denied]"

                try:
                    username = p.username()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    username = "[Protected / Access Denied]"

                ctime_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(create_time))

                details = {
                    "PID": pid,
                    "Name": name,
                    "Status": status,
                    "User": username,
                    "Threads": threads,
                    "CPU (%)": f"{cpu:.1f}%",
                    "Memory (RSS)": format_bytes(mem.rss),
                    "Memory (%)": f"{mem_pct:.1f}%",
                    "Started": ctime_str,
                    "Executable": exe,
                    "Command Line": cmdline,
                }
                return True, "Success", details
        except psutil.NoSuchProcess:
            return False, f"Process {pid} no longer exists.", None
        except psutil.AccessDenied:
            return False, f"Access denied to inspect Process {pid}. (System or elevated process)", None
        except Exception as e:
            return False, f"Error inspecting process: {str(e)}", None

    def terminate_process(self, pid: int) -> Tuple[bool, str]:
        """
        Safely terminate a process after safeguards:
        1. Checks if PID is current process (refuses suicide).
        2. Checks if PID is 0 or 4 (Windows System / Idle process).
        3. Attempts graceful terminate(), waits briefly, then falls back to kill() if necessary.
        4. Catches NoSuchProcess, AccessDenied cleanly.
        """
        if pid == self.current_pid:
            return False, "Cannot terminate the System Resource Monitor itself."

        # Critical Windows system PIDs
        if pid in (0, 4):
            return False, f"Cannot terminate protected Windows Kernel/System process (PID {pid})."

        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
            
            # Send SIGTERM equivalent on Windows
            proc.terminate()
            
            # Wait up to 1.5 seconds for graceful exit
            try:
                proc.wait(timeout=1.5)
                return True, f"Process '{proc_name}' (PID {pid}) terminated successfully."
            except psutil.TimeoutExpired:
                # Force kill if still lingering
                proc.kill()
                proc.wait(timeout=1.0)
                return True, f"Process '{proc_name}' (PID {pid}) did not respond to terminate, force killed."
        except psutil.NoSuchProcess:
            return False, f"Process {pid} has already exited or does not exist."
        except psutil.AccessDenied:
            return False, f"Permission Denied: Process {pid} requires Administrator privileges to terminate."
        except Exception as e:
            return False, f"Failed to terminate process {pid}: {str(e)}"
