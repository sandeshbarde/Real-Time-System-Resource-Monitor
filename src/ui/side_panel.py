"""
Side panel displaying System Information, Health Threshold configurations,
and live alert logs.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from ..alerts import AlertManager, AlertRule
from .theme import (
    COLOR_BG_PRIMARY,
    COLOR_BG_SECONDARY,
    COLOR_BG_TERTIARY,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_DIM,
    COLOR_ACCENT_BLUE,
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_RED,
    COLOR_ACCENT_GREEN,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_SMALL,
    FONT_MONO,
)


class SidePanel(tk.Frame):
    """
    Houses system hardware overview, threshold controls, and alert notification center.
    """

    def __init__(
        self,
        parent: tk.Widget,
        alert_manager: AlertManager,
        on_rules_changed: Optional[Callable[[AlertRule], None]] = None,
        on_refresh_rate_changed: Optional[Callable[[float], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(parent, bg=COLOR_BG_PRIMARY, width=320, **kwargs)
        self.alert_manager = alert_manager
        self.on_rules_changed = on_rules_changed
        self.on_refresh_rate_changed = on_refresh_rate_changed

        self._build_ui()

    def _build_ui(self) -> None:
        # 1. System Info Card
        info_card = tk.LabelFrame(
            self,
            text=" System Overview ",
            bg=COLOR_BG_SECONDARY,
            fg=COLOR_ACCENT_BLUE,
            font=FONT_BODY_BOLD,
            padx=10,
            pady=8,
            relief="solid",
            bd=1,
        )
        info_card.pack(fill="x", padx=10, pady=(6, 8))

        self.info_labels = {}
        fields = [
            ("hostname", "Host:"),
            ("os", "OS:"),
            ("logical_cores", "CPU Cores:"),
            ("total_ram", "Total RAM:"),
            ("uptime", "Uptime:"),
        ]
        for row_idx, (field_key, field_title) in enumerate(fields):
            lbl_title = tk.Label(
                info_card,
                text=field_title,
                bg=COLOR_BG_SECONDARY,
                fg=COLOR_TEXT_MUTED,
                font=FONT_SMALL,
                anchor="w",
            )
            lbl_title.grid(row=row_idx, column=0, sticky="w", pady=1)

            lbl_val = tk.Label(
                info_card,
                text="Loading...",
                bg=COLOR_BG_SECONDARY,
                fg=COLOR_TEXT_PRIMARY,
                font=FONT_BODY_BOLD,
                anchor="w",
                wraplength=190,
                justify="left",
            )
            lbl_val.grid(row=row_idx, column=1, sticky="w", pady=1, padx=(6, 0))
            self.info_labels[field_key] = lbl_val

        # 2. Controls & Thresholds Card
        thresh_card = tk.LabelFrame(
            self,
            text=" Monitor Settings & Alerts ",
            bg=COLOR_BG_SECONDARY,
            fg=COLOR_ACCENT_ORANGE,
            font=FONT_BODY_BOLD,
            padx=10,
            pady=8,
            relief="solid",
            bd=1,
        )
        thresh_card.pack(fill="x", padx=10, pady=4)

        # Refresh Interval
        row = 0
        lbl_refresh = tk.Label(
            thresh_card,
            text="Refresh Interval (s):",
            bg=COLOR_BG_SECONDARY,
            fg=COLOR_TEXT_MUTED,
            font=FONT_SMALL,
        )
        lbl_refresh.grid(row=row, column=0, sticky="w", pady=3)

        self.spin_refresh = ttk.Spinbox(
            thresh_card,
            from_=0.5,
            to=10.0,
            increment=0.5,
            width=6,
        )
        self.spin_refresh.set("1.0")
        self.spin_refresh.grid(row=row, column=1, sticky="e", pady=3)

        # CPU Threshold
        row += 1
        lbl_cpu = tk.Label(
            thresh_card,
            text="CPU Alert Limit (%):",
            bg=COLOR_BG_SECONDARY,
            fg=COLOR_TEXT_MUTED,
            font=FONT_SMALL,
        )
        lbl_cpu.grid(row=row, column=0, sticky="w", pady=3)

        self.spin_cpu = ttk.Spinbox(
            thresh_card,
            from_=10,
            to=99,
            increment=5,
            width=6,
        )
        self.spin_cpu.set(str(int(self.alert_manager.rules.cpu_threshold_pct)))
        self.spin_cpu.grid(row=row, column=1, sticky="e", pady=3)

        # RAM Threshold
        row += 1
        lbl_ram = tk.Label(
            thresh_card,
            text="RAM Alert Limit (%):",
            bg=COLOR_BG_SECONDARY,
            fg=COLOR_TEXT_MUTED,
            font=FONT_SMALL,
        )
        lbl_ram.grid(row=row, column=0, sticky="w", pady=3)

        self.spin_ram = ttk.Spinbox(
            thresh_card,
            from_=10,
            to=99,
            increment=5,
            width=6,
        )
        self.spin_ram.set(str(int(self.alert_manager.rules.ram_threshold_pct)))
        self.spin_ram.grid(row=row, column=1, sticky="e", pady=3)

        # Disk Threshold
        row += 1
        lbl_disk = tk.Label(
            thresh_card,
            text="Disk Alert Limit (%):",
            bg=COLOR_BG_SECONDARY,
            fg=COLOR_TEXT_MUTED,
            font=FONT_SMALL,
        )
        lbl_disk.grid(row=row, column=0, sticky="w", pady=3)

        self.spin_disk = ttk.Spinbox(
            thresh_card,
            from_=10,
            to=99,
            increment=5,
            width=6,
        )
        self.spin_disk.set(str(int(self.alert_manager.rules.disk_threshold_pct)))
        self.spin_disk.grid(row=row, column=1, sticky="e", pady=3)

        # Apply Button
        row += 1
        btn_apply = tk.Button(
            thresh_card,
            text="Apply Settings",
            command=self._on_apply_settings,
            bg=COLOR_ACCENT_BLUE,
            fg="#FFFFFF",
            relief="flat",
            font=FONT_BODY_BOLD,
            padx=8,
            pady=3,
            cursor="hand2",
            activebackground="#2563EB",
            activeforeground="#FFFFFF",
        )
        btn_apply.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(8, 2))

        # 3. Alert Event History Log
        alert_card = tk.LabelFrame(
            self,
            text=" Notification & Alert Log ",
            bg=COLOR_BG_SECONDARY,
            fg=COLOR_TEXT_PRIMARY,
            font=FONT_BODY_BOLD,
            padx=6,
            pady=6,
            relief="solid",
            bd=1,
        )
        alert_card.pack(fill="both", expand=True, padx=10, pady=(6, 8))

        # Alert Listbox
        self.alert_list = tk.Listbox(
            alert_card,
            bg=COLOR_BG_PRIMARY,
            fg=COLOR_TEXT_PRIMARY,
            font=FONT_SMALL,
            selectbackground=COLOR_BG_TERTIARY,
            highlightthickness=0,
            bd=0,
        )
        alert_scroll = ttk.Scrollbar(alert_card, orient="vertical", command=self.alert_list.yview)
        self.alert_list.configure(yscrollcommand=alert_scroll.set)

        self.alert_list.pack(side="left", fill="both", expand=True)
        alert_scroll.pack(side="right", fill="y")

        # Clear Alerts Button
        btn_clear_alerts = tk.Button(
            alert_card,
            text="Clear Log",
            command=self._on_clear_alerts,
            bg=COLOR_BG_TERTIARY,
            fg=COLOR_TEXT_MUTED,
            relief="flat",
            font=FONT_SMALL,
            cursor="hand2",
        )
        btn_clear_alerts.pack(side="bottom", fill="x", pady=(4, 0))

    def update_system_info(self, info: dict) -> None:
        """Update system labels with hardware info."""
        for k, v in info.items():
            if k in self.info_labels:
                self.info_labels[k].config(text=str(v))

    def add_alert_log(self, text: str, level: str = "INFO") -> None:
        """Append an entry to the side alert log."""
        prefix = "[ALERT]" if level == "WARNING" else "[CRIT]" if level == "CRITICAL" else "[INFO]"
        formatted = f"{prefix} {text}"
        self.alert_list.insert(0, formatted)
        # Color the latest item
        if level in ("WARNING", "CRITICAL"):
            self.alert_list.itemconfig(0, fg=COLOR_ACCENT_RED)
        elif level == "INFO":
            self.alert_list.itemconfig(0, fg=COLOR_ACCENT_GREEN)

        if self.alert_list.size() > 200:
            self.alert_list.delete(200, "end")

    def _on_clear_alerts(self) -> None:
        self.alert_list.delete(0, "end")
        self.alert_manager.clear_history()

    def _on_apply_settings(self) -> None:
        # Validate refresh rate
        try:
            rate = float(self.spin_refresh.get())
            if not (0.2 <= rate <= 30.0):
                raise ValueError("Refresh rate must be between 0.2s and 30s.")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return

        # Validate thresholds
        try:
            cpu = float(self.spin_cpu.get())
            ram = float(self.spin_ram.get())
            disk = float(self.spin_disk.get())
            self.alert_manager.update_rules(cpu, ram, disk)
        except ValueError as e:
            messagebox.showerror("Invalid Threshold", str(e))
            return

        if self.on_refresh_rate_changed:
            self.on_refresh_rate_changed(rate)

        if self.on_rules_changed:
            self.on_rules_changed(self.alert_manager.rules)

        self.add_alert_log(f"Settings updated: Refresh={rate}s, CPU={cpu}%, RAM={ram}%", level="INFO")
        messagebox.showinfo("Success", "Monitoring thresholds and refresh interval updated.")
