"""
utils/formatters.py — Response formatters for ChronicCare AI
"""

import re
from datetime import datetime


def format_health_summary(raw_text: str) -> str:
    """
    Convert raw AI text to HTML-formatted health summary.
    Handles markdown-like formatting from IBM Granite output.
    """
    if not raw_text:
        return "<p class='text-muted'>No summary available.</p>"

    lines = raw_text.split("\n")
    html_parts = []
    in_list = False

    for line in lines:
        line = line.strip()
        if not line:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append("<br>")
            continue

        # Headers
        if line.startswith("## "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            text = line[3:].replace("**", "")
            html_parts.append(f'<h5 class="text-primary mt-3 mb-2">{text}</h5>')
            continue
        if line.startswith("# "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            text = line[2:].replace("**", "")
            html_parts.append(f'<h4 class="text-primary mt-3 mb-2">{text}</h4>')
            continue

        # Bold headers with numbers (e.g., "1. VITAL SIGNS")
        if re.match(r"^\d+\.", line):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            text = _apply_inline(line)
            html_parts.append(f'<p class="fw-bold text-dark mt-2 mb-1">{text}</p>')
            continue

        # Bullet points
        if line.startswith("• ") or line.startswith("- ") or line.startswith("* "):
            if not in_list:
                html_parts.append('<ul class="mb-2">')
                in_list = True
            text = _apply_inline(line[2:])
            html_parts.append(f"<li>{text}</li>")
            continue

        # Normal paragraph
        if in_list:
            html_parts.append("</ul>")
            in_list = False
        text = _apply_inline(line)
        html_parts.append(f"<p class='mb-1'>{text}</p>")

    if in_list:
        html_parts.append("</ul>")

    return "\n".join(html_parts)


def _apply_inline(text: str) -> str:
    """Apply inline formatting: **bold**, *italic*, `code`."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


def format_medication_schedule(medications: list) -> list:
    """Format medications into a daily schedule."""
    schedule = {
        "Morning": [],
        "Afternoon": [],
        "Evening": [],
        "Night": [],
        "As needed": [],
    }
    for med in medications:
        if not med.get("is_active"):
            continue
        timing = (med.get("timing") or "").lower()
        name = med.get("name", "Unknown")
        dosage = med.get("dosage", "")
        entry = f"{name} {dosage}".strip()

        if "morning" in timing or "8am" in timing:
            schedule["Morning"].append(entry)
        if "afternoon" in timing or "12pm" in timing or "noon" in timing:
            schedule["Afternoon"].append(entry)
        if "evening" in timing or "6pm" in timing:
            schedule["Evening"].append(entry)
        if "night" in timing or "8pm" in timing or "bedtime" in timing:
            schedule["Night"].append(entry)
        if not any(
            t in timing for t in ["morning", "afternoon", "evening", "night", "8am", "8pm", "noon"]
        ):
            schedule["As needed"].append(entry)

    return [
        {"time": period, "medications": meds}
        for period, meds in schedule.items()
        if meds
    ]
