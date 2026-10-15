"""
Lightweight, resilient history chart component rendered directly onto Tkinter Canvas.
Eliminates heavy external dependencies while providing smooth, bounded real-time line charts.
"""

from __future__ import annotations
import tkinter as tk
from collections import deque
from typing import Deque, Optional
from .theme import (
    COLOR_BG_SECONDARY,
    COLOR_BG_TERTIARY,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_DIM,
    FONT_SMALL,
)


class MiniChart(tk.Canvas):
    """
    Renders a live time-series graph with a glowing line, baseline grid, and value labels.
    """

    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        color_accent: str,
        max_points: int = 60,
        y_max: float = 100.0,
        height: int = 120,
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            bg=COLOR_BG_SECONDARY,
            highlightthickness=1,
            highlightbackground=COLOR_BG_TERTIARY,
            height=height,
            **kwargs,
        )
        self.title: str = title
        self.color_accent: str = color_accent
        self.max_points: int = max_points
        self.y_max: float = y_max
        self.data: Deque[float] = deque(maxlen=max_points)

        # Pre-fill with baseline 0 to give full width immediately
        for _ in range(max_points):
            self.data.append(0.0)

        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event: tk.Event) -> None:
        self.redraw()

    def add_point(self, value: float) -> None:
        """Append a data point and redraw."""
        self.data.append(max(0.0, float(value)))
        self.redraw()

    def redraw(self) -> None:
        """Clear and repaint canvas elements."""
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()

        if width <= 10 or height <= 10:
            return

        pad_left = 38
        pad_right = 16
        pad_top = 22
        pad_bottom = 20

        plot_w = max(10, width - pad_left - pad_right)
        plot_h = max(10, height - pad_top - pad_bottom)

        # Header Title
        latest_val = self.data[-1] if self.data else 0.0
        self.create_text(
            pad_left,
            11,
            text=f"{self.title}: {latest_val:.1f}%",
            fill=self.color_accent,
            anchor="w",
            font=("Segoe UI", 9, "bold"),
        )

        # Grid lines (0%, 50%, 100%)
        grid_pcts = [0.0, 0.5, 1.0]
        for pct in grid_pcts:
            y = pad_top + plot_h * (1.0 - pct)
            self.create_line(
                pad_left,
                y,
                pad_left + plot_w,
                y,
                fill=COLOR_BG_TERTIARY,
                dash=(2, 4),
            )
            # Label
            val_label = f"{int(pct * self.y_max)}%"
            self.create_text(
                pad_left - 6,
                y,
                text=val_label,
                fill=COLOR_TEXT_DIM,
                anchor="e",
                font=FONT_SMALL,
            )

        # Compute point coordinates
        points = []
        n = len(self.data)
        if n < 2:
            return

        x_step = plot_w / (n - 1)
        for i, val in enumerate(self.data):
            x = pad_left + i * x_step
            # Clamp ratio
            ratio = min(1.0, max(0.0, val / self.y_max))
            y = pad_top + plot_h * (1.0 - ratio)
            points.append((x, y))

        # Flatten coords for line
        flat_coords = [coord for pt in points for coord in pt]

        # Draw filled gradient polygon under the curve
        poly_coords = [points[0][0], pad_top + plot_h] + flat_coords + [points[-1][0], pad_top + plot_h]
        # Canvas polygon with stipple or subtle dark tone
        self.create_polygon(
            poly_coords,
            fill="#1E293B",
            outline="",
        )

        # Draw main glowing line
        self.create_line(
            flat_coords,
            fill=self.color_accent,
            width=2,
            smooth=False,
        )

        # Draw glowing dot on current point
        curr_x, curr_y = points[-1]
        self.create_oval(
            curr_x - 3,
            curr_y - 3,
            curr_x + 3,
            curr_y + 3,
            fill="#FFFFFF",
            outline=self.color_accent,
            width=2,
        )

        # X-Axis Time indicator
        self.create_text(
            pad_left,
            height - 8,
            text=f"-{self.max_points}s",
            fill=COLOR_TEXT_MUTED,
            anchor="w",
            font=FONT_SMALL,
        )
        self.create_text(
            pad_left + plot_w,
            height - 8,
            text="now",
            fill=COLOR_TEXT_MUTED,
            anchor="e",
            font=FONT_SMALL,
        )
