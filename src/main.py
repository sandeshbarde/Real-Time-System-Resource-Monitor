"""
Real-Time System Resource Monitor
Main Entry Point

Student: Sandesh Barde
PRN/ERP: 25ET2021031
Branch: AI & Data Science (SE)
Subject: Operating System
"""

import sys
import os

# Ensure project root is present in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.ui.main_window import MainWindow


def main() -> None:
    """Launch the Real-Time System Resource Monitor Desktop Application."""
    try:
        app = MainWindow()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nShutdown requested by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error launching System Resource Monitor: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
