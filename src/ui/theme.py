"""
Design tokens, color palettes, and styles for Real-Time System Resource Monitor.
Polished professional dark navy aesthetic with vibrant, restrained accents.
"""

# Color Palette: Deep Navy & Cyber Slate
COLOR_BG_PRIMARY = "#0B0F19"      # Main application background
COLOR_BG_SECONDARY = "#111827"    # Card and container background
COLOR_BG_TERTIARY = "#1F2937"     # Subtle borders, inputs, separators
COLOR_BG_HOVER = "#2D3748"        # Interactive item hover

COLOR_TEXT_PRIMARY = "#F9FAFB"    # Bright text for metrics and headers
COLOR_TEXT_MUTED = "#9CA3AF"      # Secondary labels and subtitles
COLOR_TEXT_DIM = "#6B7280"        # Inactive elements, placeholders

# Metric Accents
COLOR_ACCENT_BLUE = "#3B82F6"     # CPU / Primary Action (Bright Blue)
COLOR_ACCENT_PURPLE = "#8B5CF6"   # RAM (Electric Violet)
COLOR_ACCENT_CYAN = "#06B6D4"     # Disk / Network Download (Cyan)
COLOR_ACCENT_ORANGE = "#F59E0B"   # Network Upload / Warning (Amber)
COLOR_ACCENT_RED = "#EF4444"      # Critical / Terminate / Alert (Coral Red)
COLOR_ACCENT_GREEN = "#10B981"    # Normal / Safe (Emerald Green)

# Typography
FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 14, "bold")
FONT_METRIC_VALUE = (FONT_FAMILY, 20, "bold")
FONT_METRIC_LABEL = (FONT_FAMILY, 9, "bold")
FONT_METRIC_SUB = (FONT_FAMILY, 8, "normal")
FONT_BODY = (FONT_FAMILY, 9, "normal")
FONT_BODY_BOLD = (FONT_FAMILY, 9, "bold")
FONT_MONO = ("Consolas", 9, "normal")
FONT_SMALL = (FONT_FAMILY, 8, "normal")
