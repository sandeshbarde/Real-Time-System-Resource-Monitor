"""
Interactive, searchable, sortable Process Table component.
Provides process inspection, protected termination modals, and export capabilities.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, List, Optional
from ..process_manager import ProcessInfo, ProcessManager
from .theme import (
    COLOR_BG_PRIMARY,
    COLOR_BG_SECONDARY,
    COLOR_BG_TERTIARY,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_DIM,
    COLOR_ACCENT_BLUE,
    COLOR_ACCENT_RED,
    COLOR_ACCENT_GREEN,
    COLOR_ACCENT_PURPLE,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_SMALL,
    FONT_MONO,
)


class ProcessView(tk.Frame):
    """
    Process list view with search filter, column sorting, detail viewer,
    and safe termination controls.
    """

    def __init__(
        self,
        parent: tk.Widget,
        process_manager: ProcessManager,
        on_action_log: Optional[Callable[[str], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(parent, bg=COLOR_BG_SECONDARY, **kwargs)
        self.process_manager = process_manager
        self.on_action_log = on_action_log

        self.sort_column = "cpu_percent"
        self.sort_descending = True
        self.search_query = ""
        self._raw_processes: List[ProcessInfo] = []
        self._displayed_processes: List[ProcessInfo] = []

        self._build_ui()

    def _build_ui(self) -> None:
        # Top toolbar: Search + Action buttons
        toolbar = tk.Frame(self, bg=COLOR_BG_SECONDARY, pady=6, padx=8)
        toolbar.pack(fill="x", side="top")

        # Search Label & Entry
        lbl_search = tk.Label(
            toolbar,
            text="Filter Processes:",
            bg=COLOR_BG_SECONDARY,
            fg=COLOR_TEXT_MUTED,
            font=FONT_BODY_BOLD,
        )
        lbl_search.pack(side="left", padx=(0, 6))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        
        search_entry = tk.Entry(
            toolbar,
            textvariable=self.search_var,
            bg=COLOR_BG_TERTIARY,
            fg=COLOR_TEXT_PRIMARY,
            insertbackground=COLOR_TEXT_PRIMARY,
            relief="flat",
            font=FONT_BODY,
            width=24,
        )
        search_entry.pack(side="left", padx=4, ipady=3)

        # Clear search button
        btn_clear = tk.Button(
            toolbar,
            text="Clear",
            command=lambda: self.search_var.set(""),
            bg=COLOR_BG_TERTIARY,
            fg=COLOR_TEXT_MUTED,
            relief="flat",
            activebackground=COLOR_BG_PRIMARY,
            activeforeground=COLOR_TEXT_PRIMARY,
            font=FONT_SMALL,
            padx=8,
            pady=1,
            cursor="hand2",
        )
        btn_clear.pack(side="left", padx=4)

        # Process Count Label
        self.lbl_count = tk.Label(
            toolbar,
            text="Processes: 0",
            bg=COLOR_BG_SECONDARY,
            fg=COLOR_TEXT_DIM,
            font=FONT_SMALL,
        )
        self.lbl_count.pack(side="left", padx=12)

        # Right side actions: Inspect & Terminate
        btn_terminate = tk.Button(
            toolbar,
            text="End Process",
            command=self._on_terminate_clicked,
            bg=COLOR_ACCENT_RED,
            fg="#FFFFFF",
            relief="flat",
            font=FONT_BODY_BOLD,
            padx=10,
            pady=2,
            cursor="hand2",
            activebackground="#DC2626",
            activeforeground="#FFFFFF",
        )
        btn_terminate.pack(side="right", padx=4)

        btn_inspect = tk.Button(
            toolbar,
            text="View Details",
            command=self._on_inspect_clicked,
            bg=COLOR_ACCENT_BLUE,
            fg="#FFFFFF",
            relief="flat",
            font=FONT_BODY_BOLD,
            padx=10,
            pady=2,
            cursor="hand2",
            activebackground="#2563EB",
            activeforeground="#FFFFFF",
        )
        btn_inspect.pack(side="right", padx=4)

        # Table Container
        table_frame = tk.Frame(self, bg=COLOR_BG_SECONDARY)
        table_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        columns = ("pid", "name", "cpu_percent", "memory_percent", "memory_rss", "status", "threads")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        # Configure Headings and Sorting Hooks
        col_headers = {
            "pid": ("PID", 70, "pid"),
            "name": ("Process Name", 180, "name"),
            "cpu_percent": ("CPU %", 75, "cpu_percent"),
            "memory_percent": ("RAM %", 75, "memory_percent"),
            "memory_rss": ("Memory (RSS)", 100, "memory_rss"),
            "status": ("Status", 85, "status"),
            "threads": ("Threads", 70, "threads"),
        }

        for col_id, (title, width, sort_key) in col_headers.items():
            self.tree.heading(
                col_id,
                text=title,
                command=lambda k=sort_key: self._on_sort_clicked(k),
            )
            self.tree.column(
                col_id,
                width=width,
                minwidth=50,
                anchor="e" if col_id in ("pid", "cpu_percent", "memory_percent", "memory_rss", "threads") else "w",
            )

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda event: self._on_inspect_clicked())

    def _on_sort_clicked(self, column: str) -> None:
        if self.sort_column == column:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_column = column
            self.sort_descending = True
        self._refresh_table()

    def _on_search_change(self, *args) -> None:
        self.search_query = self.search_var.get()
        self._refresh_table()

    def update_processes(self, processes: List[ProcessInfo]) -> None:
        """Receive updated process snapshot from background worker."""
        self._raw_processes = processes
        self._refresh_table()

    def _refresh_table(self) -> None:
        selected_pid = self.get_selected_pid()

        self._displayed_processes = self.process_manager.filter_and_sort_processes(
            self._raw_processes,
            search_query=self.search_query,
            sort_by=self.sort_column,
            descending=self.sort_descending,
        )

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        item_to_reselect = None
        for p in self._displayed_processes:
            item_id = self.tree.insert(
                "",
                "end",
                iid=str(p.pid),
                values=(
                    p.pid,
                    p.name,
                    f"{p.cpu_percent:.1f}%",
                    f"{p.memory_percent:.1f}%",
                    p.memory_human,
                    p.status,
                    p.num_threads,
                ),
            )
            if selected_pid == p.pid:
                item_to_reselect = item_id

        # Preserve selection across refresh
        if item_to_reselect and self.tree.exists(item_to_reselect):
            self.tree.selection_set(item_to_reselect)
            self.tree.see(item_to_reselect)

        self.lbl_count.config(
            text=f"Showing: {len(self._displayed_processes)} of {len(self._raw_processes)}"
        )

    def get_selected_pid(self) -> Optional[int]:
        selected = self.tree.selection()
        if not selected:
            return None
        try:
            return int(selected[0])
        except (ValueError, IndexError):
            return None

    def _on_inspect_clicked(self) -> None:
        pid = self.get_selected_pid()
        if pid is None:
            messagebox.showinfo("Select Process", "Please select a process from the table to view details.")
            return

        success, msg, details = self.process_manager.get_process_details(pid)
        if not success or not details:
            messagebox.showwarning("Process Inspection", msg)
            return

        # Modal detail window
        detail_win = tk.Toplevel(self)
        detail_win.title(f"Process Details - PID {pid} ({details.get('Name')})")
        detail_win.geometry("520x420")
        detail_win.configure(bg=COLOR_BG_PRIMARY)
        detail_win.transient(self)
        detail_win.grab_set()

        header = tk.Label(
            detail_win,
            text=f"Process Inspection: {details.get('Name')} (PID {pid})",
            bg=COLOR_BG_PRIMARY,
            fg=COLOR_TEXT_PRIMARY,
            font=FONT_BODY_BOLD,
            pady=12,
        )
        header.pack(fill="x")

        body_frame = tk.Frame(detail_win, bg=COLOR_BG_SECONDARY, padx=16, pady=12)
        body_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        for row_idx, (key, value) in enumerate(details.items()):
            k_lbl = tk.Label(
                body_frame,
                text=key + ":",
                bg=COLOR_BG_SECONDARY,
                fg=COLOR_TEXT_MUTED,
                font=FONT_BODY_BOLD,
                anchor="w",
            )
            k_lbl.grid(row=row_idx, column=0, sticky="nw", pady=2, padx=(0, 10))

            v_lbl = tk.Label(
                body_frame,
                text=str(value),
                bg=COLOR_BG_SECONDARY,
                fg=COLOR_TEXT_PRIMARY,
                font=FONT_MONO if key in ("Executable", "Command Line") else FONT_BODY,
                anchor="w",
                justify="left",
                wraplength=340,
            )
            v_lbl.grid(row=row_idx, column=1, sticky="w", pady=2)

        btn_close = tk.Button(
            detail_win,
            text="Close",
            command=detail_win.destroy,
            bg=COLOR_BG_TERTIARY,
            fg=COLOR_TEXT_PRIMARY,
            relief="flat",
            padx=16,
            pady=4,
            cursor="hand2",
        )
        btn_close.pack(pady=8)

    def _on_terminate_clicked(self) -> None:
        pid = self.get_selected_pid()
        if pid is None:
            messagebox.showinfo("Select Process", "Please select a process from the table to terminate.")
            return

        # Find process name
        p_name = "Unknown"
        for p in self._raw_processes:
            if p.pid == pid:
                p_name = p.name
                break

        # Check self-kill prevention early
        if pid == self.process_manager.current_pid:
            messagebox.showerror(
                "Action Prohibited",
                "Cannot terminate the System Resource Monitor itself. "
                "Close the application window normally to exit.",
            )
            return

        # Explicit Confirmation Modal
        confirm = messagebox.askyesno(
            "Confirm Termination",
            f"Are you sure you want to terminate:\n\n"
            f"Process: {p_name}\n"
            f"PID: {pid}\n\n"
            f"WARNING: Ending a process may cause unsaved data loss in that application.",
            icon="warning",
        )

        if not confirm:
            return

        success, msg = self.process_manager.terminate_process(pid)
        if success:
            messagebox.showinfo("Process Terminated", msg)
            if self.on_action_log:
                self.on_action_log(msg)
            # Remove from local lists immediately
            self._raw_processes = [p for p in self._raw_processes if p.pid != pid]
            self._refresh_table()
        else:
            messagebox.showerror("Termination Failed", msg)
            if self.on_action_log:
                self.on_action_log(f"Failed to end PID {pid}: {msg}")
