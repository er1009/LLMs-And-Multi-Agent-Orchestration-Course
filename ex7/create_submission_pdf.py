#!/usr/bin/env python3
"""
Generate SUBMISSION.pdf for EX7 - AI Agent League System.

Run: python create_submission_pdf.py
Requires: pip install reportlab
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors


# Fixed metadata - DO NOT MODIFY
GROUP_NAME = "eldad_ron_bar_yacobi"
MEMBER_1_ID = "207021916"
MEMBER_1_NAME = "Eldad Ron"
MEMBER_2_ID = "315471367"
MEMBER_2_NAME = "Bar Yacobi"
REPO_URL = "https://github.com/er1009/LLMs-And-Multi-Agent-Orchestration-Course/tree/main/ex7"
GRADE = 100


def create_submission_pdf():
    """Create the SUBMISSION.pdf file."""
    doc = SimpleDocTemplate(
        "SUBMISSION.pdf",
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=20,
        alignment=1,
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=11,
        spaceAfter=8,
        leading=14,
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=styles["Normal"],
        fontSize=11,
        leftIndent=20,
        spaceAfter=6,
        leading=14,
    )

    story = []

    # Title
    story.append(Paragraph("EX7 - AI Agent League System", title_style))
    story.append(Paragraph("Course Submission", styles["Heading2"]))
    story.append(Spacer(1, 20))

    # Group Information
    story.append(Paragraph("1. Group Information", heading_style))
    group_data = [
        ["Group Name:", GROUP_NAME],
        ["Member 1:", f"{MEMBER_1_NAME} (ID: {MEMBER_1_ID})"],
        ["Member 2:", f"{MEMBER_2_NAME} (ID: {MEMBER_2_ID})"],
    ]
    group_table = Table(group_data, colWidths=[4 * cm, 12 * cm])
    group_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ]))
    story.append(group_table)
    story.append(Spacer(1, 10))

    # Repository
    story.append(Paragraph("2. Repository", heading_style))
    story.append(Paragraph(f"<b>GitHub URL:</b> {REPO_URL}", body_style))
    story.append(Spacer(1, 10))

    # Self-Recommended Grade
    story.append(Paragraph("3. Self-Recommended Grade", heading_style))
    story.append(Paragraph(f"<b>Grade: {GRADE}/100</b>", body_style))
    story.append(Spacer(1, 10))

    # Justification
    story.append(Paragraph("4. Justification", heading_style))

    justification_intro = """
    This project implements a complete Multi-Agent System for an AI Agent League, 
    demonstrating advanced concepts in agent communication, protocol design, and 
    distributed systems architecture. The implementation meets the highest quality 
    standards for the following reasons:
    """
    story.append(Paragraph(justification_intro, body_style))

    justifications = [
        "<b>Complete Multi-Agent Architecture:</b> The system implements three distinct agent types "
        "(League Manager, Referee, Player) that operate as independent FastAPI processes. Each agent "
        "maintains its own state and communicates via the standardized MCP protocol, demonstrating "
        "true distributed system design principles.",

        "<b>Protocol Compliance:</b> Full implementation of JSON-RPC 2.0 over HTTP with MCP message "
        "envelopes. The protocol includes proper authentication via tokens, standardized error codes, "
        "conversation tracking, and timestamp validation. All messages follow the league.v2 protocol spec.",

        "<b>Game Implementation:</b> The Even/Odd game is fully implemented with random number drawing, "
        "parity checking, winner determination, and score calculation. The round-robin scheduler ensures "
        "fair matchups where every player faces every other player exactly once.",

        "<b>Extensibility Through Design Patterns:</b> The Strategy pattern enables seven different "
        "player strategies (random, always_even, always_odd, alternating, biased_even, biased_odd, counter). "
        "New strategies can be added without modifying existing code. The architecture supports adding "
        "new game types through configuration.",

        "<b>Production-Grade SDK:</b> The shared league_sdk provides reusable components including "
        "Pydantic models for type-safe message validation, an HTTP client wrapper, JSON-lines structured "
        "logging, and configuration loaders. All components use modern Python features (type hints, "
        "dataclasses, enums).",

        "<b>Comprehensive Documentation:</b> The project includes a detailed PRD with user stories, "
        "functional requirements, and acceptance criteria. The Architecture document provides C4 diagrams, "
        "technology justifications, and Architecture Decision Records (ADRs).",

        "<b>Testing & Quality:</b> Unit tests cover game logic, Pydantic models, player strategies, and "
        "the scheduler. The codebase follows SOLID principles with clear separation of concerns between "
        "handlers, state management, and business logic.",
    ]

    for j in justifications:
        story.append(Paragraph(f"• {j}", bullet_style))

    story.append(Spacer(1, 15))

    # Special Notes
    story.append(Paragraph("5. Special Notes", heading_style))
    notes = [
        "The orchestration script (run_league.py) provides a one-command experience to run a complete league.",
        "All agents auto-register on startup and handle communication asynchronously.",
        "Match results and standings are persisted to JSON files in SHARED/data/.",
        "Structured logs in JSON-lines format enable easy parsing and analysis.",
    ]
    for note in notes:
        story.append(Paragraph(f"• {note}", bullet_style))
    story.append(Spacer(1, 10))

    # Special Documents
    story.append(Paragraph("6. Special Documents", heading_style))
    docs = [
        "docs/PRD.md - Product Requirements Document with user stories and acceptance criteria",
        "docs/ARCHITECTURE.md - Architecture document with C4 diagrams and ADRs",
        "README.md - Quick start guide and project overview",
    ]
    for d in docs:
        story.append(Paragraph(f"• {d}", bullet_style))
    story.append(Spacer(1, 10))

    # Comments
    story.append(Paragraph("7. Additional Comments", heading_style))
    comments = """
    This project demonstrates a comprehensive understanding of multi-agent systems, 
    protocol design, and software engineering best practices. The modular architecture 
    allows for easy extension with new game types, additional agents, or alternative 
    communication protocols. The implementation balances simplicity with production-readiness, 
    making it suitable for both educational purposes and real-world applications.
    """
    story.append(Paragraph(comments, body_style))

    doc.build(story)
    print("Created SUBMISSION.pdf successfully!")


if __name__ == "__main__":
    create_submission_pdf()

