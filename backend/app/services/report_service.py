"""PDF report generation service using ReportLab."""
import io
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from sqlalchemy.orm import Session
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.models.child import Child
from app.models.answer_record import AnswerRecord

# Try to register a CJK font
CJK_FONT = "Helvetica"
try:
    # Try common system CJK fonts
    for font_path in [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    ]:
        import os
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont("CJK", font_path))
            CJK_FONT = "CJK"
            break
except Exception:
    pass


def generate_report_pdf(db: Session, child: Child, period_days: int = 30) -> bytes:
    """Generate a PDF learning report for a child."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CjkTitle", parent=styles["Title"],
        fontName=CJK_FONT, fontSize=20, alignment=TA_CENTER,
        textColor=colors.HexColor("#FF6B35"),
    )
    normal_style = ParagraphStyle(
        "CjkNormal", parent=styles["Normal"],
        fontName=CJK_FONT, fontSize=11, leading=16,
    )
    header_style = ParagraphStyle(
        "CjkHeader", parent=styles["Heading2"],
        fontName=CJK_FONT, fontSize=14,
        textColor=colors.HexColor("#4A90E2"),
    )

    story = []
    now = datetime.now(timezone.utc)
    period_start = now - timedelta(days=period_days)

    # Title
    story.append(Paragraph(f"📊 學習報告 — {child.name}", title_style))
    story.append(Spacer(1, 10*mm))

    # Basic info
    accuracy = round(child.total_correct / child.total_questions * 100, 1) if child.total_questions > 0 else 0
    grade_names = {1: "小一", 2: "小二", 3: "小三", 4: "小四", 5: "小五", 6: "小六", 7: "中一", 8: "中二", 9: "中三"}

    info_data = [
        ["姓名", child.name],
        ["年級", grade_names.get(child.grade, f"Grade {child.grade}")],
        ["報告期間", f"最近 {period_days} 天"],
        ["生成日期", now.strftime("%Y-%m-%d")],
    ]
    info_table = Table(info_data, colWidths=[40*mm, 80*mm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), CJK_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F8F5F0")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 8*mm))

    # Summary stats
    story.append(Paragraph("📈 學習摘要", header_style))
    story.append(Spacer(1, 4*mm))

    # Get period stats
    period_records = (
        db.query(AnswerRecord)
        .filter(
            AnswerRecord.child_id == child.id,
            AnswerRecord.answered_at >= period_start,
        )
        .all()
    )
    period_total = len(period_records)
    period_correct = sum(1 for r in period_records if r.is_correct)
    period_accuracy = round(period_correct / period_total * 100, 1) if period_total > 0 else 0
    period_minutes = round(sum(r.time_taken_sec for r in period_records) / 60, 1)

    summary_data = [
        ["項目", "數值"],
        ["總學習時數（分鐘）", str(period_minutes)],
        ["答題總數", str(period_total)],
        ["答對題數", str(period_correct)],
        ["正確率", f"{period_accuracy}%"],
        ["累計學習時數（分鐘）", str(child.total_study_minutes)],
        ["累計答題數", str(child.total_questions)],
    ]
    summary_table = Table(summary_data, colWidths=[60*mm, 60*mm])
    summary_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), CJK_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4A90E2")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F5F0")]),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 8*mm))

    # Subject breakdown
    story.append(Paragraph("📚 學科分析", header_style))
    story.append(Spacer(1, 4*mm))

    subject_names = {"math": "數學", "chinese": "語文", "english": "英語", "science": "科學"}
    subject_data = [["學科", "題數", "答對", "正確率"]]
    subject_records = defaultdict(lambda: {"total": 0, "correct": 0})
    for r in period_records:
        subject_records[r.subject]["total"] += 1
        if r.is_correct:
            subject_records[r.subject]["correct"] += 1

    for subj, stats in subject_records.items():
        acc = round(stats["correct"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0
        subject_data.append([
            subject_names.get(subj, subj),
            str(stats["total"]),
            str(stats["correct"]),
            f"{acc}%",
        ])

    if len(subject_data) == 1:
        subject_data.append(["暫無數據", "-", "-", "-"])

    subject_table = Table(subject_data, colWidths=[40*mm, 30*mm, 30*mm, 30*mm])
    subject_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), CJK_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FF6B35")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F5F0")]),
    ]))
    story.append(subject_table)
    story.append(Spacer(1, 8*mm))

    # Comments
    story.append(Paragraph("💬 教師評語", header_style))
    story.append(Spacer(1, 4*mm))

    if period_accuracy >= 80:
        comment = f"{child.name}表現非常優秀！正確率高達{period_accuracy}%，繼續保持！"
    elif period_accuracy >= 60:
        comment = f"{child.name}表現良好，正確率為{period_accuracy}%，還有進步空間，加油！"
    elif period_accuracy > 0:
        comment = f"{child.name}需要多加練習，目前正確率為{period_accuracy}%，建議家長陪伴複習。"
    else:
        comment = f"{child.name}最近尚未開始做題，建議開始每日練習。"

    story.append(Paragraph(comment, normal_style))
    story.append(Spacer(1, 20*mm))

    # Footer
    footer_style = ParagraphStyle(
        "Footer", parent=normal_style,
        fontSize=9, textColor=colors.grey, alignment=TA_CENTER,
    )
    story.append(Paragraph("— 親子學習互動平台 | 讓學習，成為親子間最自然的對話 —", footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
