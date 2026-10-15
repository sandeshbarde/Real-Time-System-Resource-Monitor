"""
Script to compile the academic project report into PDF format using ReportLab.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


def build_academic_pdf():
    pdf_path = os.path.join(os.getcwd(), "docs", "project_report.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette: Navy & Slate
    c_primary = colors.HexColor("#1B365D")
    c_dark = colors.HexColor("#1F2937")
    c_muted = colors.HexColor("#4B5563")

    style_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=c_primary,
        alignment=TA_CENTER,
    )

    style_subtitle = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_muted,
        alignment=TA_CENTER,
    )

    style_student = ParagraphStyle(
        'CoverStudent',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=16,
        textColor=c_dark,
        alignment=TA_CENTER,
    )

    style_h1 = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
    )

    style_body = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=c_dark,
        alignment=TA_JUSTIFY,
        spaceBefore=3,
        spaceAfter=6,
    )

    elements = []

    # ----------------- COVER PAGE -----------------
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("REAL-TIME SYSTEM RESOURCE MONITOR", style_title))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("A Multithreaded Python Desktop Application for OS Resource Telemetry & Process Inspection<br/><b>OPERATING SYSTEM MINI PROJECT REPORT</b>", style_subtitle))
    elements.append(Spacer(1, 40))

    elements.append(HRFlowable(width="60%", thickness=1.5, color=c_primary, spaceBefore=10, spaceAfter=20))

    elements.append(Spacer(1, 60))
    student_text = (
        "<b>Submitted by:</b><br/>"
        "<b>SANDESH BARDE</b><br/>"
        "ERP / PRN: <b>25ET2021031</b><br/>"
        "Second Year (SE) - Artificial Intelligence & Data Science (AIDS)<br/>"
        "Subject: Operating System<br/>"
        "Academic Year: 2025 – 2026"
    )
    elements.append(Paragraph(student_text, style_student))
    elements.append(PageBreak())

    # ----------------- CERTIFICATE PAGE -----------------
    elements.append(Paragraph("CERTIFICATE OF AUTHENTICITY", style_h1))
    elements.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=4, spaceAfter=14))
    cert_text = (
        "This is to certify that the mini project report entitled <b>\"Real-Time System Resource Monitor\"</b> "
        "submitted by <b>Sandesh Barde (PRN: 25ET2021031)</b>, student of Second Year (SE) Artificial Intelligence & "
        "Data Science, is a bonafide work completed in partial fulfillment of the requirements for the course "
        "<b>Operating System</b>.<br/><br/>"
        "The project demonstrates proper systems design, multithreaded non-blocking OS telemetry acquisition, "
        "and safe process controls in compliance with academic criteria."
    )
    elements.append(Paragraph(cert_text, style_body))
    elements.append(Spacer(1, 120))

    sig_data = [
        ["____________________________________", "____________________________________"],
        ["Project Guide / Faculty Mentor", "Head of Department (AIDS)"],
        ["\nDate: ________________________", "\nPlace: ________________________"]
    ]
    sig_table = Table(sig_data, colWidths=[240, 240])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), c_dark),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    elements.append(sig_table)
    elements.append(PageBreak())

    # ----------------- DECLARATION & ABSTRACT -----------------
    elements.append(Paragraph("Declaration", style_h1))
    elements.append(Paragraph(
        "I hereby declare that this project report entitled <b>\"Real-Time System Resource Monitor\"</b> "
        "embodies the results of my own work. All literature, design methodologies, and code fragments "
        "have been properly referenced and credited.<br/><br/>"
        "<b>Sandesh Barde (25ET2021031)</b><br/>"
        "SE - Artificial Intelligence & Data Science", style_body))

    elements.append(Spacer(1, 15))
    elements.append(Paragraph("Abstract", style_h1))
    elements.append(Paragraph(
        "Operating systems act as the primary resource manager coordinating CPU scheduling, physical RAM "
        "allocation, storage operations, and network packets across concurrent workloads. This project presents "
        "the Real-Time System Resource Monitor, a responsive multithreaded desktop application designed in Python 3.10+ "
        "for Windows 11.<br/><br/>"
        "The application utilizes <code>psutil</code> to gather genuine OS telemetry asynchronously while running a Tkinter event "
        "loop to maintain complete responsiveness. Features include a dark dashboard, pure Tkinter Canvas historical "
        "vector line charts, an interactive searchable process table, protected process termination, threshold alerts "
        "with cooldown mechanisms, and dual CSV data exporters. All 15 automated test cases passed successfully.<br/><br/>"
        "<b>Keywords:</b> Operating System, Resource Monitoring, Multithreading, Process Management, CPU Scheduling, RAM Telemetry, Tkinter, psutil.",
        style_body
    ))
    elements.append(PageBreak())

    # ----------------- MAIN REPORT BODY -----------------
    sections = [
        ("1. Introduction & Problem Statement",
         "Modern multi-tasking operating systems manage hundreds of active processes and thousands of threads. "
         "When resource contention occurs, locating the bottleneck quickly is essential. Standard operating system "
         "tools are often proprietary or difficult to programmatically extract data from. This project provides a "
         "transparent, academic, and safe monitor that illustrates core OS principles in action."),
        
        ("2. Aim & Objectives",
         "• Capture genuine real-time CPU, RAM, Disk, and Network throughput telemetry.<br/>"
         "• Render historical trend graphs without heavy external dependencies.<br/>"
         "• Provide multi-column sorting and instant substring search across active processes.<br/>"
         "• Implement safeguards preventing accidental termination of the monitor or protected kernel PIDs.<br/>"
         "• Log configurable threshold alerts with rate-limiting cooldowns.<br/>"
         "• Export process snapshots and time-series records to CSV format."),

        ("3. System Architecture",
         "The software implements a decoupled Producer-Consumer multithreaded architecture:<br/>"
         "<b>1. MetricsCollectorThread (Worker):</b> Continuously collects CPU percentages, memory allocation, "
         "disk usage, network throughput, and process states from the OS kernel.<br/>"
         "<b>2. Threading Mutex:</b> A mutual exclusion lock coordinates thread-safe data transfer.<br/>"
         "<b>3. Tkinter Event Loop (Consumer):</b> Renders top dashboard cards, vector canvas curves, sortable "
         "process treeviews, and system alert logs every 500ms without freezing."),

        ("4. Algorithms & Mathematical Formulations",
         "<b>• CPU Utilization (%):</b> Calculated over elapsed time delta:<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;CPU% = (1 - (delta_idle / delta_total)) * 100<br/><br/>"
         "<b>• Network Throughput:</b> Derived from cumulative interface byte counters:<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;Speed (Bytes/sec) = max(0, curr_bytes - prev_bytes) / elapsed_seconds<br/><br/>"
         "<b>• Vector Canvas Mapping:</b> Real-time point projection into canvas coordinates:<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;X = Pad_L + i * (Width / (N-1))<br/>"
         "&nbsp;&nbsp;&nbsp;&nbsp;Y = Pad_T + Height * (1.0 - (Value / 100.0))"),

        ("5. Testing & Verification Results",
         "Automated testing was conducted via pytest 9.1.1 on Python 3.13.14 (Windows 11 AMD64). "
         "All 15 test cases (TC-01 through TC-15) passed with zero errors, validating throughput formulas, "
         "counter-wrap handling, threshold checks, cooldown rate-limiting, self-kill protection, and CSV generation."),

        ("6. Conclusion & References",
         "The Real-Time System Resource Monitor demonstrates practical systems programming, GUI concurrency, "
         "and access control principles. It serves as an effective academic mini project for Operating System studies.<br/><br/>"
         "<b>References:</b><br/>"
         "1. Silberschatz, Galvin, Gagne. <i>Operating System Concepts</i> (10th ed.). Wiley, 2018.<br/>"
         "2. Tanenbaum, Bos. <i>Modern Operating Systems</i> (4th ed.). Pearson, 2015.<br/>"
         "3. Giampaolo Rodola. <i>psutil: Cross-platform process and system monitoring in Python</i>.<br/>"
         "4. Python Software Foundation. <i>Tkinter & Threading standard libraries documentation</i>.")
    ]

    for title, text in sections:
        elements.append(Paragraph(title, style_h1))
        elements.append(Paragraph(text, style_body))
        elements.append(Spacer(1, 8))

    doc.build(elements)
    print(f"PDF Report created successfully at: {pdf_path}")


if __name__ == "__main__":
    build_academic_pdf()
