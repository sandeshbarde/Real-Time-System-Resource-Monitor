"""
Alert and threshold management module for Real-Time System Resource Monitor.
Tracks metric breaches, warnings, and maintains alert history.
"""

from __future__ import annotations
import time
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AlertRule:
    """Configurable thresholds for system health monitoring."""
    cpu_threshold_pct: float = 85.0
    ram_threshold_pct: float = 90.0
    disk_threshold_pct: float = 90.0

    def validate(self) -> None:
        """Validate that all thresholds are within reasonable bounds [1.0, 99.0]."""
        for name, val in [
            ("CPU Threshold", self.cpu_threshold_pct),
            ("RAM Threshold", self.ram_threshold_pct),
            ("Disk Threshold", self.disk_threshold_pct),
        ]:
            if not (1.0 <= val <= 99.0):
                raise ValueError(f"{name} must be between 1.0% and 99.0%. Got: {val}")


@dataclass
class AlertEvent:
    """Represents a logged threshold breach or system warning."""
    timestamp: float
    level: str  # "WARNING", "CRITICAL", "INFO"
    resource: str  # "CPU", "RAM", "DISK", "SYSTEM"
    message: str
    current_value: float
    threshold_value: float

    @property
    def formatted_time(self) -> str:
        return time.strftime("%H:%M:%S", time.localtime(self.timestamp))


class AlertManager:
    """Evaluates metrics against rules and maintains alert buffer."""

    def __init__(self, rules: Optional[AlertRule] = None, max_history: int = 100) -> None:
        self.rules: AlertRule = rules or AlertRule()
        self.max_history: int = max_history
        self.history: List[AlertEvent] = []
        self._last_alert_times: dict[str, float] = {}
        self.cooldown_seconds: float = 5.0  # Prevent spamming alerts every refresh cycle

    def update_rules(self, cpu: float, ram: float, disk: float) -> None:
        """Update active thresholds with validation."""
        new_rules = AlertRule(
            cpu_threshold_pct=cpu,
            ram_threshold_pct=ram,
            disk_threshold_pct=disk,
        )
        new_rules.validate()
        self.rules = new_rules

    def check_metrics(
        self,
        cpu_pct: float,
        ram_pct: float,
        disk_pct: float,
        now: Optional[float] = None,
    ) -> List[AlertEvent]:
        """
        Evaluate current metrics against thresholds.
        Returns newly triggered alert events.
        """
        if now is None:
            now = time.time()

        triggered: List[AlertEvent] = []

        # Check CPU
        if cpu_pct >= self.rules.cpu_threshold_pct:
            if self._can_trigger("CPU", now):
                event = AlertEvent(
                    timestamp=now,
                    level="CRITICAL" if cpu_pct >= 95.0 else "WARNING",
                    resource="CPU",
                    message=f"High CPU utilization: {cpu_pct:.1f}% exceeds threshold ({self.rules.cpu_threshold_pct:.1f}%)",
                    current_value=cpu_pct,
                    threshold_value=self.rules.cpu_threshold_pct,
                )
                triggered.append(event)
                self._record(event, now)

        # Check RAM
        if ram_pct >= self.rules.ram_threshold_pct:
            if self._can_trigger("RAM", now):
                event = AlertEvent(
                    timestamp=now,
                    level="CRITICAL" if ram_pct >= 95.0 else "WARNING",
                    resource="RAM",
                    message=f"High RAM usage: {ram_pct:.1f}% exceeds threshold ({self.rules.ram_threshold_pct:.1f}%)",
                    current_value=ram_pct,
                    threshold_value=self.rules.ram_threshold_pct,
                )
                triggered.append(event)
                self._record(event, now)

        # Check Disk
        if disk_pct >= self.rules.disk_threshold_pct:
            if self._can_trigger("DISK", now):
                event = AlertEvent(
                    timestamp=now,
                    level="CRITICAL" if disk_pct >= 98.0 else "WARNING",
                    resource="DISK",
                    message=f"High Disk occupancy: {disk_pct:.1f}% exceeds threshold ({self.rules.disk_threshold_pct:.1f}%)",
                    current_value=disk_pct,
                    threshold_value=self.rules.disk_threshold_pct,
                )
                triggered.append(event)
                self._record(event, now)

        return triggered

    def _can_trigger(self, resource: str, now: float) -> bool:
        last = self._last_alert_times.get(resource, 0.0)
        return (now - last) >= self.cooldown_seconds

    def _record(self, event: AlertEvent, now: float) -> None:
        self._last_alert_times[event.resource] = now
        self.history.append(event)
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def add_info_alert(self, message: str) -> AlertEvent:
        """Add an informational system alert (e.g. settings updated)."""
        now = time.time()
        event = AlertEvent(
            timestamp=now,
            level="INFO",
            resource="SYSTEM",
            message=message,
            current_value=0.0,
            threshold_value=0.0,
        )
        self.history.append(event)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        return event

    def clear_history(self) -> None:
        """Clear alert log."""
        self.history.clear()
