"""
Main Application Window for Real-Time System Resource Monitor.
Orchestrates monitoring thread, metrics history, top dashboard cards,
live canvas charts, process table, side panel, and data exports.
"""

from __future__ import annotations
import os
import sys
import threading
import time
from collections import deque
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Deque, Optional, List

from ..monitoring import SystemMonitor, SystemMetrics, format_bytes
from ..process_manager import ProcessManager, ProcessInfo
from ..alerts import AlertManager, AlertRule
from ..exporter import export_processes_to_csv, export_metrics_history_to_csv

from .theme import (
    COLOR_BG_PRIMARY,
    COLOR_BG_SECONDARY,
    COLOR_BG_TERTIARY,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_DIM,
    COLOR_ACCENT_BLUE,
    COLOR_ACCENT_PURPLE,
    COLOR_ACCENT_CYAN,
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_RED,
    COLOR_ACCENT_GREEN,
    FONT_TITLE,
    FONT_METRIC_VALUE,
    FONT_METRIC_LABEL,
    FONT_METRIC_SUB,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_SMALL,
)
from .chart_widget import MiniChart
from .process_view import ProcessView
from .side_panel import SidePanel


class MainWindow(tk.Tk):
    """
    Main Tkinter application window with asynchronous data ingestion.
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("Real-Time System Resource Monitor - OS Mini Project")
        self.geometry("1240x800")
        self.minsize(1020, 680)
        self.configure(bg=COLOR_BG_PRIMARY)

        # Core logic components
        self.monitor = SystemMonitor()
        self.process_manager = ProcessManager()
        self.alert_manager = AlertManager()

        # Operational parameters
        self.refresh_interval: float = 1.0  # seconds
        self.running: bool = True
        self.metrics_history: Deque[SystemMetrics] = deque(maxlen=300)
        self.current_processes: List[ProcessInfo] = []
        self.latest_metrics: Optional[SystemMetrics] = None

        # Lock for thread safety
        self._data_lock = threading.Lock()

        # Configure TTK styles for consistent dark mode
        self._setup_ttk_styles()

        # Build UI layout
        self._build_header()
        self._build_top_metric_cards()
        self._build_main_workspace()
        self._build_status_bar()

        # Intercept window close event for clean shutdown
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Populate static system info
        static_info = self.monitor.get_static_system_info()
        self.side_panel.update_system_info(static_info)

        # Launch background collector worker thread
        self.collector_thread = threading.Thread(
            target=self._worker_loop,
            daemon=True,
            name="MetricsCollectorThread",
        )
        self.collector_thread.start()

        # Start periodic GUI update cycle
        self.after(100, self._gui_refresh_cycle)

    def _setup_ttk_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        # Treeview Styling
        style.configure(
            "Treeview",
            background=COLOR_BG_SECONDARY,
            foreground=COLOR_TEXT_PRIMARY,
            fieldbackground=COLOR_BG_SECONDARY,
            borderwidth=0,
            rowheight=26,
            font=FONT_BODY,
        )
        style.map(
            "Treeview",
            background=[("selected", COLOR_BG_TERTIARY)],
            foreground=[("selected", COLOR_TEXT_PRIMARY)],
        )

        style.configure(
            "Treeview.Heading",
            background=COLOR_BG_TERTIARY,
            foreground=COLOR_TEXT_PRIMARY,
            borderwidth=1,
            relief="flat",
            font=FONT_BODY_BOLD,
        )
        style.map(
            "Treeview.Heading",
            background=[("active", COLOR_BG_PRIMARY)],
            foreground=[("active", COLOR_ACCENT_BLUE)],
        )

        # Scrollbar Styling
        style.configure(
            "Vertical.TScrollbar",
            gripcount=0,
            background=COLOR_BG_TERTIARY,
            darkcolor=COLOR_BG_SECONDARY,
            lightcolor=COLOR_BG_TERTIARY,
            troughcolor=COLOR_BG_PRIMARY,
            bordercolor=COLOR_BG_PRIMARY,
            arrowcolor=COLOR_TEXT_MUTED,
        )

    def _build_header(self) -> None:
        header = tk.Frame(self, bg=COLOR_BG_SECONDARY, height=52, padx=16)
        header.pack(fill="x", side="top")

        # Title & Subtitle
        title_box = tk.Frame(header, bg=COLOR_BG_SECONDARY)
        title_box.pack(side="left", pady=8)

        lbl_app = tk.Label(
            title_box,
            text="REAL-TIME SYSTEM RESOURCE MONITOR",
            bg=COLOR_BG_SECONDARY,
            fg=COLOR_TEXT_PRIMARY,
            font=FONT_TITLE,
        )
        lbl_app.pack(anchor="w")

        lbl_sub = tk.Label(
            title_box,
            text="Sandesh Barde | AIDS SE (25ET2021031) | Operating System Mini Project",
            bg=COLOR_BG_SECONDARY,
            fg=COLOR_TEXT_MUTED,
            font=FONT_SMALL,
        )
        lbl_sub.pack(anchor="w")

        # Action Buttons on Right
        btn_box = tk.Frame(header, bg=COLOR_BG_SECONDARY)
        btn_box.pack(side="right", pady=10)

        btn_export_proc = tk.Button(
            btn_box,
            text="Export Processes (CSV)",
            command=self._export_processes_csv,
            bg=COLOR_BG_TERTIARY,
            fg=COLOR_TEXT_PRIMARY,
            relief="flat",
            font=FONT_SMALL,
            padx=10,
            pady=3,
            cursor="hand2",
            activebackground=COLOR_BG_PRIMARY,
        )
        btn_export_proc.pack(side="left", padx=4)

        btn_export_metrics = tk.Button(
            btn_box,
            text="Export Metrics History (CSV)",
            command=self._export_metrics_csv,
            bg=COLOR_BG_TERTIARY,
            fg=COLOR_TEXT_PRIMARY,
            relief="flat",
            font=FONT_SMALL,
            padx=10,
            pady=3,
            cursor="hand2",
            activebackground=COLOR_BG_PRIMARY,
        )
        btn_export_metrics.pack(side="left", padx=4)

    def _build_top_metric_cards(self) -> None:
        container = tk.Frame(self, bg=COLOR_BG_PRIMARY, padx=12, pady=10)
        container.pack(fill="x", side="top")

        # 4 Cards: CPU, RAM, DISK, NETWORK
        self.card_cpu = self._create_card(container, "CPU UTILIZATION", "0.0%", "Logical Cores: --", COLOR_ACCENT_BLUE)
        self.card_ram = self._create_card(container, "MEMORY (RAM)", "0.0%", "Used: 0 GB / 0 GB", COLOR_ACCENT_PURPLE)
        self.card_disk = self._create_card(container, "PRIMARY DISK", "0.0%", "Used: 0 GB / 0 GB", COLOR_ACCENT_CYAN)
        self.card_net = self._create_card(container, "NETWORK I/O", "0.0 B/s", "▲ 0.0 B/s | ▼ 0.0 B/s", COLOR_ACCENT_ORANGE)

        self.card_cpu.pack(side="left", fill="both", expand=True, padx=4)
        self.card_ram.pack(side="left", fill="both", expand=True, padx=4)
        self.card_disk.pack(side="left", fill="both", expand=True, padx=4)
        self.card_net.pack(side="left", fill="both", expand=True, padx=4)

    def _create_card(
        self,
        parent: tk.Widget,
        title: str,
        initial_val: str,
        initial_sub: str,
        accent_color: str,
    ) -> tk.Frame:
        card = tk.Frame(
            parent,
            bg=COLOR_BG_SECONDARY,
            padx=12,
            pady=10,
            relief="solid",
            bd=1,
            highlightbackground=COLOR_BG_TERTIARY,
        )

        lbl_title = tk.Label(
            card,
            text=title,
            bg=COLOR_BG_SECONDARY,
            fg=COLOR_TEXT_MUTED,
            font=FONT_METRIC_LABEL,
        )
        lbl_title.pack(anchor="w")

        lbl_val = tk.Label(
            card,
            text=initial_val,
            bg=COLOR_BG_SECONDARY,
            fg=accent_color,
            font=FONT_METRIC_VALUE,
        )
        lbl_val.pack(anchor="w", pady=(2, 0))

        lbl_sub = tk.Label(
            card,
            text=initial_sub,
            bg=COLOR_BG_SECONDARY,
            fg=COLOR_TEXT_DIM,
            font=FONT_METRIC_SUB,
        )
        lbl_sub.pack(anchor="w")

        # Save widget references into dictionary attribute
        card._lbl_val = lbl_val  # type: ignore
        card._lbl_sub = lbl_sub  # type: ignore
        return card

    def _build_main_workspace(self) -> None:
        workspace = tk.Frame(self, bg=COLOR_BG_PRIMARY, padx=12, pady=4)
        workspace.pack(fill="both", expand=True)

        # Left / Center Area (Charts + Process Table)
        main_center = tk.Frame(workspace, bg=COLOR_BG_PRIMARY)
        main_center.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Chart Row (CPU & RAM Charts)
        charts_row = tk.Frame(main_center, bg=COLOR_BG_PRIMARY)
        charts_row.pack(fill="x", side="top", pady=(0, 8))

        self.cpu_chart = MiniChart(
            charts_row,
            title="CPU Load History (60s)",
            color_accent=COLOR_ACCENT_BLUE,
            max_points=60,
            y_max=100.0,
            height=130,
        )
        self.cpu_chart.pack(side="left", fill="both", expand=True, padx=(0, 4))

        self.ram_chart = MiniChart(
            charts_row,
            title="RAM Load History (60s)",
            color_accent=COLOR_ACCENT_PURPLE,
            max_points=60,
            y_max=100.0,
            height=130,
        )
        self.ram_chart.pack(side="left", fill="both", expand=True, padx=(4, 0))

        # Process Table
        self.process_view = ProcessView(
            main_center,
            process_manager=self.process_manager,
            on_action_log=self._on_action_logged,
        )
        self.process_view.pack(fill="both", expand=True)

        # Right Area (Side Panel)
        self.side_panel = SidePanel(
            workspace,
            alert_manager=self.alert_manager,
            on_rules_changed=self._on_rules_updated,
            on_refresh_rate_changed=self._on_refresh_rate_updated,
        )
        self.side_panel.pack(side="right", fill="y")

    def _build_status_bar(self) -> None:
        status_bar = tk.Frame(self, bg=COLOR_BG_SECONDARY, height=24, padx=12)
        status_bar.pack(fill="x", side="bottom")

        self.lbl_status = tk.Label(
            status_bar,
            text="Ready. Monitoring active.",
            bg=COLOR_BG_SECONDARY,
            fg=COLOR_TEXT_MUTED,
            font=FONT_SMALL,
        )
        self.lbl_status.pack(side="left", pady=3)

        self.lbl_last_time = tk.Label(
            status_bar,
            text="Last Sample: --",
            bg=COLOR_BG_SECONDARY,
            fg=COLOR_TEXT_DIM,
            font=FONT_SMALL,
        )
        self.lbl_last_time.pack(side="right", pady=3)

    def _worker_loop(self) -> None:
        """Background thread collecting metrics and processes to keep UI responsive."""
        while self.running:
            try:
                metrics = self.monitor.collect_metrics()
                processes = self.process_manager.get_process_list()

                with self._data_lock:
                    self.latest_metrics = metrics
                    self.metrics_history.append(metrics)
                    self.current_processes = processes

                # Threshold / Alert checks
                alerts = self.alert_manager.check_metrics(
                    metrics.cpu_percent,
                    metrics.ram_percent,
                    metrics.disk_percent,
                    now=metrics.timestamp,
                )
                if alerts:
                    for ev in alerts:
                        self.side_panel.add_alert_log(ev.message, level=ev.level)

            except Exception as e:
                # Catch unforeseen worker errors
                print(f"[Worker Error] {e}", file=sys.stderr)

            # Sleep according to configured refresh interval
            time.sleep(max(0.2, self.refresh_interval))

    def _gui_refresh_cycle(self) -> None:
        """Main UI thread update hook scheduled via after()."""
        if not self.running:
            return

        with self._data_lock:
            m = self.latest_metrics
            procs = list(self.current_processes)

        if m is not None:
            # Update Top Cards
            self.card_cpu._lbl_val.config(text=f"{m.cpu_percent:.1f}%")  # type: ignore
            freq_str = f" | {m.cpu_freq_mhz:.0f} MHz" if m.cpu_freq_mhz else ""
            self.card_cpu._lbl_sub.config(text=f"Logical Cores: {m.cpu_cores_logical}{freq_str}")  # type: ignore

            self.card_ram._lbl_val.config(text=f"{m.ram_percent:.1f}%")  # type: ignore
            self.card_ram._lbl_sub.config(text=f"Used: {format_bytes(m.ram_used_bytes)} / {format_bytes(m.ram_total_bytes)}")  # type: ignore

            self.card_disk._lbl_val.config(text=f"{m.disk_percent:.1f}%")  # type: ignore
            self.card_disk._lbl_sub.config(text=f"Used: {format_bytes(m.disk_used_bytes)} / {format_bytes(m.disk_total_bytes)}")  # type: ignore

            # Total Throughput
            total_net_speed = m.net_throughput.bytes_sent_per_sec + m.net_throughput.bytes_recv_per_sec
            self.card_net._lbl_val.config(text=f"{total_net_speed / 1024:.1f} KB/s" if total_net_speed < 1024*1024 else f"{total_net_speed / (1024*1024):.2f} MB/s")  # type: ignore
            self.card_net._lbl_sub.config(text=f"▲ {m.net_throughput.human_sent} | ▼ {m.net_throughput.human_recv}")  # type: ignore

            # Update Charts
            self.cpu_chart.add_point(m.cpu_percent)
            self.ram_chart.add_point(m.ram_percent)

            # Update Status Bar
            sample_time_str = time.strftime("%H:%M:%S", time.localtime(m.timestamp))
            self.lbl_last_time.config(text=f"Last Sample: {sample_time_str}")

        if procs:
            self.process_view.update_processes(procs)

        # Schedule next cycle (every 500ms to keep UI responsive and smooth)
        self.after(500, self._gui_refresh_cycle)

    def _on_rules_updated(self, rules: AlertRule) -> None:
        self.lbl_status.config(text=f"Alert thresholds updated (CPU: {rules.cpu_threshold_pct}%, RAM: {rules.ram_threshold_pct}%)")

    def _on_refresh_rate_updated(self, rate: float) -> None:
        self.refresh_interval = rate
        self.lbl_status.config(text=f"Refresh rate set to {rate:.1f} seconds")

    def _on_action_logged(self, message: str) -> None:
        self.lbl_status.config(text=message)
        self.side_panel.add_alert_log(message, level="INFO")

    def _export_processes_csv(self) -> None:
        with self._data_lock:
            procs = list(self.current_processes)

        if not procs:
            messagebox.showwarning("Export Empty", "No process data available to export yet.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"process_snapshot_{time.strftime('%Y%m%d_%H%M%S')}.csv",
            title="Export Process Snapshot",
        )
        if not filepath:
            return

        try:
            exported_path = export_processes_to_csv(procs, filepath)
            messagebox.showinfo("Export Successful", f"Processes successfully exported to:\n{exported_path}")
            self._on_action_logged(f"Exported {len(procs)} processes to CSV.")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not write CSV: {str(e)}")

    def _export_metrics_csv(self) -> None:
        with self._data_lock:
            metrics_list = list(self.metrics_history)

        if not metrics_list:
            messagebox.showwarning("Export Empty", "No metric history captured yet.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"metrics_history_{time.strftime('%Y%m%d_%H%M%S')}.csv",
            title="Export Metrics History",
        )
        if not filepath:
            return

        try:
            exported_path = export_metrics_history_to_csv(metrics_list, filepath)
            messagebox.showinfo("Export Successful", f"Metrics history successfully exported to:\n{exported_path}")
            self._on_action_logged(f"Exported {len(metrics_list)} metric records to CSV.")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not write CSV: {str(e)}")

    def on_close(self) -> None:
        """Gracefully terminate background threads and cleanly close window."""
        self.running = False
        self.destroy()
