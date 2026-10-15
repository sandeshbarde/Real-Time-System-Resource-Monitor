"""
Monitoring module for Real-Time System Resource Monitor.
Collects CPU, RAM, Disk, and Network metrics safely using psutil.
"""

from __future__ import annotations
import platform
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional
import psutil


@dataclass
class NetworkThroughput:
    """Stores calculated network throughput values."""
    bytes_sent_per_sec: float = 0.0
    bytes_recv_per_sec: float = 0.0

    @property
    def kbps_sent(self) -> float:
        return (self.bytes_sent_per_sec * 8) / 1000.0

    @property
    def kbps_recv(self) -> float:
        return (self.bytes_recv_per_sec * 8) / 1000.0

    @property
    def human_sent(self) -> str:
        return format_bytes_speed(self.bytes_sent_per_sec)

    @property
    def human_recv(self) -> str:
        return format_bytes_speed(self.bytes_recv_per_sec)


@dataclass
class SystemMetrics:
    """Snapshot of system resource metrics."""
    timestamp: float
    cpu_percent: float
    ram_percent: float
    ram_used_bytes: int
    ram_total_bytes: int
    disk_percent: float
    disk_used_bytes: int
    disk_total_bytes: int
    net_throughput: NetworkThroughput
    cpu_cores_logical: int
    cpu_freq_mhz: Optional[float] = None


def format_bytes_speed(bytes_per_sec: float) -> str:
    """Format bytes per second into human readable string (KB/s, MB/s)."""
    if bytes_per_sec < 1024:
        return f"{bytes_per_sec:.1f} B/s"
    elif bytes_per_sec < 1024 * 1024:
        return f"{bytes_per_sec / 1024:.1f} KB/s"
    elif bytes_per_sec < 1024 * 1024 * 1024:
        return f"{bytes_per_sec / (1024 * 1024):.2f} MB/s"
    else:
        return f"{bytes_per_sec / (1024 * 1024 * 1024):.2f} GB/s"


def format_bytes(bytes_val: int | float) -> str:
    """Format total bytes into readable string (MB, GB, TB)."""
    val = float(bytes_val)
    if val < 1024:
        return f"{val:.0f} B"
    elif val < 1024 * 1024:
        return f"{val / 1024:.1f} KB"
    elif val < 1024 * 1024 * 1024:
        return f"{val / (1024 * 1024):.1f} MB"
    elif val < 1024 * 1024 * 1024 * 1024:
        return f"{val / (1024 * 1024 * 1024):.2f} GB"
    else:
        return f"{val / (1024 * 1024 * 1024 * 1024):.2f} TB"


def calculate_throughput(
    prev_bytes_sent: int,
    prev_bytes_recv: int,
    curr_bytes_sent: int,
    curr_bytes_recv: int,
    elapsed_seconds: float,
) -> NetworkThroughput:
    """
    Calculate network throughput based on counter delta over time.
    Handles counter wraps or non-positive elapsed intervals safely.
    """
    if elapsed_seconds <= 0:
        return NetworkThroughput(0.0, 0.0)

    delta_sent = curr_bytes_sent - prev_bytes_sent
    delta_recv = curr_bytes_recv - prev_bytes_recv

    # Guard against counter resets/wraps
    if delta_sent < 0:
        delta_sent = 0
    if delta_recv < 0:
        delta_recv = 0

    return NetworkThroughput(
        bytes_sent_per_sec=delta_sent / elapsed_seconds,
        bytes_recv_per_sec=delta_recv / elapsed_seconds,
    )


class SystemMonitor:
    """
    Encapsulates real-time system metrics collection.
    Maintains baseline network counters to compute rate of change.
    """

    def __init__(self) -> None:
        self.logical_cores: int = psutil.cpu_count(logical=True) or 1
        self.physical_cores: int = psutil.cpu_count(logical=False) or 1
        
        # Prime psutil CPU percent calculation without blocking
        try:
            psutil.cpu_percent(interval=None)
        except Exception:
            pass

        self._last_net_time: float = time.time()
        try:
            net_io = psutil.net_io_counters()
            self._last_bytes_sent: int = net_io.bytes_sent
            self._last_bytes_recv: int = net_io.bytes_recv
        except Exception:
            self._last_bytes_sent = 0
            self._last_bytes_recv = 0

    def get_static_system_info(self) -> Dict[str, Any]:
        """Fetch static host & OS metadata for display."""
        try:
            uname = platform.uname()
            boot_time = psutil.boot_time()
            uptime_seconds = int(time.time() - boot_time)
            hours, remainder = divmod(uptime_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime_str = f"{hours}h {minutes}m {seconds}s"
        except Exception:
            uname = None
            uptime_str = "Unavailable"

        total_ram = 0
        try:
            vm = psutil.virtual_memory()
            total_ram = vm.total
        except Exception:
            pass

        return {
            "hostname": platform.node() or "Unknown",
            "os": f"{platform.system()} {platform.release()} ({platform.version()})",
            "architecture": platform.machine(),
            "processor": platform.processor() or "Unknown",
            "logical_cores": self.logical_cores,
            "physical_cores": self.physical_cores,
            "total_ram": format_bytes(total_ram),
            "total_ram_raw": total_ram,
            "uptime": uptime_str,
        }

    def collect_metrics(self) -> SystemMetrics:
        """
        Collect current system metrics non-blockingly.
        """
        now = time.time()
        
        # CPU
        try:
            # interval=None returns immediately based on time elapsed since last call
            cpu_pct = float(psutil.cpu_percent(interval=None))
        except Exception:
            cpu_pct = 0.0

        cpu_freq = None
        try:
            freq = psutil.cpu_freq()
            if freq:
                cpu_freq = freq.current
        except Exception:
            pass

        # RAM
        ram_pct = 0.0
        ram_used = 0
        ram_total = 0
        try:
            vm = psutil.virtual_memory()
            ram_pct = float(vm.percent)
            ram_used = vm.used
            ram_total = vm.total
        except Exception:
            pass

        # Disk (Primary drive / Root filesystem)
        disk_pct = 0.0
        disk_used = 0
        disk_total = 0
        try:
            # On Windows, monitor the main root drive, typically C:\\
            root_drive = "C:\\" if platform.system() == "Windows" else "/"
            disk_info = psutil.disk_usage(root_drive)
            disk_pct = float(disk_info.percent)
            disk_used = disk_info.used
            disk_total = disk_info.total
        except Exception:
            # Fallback
            try:
                disk_info = psutil.disk_usage(".")
                disk_pct = float(disk_info.percent)
                disk_used = disk_info.used
                disk_total = disk_info.total
            except Exception:
                pass

        # Network Throughput
        net_throughput = NetworkThroughput()
        try:
            net_io = psutil.net_io_counters()
            curr_sent = net_io.bytes_sent
            curr_recv = net_io.bytes_recv
            elapsed = now - self._last_net_time
            net_throughput = calculate_throughput(
                self._last_bytes_sent,
                self._last_bytes_recv,
                curr_sent,
                curr_recv,
                elapsed,
            )
            self._last_bytes_sent = curr_sent
            self._last_bytes_recv = curr_recv
            self._last_net_time = now
        except Exception:
            pass

        return SystemMetrics(
            timestamp=now,
            cpu_percent=cpu_pct,
            ram_percent=ram_pct,
            ram_used_bytes=ram_used,
            ram_total_bytes=ram_total,
            disk_percent=disk_pct,
            disk_used_bytes=disk_used,
            disk_total_bytes=disk_total,
            net_throughput=net_throughput,
            cpu_cores_logical=self.logical_cores,
            cpu_freq_mhz=cpu_freq,
        )
